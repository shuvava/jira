#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from statistics import mean, median, median_grouped, mode
from itertools import groupby
from operator import itemgetter

from dev_metrics.pass_mng import getuser, get_jira_password, remove_jira_password
from dev_metrics import JiraApi


base_url = 'https://ira_host'


jra = JiraApi(base_url)

def get_all_project():
    prjs = jra.get_projects()
    for prj in prjs:
        print(f'name={prj.name} key={prj.key} id={prj.id}')

def get_all_issues_for_prj():
    issues = jra.get_all_issues_for_project('PAYPROC')
    print(f'cnt={len(issues)}')

def get_issue_details():
    issue = jra.get_issue('PAYPROC-277')
    history = [(h.created, i.fromString, i.toString) for h in issue.changelog.histories for i in h.items if i.field == 'status']
    print(f'id={issue.id} key={issue.key}')
    now = datetime.now()
    for h in history:
        print(h)
    created_dt=min(history)[0]
    created_dt = datetime.strptime(created_dt, "%Y-%m-%dT%H:%M:%S.%f+0000")
    dev_dt= next((i[0] for i in history if i[2]=='In Development'), created_dt)
    if  isinstance(dev_dt, str):
        dev_dt = datetime.strptime(dev_dt, "%Y-%m-%dT%H:%M:%S.%f+0000")
    last_dt = next((i[0] for i in history if i[2]=='Closed'), now)
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

def get_team_stats_lead_time(team_name='PAYPROC'):
    issues = jra.get_all_issues_for_project(team_name)
    time_to_dev = []
    time_to_dep = []
    story_points = []
    now = datetime.now()
    now_week = now.isocalendar()[1]
    for issue in issues:
        history = [(h.created, i.fromString, i.toString) for h in issue.changelog.histories for i in h.items if i.field == 'status']
        if len(history) > 0:
            created_dt=min(history)[0]
            created_dt = datetime.strptime(created_dt, "%Y-%m-%dT%H:%M:%S.%f+0000")
            dev_dt= next((i[0] for i in history if i[2]=='In Development'), created_dt)
            if  isinstance(dev_dt, str):
                dev_dt = datetime.strptime(dev_dt, "%Y-%m-%dT%H:%M:%S.%f+0000")
            last_dt = next((i[0] for i in history if i[2]=='Closed'), now)
            if  isinstance(last_dt, str):
                last_dt = datetime.strptime(last_dt, "%Y-%m-%dT%H:%M:%S.%f+0000")
            _time_to_dev=dev_dt-created_dt
            _time_to_dep=last_dt-dev_dt
            time_to_dev.append(_time_to_dev.days)
            time_to_dep.append(_time_to_dep.days)
            yr = last_dt.isocalendar()[0]
            week = last_dt.isocalendar()[1]
            sp = 0
            if hasattr(issue.fields, 'customfield_10002'):
                sp = issue.fields.customfield_10002
            story_points.append((yr, week, sp))
    if len(time_to_dev)>0:
        print(f'    time to development stats avg={avg(time_to_dev):.2f} mean={mean(time_to_dev):.2f} median={median(time_to_dev):.2f}')
    if len(time_to_dep)>0:
        print(f'    time to deployment  stats avg={avg(time_to_dep):.2f} mean={mean(time_to_dep):.2f} median={median(time_to_dep):.2f}')
    print('\n    story point stats')
    story_points = [i for i in story_points if i[2] is not None]
    story_points = sorted(story_points, key= lambda d: (d[0], d[1]))
    groups = groupby(story_points, key= lambda d: (d[0], d[1]))
    for key, data in groups:
        sp = [i[2] for i in data if i[2] is not None and i[0]==2019 and i[1] != now_week]
        if len(sp)> 0:
            print(f'        key={key} story points={sum(sp)}')

def stat_for_all_teams():
    prjs = jra.get_projects()
    for prj in prjs:
        print(f'team {prj.key}')
        get_team_stats_lead_time(prj.key)

if __name__ == "__main__":
    usr = getuser()
    print(usr)
    #get_all_project()
    stat_for_all_teams()
    print('done')
