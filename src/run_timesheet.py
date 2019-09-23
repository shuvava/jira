#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from sys import path
from datetime import datetime

from dev_metrics import JiraApi
from dev_metrics.pass_mng import getuser, get_jira_password, remove_jira_password

base_url = 'https://ira_host'

jra = JiraApi(base_url)

def prase_time(dt):
    try:
        return datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S.%f+0000")
    except:
        return None

def truncate_time(dt):
    return datetime(dt.year, dt.month, dt.day)

def time_to_str(dt):
    return dt.strftime("%Y-%m-%d")

def get_updated():
    usr = getuser().lower()
    items = jra.get_all_issues_for_period()
    print(f'count={len(items)}')
    timesheets = []
    for issue in items:
         for worklog in issue.fields.worklog.worklogs:
            if worklog.author.name.lower() == usr:
                dt = prase_time(worklog.started)
                if dt:
                    dt = time_to_str(dt)
                    timesheets.append((dt, issue.key, worklog.timeSpentSeconds, worklog.author.name))
    timesheets = sorted(timesheets, key= lambda d: (d[0], d[1]))
    for item in timesheets:
        print(f'dt={item[0]} issue={item[1]} hours={item[2]/3600}')
    return timesheets

if __name__ == "__main__":
    usr = getuser()
    # remove_jira_password()
    print(usr)

    get_updated()
    print('done')
