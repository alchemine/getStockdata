import os
import win32com.client
import pandas as pd
import datetime as dt
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
import time


def checkPrivilege():
    import ctypes
    if ctypes.windll.shell32.IsUserAnAdmin():
        print("관리자 권한으로 정상적으로 실행되었습니다.")
    else:
        print("관리자 권한으로 실행되지 않았습니다. 관리자권한으로 실행하세요.")
        exit(1)


class Creon:
    def __init__(self):
        """
        :param None:
        :return None:
        - Make connection with CREON API and verify connectivity
        - Initialize the field info wanted to get
        """
        checkPrivilege()
        self.obj_CpCodeMgr = win32com.client.Dispatch('CpUtil.CpCodeMgr')
        self.obj_CpCybos = win32com.client.Dispatch('CpUtil.CpCybos')
        self.obj_StockChart = win32com.client.Dispatch('CpSysDib.StockChart')
        b_connected = self.obj_CpCybos.IsConnect
        if b_connected == 0:
            print("연결 실패 - Creon Plus가 정상적으로 실행되었는지 확인하고",
                  "계속 문제 발생 시 Creon Plus를 다시 실행하세요.")
            exit(1)

        self.list_field_key = [0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 37]
        self.list_field_name = ['종목코드', '날짜', '시간', '시가', '고가', '저가', '종가',
                                '거래량', '거래대금', '누적체결매도수량', '누적체결매수수량', '대비부호']
        self.list_code = []

    def loadCodeFile(self, file):
        """
        :param file: code list excel file
        :return None:
        - Load stock codes from the file and assign them to self.list_code
        """
        df = pd.read_csv(file, encoding='cp949')
        self.list_code = df['code']  # Series

    def crawling(self, param):
        """
        :param unit: can be 'm'(minutes) or 'T'(Ticks)
        :param mode: can be 'A'(Auto) or 'M'(Manual)
        :param start: (int) start date
        :param end: (int) end date
        :param test: (bool) test flag
        :return None:
        - For self.list_code, crawl info and save as csv file in each unit folder
        """
        self.start_time = time.time()

        unit, mode, start, end, test = param['unit'], param['mode'], param['start'], param['end'], param['test']
        first = last = 0

        # Test
        if test is True:
            self.list_code = ['036570']

        for step, code in enumerate(self.list_code):
            # Initialize dt_start, dt_end
            if mode == 'A':
                dt_start, dt_end = self.setDate(unit, months=1, days=0)  # crawling 1 month
            else:
                dt_start, dt_end = self.rangeCheck(start, end, unit)

            df_code, first, last = self.splitDate(code, dt_start, dt_end, unit)
            DIR = os.path.join("..", self.fullName(unit), "{}~{}".format(first, last))
            CSV_PATH = os.path.join(DIR, "{}.csv".format(code))

            os.makedirs(DIR, exist_ok=True)
            df_code.to_csv(CSV_PATH, index=False, encoding='ms949')  # cp949

            print("Elpased time: {:.2f}s for {} / {} ({})".format(
                time.time() - self.start_time, step, len(self.list_code), step / len(self.list_code) * 100))
        print("\rCrawling Complete!")

    def rangeCheck(self, start, end, unit):
        """
        :param start: (int) start date
        :param end: (int) end dqte
        :param unit: can be 'm'(minutes) or 'T'(Ticks)
        :return dt_start, dt_end: (datetime, datetime) dates
        - Verify the range of start, end date and shrink if necessary
        """
        dt_start, dt_end = parse(str(start)), parse(str(end))

        today = dt.datetime.today()
        # Check start date (necessary?)
        if unit == 'T':
            limit = today - relativedelta(months=1)
        else:
            limit = today - relativedelta(years=2)  # ??

        if (limit - dt_start).days > 0:
            dt_start = limit

        # Check end date
        if (dt_end - dt_start).days < 0:
            dt_end = dt_start

        return dt_start, dt_end

    def splitDate(self, code, dt_start, dt_end, unit):
        """
        :param code: stock code
        :param dt_start: (datetime) start date
        :param dt_end: (datetime) start date
        :return rst: (pd.DataFrame) crawled info
        :return first: (str) first true date
        :return last: (str) last true date
        - CREON API doesn't work well over a wide range. So the date range should be splitted into 5 days.
        - Then, using CREON API attach all splitted date range
        """
        rst = pd.DataFrame()
        list_date = []

        first = dt_start.strftime("%Y%m%d")
        last = dt_end.strftime("%Y%m%d")

        if (dt_end - dt_start).days < 5:
            list_date.append((dt_start, dt_end))
        else:
            list_date.append((dt_start, dt_end))
            s = dt_start
            e = s + dt.timedelta(days=5)

            delta = 1
            while delta > 0:
                list_date.append((s, e))
                delta = (dt_end - e).days
                s = e + dt.timedelta(days=1)
                e = s + dt.timedelta(days=5)
            list_date.reverse()  # From new to old

        for step, (dt_start, dt_end) in enumerate(list_date):
            arg_start, arg_end = int(dt_start.strftime("%Y%m%d")), int(dt_end.strftime("%Y%m%d"))
            tmp = self.creonAPI(code, arg_start, arg_end, unit)
            rst = rst.append(tmp)

            numerator = list(self.list_code).index(code) * len(list_date) + step
            denominator = len(self.list_code) * len(list_date)
            progress = numerator / denominator * 100
            print("%.2f%% Complete.. \t %d초 경과" % (progress, time.time() - self.start_time), end='\r')

        return rst, first, last

    def setDate(self, unit, months=0, days=0):
        """
        :param unit: can be 'm'(minutes) or 'T'(Ticks)
        :param months: crawl info from 'months' ago to now
        :param days: crawl info from 'days' ago to now
        :return dt_start, dt_end: (datetime, datetime) date set
        """
        dt_end = dt.datetime.now()  # 2020. 3. 9 (FIxed value)

        # Set date from 'months' or 'days' ago to now
        dt_start = dt_end - relativedelta(months=months, days=days)

        return dt_start, dt_end

    def fullName(self, unit):
        """
        :param unit: can be 'm'(minutes) or 'T'(Ticks)
        :return FullName of unit:
        """
        if unit == 'T':
            return "tick"
        elif unit == 'm':
            return "minute"
        elif unit == 'D':
            return "day"
        else:
            exit(1)

    def creonAPI(self, code, start, end, unit):
        """
        :param code: stock code
        :param start: (int) start date
        :param end: (int) end date
        :param unit: can be 'm'(minutes) or 'T'(Ticks)
        :return crawled info: (pd.DataFrame)
        """
        dict_chart = {name: [] for name in self.list_field_name}

        print(end, start)

        self.obj_StockChart.SetInputValue(0, code)
        self.obj_StockChart.SetInputValue(1, ord('1'))             # 0: 개수, 1: 기간
        self.obj_StockChart.SetInputValue(2, end)                  # 종료일
        self.obj_StockChart.SetInputValue(3, start)                # 시작일
        self.obj_StockChart.SetInputValue(5, self.list_field_key)  # 필드
        self.obj_StockChart.SetInputValue(6, ord(unit))            # mode: 'D', 'W', 'M', 'm', 'T'

        self.obj_StockChart.BlockRequest()  # 설정에 따라 데이터를 요청

        status = self.obj_StockChart.GetDibStatus()
        cnt = self.obj_StockChart.GetHeaderValue(3)  # 수신개수

        if status != 0:
            msg = self.obj_StockChart.GetDibMsg1()
            print("통신상태: {} {}".format(status, msg))
            exit(1)
        elif cnt == 0:
            print("API로부터 받은 데이터가 없습니다.")
            exit(1)

        for i in range(cnt):
            key = self.list_field_name
            value = lambda pos: code if pos == 0 else self.obj_StockChart.GetDataValue(pos-1, i)
            dict_item = {name: value(pos) for pos, name in enumerate(key)}

            date = str(dict_item['날짜'])
            time = str(dict_item['시간'])

            dict_item['종목코드'] = code
            dict_item['날짜'] = "{Y:2}-{M:2}-{D:2}".format(Y=date[:4], M=date[4:6], D=date[6:])
            dict_item['시간'] = "{H:0>2}:{M:2}:00".format(H=time[:-2], M=time[-2:])

            for k, v in dict_item.items():
                dict_chart[k].append(v)

        return pd.DataFrame(dict_chart, columns=self.list_field_name)


if __name__ == '__main__':
    creon = Creon()

    # User Input parameter
    param = {'unit': 'D',  # 'T': Tick / 'm': minute / 'D': Day
                           # (Limit is 1 month ago in Tick, 2 years ago in minute, 10 years ago in day)
             'mode': 'M',  # 'M': Manual / 'A': Auto (Default is 1 month ago to now.
                           #                          The range can be modified in creon.crawling())
             'start': 20200306,  # Only used in 'M'anual mode
             'end':   20200309,  # Only used in 'M'anual mode
             'test': True       # True: Crawl only 1 stock / False: Crawl every stock
             }

    # 1. Load code list from csv file
    creon.loadCodeFile('../codename(kospi,2020-03-09).csv')

    # 2. Crawling
    creon.crawling(param)
