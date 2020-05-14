"""
Module contains commands for the bash operators
"""
from utils.venv_tool import pipeline_home, VenvTag, VenvTool
from enum import Enum


class OpCommand(Enum):
    ''' Operator commands '''

    audit_report = 1


class Trigger(object):
    ''' Contains string representation of commands that would trigger operator processes '''

    def get_op_runner_cmd(self, cmd_tag: OpCommand) -> str:
        ''' Get the op_runner command for the specific command tag '''
        ghp_cmd = f'python3 {pipeline_home}/ghp.py'
        return f'{ghp_cmd} op_runner {cmd_tag.name}'

    def get_activate_cmd(self, tag: VenvTag) -> str:
        ''' Generates command to activate a virtual environment '''
        v_tool = VenvTool(tag)
        return f'. {v_tool.path}/bin/activate'

    def get_bash_command(self, v_tag: VenvTag, cmd_tag: OpCommand) -> str:
        ''' Get bash command for op_runner process '''
        activate_cmd = self.get_activate_cmd(v_tag)
        op_runner_cmd = self.get_op_runner_cmd(cmd_tag)
        return f'{activate_cmd} && {op_runner_cmd} && deactivate'

    @property
    def audit_report(self) -> str:
        ''' Run audit report generation '''
        return self.get_bash_command(VenvTag.operators, OpCommand.audit_report)
