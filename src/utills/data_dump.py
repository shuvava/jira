# -*- coding: utf-8 -*-
'''
utility to dump as a ndjson(jsonline) into file
jsonl
'''
import json
import gzip
from datetime import datetime, date
from collections.abc import Iterable

from jsonlines import Writer, Reader

from models import Issue, IssueHistory

def __default(o):
    if isinstance(o, (date, datetime)):
        return o.isoformat()


def write_issues(file_name, items):
    if not isinstance(items, Iterable):
        items = [items]
    dumps = json.JSONEncoder(ensure_ascii=False, sort_keys=True, separators=(',', ':'), default=__default).encode
    with gzip.open(f'{file_name}.gz', 'wb+') as f:
        writer = Writer(f, dumps=dumps)
        for item in items:
            if hasattr(item, 'toDict'):
                writer.write(item.toDict)
            else:
                writer.write(item)

def create_obj(obj, inst):
    pr = inst
    for k, v in obj.items():
        if k in ['create_dt', 'create_dt', 'time_to_dev', 'time_in_dev', 'time_in_qa', 'time_to_dep','dt']:
            setattr(pr, k, datetime.strptime(v, '%Y-%m-%dT%H:%M:%S'))
        elif k in ['history']:
            r = []
            for vv in v:
                obj = create_obj(vv, IssueHistory())
                r.append(obj)
                setattr(pr, k, r)
        else:
            setattr(pr, k, v)
    return pr

def read_issues(file_name):
    items = []
    with gzip.open(f'{file_name}.gz', 'rb') as f:
        reader = Reader(f)
    # with jsonlines.open(file_name) as reader:
        for obj in reader:
            pr = create_obj(obj, Issue())
            items.append(pr)
    return items
