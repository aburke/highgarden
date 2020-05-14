"""
Pull db data
"""
import psycopg2
import os

from utils.aws import secrets
from typing import Iterable


def customer_pipelines(table: str, batch_size: int = 10000) -> Iterable:
    ''' Get table/view data from custmers.pipelines schema '''
    secret_key = 'bastille/app/businesslogicapi/CustomerDB'
    db_details = secrets.fetch_secret(secret_key)
    database = os.environ.get('customer_db', db_details['database'])
    user = os.environ.get('customer_db_user', db_details['user'])
    host = os.environ.get('customer_db_host', db_details['host'])
    password = os.environ.get('customer_db_password', db_details['password'])
    pipelines_schema = os.environ.get('pipelines_schema', 'pipelines')
    conn_str = f"dbname='{database}' user='{user}' host='{host}' password='{password}'"
    query = f'SELECT * FROM {pipelines_schema}.{table}'
    conn = psycopg2.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute(query)
    desc = [q.name for q in cursor.description]
    records = [{i: x for i, x in zip(desc, qd)} for qd in cursor.fetchmany(batch_size)]
    while records:
        yield records
        records = [{i: x for i, x in zip(desc, qd)} for qd in cursor.fetchmany(batch_size)]
