"""
GH-Pipelines CLI
"""

import argparse
import logging
import sys

from utils.arg_parser import configure, renv, start, list_envs, discover, op_runner

parse_options = {
    'configure': configure,
    'renv': renv,
    'start': start,
    'list-envs': list_envs,
    'discover': discover,
    'op_runner': op_runner
}


def configure_logging() -> None:
    ''' Configure logging for ghp output '''
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '{%(filename)s:%(lineno)d} - %(message)s'
    )
    handler.setFormatter(formatter)
    root.addHandler(handler)


if __name__ == "__main__":
    configure_logging()

    ghp_parser = argparse.ArgumentParser(
        description="GH-Pipelines CLI"
    )

    ghp_parser.add_argument(
        'command',
        help="gh-pipeline command",
        choices=parse_options.keys()
    )

    ghp_parser.add_argument(
        'args',
        help="ghp args",
        nargs=argparse.REMAINDER
    )

    args = ghp_parser.parse_args()

    command_parser = parse_options[args.command]

    command_parser.parse(args.args)
