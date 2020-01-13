# Basico P/S - Automation Orchestrator Executor

The Automation Orchestrator Executor is an add-on to the [Automation Orchestrator](https://github.com/Basico-PS/AutomationOrchestrator) allowing you to monitor the execution queue from a different machine in your protected internal network and execute the pending scripts assigned to your machine and user. This is relevant if you wish to either:
- Run the Automation Orchestrator on one machine but execute the scripts on a different machine, or
- Run the Automation Orchestrator on a machine (for example, a Windows Terminal Server) with multiple users that are supposed to execute scripts

IMPORTANT: For the Automation Orchestrator to work, you need to run the server in your protected internal network.

## Table of contents

- [Installation](#installation)
- [Usage](#usage)
- [Copyrights](#copyrights)
- [Contact](#contact)

## Installation

We highly recommend that the Automation Orchestrator Executor is installed and setup only by people experienced with both Python and Nintex RPA. You are always welcome to contact us for assistance via: robotics@basico.dk

For the Automation Orchestrator Executor to work, you need to install [Python](https://www.python.org/downloads/windows/). The Automation Orchestrator is tested with [![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/windows/) and [![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/windows/). If you are in any doubts on how to correctly install Python, follow [this guide](https://www.mbalslow.com/blog/article/how-to-install-python/).

After installing Python, you are now ready to install the Automation Orchestrator Executor. Follow these steps precisely:

1. Create a folder called "AutomationOrchestratorExecutor" on your machine, for example, directly on the C: drive or in the "Program Files" folder. So, your path should be similar to "C:\AutomationOrchestratorExecutor" or "C:\Program Files\AutomationOrchestratorExecutor".

2. Navigate to the [list of releases](https://github.com/Basico-PS/AutomationOrchestratorExecutor/releases) and download the source code (ZIP) of the latest version.

3. Unzip the folder in your created "AutomationOrchestratorExecutor" folder. So, your path could be similar to "C:\AutomationOrchestratorExecutor\AutomationOrchestratorExecutor-0.0.6" or "C:\Program Files\AutomationOrchestratorExecutor\AutomationOrchestratorExecutor-0.0.6".

4. After unzipping the folder, run the "INSTALL.bat" [file](https://github.com/Basico-PS/AutomationOrchestratorExecutor/blob/master/INSTALL.bat) for an automated installation process. Remember to run the batch file (or commands manually) as an administrator.

5. The last command of the installation process will prompt you to write your username and password of the user created in the Automation Orchestrator.

## Usage

After a succesful installation, and as long as the Automation Orchestrator server is running in your protected internal network, you can now run the Automation Orchestrator Executor using the "RUN_EXECUTOR.bat" [file](https://github.com/Basico-PS/AutomationOrchestratorExecutor/blob/master/RUN_EXECUTOR.bat). Remember to run the batch file (or commands manually) as an administrator. 

The first time you run the executor, you will need to configure it. First, you need to specify the base url of the server and press enter, for example:

<p align="center">
  <img src="/images/base%20url.png">
</p>

Hereafter, specify your username and password to your Automation Orchestrator user and press enter, for example:

<p align="center">
  <img src="/images/username%20password.png">
</p>

The Automation Orchestrator Executor will monitor the execution queue by frequently sending a request to the server and wait for a queue item assigned to your machine and user.

IMPORTANT: For the executor to succesfully work, it needs to be always running. A recommended way of ensuring this it to add a task in the Windows Task Scheduler that runs every minute of every day to run the batch file but only start if it is not already running.

<p align="center">
  <img src="/images/run%20executor.png">
</p>

IMPORTANT: When you wish to stop the server, you MUST click the shortcut ctrl+c in the server window to see the confirmation that the server is stopped before closing the window. Make sure to NOT close the server while anything is running. Sometimes you need to click the shortcut a couple of times before it is registered by the server.

<p align="center">
  <img src="/images/stop%20executor.png">
</p>

## Copyrights

Starting from 0.0.7 Basico P/S - Automation Orchestrator Executor is distributed under the [BSD 3-clause license](https://github.com/Basico-PS/AutomationOrchestratorExecutor/blob/master/LICENSE). Basico P/S - Automation Orchestrator 0.0.6 and before was distributed under the MIT license.

(c) Basico P/S, Mathias Balsløw 2019

## Contact

For contact or support, please write to us at: robotics@basico.dk
