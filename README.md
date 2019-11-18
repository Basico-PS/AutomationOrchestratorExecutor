# Basico P/S - Automation Orchestrator Executor

<i>More documentation is underway...</i>

For support, please contact us: robotics@basico.dk

The Automation Orchestrator Executor is an add-on to the [Automation Orchestrator](https://github.com/Basico-PS/AutomationOrchestrator) allowing you to monitor the execution queue from a different machine in your protected internal network and execute the pending scripts assigned to your machine and user. This is relevant if you wish to either:
- Run the Automation Orchestrator on one machine but execute the scripts on a different machine, or
- Run the Automation Orchestrator on a machine (for example, a Windows Terminal Server) with multiple users that are supposed to execute scripts

## Installation

For the solution to work, you need to install [Python](https://www.python.org/). The solution is tested with Python 3.7 and 3.8.

1. Download the [latest version](https://github.com/Basico-PS/AutomationOrchestratorExecutor/archive/v0.0.4.zip).
2. Create a folder called "Automation Orchestrator Executor" somewhere convenient, for example, directly on the C: drive or in the "Program Files" folder.
3. Unzip the folder in your created "Automation Orchestrator Executor" folder. So, your path could be similar to "C:\Automation Orchestrator Executor\AutomationOrchestratorExecutor-0.0.4" or "C:\Program Files\Automation Orchestrator\AutomationOrchestratorExecutor-0.0.4". However, you may unzip the folder anywhere on your system.
4. After unzipping the folder, run the "INSTALL.bat" [file](https://github.com/Basico-PS/AutomationOrchestratorExecutor/blob/master/INSTALL.bat) for an automated installation process. You may also manually run the installation steps via, for example, the CMD. Remember to run the batch file (or commands manually) as an administrator.
5. The last command of the installation process will prompt you to write your username and password of the user created in the Automation Orchestrator.

## Usage

After a succesful installation, and as long as the Automation Orchestrator server is running in your protected internal network, you can now run the Automation Orchestrator Executor using the "RUN_SERVER.bat" [file](https://github.com/Basico-PS/AutomationOrchestratorExecutor/blob/master/RUN_EXECUTOR.bat). Remember to run the batch file (or commands manually) as an administrator.

The Automation Orchestrator Executor will monitor the execution queue and wait for a script assigned to your machine and user.

<i>More documentation is underway...</i>
