from env import *
import win32com.client


class DataLoader:
    def __init__(self):
        check_privilege()
        self.obj_StockChart = None
        self._connecting()

    def _connecting(self):
        # obj_CpCodeMgr = win32com.client.Dispatch('CpUtil.CpCodeMgr')
        obj_CpCybos = win32com.client.Dispatch('CpUtil.CpCybos')
        b_connected = obj_CpCybos.IsConnect
        if b_connected == 0:
            print("연결 실패 - Creon Plus가 정상적으로 실행되었는지 확인하고",
                  "계속 문제 발생 시 Creon Plus를 다시 실행하세요.")
            exit(1)
        self.obj_StockChart = win32com.client.Dispatch('CpSysDib.StockChart')

    def load(self, code, start, end, unit):
        # 받아올 값
        list_field_key = [0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 13, 17, 26, 37]
        list_field_name = ['날짜', '시간', '시가', '고가', '저가', '종가', '거래량', '거래대금', '누적체결매도수량',
                           '누적체결매수수량', '시가총액', '외국인현보유비율', '거래성립률', '대비부호']

        self.obj_StockChart.SetInputValue(0, code)
        self.obj_StockChart.SetInputValue(1, ord('1'))
        self.obj_StockChart.SetInputValue(2, end)
        self.obj_StockChart.SetInputValue(3, start)
        self.obj_StockChart.SetInputValue(5, list_field_key)
        self.obj_StockChart.SetInputValue(6, ord(unit))
        self.obj_StockChart.SetInputValue(9, ord('1'))  # 수정주가
        self.obj_StockChart.BlockRequest()  # 설정에 따라 데이터를 요청

        status = self.obj_StockChart.GetDibStatus()
        cnt = self.obj_StockChart.GetHeaderValue(3)  # 수신개수

        if status != 0:
            msg = self.obj_StockChart.GetDibMsg1()
            print("통신상태: {} {}".format(status, msg))
            exit(1)

        return self._generate_dataframe(cnt, list_field_name)

    def _generate_dataframe(self, cnt, list_field_name):
        dic = {key: [] for key in list_field_name}

        for i in range(cnt):
            key = list_field_name
            value = lambda pos: self.obj_StockChart.GetDataValue(pos, i)
            tmp = {name: value(pos) for pos, name in enumerate(key)}

            date, time = str(tmp['날짜']), str(tmp['시간'])
            tmp['날짜'] = "{Y:2}-{M:2}-{D:2}".format(Y=date[:4], M=date[4:6], D=date[6:])
            tmp['시간'] = "{H:0>2}:{M:2}:00".format(H=time[:-2], M=time[-2:])

            for k, v in tmp.items():
                dic[k].append(v)
        rst = pd.DataFrame(dic, columns=list_field_name)

        state = self.obj_StockChart.GetHeaderValue(17)  # 종목상태
        rst['종목상태'] = chr(state)
        return rst
