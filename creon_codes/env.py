import os
from os.path import join

import datetime as dt
from dateutil.relativedelta import relativedelta

import pandas as pd
from tqdm import tqdm


# PATH
ROOT_DIR = '..'
CODENAME_PATH = join(ROOT_DIR, "codename(kospi,2020-03-09).csv")

TODAY = dt.datetime.today().strftime('%Y%m%d')


def check_privilege():
    import ctypes
    if ctypes.windll.shell32.IsUserAnAdmin():
        print("관리자 권한으로 정상적으로 실행되었습니다.")
    else:
        print("관리자 권한으로 실행되지 않았습니다. 관리자권한으로 실행하세요.")
        exit(1)


def next_time(df, unit, abnormal=False):
    start, end = df.iloc[-1]['날짜'], df.iloc[0]['날짜']

    if abnormal is False:
        # int → datetime
        start, end = dt.datetime.strptime(str(start), '%Y-%m-%d'), dt.datetime.strptime(str(end), '%Y-%m-%d')

        # delta
        if unit == 'D':
            start, end = start - relativedelta(years=5), start
        #TODO
        # minute, ...
    else:
        # int → datetime
        start, end = dt.datetime.strptime(str(start), '%Y%m%d'), dt.datetime.strptime(str(end), '%Y%m%d')

        # delta
        if unit == 'D':
            end -= relativedelta(years=5)
            start = end - relativedelta(years=5)
        #TODO
        # minute, ...

    # datetime → int
    start, end = start.strftime('%Y%m%d'), end.strftime('%Y%m%d')
    return start, end


def merge_dataframes(df_list, code, unit):
    if len(df_list) == 0:
        return

    # 1. List all csv files starting with 'code'
    rst = pd.concat(df_list).drop_duplicates().sort_values(by=['날짜'], ascending=False)
    start, end = rst.iloc[-1]['날짜'], rst.iloc[0]['날짜']
    CSV_PATH = join(ROOT_DIR, full_name(unit), "{}({}~{}).csv".format(code, start, end))
    rst.to_csv(CSV_PATH, encoding='cp949', index=False)


def full_name(unit):
    name_dic = {'D': 'day', 'm': 'minute', 'T': 'tick'}
    return name_dic[unit]