"""
Module provides utility funcitons for getting meta data s3
"""

import boto3
import os


def get_account_id() -> str:
    ''' Get aws account id '''
    return boto3.client('sts').get_caller_identity()['Account']


def get_profile() -> str:
    ''' Get aws profile name '''
    return os.environ.get('AWS_PROFILE', '')
