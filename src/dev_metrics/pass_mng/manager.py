# -*- coding: utf-8 -*-
from getpass import getpass, getuser

from keyring import get_password, set_password, delete_password

__SERVICE__ = 'JIRA'

def get_jira_password(prompt_console=False):
    usr = getuser()
    pwd = get_password(__SERVICE__, usr)
    if not pwd and prompt_console:
        pwd = getpass(prompt='Jira password')
        set_password(__SERVICE__, usr, pwd)
    return pwd

def remove_jira_password():
    usr = getuser()
    delete_password(__SERVICE__, usr)

def update_jira_password(pwd=None):
    usr = getuser()
    if not pwd:
        pwd = getpass(prompt='Jira password')
    set_password(__SERVICE__, usr, pwd)
