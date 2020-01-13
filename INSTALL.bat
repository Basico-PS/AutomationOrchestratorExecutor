call cd %~dp0
call python -m venv venv
call venv\scripts\activate
call pip install -r requirements.txt --no-cache-dir
