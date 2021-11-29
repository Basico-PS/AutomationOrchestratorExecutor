@echo off

call cd %~dp0
call python -m venv venv
call venv\scripts\activate
CALL python -m pip install --upgrade pip
call pip install -r requirements.txt --no-cache-dir

echo The installation is now complete!
TIMEOUT 15
