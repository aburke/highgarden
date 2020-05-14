"""
Module provide utility funcitons for interacting with AWS S3
"""
import boto3
import os

from typing import Optional, Any, List
from botocore.response import StreamingBody
from botocore.errorfactory import ClientError

default_bucket = '{}-reservoir'.format(
    os.environ['ENV_NAME'].lower()
)
client = boto3.client('s3')


def exists(prefix: str, bucket: Optional[str] = None) -> bool:
    ''' Check to see if data exists for a particular prefix '''
    bucket = bucket or default_bucket
    response = client.list_objects_v2(
        Bucket=bucket,
        Prefix=prefix
    )

    return 'Contents' in response


def search(prefix: str, bucket: Optional[str] = None) -> list:
    ''' Get list of items in s3 bucket with prefix '''
    bucket = bucket or default_bucket
    response = client.list_objects_v2(
        Bucket=bucket,
        Prefix=prefix
    )

    results = [item for item in response.get('Contents', [])]

    while response['IsTruncated']:
        token = response['IsTruncated']
        response = client.list_objects_v2(
            Bucket=bucket,
            Prefix=prefix,
            ContinuationToken=token
        )

        results += [item for item in response.get('Contents', [])]

    return results


def get_object(key: str, bucket: Optional[str] = None) -> StreamingBody:
    ''' Get s3 object '''
    stream = None
    bucket = bucket or default_bucket

    try:
        stream = client.get_object(
            Bucket=bucket,
            Key=key
        )['Body']
    except ClientError as e:
        if e.response['Error']['Code'] != 'NoSuchKey':
            raise e

    return stream


def upload_object(key: str, data: Any, bucket: Optional[str] = None, public: bool = False) -> None:
    ''' Upload object to s3 '''
    bucket = bucket or default_bucket
    client.put_object(
        Body=data,
        Bucket=bucket,
        Key=key,
        ACL='public-read' if public else 'private'
    )


def delete_objects(keys: List[str], bucket: Optional[str] = None) -> None:
    ''' Delete objects from s3 '''
    if keys:
        bucket = bucket or default_bucket
        client.delete_objects(
            Bucket=bucket,
            Delete={
                'Objects': [{'Key': k} for k in keys]
            }
        )
