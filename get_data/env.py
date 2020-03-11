import os
from os.path import join

import datetime as dt
from argparse import ArgumentParser
from tqdm import tqdm

import pandas as pd


# PATH
ROOT_DIR = "D:/data/stock"
CODENAME_PATH = join("stockcode", "stockcode(kospi,2020-03-09).csv")


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


def next_time(df, start_day):
    start, end = df.iloc[-1]['날짜'], df.iloc[0]['날짜']
    start, end = start_day, str(start).replace('-', '')
    return start, end


def merge_dataframes(df_list, code, unit):
    if len(df_list) == 0:
        return

    # List all csv files starting with 'code'
    rst = pd.concat(df_list).drop_duplicates()
    start, end = rst.iloc[-1]['날짜'], rst.iloc[0]['날짜']
    CSV_PATH = join(ROOT_DIR, full_name(unit), "{}({}~{}).csv".format(code, start, end))
    rst.to_csv(CSV_PATH, encoding='cp949', index=False)
