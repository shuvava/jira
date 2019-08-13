# -*- coding: utf-8 -*-
from  jira import JIRA

from .pass_mng import getuser, get_jira_password

class JiraApi:
    def __init__(self, url):
        usr = getuser()
        passwd = get_jira_password(True)
        self.jira = JIRA(url, basic_auth=(usr, passwd))

    def get_projects(self):
        return self.jira.projects()

    def get_statuses(self):
        return self.jira.statuses()

    def get_all_issues_for_project(self, project_key, fields='id,key,status,summary'):
        result = []
        current = 0
        total = 1
        while current<total:
            #
            items = self.jira.search_issues(f'project={project_key} order by id', fields=fields, expand='changelog' , maxResults=50, startAt=current)
            total = items.total
            current += len(items)
            result.extend(items)
        return result
