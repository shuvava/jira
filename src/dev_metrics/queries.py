# -*- coding: utf-8 -*-
from  jira import JIRA

from .pass_mng import getuser, get_jira_password

# get filed ids and meanings /rest/api/2/field
# {
#     "id": "customfield_10002",
#     "name": "Story Points",
#     "custom": true,
#     "orderable": true,
#     "navigable": true,
#     "searchable": true,
#     "clauseNames": [
#         "cf[10002]",
#         "Story Points"
#     ],
#     "schema": {
#         "type": "number",
#         "custom": "com.atlassian.jira.plugin.system.customfieldtypes:float",
#         "customId": 10002
#     }
# }
class JiraApi:
    def __init__(self, url, userdomain=None):
        if userdomain is None:
            userdomain = ''
        usr = f'{getuser()}{userdomain}'
        passwd = get_jira_password(True)
        self.jira = JIRA(url, basic_auth=(usr, passwd))

    def get_projects(self):
        return self.jira.projects()

    def get_statuses(self):
        return self.jira.statuses()

    def get_all_issues_for_project(self, project_key, fields='id,key,status,summary,customfield_10002,created,updated', expand='changelog'):
        result = []
        current = 0
        total = 1
        while current<total:
            #
            items = self.jira.search_issues(
                f'project={project_key} order by id',
                fields=fields,
                expand=expand ,
                maxResults=50,
                startAt=current,
                )
            total = items.total
            current += len(items)
            result.extend(items)
        return result

    def get_all_issues_for_period(self, start_date='-7d', fields='id,key,status,summary,customfield_10002,created,updated,worklog', expand='changelog'):
        result = []
        current = 0
        total = 1
        while current<total:
            #
            items = self.jira.search_issues(
                f'updated >= {start_date} order by id',
                fields=fields,
                expand=expand ,
                maxResults=50,
                startAt=current,
                )
            total = items.total
            current += len(items)
            result.extend(items)
        return result

    def get_issue(self, issue_id, fields='id,key,status,summary,customfield_10002,created,updated', expand='changelog'):
        return self.jira.issue(issue_id, fields=fields, expand=expand)
