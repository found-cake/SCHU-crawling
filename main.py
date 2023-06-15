from datetime import datetime, timedelta

import yaml
from selenium import webdriver
from selenium.webdriver.common.by import By

# 요일 클래스 정보
month_class_names = [
    'month_1',
    'month_2',
    'month_3',
    'month_4',
    'month_5',
    'month_6',
    'month_7',
    'month_8',
    'month_9',
    'month_10',
    'month_11',
    'month_12'
]

ONE_DAY = timedelta(days=1)
FORMAT = '%Y.%m.%d'

driver = webdriver.Chrome('chromedriver')
driver.implicitly_wait(3)

data = {}


def push(key: str, value: str) -> None:
    if not (key in data):
        data[key] = []
    data[key].append(value)


def parse(dt: str, dd: str, year: int) -> None:
    isDts = ' ~ ' in dt
    if isDts:
        first, late = dt.split(' ~ ')
        first = f'{year}.{first}'
        late = f'{year}.{late}'
    else:
        first = late = f'{year}.{dt}'
    first = first.strip()
    late = late.strip()
    if first == late:
        push(first, dd)
        return
    first = datetime.strptime(first, FORMAT)
    late = datetime.strptime(late, FORMAT) + ONE_DAY
    while first.day != late.day:
        push(first.strftime(FORMAT), dd)
        first += ONE_DAY


def removeWeakDay(text: str) -> str:
    return text\
        .replace('(월)', '')\
        .replace('(화)', '')\
        .replace('(수)', '')\
        .replace('(목)', '')\
        .replace('(금)', '')\
        .replace('(토)', '')\
        .replace('(일)', '')\
        .replace('(Mon)', '')\
        .replace('(Tue)', '')\
        .replace('(Wed)', '')\
        .replace('(Thu)', '')\
        .replace('(Fri)', '')\
        .replace('(Sat)', '')\
        .replace('(Sun)', '')


def getInfo(year) -> str:
    URL = f'https://home.sch.ac.kr/sch/05/010000.jsp?board_no=20110224223754285127&defparam-year_month={year}-01'
    driver.get(URL)
    info = driver.find_element(By.XPATH, '/html/body/div/div[1]/div[2]/div/div/div[2]')
    for i in range(12):
        monthInfo = info.find_element(By.CLASS_NAME, month_class_names[i])
        infoList = monthInfo.find_element(By.CSS_SELECTOR, 'div.list > dl').text
        for value in infoList.split('\n'):
            yield value


def read(year):
    dt: str = ''
    count = 1
    for value in getInfo(year):
        if value == '':
            continue
        if count % 2 != 0:  # dt
            dt = removeWeakDay(value)
        else:
            parse(dt, value, year)
        count += 1


now: int = datetime.today().year

read(now)
read(now + 1)

# 종료 마무리
driver.quit()

with open("schedule.yml", 'w', encoding="UTF-8") as file:
    yaml.dump(data, file, default_style=False, allow_unicode=True)
