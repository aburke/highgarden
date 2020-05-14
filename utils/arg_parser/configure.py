"""
Configure gh-pipelines virtual enviroments
"""
import threading
import logging

from argparse import ArgumentParser
from utils.venv_tool import VenvTool, VenvTag
from typing import List


def setup_env(venv_tag: VenvTag) -> None:
    ''' Configure a single environment '''
    env_tool = VenvTool(venv_tag)
    env_tool.configure()


def parse(args: List[str]) -> None:
    ''' Configure gh-pipline environments '''
    parser = ArgumentParser(
        prog="configure",
        description="Configure gh-pipeline virtual enviroments"
    )

    parser.add_argument(
        'selected_tags',
        help="environment options",
        nargs='*'
    )

    command_args = parser.parse_args(args)

    venv_tags = [t for t in VenvTag]

    if command_args.selected_tags:
        tag_strings = [t.name for t in venv_tags]
        actual_set = set(tag_strings)
        selected_set = set(command_args.selected_tags)
        invalid_tags = selected_set - actual_set
        valid_tags = selected_set.intersection(actual_set)
        for tag in invalid_tags:
            message = '{} is not valid environment option.'
            logging.warning(message.format(tag))
        venv_tags = [VenvTag[st] for st in valid_tags]

    threads = []
    for tag in venv_tags:
        config_thread = threading.Thread(
            target=setup_env,
            args=(tag,),
            daemon=True
        )
        threads.append(config_thread)
        config_thread.start()

    for thread in threads:
        thread.join()
