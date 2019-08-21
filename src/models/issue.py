# -*- coding: utf-8 -*-
from datetime import datetime

def get_attr(attr, obj, default=None):
    if obj and hasattr(obj, attr):
        return obj[attr]
    else:
        return default

class Issue:
    def __init__(self, obj=None):
        self.team = ''
        self.id = ''
        self.story_points = 0
        self.status = ''
        self.create_dt = None
        self.close_dt = None
        self.time_to_dev = None
        self.time_in_dev = None
        self.time_in_qa = None
        self.time_to_dep = None
        self.history = []

    @property
    def toDict(self):
        #return self.__dict__
        arr = []
        for h in self.history:
            arr.append(h.toDict)
        result = self.__dict__.copy()
        result['history'] = arr
        return result

class IssueHistory:
    def __init__(self, status='', dt=None):
        self.status = status
        self.dt = dt

    @property
    def toDict(self):
        return self.__dict__
