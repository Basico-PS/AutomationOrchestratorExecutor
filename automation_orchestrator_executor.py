import subprocess
import pytz
from sys import exit, stdout
from time import sleep
from json import dumps, loads
from os import environ, path, system
from datetime import datetime
from getpass import getpass
from operator import itemgetter
from traceback import format_exc
from random import randrange
from requests import Session	
from requests.auth import HTTPBasicAuth
from cryptography.fernet import Fernet


interval = 5
env_var_name = "AUTOMATIONORCHESTRATOR_SECRET_KEY"
cfg_file_name = "automationorchestrator.cfg"


def create_env_variable():
    key = Fernet.generate_key()
    
    process = subprocess.Popen(['setx', env_var_name, key.decode("utf-8")], stdout=subprocess.PIPE)
    process_out, process_err = process.communicate()
    
    if process_out.decode("utf-8").strip() != "SUCCESS: Specified value was saved.":
        input(f"""
Please make sure to create an environment variable called "{env_var_name}"
and set the value to: {key.decode("utf-8")}
Once you have done so, press Enter to continue...
    """)
        
    exit()
    
    
def create_cfg_file():    
    while True:
        url = input("Please input the Automation Orchestrator base url: ")
        username = input("Please input your username: ")
        password = getpass("Please input your password: ")
        password_check = getpass("Please input your password again: ")
        
        if password != password_check:
            print("The passwords do not match...")
        elif get_data(url, username, password) == False:
            print("The user authentication failed...")
        else:
            break
    
    with open(cfg_file_name, 'wb') as f:
        f.write(Fernet(environ[env_var_name].encode("utf-8")).encrypt(dumps({'url': url, 'username': username, 'password': password}).encode('utf-8')))
        

def get_data(url, username, password):
    while True:	
        with Session() as request:
            response = request.get(f'{url}api/0/execution/', auth=HTTPBasicAuth(username, password))

        if response.status_code == 401:
            return False
        if response.status_code != 429:
            break
        
    return response.json()
        

def patch_data(url, username, password, record, data):
    while True:	
        with Session() as request:
            response = request.patch(f'{url}api/0/execution/{record}/', auth=HTTPBasicAuth(username, password), data=data)

        if response.status_code != 429:
            break
        
        sleep(1)
        

def run_executions(url, username, password, items):	
    items = [item for item in items if item['status'] == "Pending" and item['computer_name'].upper() == environ['COMPUTERNAME'].upper() and item['user_name'].upper() == environ['USERNAME'].upper()]	
    items = sorted(sorted(items, key=itemgetter('priority'), reverse=True), key=itemgetter('time_queued'), reverse=False)

    for item in items:	
        if any(item["app"].split("\\")[-1].lower() in process.lower() for process in subprocess.run(["wmic", "process", "get", "description,executablepath"], stdout=subprocess.PIPE, text=True).stdout.split('\n')):	
            continue
            
        data = {"time_start": datetime.now(pytz.timezone('Europe/Copenhagen')).strftime(f"%Y-%m-%dT%H:%M:%S+0{str(int(datetime.now(pytz.timezone('Europe/Copenhagen')).utcoffset().seconds / 60 / 60))}:00"), "status": "Running"}
        patch_data(url, username, password, str(item['id']), data)

        status = "Completed"

        if path.isfile(item['botflow']):
            if not [{'botflow': x['botflow'], 'trigger': x['trigger']} for x in items if x['status'] == 'Completed'].count({'botflow': item['botflow'], 'trigger': item['trigger']}) >= 1:	
                try:	
                    if 'foxtrot' or 'foxbot' in item["app"].lower():	
                        subprocess.run([item["app"], r'/Open', item['botflow'], r'/Run', r'/Close', r'/Exit'], timeout=(item["timeout_minutes"] * 60))	
                    else:	
                        subprocess.run([item["app"], item['botflow']], timeout=(item["timeout_minutes"] * 60))	

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
                status = "Skipped - Duplicate Queue Items Detected"	

        else:	
            status = "Error - Botflow Missing"	

        data = {"time_end": datetime.now(pytz.timezone('Europe/Copenhagen')).strftime(f"%Y-%m-%dT%H:%M:%S+0{str(int(datetime.now(pytz.timezone('Europe/Copenhagen')).utcoffset().seconds / 60 / 60))}:00"), "status": status}
        patch_data(url, username, password, str(item['id']), data)	

        break

    
def main():
    try:
        if not env_var_name in environ:
            create_env_variable()
            
        if not path.exists(cfg_file_name):
            create_cfg_file()
            
        with open(cfg_file_name, 'rb') as f:
            data = loads(Fernet(environ[env_var_name].encode("utf-8")).decrypt(f.read()).decode("utf-8"))

        if get_data(data['url'], data['username'], data['password']) == False:
            print("The user authentication failed...")
            
        while True:
            range(10000)	
            sleep(interval)
            
            items = get_data(data['url'], data['username'], data['password'])
            run_executions(data['url'], data['username'], data['password'], items)

    except:	
        with open("error.txt", 'w') as f:	
            try:	
                f.write(format_exc())	
                print(format_exc())	
            except:	
                pass
            
        sleep(10)
        exit()

if __name__ == '__main__':
    main()
