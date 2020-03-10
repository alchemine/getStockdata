import pymysql
import numpy as np
import matplotlib.pyplot as plt
import re


def normalization(data):
    s = data[0]
    return list(np.divide(data, s))


def name_code(code):
    if code == "A000880":
        return "한화"
    elif code == "A066570":
        return "LG전자"
    elif code == "A000640":
        return "동아쏘시오홀딩스"
    elif code == "A005610":
        return "SPC삼립"


def make_xticks(flag1, flag6, tick):
    if flag1 is False:
        flag1 = True
        flag6 = False
    else:   # flag6 is False
        flag6 = True
        flag1 = False

    xticks.append(tick)
    xticklabels.append(name[:5])

    return flag1, flag6


conn = pymysql.connect(host='165.246.45.191', user='root', password='dblab1404!!', db='StockData', charset='utf8')
curs = conn.cursor(pymysql.cursors.DictCursor)

plot_data = []
list_code = ["A066570", "A000880", "A000640", "A005610"]
start_date = "2018-01-01"  # SQL Format

for idx, code in enumerate(list_code):
    query = "select date, time, start from stock where code='%s' and date >= '%s' order by date, time" % (code, start_date)
    curs.execute(query)
    rst = curs.fetchall()

    _start = [int(elem['start']) for elem in rst]   # Original scale
    start = normalization(_start)   # Based on start scale

    time = np.array([elem['time'].seconds for elem in rst])
    hours, remainder = divmod(time, 3600)
    minutes, seconds = divmod(remainder, 60)
    hours = ["{:0>2}".format(elem) for elem in hours.astype(str)]
    minutes = ["{:0>2}".format(elem) for elem in minutes.astype(str)]
    time = [':'.join(elem) for elem in zip(hours, minutes)]

    date = [elem['date'].strftime("%y-%m-%d") for elem in rst]
    date = [' '.join(elem) for elem in zip(date, time)]

    plot_data.append((date, start, code))


# Maximum range Domain / Range 만들기
domain = set()
for x, _, _ in plot_data:
    domain = domain | set(x)
domain = sorted(list(domain))

for idx, (x, y, code) in enumerate(plot_data):
    for i, elem in enumerate(domain):
        if elem != x[i] or i == len(x):     # 부족한 부분은 채우기
            x.insert(i, elem)
            y.insert(i, y[i - 1] if i != 0 else y[i + 1])   # Nearest neighborhood interpolation

list_color = ['r', 'g', 'b', 'c']
for idx, (x, y, code) in enumerate(plot_data):
    plt.plot(x, y, label=code, color=list_color[idx], linewidth=1.0)

xticks = []
xticklabels = []
flag1 = flag6 = False
for tick, name in enumerate(plot_data[0][0]):   # max range date
    if flag1 is False:
        if re.search("^[0-9]{2}.01.[0-9]{2}", name):
            flag1, flag6 = make_xticks(flag1, flag6, tick)
            continue

    if flag6 is False:
        if re.search("^[0-9]{2}.06.[0-9]{2}", name):
            flag1, flag6 = make_xticks(flag1, flag6, tick)
            continue

    if tick == 0 or tick == len(plot_data[0][0]) - 1:   # 시작값과 마지막값 무조건 추가
        xticks.append(tick)
        xticklabels.append(name[:5])

# 종목이름 출력
for code in list_code:
    print("%s: %s" % (code, name_code(code)))

ax = plt.gca()
ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels)

plt.title("Start ratio per date")
plt.xlabel("date")
plt.ylabel("price (ratio)")
plt.grid(True)
plt.legend()

plt.show()
