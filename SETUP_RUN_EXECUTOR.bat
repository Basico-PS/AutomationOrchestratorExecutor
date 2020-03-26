CALL CD %~dp0
CALL SCHTASKS /CREATE /SC DAILY /TN "AutomationOrchestratorExecutorRunExecutor" /TR "%CD%\run_executor\RUN_EXECUTOR.bat" /ST 00:00 /RI 1 /DU 23:59 /RL HIGHEST /F