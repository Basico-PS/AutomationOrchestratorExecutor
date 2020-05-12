import os
import subprocess
import pytz
from time import sleep
from json import dumps, loads
from os import environ, path, system, remove
from datetime import datetime
from getpass import getpass
from operator import itemgetter
from traceback import format_exc
from random import randint
from requests import Session
from requests.auth import HTTPBasicAuth
from requests.exceptions import Timeout
from cryptography.fernet import Fernet
from operator import itemgetter


env_var = "BASICO_AUTOMATIONORCHESTRATOREXECUTOR_SECRET_KEY"
env_computer = environ['COMPUTERNAME'].lower()
env_user = environ['USERNAME'].lower()
cfg_cred_file = "configuration\\credentials.cfg"
error_log_file = "logs\\error_log.txt"
executor_log_file = "logs\\executor_log.txt"
botflow_execution_url = "api/0/botflowexecution/"
error_count_max = 10


def create_env_variable():
    key = Fernet.generate_key()

    process = subprocess.run(['setx', env_var, key.decode("utf-8")], stdout=subprocess.PIPE)

    if process.stdout.decode("utf-8").strip() != "SUCCESS: Specified value was saved.":
        input(f"""
Please make sure to create an environment variable called "{env_var}"
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
            print("Failed to connect to the Automation Orchestrator, please retry...")
        else:
            break

    with open(cfg_cred_file, 'wb') as f:
        f.write(Fernet(environ[env_var].encode("utf-8")).encrypt(dumps({'url': url, 'username': username, 'password': password}).encode('utf-8')))


def get_data(url, username, password):
    errors = 1

    while True:
        sleep(1)

        if errors <= error_count_max:
            with Session() as request:
                try:
                    request_filters = f"?computer_name__iexact={env_computer}&user_name__iexact={env_user}&status=Pending"
                    response = request.get(f'{url}{botflow_execution_url}{request_filters}', auth=HTTPBasicAuth(username, password), timeout=10)

                except Timeout:
                    print(f"{datetime.now()}: The request to Automation Orchestrator timed out, retrying...")

                    with open(error_log_file, 'a') as f:
                        try:
                            f.write(f"{format_exc()}\n")
                            f.write(f"{datetime.now()}: The request to Automation Orchestrator timed out, retrying...\n")
                        except:
                            pass

                    errors += 1
                    continue

                except:
                    print(f"{datetime.now()}: Failed to connect to Automation Orchestrator, retrying...")

                    with open(error_log_file, 'a') as f:
                        try:
                            f.write(f"{format_exc()}\n")
                            f.write(f"{datetime.now()}: Failed to connect to Automation Orchestrator, retrying...\n")
                        except:
                            pass

                    errors += 1
                    continue

            if response.status_code == 401:
                print(f"{datetime.now()}: The user authentication failed! The executor will close and restart now, prompting for new credentials...")

                if path.exists(cfg_cred_file):
                    remove(cfg_cred_file)

                with open(error_log_file, 'a') as f:
                    try:
                        f.write(f"{datetime.now()}: The user authentication failed!\n")
                    except:
                        pass

                sleep(10)
                return False

            if response.status_code != 429:
                break

        else:
            return False

    try:
        request_response = response.json()

        with open(executor_log_file, 'a') as f:
            try:
                f.write(f"{datetime.now()}: GET\n")
                f.write(f"{datetime.now()}: {str(request_response)}\n")
            except:
                pass

    except:
        request_response = None

    return request_response


def patch_data(url, username, password, record, data):
    errors = 1

    while True:
        sleep(1)

        if errors <= error_count_max:
            with Session() as request:
                try:
                    response = request.patch(f'{url}{botflow_execution_url}{record}/', auth=HTTPBasicAuth(username, password), timeout=10, data=data)

                except Timeout:
                    print(f"{datetime.now()}: The request to Automation Orchestrator timed out, retrying...")

                    with open(error_log_file, 'a') as f:
                        try:
                            f.write(f"{format_exc()}\n")
                            f.write(f"{datetime.now()}: The request to Automation Orchestrator timed out, retrying...\n")
                        except:
                            pass

                    errors += 1
                    continue

                except:
                    print(f"{datetime.now()}: Failed to connect to Automation Orchestrator, retrying...")

                    with open(error_log_file, 'a') as f:
                        try:
                            f.write(f"{format_exc()}\n")
                            f.write(f"{datetime.now()}: Failed to connect to Automation Orchestrator, retrying...\n")
                        except:
                            pass

                    errors += 1
                    continue

            if response.status_code == 401:
                print(f"{datetime.now()}: The user authentication failed! The executor will close and restart now, prompting for new credentials...")

                if path.exists(cfg_cred_file):
                    remove(cfg_cred_file)

                with open(error_log_file, 'a') as f:
                    try:
                        f.write(f"{datetime.now()}: The user authentication failed!\n")
                    except:
                        pass

                sleep(10)
                return False

            if response.status_code != 429:
                break

        else:
            return False

    try:
        request_response = response.json()

        with open(executor_log_file, 'a') as f:
            try:
                f.write(f"{datetime.now()}: PATCH\n")
                f.write(f"{datetime.now()}: {str(request_response)}\n")
            except:
                pass

    except:
        pass

    return True


def monitor_executions(credentials):
    start_time = datetime.now()

    try:
        print(f"{datetime.now()}: The executor is now running!")

        while True:
            range(10000)
            sleep(randint(5, 15))

            items = get_data(credentials['url'], credentials['username'], credentials['password'])

            if items == None:
                continue

            elif items == False:
                break

            if not run_executions(credentials['url'], credentials['username'], credentials['password'], items):
                break

    except KeyboardInterrupt:
        print(f"{datetime.now()}: Stopping the monitoring...")
        sleep(5)

    except:
        print(f"{datetime.now()}: {format_exc()}")
        print(f"{datetime.now()}: An unexpected error occurred!  The executor will close and restart now...")

        with open(error_log_file, 'a') as f:
            try:
                f.write(f"{datetime.now()}: {format_exc()}\n")
            except:
                pass

        sleep(10)


def run_executions(url, username, password, items):
    items = [item for item in items if item['status'] == "Pending" and item['computer_name'].lower() == env_computer and item['user_name'].lower() == env_user]
    items = sorted(items, key=itemgetter('priority', 'id'))

    for item in items:
        app = item['app'].split("\\")[-1].lower()

        if app == "foxbot.exe" or app == "foxtrot.exe":
            processes = subprocess.run(["wmic", "process", "where", f"name='{app}'", "call", "GetOwner"], stdout=subprocess.PIPE, text=True).stdout.split('\n')

            if any(str(f'\tuser = "{env_user}";') in user.lower() for user in processes):
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

        if not patch_data(url, username, password, str(item['id']), data):
            return False

        status = "Completed"

        if path.isfile(item['app']) and path.isfile(item['botflow']):
            try:
                with open(executor_log_file, 'a') as executor_log:
                    executor_log.write(f"{datetime.now()}: EXECUTING BOTFLOW\n")

                    if app == "foxbot.exe" or app == "foxtrot.exe":
                        if item['close_bot_automatically']:
                            subprocess.run(
                                [item['app'], '/Open', item['botflow'], '/Run', '/Close', '/Exit'],
                                timeout=(int(item['timeout_minutes']) * 60),
                                cwd=path.dirname(item['app']),
                                stdout=executor_log
                            )

                        else:
                            subprocess.run(
                                [item['app'], '/Open', item['botflow'], '/Run'],
                                timeout=(int(item['timeout_minutes']) * 60),
                                cwd=path.dirname(item['app']),
                                stdout=executor_log
                            )

                    elif app == "uirobot.exe":
                        subprocess.run(
                            [item['app'], "execute", "--file", item['botflow'], "--input", str({'aoId': str(item['id']), 'aoTrigger': item['trigger']})],
                            timeout=(int(item['timeout_minutes']) * 60),
                            cwd=path.dirname(item['botflow']),
                            stdout=executor_log
                        )

                    elif (app == "python.exe" or app == "pythonw.exe" or app == "cscript.exe" or app == "wscript.exe"):
                        subprocess.run(
                            [item['app'], item['botflow'], str(item['id']), item['trigger']],
                            timeout=(int(item['timeout_minutes']) * 60),
                            cwd=path.dirname(item['botflow']),
                            stdout=executor_log
                        )

                    else:
                        subprocess.run(
                            [item['app'], item['botflow']],
                            timeout=(int(item['timeout_minutes']) * 60),
                            cwd=path.dirname(item['botflow']),
                            stdout=executor_log
                        )

            except subprocess.TimeoutExpired:
                status = "Error - Botflow Timeout"

                try:
                    if app == "foxbot.exe" or app == "foxtrot.exe":
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
            if not path.isfile(item['app']):
                status = "Error - App Missing"
            elif not path.isfile(item['botflow']):
                status = "Error - Botflow Missing"
            else:
                status = "Error - Unknown Issue"

        data = {"time_end": datetime.now(pytz.timezone('Europe/Copenhagen')).strftime(f"%Y-%m-%dT%H:%M:%S+0{str(int(datetime.now(pytz.timezone('Europe/Copenhagen')).utcoffset().seconds / 60 / 60))}:00"), "status": status}

        if not patch_data(url, username, password, str(item['id']), data):
            return False

        return True

    return True


def main():
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    if path.exists(error_log_file):
        remove(error_log_file)

    if path.exists(executor_log_file):
        remove(executor_log_file)

    if not env_var in environ:
        create_env_variable()

        print("""
An environment variable has been created with a unique encryption key.
This program will close down in 10 seconds. Hereafter, please restart the program...
""")
        sleep(10)
        return None

    if not path.exists(cfg_cred_file):
        create_cfg_file()

    else:
        with open(cfg_cred_file, 'rb') as f:
            file_content = f.read()

        if file_content == "" or file_content == b"":
            remove(cfg_cred_file)
            create_cfg_file()

            with open(cfg_cred_file, 'rb') as f:
                file_content = f.read()

    credentials = loads(Fernet(environ[env_var].encode("utf-8")).decrypt(file_content).decode("utf-8"))

    monitor_executions(credentials)


if __name__ == '__main__':
    main()
