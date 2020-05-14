"""
Module that provides utility functions for getting aws secrets
"""

import boto3
import json

client = boto3.client('secretsmanager')


def fetch_secret(secret_id: str) -> dict:
    ''' Get aws secrets '''
    secret = {}
    response = client.get_secret_value(
        SecretId=secret_id
    )
    if response is not None:
        secret = json.loads(response['SecretString'])

    return secret
