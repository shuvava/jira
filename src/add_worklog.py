#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from datetime import datetime

from dev_metrics import JiraApi
from dev_metrics.pass_mng import getuser, get_jira_password, remove_jira_password

base_url = 'https://ira_host'
user_domain = '@comp.com'

jra = JiraApi(base_url, user_domain)

def prase_time(dt=None):
    try:
        if not dt:
            dt = sys.argv[3]
        return datetime.strptime(dt, "%Y-%m-%d")
    except:
        return datetime.now()

def add_work(issue_id, hours, dt, comment=None):
    issue = jra.get_issue(issue_id)
    if issue:
        jra.jira.add_worklog(issue, f'{hours}h', started=dt)

if __name__ == "__main__":
    usr = getuser()
    # remove_jira_password()
    print(usr)
    try:
        issue_id = sys.argv[1]
    except:
        pass
    print(f'JIRA issue {issue_id}')
    try:
        hours = int(sys.argv[2])
    except:
        hours = 8
    print(f'logged hours {hours}')
    dt=prase_time()
    try:
        comment = sys.argv[4]
    except:
        comment = None
    print(f'date {dt}')
    add_work(issue_id, hours, dt, comment)
    print('done')
