import pymysql
import pandas as pd
import time
import csv


class SQL:
    def __init__(self, param):
        """
        :param param: Input parameter(host, user, pw, db, charset, query)
        :return None:
        - MySQL Connection 연결
        - Initialize member vars
        """
        host, user, pw, db, charset = param.values()
        self.conn = pymysql.connect(host=host, user=user, password=pw, db=db, charset=charset)
        self.curs = self.conn.cursor(pymysql.cursors.DictCursor)
        self.list_code = []
        self.list_name = []

    def __del__(self):
        self.conn.close()

    def load_code_file(self, file):
        """
        :param file: code list excel file
        :return None:
        - Load stock codes from the file and assign them to self.list_code
        """
        df = pd.read_excel(file, sheet_name='KOSPI_KOSDAQ')
        idx_code, idx_name = df.columns[0], df.columns[1]   # CODE
        self.list_code, self.list_name = df[idx_code], df[idx_name]

    def query(self, param):
        """
        :param param: (str, str) is tuple of query strings to be executed
        :return None: prints result of query
        - Make bulk from csv
        - Execute query
        """
        # First insert into name (Execute only once, then make comment)
        #self.insert_into_name(param["name"])

        # Second insert into stock
        #self.insert_into_stock(param["stock"])

        # Finally check the number of each code
        self.check_number()

        print("\rInsertion 완료!")

    def insert_into_name(self, query):
        batch = [inst for inst in zip(self.list_code, self.list_name)]
        self.curs.executemany(query, batch)
        self.conn.commit()

    def insert_into_stock(self, query):
        # codes ← Remained codes in table
        self.curs.execute("select distinct(code) from stock")
        tmp = self.curs.fetchall()
        codes = [elem['code'] for elem in tmp]

        start = time.time()
        n_code = len(self.list_code)

        print("# code of file: %s \t Except KOSPI, KOSDAQ: %s" % (n_code, n_code - 2))
        print("# code of db: %s \t\t # code of zero-data: 186 \t # code of total: %s \n"
              % (len(codes), len(codes) + 186))

        for step, code in enumerate(self.list_code):
            if code in codes:
                continue
            else:
                batch = []
                try:
                    with open("Minute data\\%s.csv" % code) as csv_file:
                        csv_reader = csv.reader(csv_file)
                        for line in csv_reader:
                            line.pop(11)
                            batch.append(line)

                            print("\r%s: %dth insertion 완료 \t %.2f%% \t %d초 경과" %
                                  (code, step, 100 * step / n_code, time.time() - start), end='')
                except FileNotFoundError as e:
                    if code == "KOSPI" or code == "KOSDAQ":
                        continue
                    else:
                        print(e)
                        exit(1)

                batch.pop(0)    # index
                self.curs.executemany(query, batch)
                self.conn.commit()

                """
                    # Small Batch version
                    with open("Minute data\\%s.csv" % code) as csv_file:
                        csv_reader = csv.reader(csv_file)
                        batch = []
                        for idx, line in enumerate(csv_reader):
                            if idx == 0:
                                continue

                            line.pop(11)
                            batch.append(line)

                        batch_size = int(len(batch) / 10)
                        for i in range(10):
                            if i == 9:
                                tmp = batch[i*batch_size:]
                            else:
                                tmp = batch[i*batch_size:(i+1)*batch_size]
                            self.curs.executemany(query, tmp)
                            self.conn.commit()

                        print("\r%s: %dth insertion 완료 \t %.2f%% \t %d초 경과" %
                              (code, step, 100 * step / n_code, time.time() - start), end='')
                except FileNotFoundError as e:
                    if code == "KOSPI" or code == "KOSDAQ":
                        print("\nKOSPI / KOSDAQ is excluded.")
                        continue
                    else:
                        print(e)
                        exit(1)
                """

    def check_number(self):
        list_code = []
        correct = []
        for step, code in enumerate(self.list_code):
            if code < "A149940":
                continue

            target = 0
            try:
                with open("Minute data\\%s.csv" % code) as csv_file:
                    target = len(list(csv.reader(csv_file)))
                    target -= 1  # index
            except FileNotFoundError as e:
                if code == "KOSPI" or code == "KOSDAQ":
                    continue
                else:
                    print(e)
                    exit(1)

            query = "select count(code) from stock where code='%s'" % code
            self.curs.execute(query)
            real = self.curs.fetchall()
            real = real[0]['count(code)']

            if target == real:
                correct.append(1)
                print("%s'th code: %s is inserted successfully \t %.2f%% Success" %
                      (step, code, 100*step / len(self.list_code)))
            else:
                correct.append(0)
                list_code.append(code)
                print("%s'th code: %s is not inserted successfully \t %.2f%% Fail" %
                      (step, code, 100*step / len(self.list_code)))
                delete_query = "delete from stock where code=%s"
                insert_query = "insert into stock values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

                # Delete code's data
                self.curs.execute(delete_query, (code,))
                self.conn.commit()

                # Insert data
                batch = []
                try:
                    with open("Minute data\\%s.csv" % code) as csv_file:
                        csv_reader = csv.reader(csv_file)
                        for line in csv_reader:
                            line.pop(11)
                            batch.append(line)
                except FileNotFoundError as e:
                    print(e)
                    exit(1)

                batch.pop(0)  # index
                self.curs.executemany(insert_query, batch)
                self.conn.commit()

                print("%s'th code: %s is inserted successfully \t %.2f%% Success" %
                      (step, code, 100*step / len(self.list_code)))

        print("Incorrect # code: {}, Accuracy: {:.2}%%".format(sum(correct), 100*sum(correct) / len(correct)))


if __name__ == "__main__":
    # User Input parameter
    init_param = {
        "host": "165.246.45.191",
        "user": "root",
        "password": "dblab1404!!",
        "db": "StockData",
        "charset": "utf8"
    }

    query_param = {
        "name": "insert into name values(%s, %s)",
        "stock": "insert into stock values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    }

    sql = SQL(init_param)
    sql.load_code_file('code.xlsx')
    sql.query(query_param)
