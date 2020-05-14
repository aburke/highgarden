"""
Tools for gh-pipeline virtual environment configuration and
command line execution
"""

import os
import subprocess
import logging

from enum import Enum

venv_home = os.environ.get('GH_VENV_HOME', '~')
pipeline_home = os.environ['PYTHONPATH']


class VenvTag(Enum):
    ''' Virtual environment tag type '''

    airflow = 'airflow'
    dbt = 'dbt'
    local = 'local'
    tap_s3_csv = 'tap-s3-csv'
    singer_target_postgres = 'target-postgres'
    tap_amplitude = 'tap-amplitude'
    tap_sftp = 'tap-sftp'
    tap_google_analytics = 'tap-google-analytics'
    pipelinewise_target_s3_csv = 'pipelinewise-target-s3-csv'
    operators = 'operators'


class InvalidTagExceptions(Exception):
    ''' Exception for invalide VenvTag '''
    pass


class VenvTool(object):
    ''' Tool for configuring pipeline virtual environments '''

    def __init__(self, venv_tag: VenvTag):
        if not isinstance(venv_tag, VenvTag):
            raise InvalidTagExceptions('Invalid venv tag.')
        self.venv_tag = venv_tag
        self.path = os.path.join(venv_home, venv_tag.name)

    @property
    def create_env_command(self) -> str:
        ''' Virtual environment command string from tag '''
        command_skeleton = 'python3 -m venv {}/{}'
        return command_skeleton.format(venv_home, self.venv_tag.name)

    @property
    def activate_env_command(self) -> str:
        ''' Command string to activate the virtual env '''
        command_skeleton = '. {}/{}/bin/activate'
        return command_skeleton.format(venv_home, self.venv_tag.name)

    @property
    def upgrade_pip_command(self) -> str:
        ''' Command string to upgrade pip'''
        return 'pip3 -q install --upgrade pip'

    @property
    def install_command(self) -> str:
        ''' Command string to install requirements based on the tag '''
        command_skeleton = '{}/requirements/{}.txt'
        requirements = command_skeleton.format(
            pipeline_home,
            self.venv_tag.name
        )
        return 'pip3 -q install -r {}'.format(requirements)

    @property
    def remove_env_dir(self) -> str:
        ''' Command string to remove config venv directory '''
        command_skeleton = 'rm -rf {}/{}'
        return command_skeleton.format(
            venv_home,
            self.venv_tag.name
        )

    def configure(self) -> None:
        ''' Configure virtual environment '''
        command_list = []
        if self.venv_tag != VenvTag.local:
            command_list += [
                self.remove_env_dir,
                self.create_env_command,
                self.activate_env_command
            ]

        command_list += [
            self.upgrade_pip_command,
            self.install_command
        ]

        setup_commands = '\n'.join(command_list)
        subprocess.run(setup_commands, shell=True, check=True)
        logging.info('{} environment configured.'.format(self.venv_tag.name))
