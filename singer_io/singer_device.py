"""
This module serves as the for Singer related migration processes.
All Tap/Target classes should inherit from the SingerDevice class.
The SingerDevice class serves as a python wrapper for the Singer cli standard.
"""

import inspect
import os
import json
import subprocess
import logging

from utils.venv_tool import VenvTag, VenvTool
from utils.aws import s3
from typing import Tuple
from enum import Enum
from datetime import datetime


class SProp(Enum):
    ''' Singer properties '''

    config = 'config'
    catalog = 'catalog'
    properties = 'properties'
    state = 'state'


class SingerDevice(object):
    ''' Wrapper for singer io command line utility to be used as base class for
    Tap/Target classes.
    '''

    env = VenvTool(VenvTag.local)
    cmd_name = ''

    def __init__(self):
        cmd_name = self.cmd_name or self.env.venv_tag.value
        self.cmd_path = os.path.join(
            self.env.path,
            'bin',
            cmd_name
        )

    def get_prop_details(self, sprop: SProp) -> Tuple[str, str, str]:
        ''' Get standard name for sprop file '''
        module_name = self.__module__.split('.')[-1]
        s3_folder = '/'.join(['singer_io', module_name])
        prop_name = '_'.join([
            module_name,
            self.__class__.__name__.lower(),
            sprop.value + '.json'
        ])
        module_dir, _ = os.path.split(inspect.getfile(self.__class__))
        template_folder = os.path.join(
            module_dir,
            'templates',
            module_name
        )

        return s3_folder, prop_name, template_folder

    def get_template(self, sprop: SProp) -> dict:
        ''' Get template data for the sprop extracted
            from its correspoding json file
        '''
        _, prop_name, template_folder = self.get_prop_details(sprop)
        template_path = os.path.join(
            template_folder,
            prop_name
        )
        with open(template_path) as s_file:
            template = json.loads(s_file.read())

        return template

    def create_sprop_file(self, sprop: SProp, directory: str) -> str:
        ''' Create singer properties file in local directory
            and return path of file
        '''
        property_data = getattr(self, sprop.value)
        _, file_name, _ = self.get_prop_details(sprop)
        full_path = os.path.join(directory, file_name)
        with open(full_path, 'w') as s_file:
            json.dump(property_data, s_file, indent=2)

        return full_path

    def get_latest_state(self) -> dict:
        ''' Pulls the most recent state object if one exists '''
        data = self.download(SProp.state)
        states = [s for s in data.decode('utf-8').split('\n') if s]
        return json.loads(states[-1]) if states else {}

    def download(self, sprop: SProp) -> bytes:
        ''' Download singer property file from s3 '''
        s3_folder, prop_name, _ = self.get_prop_details(sprop)
        key = '/'.join([s3_folder, prop_name])
        stream = s3.get_object(key)
        data = bytes()
        if stream:
            for s in stream:
                data += s

        return data

    def upload(self, sprop: SProp, file_path: str) -> None:
        ''' Upload singer propery file to s3 '''
        s3_folder, prop_name, _ = self.get_prop_details(sprop)
        key = '/'.join([s3_folder, prop_name])
        with open(file_path) as s_file:
            s3.upload_object(key, s_file.read())

    def setup_command_part(self, setup_path: str) -> str:
        ''' Get migration command for singer device
            and create property files
        '''
        command_list = [self.cmd_path]
        for prop in SProp:
            if hasattr(self, prop.value):
                file_path = self.create_sprop_file(prop, setup_path)
                option_tag = '--{} {}'.format(
                    prop.value,
                    file_path
                )
                command_list.append(option_tag)
        return ' '.join(command_list)


def migrate(tap: SingerDevice, target: SingerDevice) -> None:
    ''' Migrate data from source sytem to target system '''
    module_name = tap.__module__.split('.')[-1]
    _, prop_name, _ = tap.get_prop_details(SProp.state)
    process_folder_name = module_name + '_' + datetime.now().strftime(
        '%Y_%m_%d_%H%M%S'
    )
    process_path = os.path.join('/tmp', process_folder_name)

    os.mkdir(process_path)

    tap_command = tap.setup_command_part(process_path)
    target_command = target.setup_command_part(process_path)
    proess_command = '{} | {}'.format(tap_command, target_command)

    has_state = hasattr(tap, SProp.state.value)

    if has_state:
        state_file_path = os.path.join(process_path, 'new_' + prop_name)
        proess_command += ' >> ' + state_file_path

    logging.info('Running migrate command for {}'.format(module_name))
    logging.info(proess_command)

    completed_process = subprocess.run(
        proess_command,
        shell=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

    if completed_process.returncode != 0:
        raise Exception(completed_process.stdout)

    for message in completed_process.stdout.split('\n'):
        logging.info(message)

    if has_state:
        logging.info('Saving {} state.'.format(module_name))
        tap.upload(SProp.state, state_file_path)
