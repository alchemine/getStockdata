# Remarks
대신증권에서 제공하는 CreonPlus API를 사용하여 원하는 기간동안 원하는 단위로 주가 데이터를 받아올 수 있습니다.  
`get_data/get_stock.py`를 실행시킬 때 `unit`, `start`, `end`를 argument로 넘겨주는 방식으로 데이터를 받아오도록 구현하였습니다.  
`save_dir` argument를 통해 데이터를 저장할 directory를 지정할 수 있습니다.  

이 프로그램은 대신증권 CreonPlus를 이용하여 데이터를 받아오기 때문에 반드시 CreonPlus가 실행되어 있는지 먼저 확인해야 합니다. 그리고 관리자 권한으로 실행되었는지 확인하세요.  
CreonPlus는 Python 32bit에서만 작동하기 때문에 일반적으로 사용하는 64bit Python에서는 사용할 수 없습니다. 32bit 가상환경을 생성하여 돌리시는 것을 추천합니다.  
또한, `Python 3.5` 에서 작업한 코드로 타 버전에서는 호환이 안 될 수 있습니다. 32bit 가상환경을 생성할 때 `Python 3.5` 를 설치하는 것을 추천합니다.  


# Usage
```
$ pip install -r requirements.txt
$ python get_stock.py --unit D --start 19000101 --end 20200309
$ python get_stock.py --unit m --start 19000101 --end 20200309  // 약 4시간 반 소요
$ python get_stock.py --unit T --start 19000101 --end 20200309
```