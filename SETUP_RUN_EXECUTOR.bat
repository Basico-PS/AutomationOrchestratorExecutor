@echo off

CALL CD %~dp0

echo It is recommended NOT to run with highest privileges unless it is necessary for the command to be executed.
CALL SET /P privileges=Would you like to run the executor with highest privileges (Y/N)?

IF %privileges% == Y (
    CALL SET level=HIGHEST
) else (
    IF %privileges% == y (
        CALL SET level=HIGHEST
    ) else (
        CALL SET level=LIMITED
    )
)

CALL SCHTASKS /CREATE /SC DAILY /TN "AutomationOrchestratorExecutorRunExecutor" /TR "%CD%\run_executor\RUN_EXECUTOR.bat" /ST 00:00 /RI 1 /DU 23:59 /RL %level% /F
TIMEOUT 15
