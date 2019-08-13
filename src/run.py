#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dev_metrics.pass_mng import getuser, get_jira_password, remove_jira_password
from dev_metrics import JiraApi


base_url = 'https://ira_host'

def get_all_project():
    jra = JiraApi(base_url)
    prjs = jra.get_projects()
    for prj in prjs:
        print(f'name={prj.name} key={prj.key} id={prj.id}')

def get_all_issues_for_prj():
    jra = JiraApi(base_url)
    issues = jra.get_all_issues_for_project('PAYPROC')
    print(f'cnt={len(issues)}')

if __name__ == "__main__":
    usr = getuser()
    print(usr)
    get_all_issues_for_prj()
    print('done')