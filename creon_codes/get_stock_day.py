from env import *
from DataLoader_day import DataLoader


if __name__ == "__main__":
    # 1. 객체 생성 및 연결
    loader = DataLoader()


    # 2. 종목코드 얻기
    list_code = pd.read_csv(CODENAME_PATH, encoding='cp949')['code']
    # list_code = ['036570']  # For test


    # 3. 받아오기
    unit = 'D'
    UNIT_DIR = join(ROOT_DIR, full_name(unit))
    os.makedirs(UNIT_DIR, exist_ok=True)
    for code in tqdm(list_code):
        if len([i for i in os.listdir(UNIT_DIR) if i.startswith(code)]) > 0:
            continue

        param = {'code': 'A'+code,  # A036570 (stock)
                 'start': '19000101',
                 'end': '20200309',  # TODAY
                 'unit': unit}

        df_list = []
        while True:
            df = loader.load(**param)
            if len(df) == 1:
                break
            elif len(df) == 0:
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
            param['start'], param['end'] = next_time(df, param['unit'])

        merge_dataframes(df_list, code, param['unit'])
