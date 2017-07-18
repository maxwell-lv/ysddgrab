import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd
from sqlalchemy.sql import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, MetaData
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
import sqlite3
from datetime import datetime
import re


db = "sqlite:///ysdd.db"
Session = sessionmaker()

class MyList(Base):
    __tablename__ = 'list'
    name = Column(String, primary_key=True)
    type = Column(String)
    date = Column(Date, primary_key=True)
    marketvalue = Column(Integer)
    investorratio = Column(Float)
    traderratio = Column(Float)
    ratioperday = Column(Float)

def init_driver():
    driver = webdriver.Chrome()
    driver.wait = WebDriverWait(driver, 10)
    return driver


def login(driver, u, p):
    driver.get("http://www.vipysdd.com")
    try:
        userId = driver.wait.until(EC.presence_of_element_located((By.ID, "userId")))
        password = driver.wait.until(EC.presence_of_element_located((By.ID, "password")))
        button = driver.wait.until(EC.element_to_be_clickable((By.ID, "loginBtn")))
        userId.send_keys(u)
        password.send_keys(p)
        button.click()
    except TimeoutException:
        print("Fields or Button not found in ysdd")

def getPerformance(driver):
    driver.get("http://www.vipysdd.com/common/yjggList.html?code=yjgg&no=0")
    base_name = "【业绩公布%d】"
    table = []
    page_link_list = []
    for i in range(1, 10):
        performance_page_name = base_name % i
        try:
            page = driver.wait.until(EC.presence_of_element_located((By.LINK_TEXT, performance_page_name)))
            page_link = page.get_attribute('href')
            page_link_list.append(page_link)
        except TimeoutException:
            if i == 1:
                print("Can't find any performance page")
            else:
                break
    for page_link in page_link_list:
        table = table + getPerformanceList(driver, page_link)
    return table


def getPerformanceList(driver, page_link):
    driver.get(page_link)
    table = []
    for n in range(1, 100):
        try:
            line = driver.wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="content"]/table/tbody/tr[%d]' % n)))
            table.append(line)
        except TimeoutException:
            break
    performance_list = []
    for l in table[1:-1]:
        row = parse_line(driver, l)
        if len(row) == 0:
            continue
        performance_list.append(row)
    return performance_list


def parse_line(driver, line):
    fields = line.find_elements_by_tag_name('td')
    # project_tag = fields[0].find_elements_by_tag_name('span')
    row = {}
    if len(fields) < 4:
        return row
    # row['name'] = project_tag[0].text
    # row['type'] = project_tag[1].text
    project = fields[0].text.split('\n')
    row['name'] = project[0]
    row['type'] = project[1]
    row['phase'] = fields[1].text
    row['rate'] = fields[2].text
    row['position'] = fields[3].text
    return row


def open_database():
    engine = create_engine(db)
    return engine


def get_latest_date(engine):
    perf = pd.read_sql_table('list', engine)
    latest_date = perf.iloc[-1]['date']
    return latest_date


def get_phase(driver):
    driver.get('http://www.vipysdd.com/common/xmjsList.html?code=xmjs&no=0')
    engine = open_database()
    latest_date = get_latest_date(engine)
    table = get_phase_list(driver)
    last_date = table[-1]['date']
    while latest_date < last_date:
        try:
            next_page = driver.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "jp-next")))
            next_page.click()
            time.sleep(5)
            next_table = get_phase_list(driver)
            table = table + next_table
            last_date = next_table[-1]['date']
        except TimeoutException:
            print("can't find next page")

    i = 0
    table.reverse()
    for row in table:
        if row['date'] <= latest_date:
            i += 1
        else:
            break
    write_to_db(engine, table[i:])


def write_to_db(engine, table):
    Session.configure(bind=engine)
    session = Session()
    for row in table:
        days = find_period(row['type'])
        session.add(MyList(name=row['name'], type=row['type'], date=row['date'],
                           marketvalue=int(row['marketvalue']), investorratio=float(row['investorratio'])/100,
                           traderratio=float(row['traderratio'])/100, ratioperday=float(row['investorratio'])/100/days)
                    )
    session.commit()


def find_period(value):
    result = re.search("\d+\*\d+", value)
    p, n = result.group(0).split('*')
    return int(p)


def get_phase_list(driver):
    try:
        table_element = driver.wait.until(EC.presence_of_element_located((By.TAG_NAME, 'tbody')))
        rows = table_element.find_elements_by_tag_name('tr')
        table = []
        for row in rows:
            fields = row.find_elements_by_tag_name('td')
            phase = {}
            phase['name'], phase['type'] = get_name_type(fields[0].text)
            phase['date'] = datetime.strptime(fields[1].text, "%Y-%m-%d")
            phase['marketvalue'] = fields[2].text
            phase['investorratio'] = fields[3].text
            phase['traderratio'] = fields[4].text
            table.append(phase)
        return table
    except TimeoutException:
        print("can't get phase list")


def get_name_type(project):
    parts = project.rstrip('】').split('【')
    return parts[0], parts[1]


if __name__ == "__main__":
    userId = sys.argv[1]
    password = sys.argv[2]
    driver = init_driver()
    login(driver, userId, password)
    time.sleep(5)
    table = getPerformance(driver)
    df = pd.DataFrame(table)
    df.to_excel('performance.xlsx',  sheet_name='test', index=False)
    driver.quit()

