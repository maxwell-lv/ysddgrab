import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd

def init_driver():
    driver = webdriver.Chrome()
    driver.wait = WebDriverWait(driver, 5)
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
        row = parseLine(driver, l)
        performance_list.append(row)
    return performance_list

def parseLine(driver, line):
    fields = line.find_elements_by_tag_name('td')
    # project_tag = fields[0].find_elements_by_tag_name('span')
    row = {}
    # row['name'] = project_tag[0].text
    # row['type'] = project_tag[1].text
    project = fields[0].text.split('\n')
    row['name'] = project[0]
    row['type'] = project[1]
    row['phase'] = fields[1].text
    row['rate'] = fields[2].text
    row['position'] = fields[3].text
    return row

if __name__ == "__main__":
    userId = sys.argv[1]
    password = sys.argv[2]
    driver = init_driver()
    login(driver, userId, password)
    time.sleep(5)
    table = getPerformance(driver)
    df = pd.DataFrame(table)
    df.to_excel('performance.xlsx', index=False)
    driver.quit()

