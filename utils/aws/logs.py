"""
Module contains helper functions for extracting log data from aws
"""
import boto3
import time

from enum import Enum
from datetime import datetime
from utils.aws import s3
from io import BytesIO
from gzip import GzipFile
from typing import Iterator
from datetime import timezone


log_archive_path = 'log-archive'
client = boto3.client('logs')


class LogGroup(Enum):
    ''' Category of log groups '''

    blapi = '/aws/elasticbeanstalk/businesslogicapi/var/log/nodejs/nodejs.log'
    blapi_admin = '/aws/elasticbeanstalk/businesslogicapi-admin/var/log/\
nodejs/nodejs.log'


def archive_logs(
    log_group: LogGroup,
    start: datetime,
    end: datetime,
    bucket: str = s3.default_bucket,
    archive_path: str = log_archive_path
) -> str:
    ''' Archive logs from a specific log group to s3 withing a time range '''
    utc_start = int(start.replace(tzinfo=timezone.utc).timestamp() * 1000)
    utc_end = int(end.replace(tzinfo=timezone.utc).timestamp() * 1000)

    export_resp = client.create_export_task(
        taskName='export_task',
        logGroupName=log_group.value,
        fromTime=utc_start,
        to=utc_end,
        destination=bucket,
        destinationPrefix=archive_path
    )

    desc_resp = client.describe_export_tasks(taskId=export_resp['taskId'])
    status = desc_resp['exportTasks'][0]['status']['code']
    pending_status = ['PENDING', 'PENDING_CANCEL']
    while status in pending_status:
        time.sleep(1)
        desc_resp = client.describe_export_tasks(taskId=export_resp['taskId'])
        status = desc_resp['exportTasks'][0]['status']['code']

    if status == 'FAILED':
        message = "Log export failed for the following task id: {}".format(
            export_resp['taskId']
        )
        raise RuntimeError(message)

    return export_resp['taskId']


def log_stream(log_group: LogGroup,
               start: datetime, end: datetime) -> Iterator[str]:
    ''' Get logs for a particular log group within a given time frame '''
    task_id = archive_logs(log_group, start, end)
    log_prefix = '/'.join([log_archive_path, task_id])
    search_response = s3.search(log_prefix)
    logzfiles = [r['Key'] for r in search_response]
    try:
        for gzfile in logzfiles:
            stream = s3.get_object(gzfile)
            buffer = BytesIO(stream.read())
            with GzipFile(fileobj=buffer) as gz_bytes:
                for record in gz_bytes:
                    yield record.decode('utf-8').strip()
    finally:
        s3.delete_objects(logzfiles)
