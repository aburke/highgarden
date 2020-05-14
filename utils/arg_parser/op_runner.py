from argparse import ArgumentParser
from typing import List
from operators.process import OpCommand
from operators.audit_trail.audit_ops import generate_audit_report


command_map = {
    OpCommand.audit_report: generate_audit_report
}


def parse(args: List[str]) -> None:
    ''' Run operator process '''
    parser = ArgumentParser(
        prog="operator",
        description="Run operator process"
    )

    parser.add_argument(
        'command',
        help="operator command"
    )

    command_args = parser.parse_args(args)

    cmd = command_map[OpCommand[command_args.command]]
    cmd()
