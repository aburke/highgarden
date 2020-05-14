"""
Module executes commands against a gh-pipeline environment.
"""
from argparse import ArgumentParser
from utils.venv_tool import VenvTag, VenvTool, pipeline_home

import os
import subprocess

working_dir_options = {
    VenvTag.dbt.name: '{}/dbt_transforms'.format(pipeline_home)
}


def execute(name: str, command: str) -> None:
    ''' Executes command in respective enviromnet '''
    venv_tool = VenvTool(VenvTag[name])
    activate_exec = os.path.join(
        venv_tool.path,
        'bin',
        'activate'
    )
    working_dir = working_dir_options.get(name, pipeline_home)
    source = '. {}'.format(activate_exec)
    command_list = [source, command]
    subprocess.run(
        '\n'.join(command_list),
        shell=True,
        check=True,
        cwd=working_dir
    )


def parse(args: list) -> None:
    ''' Execute commands againt a gh-pipeline environment '''
    parser = ArgumentParser(
        prog="renv",
        description="Execute commands againt a gh-pipeline environment"
    )

    parser.add_argument(
        'env',
        help="specify which environment to run a command against",
        choices=[e.name for e in VenvTag]
    )

    parser.add_argument(
        '-s', '--single',
        help="Cause program to exist after first input",
        action='store_true'
    )

    command_args = parser.parse_args(args)

    while True:
        cmd = input('({}) >>> '.format(command_args.env))
        if cmd == 'exit':
            break
        try:
            execute(command_args.env, cmd)
        except Exception:
            pass

        if command_args.single:
            break
