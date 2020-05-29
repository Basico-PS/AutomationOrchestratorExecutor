import os
import glob
import subprocess
import pytz
import psutil
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
from infi.systray import SysTrayIcon


ENV_VAR = "BASICO_AUTOMATIONORCHESTRATOREXECUTOR_SECRET_KEY"
ENV_COMPUTER = environ['COMPUTERNAME'].lower()
ENV_USER = environ['USERNAME'].lower()
CFG_CRED_FILE = "configuration\\credentials.cfg"
ERROR_LOG_FILE = "logs\\error_log.txt"
EXECUTOR_LOG_FILE = "logs\\executor_log.txt"
BOTFLOW_EXECUTION_URL = "api/0/botflowexecution/"
ERROR_COUNT_MAX = 10
SHUT_DOWN = False


def create_env_variable():
    key = Fernet.generate_key()

    process = subprocess.run(['setx', ENV_VAR, key.decode("utf-8")], stdout=subprocess.PIPE)

    if process.stdout.decode("utf-8").strip() != "SUCCESS: Specified value was saved.":
        input(f"""
Please make sure to create an environment variable called "{ENV_VAR}"
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

    with open(CFG_CRED_FILE, 'wb') as f:
        f.write(Fernet(environ[ENV_VAR].encode("utf-8")).encrypt(dumps({'url': url, 'username': username, 'password': password}).encode('utf-8')))


def get_data(url, username, password):
    errors = 1

    while True:
        sleep(1)

        if errors <= ERROR_COUNT_MAX:
            with Session() as request:
                try:
                    request_filters = f"?computer_name__iexact={ENV_COMPUTER}&user_name__iexact={ENV_USER}&status=Pending"
                    response = request.get(f'{url}{BOTFLOW_EXECUTION_URL}{request_filters}', auth=HTTPBasicAuth(username, password), timeout=10)

                except Timeout:
                    print(f"{datetime.now()}: The request to Automation Orchestrator timed out, retrying...")

                    with open(ERROR_LOG_FILE, 'a') as f:
                        try:
                            f.write(f"{format_exc()}\n")
                            f.write(f"{datetime.now()}: The request to Automation Orchestrator timed out, retrying...\n")
                        except:
                            pass

                    errors += 1
                    continue

                except:
                    print(f"{datetime.now()}: Failed to connect to Automation Orchestrator, retrying...")

                    with open(ERROR_LOG_FILE, 'a') as f:
                        try:
                            f.write(f"{format_exc()}\n")
                            f.write(f"{datetime.now()}: Failed to connect to Automation Orchestrator, retrying...\n")
                        except:
                            pass

                    errors += 1
                    continue

            if response.status_code == 401:
                print(f"{datetime.now()}: The user authentication failed! The executor will close and restart now, prompting for new credentials...")

                if path.exists(CFG_CRED_FILE):
                    remove(CFG_CRED_FILE)

                with open(ERROR_LOG_FILE, 'a') as f:
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

        with open(EXECUTOR_LOG_FILE, 'a') as f:
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

        if errors <= ERROR_COUNT_MAX:
            with Session() as request:
                try:
                    response = request.patch(f'{url}{BOTFLOW_EXECUTION_URL}{record}/', auth=HTTPBasicAuth(username, password), timeout=10, data=data)

                except Timeout:
                    print(f"{datetime.now()}: The request to Automation Orchestrator timed out, retrying...")

                    with open(ERROR_LOG_FILE, 'a') as f:
                        try:
                            f.write(f"{format_exc()}\n")
                            f.write(f"{datetime.now()}: The request to Automation Orchestrator timed out, retrying...\n")
                        except:
                            pass

                    errors += 1
                    continue

                except:
                    print(f"{datetime.now()}: Failed to connect to Automation Orchestrator, retrying...")

                    with open(ERROR_LOG_FILE, 'a') as f:
                        try:
                            f.write(f"{format_exc()}\n")
                            f.write(f"{datetime.now()}: Failed to connect to Automation Orchestrator, retrying...\n")
                        except:
                            pass

                    errors += 1
                    continue

            if response.status_code == 401:
                print(f"{datetime.now()}: The user authentication failed! The executor will close and restart now, prompting for new credentials...")

                if path.exists(CFG_CRED_FILE):
                    remove(CFG_CRED_FILE)

                with open(ERROR_LOG_FILE, 'a') as f:
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

        with open(EXECUTOR_LOG_FILE, 'a') as f:
            try:
                f.write(f"{datetime.now()}: PATCH\n")
                f.write(f"{datetime.now()}: {str(request_response)}\n")
            except:
                pass

    except:
        pass

    return True


def monitor_executions(credentials):
    global SHUT_DOWN

    start_time = datetime.now()

    try:
        print(f"{datetime.now()}: The executor is now running!")

        while True:
            range(10000)
            sleep(randint(5, 15))

            items = get_data(credentials['url'], credentials['username'], credentials['password'])

            if SHUT_DOWN:
                break

            elif items == None:
                continue

            elif items == False:
                break

            elif not run_executions(credentials['url'], credentials['username'], credentials['password'], items):
                break

    except KeyboardInterrupt:
        print(f"{datetime.now()}: Stopping the executor...")
        sleep(5)

    except:
        print(f"{datetime.now()}: {format_exc()}")
        print(f"{datetime.now()}: An unexpected error occurred!  The executor will close and restart now...")

        with open(ERROR_LOG_FILE, 'a') as f:
            try:
                f.write(f"{datetime.now()}: {format_exc()}\n")
            except:
                pass

        sleep(10)


def run_executions(url, username, password, items):
    items = [item for item in items if item['status'] == "Pending" and item['computer_name'].lower() == ENV_COMPUTER and item['user_name'].lower() == ENV_USER]
    items = sorted(items, key=itemgetter('priority', 'id'))

    for item in items:
        app = item['app'].split("\\")[-1].lower()

        nintex_rpa_license_path = ""

        if app == "foxbot.exe" or app == "foxtrot.exe":
            processes = [proc.as_dict(attrs=['name', 'username']) for proc in psutil.process_iter()]
            processes = [proc for proc in processes if str(proc['name']).lower() == "foxtrot.exe" or str(proc['name']).lower() == "foxbot.exe"]
            processes = [proc for proc in processes if ENV_USER in str(proc['username']).lower()]

            if len(processes):
                continue

            try:
                nintex_rpa_license_path = str(item['nintex_rpa_license_path']).strip()
            except:
                nintex_rpa_license_path = ""

            if nintex_rpa_license_path != "":
                nintex_rpa_license_path = os.path.join(nintex_rpa_license_path, "System")

                if os.path.exists(nintex_rpa_license_path):
                    if app == "foxbot.exe":
                        if item['nintex_rpa_available_foxbot_licenses'] <= len([file for file in os.listdir(nintex_rpa_license_path) if file.startswith("RPA") and file.endswith(".net")]):
                            continue

                    elif app == "foxtrot.exe":
                        if item['nintex_rpa_available_foxtrot_licenses'] <= len([file for file in os.listdir(nintex_rpa_license_path) if file.startswith("FTE") and file.endswith(".net")]):
                            continue

                else:
                    nintex_rpa_license_path = None

        data = {"time_start": datetime.now(pytz.timezone('Europe/Copenhagen')).strftime(f"%Y-%m-%dT%H:%M:%S+0{str(int(datetime.now(pytz.timezone('Europe/Copenhagen')).utcoffset().seconds / 60 / 60))}:00"), "status": "Running"}

        if not patch_data(url, username, password, str(item['id']), data):
            return False

        status = "Completed"

        if path.isfile(item['app']) and path.isfile(item['botflow']):
            try:
                with open(EXECUTOR_LOG_FILE, 'a') as executor_log:
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

                if str(item['timeout_kill_processes']).strip() != "":
                    timeout_kill_processes = [str(process).strip() for process in item['timeout_kill_processes'].split(",")]

                    for process in timeout_kill_processes:
                        try:
                            system(f'taskkill /f /im {process}')
                        except:
                            pass

                if app == "foxbot.exe" or app == "foxtrot.exe":
                    if os.path.exists(str(nintex_rpa_license_path)):
                        for file in glob.glob(os.path.join(nintex_rpa_license_path, '*.net')):
                            try:
                                os.remove(file)
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

    if path.exists(ERROR_LOG_FILE):
        remove(ERROR_LOG_FILE)

    if path.exists(EXECUTOR_LOG_FILE):
        remove(EXECUTOR_LOG_FILE)

    if not ENV_VAR in environ:
        create_env_variable()

        print("""
An environment variable has been created with a unique encryption key.
This program will close down in 10 seconds. Hereafter, please restart the program...
""")
        sleep(10)
        return None

    if not path.exists(CFG_CRED_FILE):
        create_cfg_file()

    else:
        with open(CFG_CRED_FILE, 'rb') as f:
            file_content = f.read()

        if file_content == "" or file_content == b"":
            remove(CFG_CRED_FILE)
            create_cfg_file()

            with open(CFG_CRED_FILE, 'rb') as f:
                file_content = f.read()

    credentials = loads(Fernet(environ[ENV_VAR].encode("utf-8")).decrypt(file_content).decode("utf-8"))

    with SysTrayIcon("automation_orchestrator_executor\\static\\favicon.ico", "Automation Orchestrator Executor", on_quit=on_quit_callback) as systray:
        monitor_executions(credentials)


def on_quit_callback(systray):
    global SHUT_DOWN
    if not SHUT_DOWN:
        SHUT_DOWN = True

        print(f"{datetime.now()}: Stopping the executor...")


if __name__ == '__main__':
    main()
