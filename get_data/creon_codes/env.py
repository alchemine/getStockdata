import os
from os.path import join

import datetime as dt
from dateutil.relativedelta import relativedelta

import pandas as pd
from tqdm import tqdm


# PATH
ROOT_DIR = "D:/data/stock"
CODENAME_PATH = join("..", "codename(kospi,2020-03-09).csv")


TODAY = dt.datetime.today().strftime('%Y%m%d')
START_DAY = '19000101'


def check_privilege():
    import ctypes
    if ctypes.windll.shell32.IsUserAnAdmin():
        print("관리자 권한으로 정상적으로 실행되었습니다.")
    else:
        print("관리자 권한으로 실행되지 않았습니다. 관리자권한으로 실행하세요.")
        exit(1)


def full_name(unit):
    name_dic = {'D': 'day', 'm': 'minute', 'T': 'tick'}
    return name_dic[unit]
