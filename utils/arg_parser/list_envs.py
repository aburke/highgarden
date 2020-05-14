"""
List gh-pipelines environments
"""
import logging

from argparse import ArgumentParser
from utils.venv_tool import VenvTag


def parse(args: str) -> None:
    ''' List gh-pipelines environments '''
    parser = ArgumentParser(
        prog="list-envs",
        description="List gh-pipelines environments"
    )

    parser.parse_args(args)

    envs = sorted(e.name for e in VenvTag)

    for e in envs:
        logging.info(e)
