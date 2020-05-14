"""
Module provides functions for processing admin logs
"""
import operators.audit_trail.audit_parser as ap
import logging
import os

from operators.audit_trail.reference import RefTool, AuditRecord
from typing import Iterable, Iterator, List
from utils.aws import logs, s3
from utils import slackapi
from datetime import datetime, timedelta


class AuditOps(object):
    ''' Tool to handle audit report generation operations '''

    def __init__(self, proc_dt: datetime):
        self.proc_dt = proc_dt
        self.s3_audit_trail_path = 'audit-trail'

    @property
    def audit_report_channel(self) -> str:
        ''' Audit report channel '''
        channel = '#core-systems'
        if os.environ.get('ENV_NAME', '').upper() == 'PROD':
            channel = '#risk-reports'
        return channel

    @property
    def audit_report_url(self) -> str:
        ''' Audit report s3 object url '''
        base_url = f'https://{s3.default_bucket}.s3.amazonaws.com'
        link = f'{base_url}/{self.audit_trail_key}'
        return link

    @property
    def date_str(self) -> str:
        ''' Date string representing process date '''
        report_date = datetime(self.proc_dt.year, self.proc_dt.month, self.proc_dt.day) - timedelta(days=1)
        return report_date.strftime('%Y-%m-%d')

    @property
    def audit_trail_key(self) -> str:
        ''' S3 key for audit report document '''
        return f'{self.s3_audit_trail_path}/{self.date_str}/{self.date_str}_Admin_Panel_Audit_Report.csv'

    @property
    def auditors(self) -> List[ap.AuditParser]:
        ''' List of Audit parsers used for the audit report '''
        ref_tool = RefTool()
        return [
            ap.ApprovePendingCustomer(),
            ap.RejectPendingCustomer(ref_tool),
            ap.ApprovePendingAccount(ref_tool),
            ap.RejectPendingAccount(ref_tool),
            ap.ApprovePendingAuthorizer(ref_tool),
            ap.RejectPendingAuthorizer(ref_tool),
            ap.ResetCustomerPassword(ref_tool),
            ap.ApproveOFACFlaggedTransaction(),
            ap.RejectOFACFlaggedTransaction(ref_tool),
            ap.ApproveHybridTransaction(),
            ap.RejectHybridTransaction(ref_tool),
            ap.ChangeWireWindow(),
            ap.DeactivateUser(ref_tool),
            ap.AddNewEntity()
        ]

    def pull_admin_logs(self) -> Iterator[str]:
        ''' Get stream of admin logs for a 24 hour period ending at the proc_dt '''
        start = datetime(self.proc_dt.year, self.proc_dt.month, self.proc_dt.day) - timedelta(days=1)
        end = datetime(self.proc_dt.year, self.proc_dt.month, self.proc_dt.day)

        admin_logs = logs.log_stream(
            logs.LogGroup.blapi_admin,
            start,
            end
        )

        return admin_logs

    def parse_logs(self, log_messages: Iterable[str]) -> str:
        ''' Parse log messages and return csv of extracted data '''
        audit_record_csv = [','.join(f.upper() for f in AuditRecord._fields)]

        action_id = 1
        for log in log_messages:
            is_audit_record = False
            for adt in self.auditors:
                adt.log_message = log
                audit_details = adt.extract_audit_details(str(action_id))
                if audit_details:
                    is_audit_record = True
                    break

            if is_audit_record:
                action_id += 1
                audit_record_csv += [','.join(detail) for detail in audit_details]

        return '\n'.join(audit_record_csv)


def generate_audit_report(proc_dt: datetime = datetime.now()):
    ''' Generate audit report and store it in s3 '''
    audit_ops = AuditOps(proc_dt)

    logging.info(f'Pull admin logs for report date: {audit_ops.date_str}')
    admin_logs = audit_ops.pull_admin_logs()

    logging.info('Parse admin log messages')
    audit_report_csv = audit_ops.parse_logs(admin_logs)

    logging.info('Upload report to s3')
    s3.upload_object(
        key=audit_ops.audit_trail_key,
        data=audit_report_csv,
        public=True
    )

    logging.info(f'Post link to {audit_ops.audit_report_channel} channel')
    slackapi.send_message(
        channel=audit_ops.audit_report_channel,
        message=audit_ops.audit_report_url
    )
