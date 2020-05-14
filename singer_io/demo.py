"""
Demo showing configuration needed for singer tap and targets
"""


from utils.venv_tool import VenvTag, VenvTool
from utils.aws import meta, s3
from singer_io.singer_device import SingerDevice, SProp


class Tap(SingerDevice):
    ''' Provides config details to extracts data from s3 csv for demo '''

    env = VenvTool(VenvTag.tap_s3_csv)

    @property
    def config(self) -> dict:
        ''' Get config '''
        config_prop = self.get_template(SProp.config)
        config_prop['account_id'] = meta.get_account_id()
        config_prop['role_name'] = meta.get_profile()
        config_prop['bucket'] = s3.default_bucket
        return config_prop

    @property
    def catalog(self) -> dict:
        ''' Get catalog'''
        return self.get_template(SProp.catalog)

    @property
    def properties(self) -> dict:
        ''' Get propeties '''
        return self.get_template(SProp.catalog)

    @property
    def state(self) -> dict:
        ''' Get state '''
        return self.get_latest_state()


class Target(SingerDevice):
    ''' Provide configure details to loads data into postgres databse
    for demo '''

    env = VenvTool(VenvTag.singer_target_postgres)

    @property
    def config(self) -> dict:
        ''' Get config '''
        config_prop = self.get_template(SProp.config)
        return config_prop
