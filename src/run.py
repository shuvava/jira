#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from sys import path
from datetime import datetime
from statistics import mean, median, median_grouped, mode
from itertools import groupby
from operator import itemgetter

from dev_metrics.pass_mng import getuser, get_jira_password, remove_jira_password
from dev_metrics import JiraApi
from models import Issue, IssueHistory
from utills.data_dump import write_issues


base_url = 'https://ira_host'

BACKUP_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../backup'))

def get_filename(path=BACKUP_PATH, team=''):
    now = datetime.now().strftime("%Y%m%d%H%M%S") # current date and time
    if not os.path.exists(path):
        os.makedirs(path)
    file_name = f'search_{team}_{now}.jsonl'
    return os.path.join(path, file_name)

jra = JiraApi(base_url)

final_statuses = {'Closed', 'Done', 'Deployed'}

def get_statuses():
    sts = jra.get_statuses()
    for st in sts:
        print(f'    {st.name}')

def get_all_project():
    prjs = jra.get_projects()
    for prj in prjs:
        print(f'name={prj.name} key={prj.key} id={prj.id}')

def get_all_issues_for_prj():
    issues = jra.get_all_issues_for_project('PAYPROC')
    print(f'cnt={len(issues)}')

def get_issue_details(key='PAYPROC-277'):
    issue = jra.get_issue(key, fields=None)
    history = [(h.created, i.fromString, i.toString) for h in issue.changelog.histories for i in h.items if i.field == 'status']
    print(f'id={issue.id} key={issue.key}')
    now = datetime.now()
    for h in history:
        print(h)
    created_dt=issue.fields.created
    created_dt = datetime.strptime(created_dt, "%Y-%m-%dT%H:%M:%S.%f+0000")
    dev_dt= next((i[0] for i in history if i[2]=='In Development'), created_dt)
    if  isinstance(dev_dt, str):
        dev_dt = datetime.strptime(dev_dt, "%Y-%m-%dT%H:%M:%S.%f+0000")
    last_dt = next((i[0] for i in history if i[2] in final_statuses), now)
    if  isinstance(last_dt, str):
        last_dt = datetime.strptime(last_dt, "%Y-%m-%dT%H:%M:%S.%f+0000")
    time_to_dev=dev_dt-created_dt
    time_to_dep=last_dt-dev_dt
    print(f'created_dt={created_dt} dev_dt={dev_dt} last_dt={last_dt}')
    print(f'time_to_dev={time_to_dev.days} time_to_dep={time_to_dep.days}')

def avg(lst):
    if len(lst)>0:
        return sum(lst) / len(lst)
    return 0

def get_team_stats_lead_time(team_name='PAYPROC', show_points=True):
    issues = jra.get_all_issues_for_project(team_name)
    time_to_dev = []
    time_in_dev = []
    time_in_qa = []
    time_to_dep = []
    story_points = []
    now = datetime.now()
    now_week = now.isocalendar()[1]
    arr_issues = []
    for issue in issues:
        i = Issue()
        i.team = team_name
        i.id = issue.key
        i.status = issue.fields.status.name
        # if issue.fields.status.name not in final_statuses:
        #     continue
        history = [(h.created, i.fromString, i.toString) for h in issue.changelog.histories for i in h.items if i.field == 'status']
        if len(history) > 0:
            created_dt=issue.fields.created
            created_dt = datetime.strptime(created_dt, "%Y-%m-%dT%H:%M:%S.%f+0000")
            dev_dt= next((i[0] for i in history if i[2] in {'In Development', 'Selected for Development'}), created_dt)
            if  isinstance(dev_dt, str):
                dev_dt = datetime.strptime(dev_dt, "%Y-%m-%dT%H:%M:%S.%f+0000")
            qa_dt= next((i[0] for i in history if i[2]in {'Ready For Review', 'Needs Review'}), dev_dt)
            if  isinstance(qa_dt, str):
                qa_dt = datetime.strptime(qa_dt, "%Y-%m-%dT%H:%M:%S.%f+0000")
            dep_dt= next((i[0] for i in history if i[2]=='Ready for Deployment'), qa_dt)
            if  isinstance(dep_dt, str):
                dep_dt = datetime.strptime(dep_dt, "%Y-%m-%dT%H:%M:%S.%f+0000")
            last_dt = next((i[0] for i in history if i[2] in final_statuses), now)
            if  isinstance(last_dt, str):
                last_dt = datetime.strptime(last_dt, "%Y-%m-%dT%H:%M:%S.%f+0000")
            _time_to_dev=dev_dt-created_dt
            _time_in_dev=qa_dt-dev_dt
            _time_in_qa=dep_dt-qa_dt
            _time_to_dep=last_dt-dev_dt
            i.create_dt = created_dt
            i.close_dt = last_dt
            i.time_to_dev = _time_to_dev.days
            i.time_in_dev = _time_in_dev.days
            i.time_in_qa = _time_in_qa.days
            i.time_to_dep = _time_to_dep.days
            for h in history:
                _h = IssueHistory(h[2], h[0])
                i.history.append(_h)
            time_to_dev.append(_time_to_dev.days)
            time_in_dev.append(_time_in_dev.days)
            time_in_qa.append(_time_in_qa.days)
            time_to_dep.append(_time_to_dep.days)
            yr = last_dt.isocalendar()[0]
            week = last_dt.isocalendar()[1]
            sp = 0
            if hasattr(issue.fields, 'customfield_10002'):
                sp = issue.fields.customfield_10002
            i.story_points = sp
            story_points.append((yr, week, sp))
            arr_issues.append(i)
    if len(time_to_dev)>0:
        print(f'    days to start ticket development: avg={avg(time_to_dev):.4f} mean={mean(time_to_dev):.4f} median={median(time_to_dev):.4f}')
    if len(time_in_dev)>0:
        print(f'    days of ticket in development: avg={avg(time_in_dev):.4f} mean={mean(time_in_dev):.4f} median={median(time_in_dev):.4f}')
    if len(time_in_qa)>0:
        print(f'    days of ticket in qa: avg={avg(time_in_qa):.4f} mean={mean(time_in_qa):.4f} median={median(time_in_qa):.4f}')
    if len(time_to_dep)>0:
        print(f'    Lead time (days from start of development to deployment) : avg={avg(time_to_dep):.4f} mean={mean(time_to_dep):.4f} median={median(time_to_dep):.4f}')
    if show_points:
        print('\n    story point stats')
        story_points = [i for i in story_points if i[2] is not None]
        story_points = sorted(story_points, key= lambda d: (d[0], d[1]))
        groups = groupby(story_points, key= lambda d: (d[0], d[1]))
        for key, data in groups:
            sp = [i[2] for i in data if i[2] is not None and i[0]==2019 and i[1] != now_week]
            if len(sp)> 0:
                print(f'        key={key} story points={sum(sp)}')
    if len(arr_issues) > 0:
        filename = get_filename(team=team_name)
        print(f'backup file name: {filename}')
        write_issues(filename, arr_issues)
        print(f'count = {len(arr_issues)}')

def stat_for_all_teams():
    prjs = jra.get_projects()
    for prj in prjs:
        print(f'team {prj.key}')
        get_team_stats_lead_time(prj.key, False)

def stat_some_teams():
    teams = ['PAY','PAYPROC','PARK','BACK']
    for team in teams:
        print(f'team {team}')
        get_team_stats_lead_time(team, False)

def get_updated():
    items = jra.get_all_issues_for_period()
    print(len(items))

if __name__ == "__main__":
    usr = getuser()
    print(usr)
    #get_statuses()
    #get_all_project()
    #get_issue_details('BACK-2075')
    #stat_for_all_teams()
    #get_team_stats_lead_time()
    stat_some_teams()
    print('done')
