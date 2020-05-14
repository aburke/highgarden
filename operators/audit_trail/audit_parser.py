"""
Log parsers for audit trail data
"""
from typing import Dict, List
from operators.audit_trail.reference import AuditRecord, Section, PageTitle, RefTool, Label


class AuditParser(object):
    ''' Base class for extracting audit logs data from blapi admin logs '''

    action = ''
    signature = 'module=lib/auditLog.js'

    def __init__(self):
        self.log_message = ''

    def get_tokens(self) -> Dict[str, str]:
        ''' Extract key value pairs from the log message '''
        tokens = {}
        i = 0
        sections = self.log_message.split(' ')
        log_len = len(sections)
        while i < log_len:
            if '=' in sections[i]:
                key, val = sections[i].split('=')
                i += 1
                while i < log_len and '=' not in sections[i]:
                    val = f'{val} {sections[i]}'
                    i += 1
                tokens[key] = val[:-1] if val[-1] == ',' else val
            else:
                i += 1

        if sections:
            tokens['timestamp'] = sections[0]

        return tokens

    def scope_parse(self, action_id: str) -> List[AuditRecord]:
        ''' Parse logs for specific audit log scenario '''
        return []

    def extract_audit_details(self, action_id: str = '-1') -> List[AuditRecord]:
        ''' Get data relavent for the specific audit report type from log mesasge'''
        is_audit_log = self.signature in self.log_message
        has_action = self.action in self.log_message
        return self.scope_parse(action_id) if is_audit_log and has_action else []


class ApprovePendingCustomer(AuditParser):
    ''' Parser for "Approve Pending Customer" logs '''

    action = 'Approve Pending Customer'

    def scope_parse(self, action_id: str) -> List[AuditRecord]:
        ''' Parse log message for "approve pending customer" scenario '''
        tk = self.get_tokens()
        records = []
        records.append(AuditRecord(
            action_id=action_id,
            timestamp=tk.get('timestamp', ''),
            user=tk.get('adminFullName', ''),
            action=self.action,
            section=Section.customer.value,
            title=PageTitle.customer.value,
            label=Label.company_name.value,
            value=tk.get('customerName', '')
        ))
        return records


class RejectPendingCustomer(AuditParser):
    ''' Parser for "Reject Pending Customer" logs '''

    action = 'Reject Pending Customer'

    def __init__(self, ref_tool: RefTool):
        super().__init__()
        self.ref_tool = ref_tool

    def scope_parse(self, action_id: str) -> List[AuditRecord]:
        ''' Parse log message for "reject pending customer" scenario '''
        tk = self.get_tokens()
        records = []
        records.append(AuditRecord(
            action_id=action_id,
            timestamp=tk.get('timestamp', ''),
            user=tk.get('adminFullName', ''),
            action=self.action,
            section=Section.customer.value,
            title=PageTitle.customer.value,
            label=Label.company_name.value,
            value=self.ref_tool.company_map.get(tk.get('companyId', ''), '')
        ))
        records.append(AuditRecord(
            action_id=action_id,
            timestamp=tk.get('timestamp', ''),
            user=tk.get('adminFullName', ''),
            action=self.action,
            section=Section.customer.value,
            title=PageTitle.customer.value,
            label=Label.reject_reason.value,
            value=tk.get('rejectionReason', '')
        ))
        return records


class ApprovePendingAccount(AuditParser):
    ''' Parser for "Approve Pending Account" logs '''

    action = 'Approve Pending Account'

    def __init__(self, ref_tool: RefTool):
        super().__init__()
        self.ref_tool = ref_tool

    def scope_parse(self, action_id: str) -> List[AuditRecord]:
        ''' Parse log message for "approve pending account" scenario '''
        tk = self.get_tokens()
        records = []
        records.append(AuditRecord(
            action_id=action_id,
            timestamp=tk.get('timestamp', ''),
            user=tk.get('adminFullName', ''),
            action=self.action,
            section=Section.customer.value,
            title=PageTitle.account.value,
            label=Label.company_name.value,
            value=self.ref_tool.company_map.get(tk.get('companyId', ''), '')
        ))
        records.append(AuditRecord(
            action_id=action_id,
            timestamp=tk.get('timestamp', ''),
            user=tk.get('adminFullName', ''),
            action=self.action,
            section=Section.customer.value,
            title=PageTitle.account.value,
            label=Label.account_type.value,
            value=tk.get('accountType', '')
        ))

        return records


class RejectPendingAccount(AuditParser):
    ''' Parser for "Reject Pending Account" logs '''

    action = 'Reject Pending Account'

    def __init__(self, ref_tool: RefTool):
        super().__init__()
        self.ref_tool = ref_tool

    def scope_parse(self, action_id: str) -> List[AuditRecord]:
        ''' Parse log message for "reject pending account" scenario '''
        tk = self.get_tokens()
        records = []
        records.append(AuditRecord(
            action_id=action_id,
            timestamp=tk.get('timestamp', ''),
            user=tk.get('adminFullName', ''),
            action=self.action,
            section=Section.customer.value,
            title=PageTitle.account.value,
            label=Label.company_name.value,
            value=self.ref_tool.company_map.get(tk.get('companyId', ''), '')
        ))

        return records


class ApprovePendingAuthorizer(AuditParser):
    ''' Parser for "Approve Pending Authorizer" logs '''

    action = 'Approve Pending Authorizer'

    def __init__(self, ref_tool: RefTool):
        super().__init__()
        self.ref_tool = ref_tool

    def scope_parse(self, action_id: str) -> List[AuditRecord]:
        ''' Parse log message for "approve pending authorizer" scenario '''
        tk = self.get_tokens()
        records = []
        records.append(AuditRecord(
            action_id=action_id,
            timestamp=tk.get('timestamp', ''),
            user=tk.get('adminFullName', ''),
            action=self.action,
            section=Section.user.value,
            title=PageTitle.authorizer.value,
            label=Label.authorizer.value,
            value=tk.get('authorizerFullname', '')
        ))
        records.append(AuditRecord(
            action_id=action_id,
            timestamp=tk.get('timestamp', ''),
            user=tk.get('adminFullName', ''),
            action=self.action,
            section=Section.user.value,
            title=PageTitle.authorizer.value,
            label=Label.company_name.value,
            value=self.ref_tool.company_map.get(tk.get('companyId', ''), '')
        ))

        return records


class RejectPendingAuthorizer(AuditParser):
    ''' Parser for "Reject Pending Authorizer" logs '''

    action = 'Reject Pending Authorizer'

    def __init__(self, ref_tool: RefTool):
        super().__init__()
        self.ref_tool = ref_tool

    def scope_parse(self, action_id: str) -> List[AuditRecord]:
        ''' Parse log message for "reject pending authorizer" scenario '''
        tk = self.get_tokens()
        records = []
        records.append(AuditRecord(
            action_id=action_id,
            timestamp=tk.get('timestamp', ''),
            user=tk.get('adminFullName', ''),
            action=self.action,
            section=Section.user.value,
            title=PageTitle.authorizer.value,
            label=Label.authorizer.value,
            value=tk.get('authorizerFullname', '')
        ))
        records.append(AuditRecord(
            action_id=action_id,
            timestamp=tk.get('timestamp', ''),
            user=tk.get('adminFullName', ''),
            action=self.action,
            section=Section.user.value,
            title=PageTitle.authorizer.value,
            label=Label.company_name.value,
            value=self.ref_tool.company_map.get(tk.get('companyId', ''), '')
        ))

        return records


class ResetCustomerPassword(AuditParser):
    ''' Parser for "Reset Customer Password" logs '''

    action = 'Reset Customer Password'

    def __init__(self, ref_tool: RefTool):
        super().__init__()
        self.ref_tool = ref_tool

    def scope_parse(self, action_id: str) -> List[AuditRecord]:
        ''' Parse log message for "reset customer password" scenario '''
        tk = self.get_tokens()
        records = []
        user_name, companies = self.ref_tool.get_user_details(tk.get('userId', ''))
        records.append(AuditRecord(
            action_id=action_id,
            timestamp=tk.get('timestamp', ''),
            user=tk.get('adminFullName', ''),
            action=self.action,
            section=Section.user.value,
            title=PageTitle.management.value,
            label=Label.user_name.value,
            value=user_name
        ))

        for company in companies:
            records.append(AuditRecord(
                action_id=action_id,
                timestamp=tk.get('timestamp', ''),
                user=tk.get('adminFullName', ''),
                action=self.action,
                section=Section.user.value,
                title=PageTitle.authorizer.value,
                label=Label.company_name.value,
                value=company
            ))

        return records


class ApproveOFACFlaggedTransaction(AuditParser):
    ''' Parser for "Approve OFAC Flagged Transaction" logs '''

    action = 'Approve OFAC Flagged Transaction'

    def scope_parse(self, action_id: str) -> List[AuditRecord]:
        ''' Parse log message for "approve ofac flagged" scenario '''
        tk = self.get_tokens()
        records = []
        records.append(AuditRecord(
            action_id=action_id,
            timestamp=tk.get('timestamp', ''),
            user=tk.get('adminFullName', ''),
            action=self.action,
            section=Section.transactions.value,
            title=PageTitle.wire.value,
            label=Label.txn_amount.value,
            value=tk.get('amount', '')
        ))
        records.append(AuditRecord(
            action_id=action_id,
            timestamp=tk.get('timestamp', ''),
            user=tk.get('adminFullName', ''),
            action=self.action,
            section=Section.transactions.value,
            title=PageTitle.wire.value,
            label=Label.company_name.value,
            value=tk.get('companyName', '')
        ))

        return records


class RejectOFACFlaggedTransaction(AuditParser):
    ''' Parser for "Rejet OFAC Flagged Transaction" logs '''

    action = 'Reject OFAC Flagged Transaction'

    def __init__(self, ref_tool: RefTool):
        super().__init__()
        self.ref_tool = ref_tool

    def scope_parse(self, action_id: str) -> List[AuditRecord]:
        ''' Parse log message for "reject ofac flagged" scenario '''
        tk = self.get_tokens()
        records = []
        records.append(AuditRecord(
            action_id=action_id,
            timestamp=tk.get('timestamp', ''),
            user=tk.get('adminFullName', ''),
            action=self.action,
            section=Section.transactions.value,
            title=PageTitle.wire.value,
            label=Label.txn_amount.value,
            value=tk.get('amount', '')
        ))
        records.append(AuditRecord(
            action_id=action_id,
            timestamp=tk.get('timestamp', ''),
            user=tk.get('adminFullName', ''),
            action=self.action,
            section=Section.transactions.value,
            title=PageTitle.wire.value,
            label=Label.company_name.value,
            value=self.ref_tool.company_map.get(tk.get('companyId', ''), '')
        ))

        return records


class ApproveHybridTransaction(AuditParser):
    ''' Parser for "Approve Hybrid Transaction" logs '''

    action = 'Approve Hybrid Transaction'

    def scope_parse(self, action_id: str) -> List[AuditRecord]:
        ''' Parse log message for "approve hybrid transaction" scenario '''
        tk = self.get_tokens()
        records = []
        records.append(AuditRecord(
            action_id=action_id,
            timestamp=tk.get('timestamp', ''),
            user=tk.get('adminFullName', ''),
            action=self.action,
            section=Section.transactions.value,
            title=PageTitle.hybrid.value,
            label=Label.txn_amount.value,
            value=tk.get('amount', '')
        ))
        records.append(AuditRecord(
            action_id=action_id,
            timestamp=tk.get('timestamp', ''),
            user=tk.get('adminFullName', ''),
            action=self.action,
            section=Section.transactions.value,
            title=PageTitle.hybrid.value,
            label=Label.t24_txn_id.value,
            value=tk.get('t24TransactionId', '')
        ))
        records.append(AuditRecord(
            action_id=action_id,
            timestamp=tk.get('timestamp', ''),
            user=tk.get('adminFullName', ''),
            action=self.action,
            section=Section.transactions.value,
            title=PageTitle.hybrid.value,
            label=Label.company_name.value,
            value=tk.get('companyName', '')
        ))

        return records


class RejectHybridTransaction(AuditParser):
    ''' Parser for "Reject Hybrid Transaction" logs '''

    action = 'Reject Hybrid Transaction'

    def __init__(self, ref_tool: RefTool):
        super().__init__()
        self.ref_tool = ref_tool

    def scope_parse(self, action_id: str) -> List[AuditRecord]:
        ''' Parse log message for "reject hybrid transaction" scenario '''
        tk = self.get_tokens()
        records = []
        records.append(AuditRecord(
            action_id=action_id,
            timestamp=tk.get('timestamp', ''),
            user=tk.get('adminFullName', ''),
            action=self.action,
            section=Section.transactions.value,
            title=PageTitle.hybrid.value,
            label=Label.txn_amount.value,
            value=tk.get('amount', '')
        ))
        records.append(AuditRecord(
            action_id=action_id,
            timestamp=tk.get('timestamp', ''),
            user=tk.get('adminFullName', ''),
            action=self.action,
            section=Section.transactions.value,
            title=PageTitle.hybrid.value,
            label=Label.company_name.value,
            value=self.ref_tool.company_map.get(tk.get('companyId', ''), '')
        ))

        return records


class ChangeWireWindow(AuditParser):
    ''' Parser for "Change Wire Window" logs '''

    action = 'Change Wire Window'

    def scope_parse(self, action_id: str) -> List[AuditRecord]:
        ''' Parse log message for "change wire window" scenario '''
        tk = self.get_tokens()
        records = []
        records.append(AuditRecord(
            action_id=action_id,
            timestamp=tk.get('timestamp', ''),
            user=tk.get('adminFullName', ''),
            action=self.action,
            section=Section.wire_window.value,
            title=PageTitle.window.value,
            label=Label.wire_status.value,
            value=tk.get('wireStatus', '')
        ))

        return records


class DeactivateUser(AuditParser):
    ''' Parser for "Deactivate User" logs '''

    action = 'Deactivate User'

    def __init__(self, ref_tool: RefTool):
        super().__init__()
        self.ref_tool = ref_tool

    def scope_parse(self, action_id: str) -> List[AuditRecord]:
        ''' Parse log message for "deactivate user" scenario '''
        tk = self.get_tokens()
        records = []
        user_name, companies = self.ref_tool.get_user_details(tk.get('userId', ''))
        records.append(AuditRecord(
            action_id=action_id,
            timestamp=tk.get('timestamp', ''),
            user=tk.get('adminFullName', ''),
            action=self.action,
            section=Section.user.value,
            title=PageTitle.management.value,
            label=Label.user_name.value,
            value=user_name
        ))

        for company in companies:
            records.append(AuditRecord(
                action_id=action_id,
                timestamp=tk.get('timestamp', ''),
                user=tk.get('adminFullName', ''),
                action=self.action,
                section=Section.user.value,
                title=PageTitle.management.value,
                label=Label.company_name.value,
                value=company
            ))

        return records


class AddNewEntity(AuditParser):
    ''' Parser for "Add new Entity to firm" logs '''

    action = 'Add new entity to firm'

    def scope_parse(self, action_id: str) -> List[AuditRecord]:
        ''' Parse log message for "deactivate user" scenario '''
        tk = self.get_tokens()
        records = []
        records.append(AuditRecord(
            action_id=action_id,
            timestamp=tk.get('timestamp', ''),
            user=tk.get('adminFullName', ''),
            action=self.action,
            section=Section.customer.value,
            title=PageTitle.entity.value,
            label=Label.company_name.value,
            value=tk.get('companyName', '')
        ))
        records.append(AuditRecord(
            action_id=action_id,
            timestamp=tk.get('timestamp', ''),
            user=tk.get('adminFullName', ''),
            action=self.action,
            section=Section.customer.value,
            title=PageTitle.entity.value,
            label=Label.firm_name.value,
            value=tk.get('firmName', '')
        ))

        return records
