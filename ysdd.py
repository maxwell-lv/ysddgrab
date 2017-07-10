import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def init_driver():
    driver = webdriver.Chrome()
    driver.wait = WebDriverWait(driver, 5)
    return driver


def login(driver):
    driver.get("http://www.vipysdd.com")
    try:
        userId = driver.wait.until(EC.presence_of_element_located((By.ID, "userId")))
        password = driver.wait.until(EC.presence_of_element_located((By.ID, "password")))
        button = driver.wait.until(EC.element_to_be_clickable((By.ID, "loginBtn")))
        userId.send_keys("")
        password.send_keys("")
        button.click()
    except TimeoutException:
        print("Box or Button not found in google.com")


if __name__ == "__main__":
    driver = init_driver()
    login(driver)
    time.sleep(5)
    driver.quit()

