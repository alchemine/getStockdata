# https://money2.creontrade.com/e5/mboard/ptype_basic/HTS_Plus_Helper/DW_Basic_Read_Page.aspx?boardseq=284&seq=102&page=1&searchString=CpSysDib.StockChart&p=8841&v=8643&m=9505 참조


from env import *
from DataLoader import *

parser = ArgumentParser(description='unit, start, end')
parser.add_argument('--unit', type=str, default='m')         # 'D', 'm', 'T'
parser.add_argument('--start', type=str, default=START_DAY)  # yyyymmdd
parser.add_argument('--end', type=str, default='20200309')   # yyyymmdd


if __name__ == "__main__":
    # 0. Parser
    args = parser.parse_args()


    # 1. 종목코드 얻기
    list_code = pd.read_csv(CODENAME_PATH, encoding='cp949')['code']
    list_code = ['000020']  # For test


    # 2. 객체 생성 및 연결
    unit = args.unit  # 'D', 'm', 'T'
    loader = DataLoader(unit)
    UNIT_DIR = join(ROOT_DIR, full_name(unit))
    os.makedirs(UNIT_DIR, exist_ok=True)


    # 3. 받아오기
    for code in tqdm(list_code):
        if len([i for i in os.listdir(UNIT_DIR) if i.startswith(code)]) > 0:
            continue

        param = {'code': 'A'+code,  # A036570 (stock)
                 'start': args.start,
                 'end': args.end,  # TODAY
                 'unit': unit}

        df_list = []
        while True:
            df = loader.load(**param)

            if len(df) == 0:
                if param['code'].startswith('A'):  # Not in A(Stock). Check with Q(ETN)
                    param['code'] = 'Q'+code
                    continue
                elif param['code'].startswith('Q'):  # Not int Q(ETN). Check with J(ELW)
                    param['code'] = 'J'+code
                    continue
                else:
                    print("There are no data with", code)
                    break

            df_list.append(df)
            if len(df) < 500:  # 마지막으로 받아올 수 있는 데이터인 경우,
                break

            param['start'], param['end'] = next_time(df, args.start)
        merge_dataframes(df_list, code, param['unit'])
