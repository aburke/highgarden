"""
Module starts airflow webserver and scheduler
"""
import threading
import os
import subprocess

from utils.venv_tool import VenvTool, VenvTag
from argparse import ArgumentParser

airflow_venv = VenvTool(VenvTag.airflow)


def execute(command: str) -> None:
    ''' Execute command in airflow venv '''
    activate_exec = os.path.join(
        airflow_venv.path,
        'bin',
        'activate'
    )
    source_airflow = 'source {}'.format(activate_exec)
    command_list = [source_airflow, command]
    subprocess.run(
        '\n'.join(command_list),
        shell=True,
        check=True
    )


def start_webserver() -> None:
    ''' Starts airflow webserver '''
    execute('airflow webserver -p 8080')


def start_scheduler() -> None:
    ''' Starts airflow scheduler '''
    execute('airflow scheduler')


def init_db() -> None:
    ''' Initializes airflow db '''
    execute('airflow initdb')


def parse(args: list) -> None:
    ''' Run start processes '''
    parser = ArgumentParser(
        prog="start",
        description="Starts airflow webserver and scheduler"
    )

    parser.parse_args(args)

    init_db()

    webserver_thread = threading.Thread(target=start_webserver, daemon=True)
    scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)

    webserver_thread.start()
    scheduler_thread.start()

    webserver_thread.join()
    scheduler_thread.join()
