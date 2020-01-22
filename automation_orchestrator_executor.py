import os
import subprocess
import pytz
from time import sleep
from json import dumps, loads
from os import environ, path, system
from datetime import datetime
from getpass import getpass
from operator import itemgetter
from traceback import format_exc
from random import randint
from requests import Session	
from requests.auth import HTTPBasicAuth
from requests.exceptions import Timeout
from cryptography.fernet import Fernet


env_var_name = "AUTOMATIONORCHESTRATOR_SECRET_KEY"
cfg_file_name = "automationorchestrator.cfg"
error_count_max = 10
botflow_execution_url = "api/0/botflowexecution/"


def create_env_variable():
    key = Fernet.generate_key()

    process = subprocess.run(['setx', env_var_name, key.decode("utf-8")], stdout=subprocess.PIPE)

    if process.stdout.decode("utf-8").strip() != "SUCCESS: Specified value was saved.":
        input(f"""
Please make sure to create an environment variable called "{env_var_name}"
and set the value to: {key.decode("utf-8")}
Once you have done so, press Enter to continue...
""")


def create_cfg_file():
    while True:
        url = input("Please input the Automation Orchestrator base url: ")
        username = input("Please input your username: ")
        password = getpass("Please input your password: ")
        password_check = getpass("Please input your password again: ")

        if password != password_check:
            print("The passwords do not match, please retry...")
        elif get_data(url, username, password) == False:
            print("The user authentication failed, please retry...")
        else:
            break

    with open(cfg_file_name, 'wb') as f:
        f.write(Fernet(environ[env_var_name].encode("utf-8")).encrypt(dumps({'url': url, 'username': username, 'password': password}).encode('utf-8')))


def get_data(url, username, password):
    errors = 1

    while True:
        sleep(2)

        if errors <= error_count_max:
            with Session() as request:
                try:
                    response = request.get(f'{url}{botflow_execution_url}', auth=HTTPBasicAuth(username, password), timeout=10)

                except Timeout:
                    return None

                except:
                    print(f"{datetime.now()}: Connecting to the server failed...")
                    errors += 1
                    continue

            if response.status_code == 401:
                return False
            if response.status_code != 429:
                break

        else:
            return False

    try:
        request_response = response.json()
    except:
        request_response = None

    return request_response


def patch_data(url, username, password, record, data):
    while True:
        with Session() as request:
            response = request.patch(f'{url}{botflow_execution_url}{record}/', auth=HTTPBasicAuth(username, password), data=data)

        if response.status_code != 429:
            break

        sleep(1)


def monitor_executions(data):
    print(f"{datetime.now()}: The monitoring is now running!")

    while True:
        range(10000)
        sleep(randint(5, 15))

        items = get_data(data['url'], data['username'], data['password'])

        if items == None:
            continue

        elif items == False:
            return False

        run_executions(data['url'], data['username'], data['password'], items)


def run_executions(url, username, password, items):
    items = [item for item in items if item['status'] == "Pending" and item['computer_name'].upper() == environ['COMPUTERNAME'].upper() and item['user_name'].upper() == environ['USERNAME'].upper()]

    for item in items:
        app = item['app'].split("\\")[-1].lower()

        if app == "foxbot.exe" or app == "foxtrot.exe":
            processes = subprocess.run(["wmic", "process", "where", f"name='{app}'", "call", "GetOwner"], stdout=subprocess.PIPE, text=True).stdout.split('\n')

            username = environ['USERNAME'].lower()

            if any(str(f'\tuser = "{username}";') in user.lower() for user in processes):
                continue

            try:
                nintex_rpa_license_path = item['nintex_rpa_license_path']
            except:
                nintex_rpa_license_path = ""

            if nintex_rpa_license_path != "":
                if os.path.exists(nintex_rpa_license_path):
                    nintex_rpa_license_path = os.path.join(nintex_rpa_license_path, "System")

                    if os.path.exists(nintex_rpa_license_path):
                        if app == "foxbot.exe":
                            if item['nintex_rpa_available_foxbot_licenses'] <= len([file for file in os.listdir(nintex_rpa_license_path) if file.startswith("RPA") and file.endswith(".net")]):
                                continue

                        elif app == "foxtrot.exe":
                            if item['nintex_rpa_available_foxtrot_licenses'] <= len([file for file in os.listdir(nintex_rpa_license_path) if file.startswith("FTE") and file.endswith(".net")]):
                                continue

        data = {"time_start": datetime.now(pytz.timezone('Europe/Copenhagen')).strftime(f"%Y-%m-%dT%H:%M:%S+0{str(int(datetime.now(pytz.timezone('Europe/Copenhagen')).utcoffset().seconds / 60 / 60))}:00"), "status": "Running"}
        patch_data(url, username, password, str(item['id']), data)

        status = "Completed"

        if path.isfile(item['botflow']):
            try:
                if 'foxtrot' or 'foxbot' in item['app'].lower():
                    if item['close_bot_automatically']:
                        subprocess.run([item['app'], '/Open', item['botflow'], '/Run', '/Close', '/Exit'], timeout=(int(item['timeout_minutes']) * 60))
                    else:
                        subprocess.run([item['app'], '/Open', item['botflow'], '/Run'], timeout=(int(item['timeout_minutes']) * 60))

            except subprocess.TimeoutExpired:
                status = "Error - Botflow Timeout"

                try:
                    if 'foxtrot' or 'foxbot' in item["app"].lower():
                        system('taskkill /f /im foxtrot64.exe')
                except:
                    pass

                timeout_kill_processes = [str(process).strip() for process in item['timeout_kill_processes'].split(",")]

                for process in timeout_kill_processes:
                    try:
                        system(f'taskkill /f /im {process}')
                    except:
                        pass

        else:
            status = "Error - Botflow Missing"

        data = {"time_end": datetime.now(pytz.timezone('Europe/Copenhagen')).strftime(f"%Y-%m-%dT%H:%M:%S+0{str(int(datetime.now(pytz.timezone('Europe/Copenhagen')).utcoffset().seconds / 60 / 60))}:00"), "status": status}
        patch_data(url, username, password, str(item['id']), data)

        break


def main():
    try:
        if os.path.exists("error.txt"):
            os.remove("error.txt")
    
        if not env_var_name in environ:
            create_env_variable()

            print("""
An environment variable has been created with a unique encryption key.
This program will close down in 10 seconds. Hereafter, please restart the program...
""")

            sleep(10)
            return None

        if not path.exists(cfg_file_name):
            create_cfg_file()

        else:
            with open(cfg_file_name, 'rb') as f:
                if f.read() == "":
                    create_cfg_file()

        with open(cfg_file_name, 'rb') as f:
            data = loads(Fernet(environ[env_var_name].encode("utf-8")).decrypt(f.read()).decode("utf-8"))

        if get_data(data['url'], data['username'], data['password']) == False:
            return None

        monitor_executions(data)

    except KeyboardInterrupt:
        print(f"{datetime.now()}: Stopping the monitoring...")

        sleep(2)
        return None

    except:
        with open("error.txt", 'w') as f:
            try:
                f.write(format_exc())
                print(format_exc())
            except:
                pass

        sleep(10)
        return None


if __name__ == '__main__':
    main()
