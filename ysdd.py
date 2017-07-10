import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


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
        print("Box or Button not found in google.com")


if __name__ == "__main__":
    userId = sys.argv[1]
    password = sys.argv[2]
    driver = init_driver()
    login(driver, userId, password)
    time.sleep(5)
    driver.quit()

