"""
Helper functions for tap s3 csv tasks
"""
from singer_io.singer_device import SingerDevice, SProp
from utils.aws import meta, s3


def get_config_with_aws_details(sd: SingerDevice) -> dict:
    ''' Get config template with aws meta details '''
    config_prop = sd.get_template(SProp.config)
    config_prop['account_id'] = meta.get_account_id()
    config_prop['role_name'] = meta.get_profile()
    config_prop['bucket'] = s3.default_bucket
    return config_prop
