"""
Reference data for audit trail process
"""


from typing import NamedTuple, Dict, Tuple
from enum import Enum
from utils import db


class AuditRecord(NamedTuple):
    ''' Represents audit report row '''

    action_id: str
    timestamp: str
    user: str
    action: str
    section: str
    title: str
    label: str
    value: str


class Section(Enum):
    ''' Value options for the section column in audit trail report '''

    customer = 'Customer'
    user = 'User'
    transactions = 'Transactions'
    wire_window = 'Wire Window'


class PageTitle(Enum):
    ''' Value options for the page title column in audit trail report '''

    customer = 'ADMIN PANEL / CUSTOMER'
    account = 'ADMIN PANEL / ACCOUNT'
    authorizer = 'ADMIN PANEL / PENDING AUTHORIZER'
    management = 'ADMIN PANEL / USER MANAGEMENT'
    wire = 'ADMIN PANEL / WIRE'
    hybrid = 'ADMIN PANEL / HYBRID TRANSACTIONS'
    window = 'ADMIN PANEL / CHANGE WIRE WINDOW'
    entity = 'ADMIN PANEL / ADD NEW ENTITY'


class Label(Enum):
    ''' Value options for the Label column in the audit trail report '''

    company_name = 'Company Name'
    reject_reason = 'Reject Reason'
    account_type = 'Account Type'
    authorizer = 'Authorizer Name'
    user_name = 'User Name'
    txn_amount = 'Transaction Amount'
    t24_txn_id = 'T24 Transaction ID'
    wire_status = 'Wire Status'
    firm_name = 'Firm Name'


class RefTool(object):
    ''' Tool for pulling reference data for audit trail report '''

    def __init__(self):
        self._company_map = {}
        self._user_company = []

    @property
    def company_map(self) -> Dict[str, str]:
        ''' Mapping of company id to company name '''
        if not self._company_map:
            company_batches = db.customer_pipelines('audit_trail_company_map_vw')
            self._company_map = {str(row['id']): row['name'] for batch in company_batches for row in batch}

        return self._company_map

    def get_user_details(self, user_id: str) -> Tuple[str, list]:
        ''' Provides user details for user id '''
        if not self._user_company:
            user_details = db.customer_pipelines('audit_trail_user_company_vw')
            self._user_company = [row for batch in user_details for row in batch]

        companies = [uc['company_name'] for uc in self._user_company if str(uc['user_id']) == user_id]
        user_name = next((u['user_name'] for u in self._user_company if str(u['user_id']) == user_id), '')

        return user_name, companies
