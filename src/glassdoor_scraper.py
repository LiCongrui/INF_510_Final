import time, pickle, re
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

from const import glassdoor, salaries
from mysql_db import conn, cur

username = "rick96120@126.com"
password = "fihPur-1qokno-syjxid"

def init_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(executable_path="./chromedriver")

    driver.wait = WebDriverWait(driver, 10)

    return driver


def login(driver, username, password):
    driver.get("http://www.glassdoor.com/profile/login_input.htm")
    try:
        user_field = driver.wait.until(EC.presence_of_element_located((By.NAME, "username")))
        pw_field = driver.find_element_by_id("userPassword")
        # login_button = driver.find_element_by_class_name("gd-btn gd-btn-1 minWidthBtn")
        user_field.send_keys(username)
        user_field.send_keys(Keys.TAB)
        time.sleep(1)
        pw_field.send_keys(password)
        time.sleep(1)
        # login_button.click()
        driver.find_element_by_xpath('//button[@type="submit"]').click()

    except TimeoutException:
        print("TimeoutException! Username/password field or login button not found on glassdoor.com")

def get_salaries_by_comp(comp, driver, companyURL, refresh):
    driver.get(companyURL)
    HTML = driver.page_source
    soup = BeautifulSoup(HTML, "html.parser")
    # salaries = soup.find_all("div", {"id": ""})
    for line in soup.find_all("div", {"class": ["salaryRow__SalaryRowStyle__row"]}):
        print(line)
    return soup

def get_salaries():
    driver = init_driver()
    time.sleep(3)

    print("Logging into Glassdoor account ...")
    login(driver, username, password)
    time.sleep(5)

    data = []
    for title, url in salaries.items():
        print("Starting data scraping for " +title+ " ...")
        for i in range(1, 6):
            currentURL = url[:-4] + "_IP" + str(i) + ".htm"
            data = parse_salary_data(driver, currentURL, title, data)
            time.sleep(1)
        time.sleep(1)

    print(data)
    pickle.dump(data, open('sss', 'wb'))
    driver.quit()

def parse_salary_data(driver, url, title, data):
    driver.get(url)
    HTML = driver.page_source
    soup = BeautifulSoup(HTML, "html.parser")
    for line in soup.find_all("div", {"class": ["salaryRow__SalaryRowStyle__row"]}):
        comp = line.find_all('div', {'class': ['salaryRow__JobInfoStyle__employerName']})[0].text
        basePay = line.find_all('div', {'class': ['salaryRow__JobInfoStyle__meanBasePay']})[0].text
        count = line.find_all('div', {'class': ['salaryRow__JobInfoStyle__jobCount']})[0].text
        if '/yr' in basePay:
            basePay = int(basePay.replace(',', '').replace('$', '').replace('/yr', ''))
        elif '/mo' in basePay:
            basePay = int(basePay.replace(',', '').replace('$', '').replace('/mo', '')) * 12
        elif '/hr' in basePay:
            basePay = int(basePay.replace(',', '').replace('$', '').replace('/hr', '')) * 8 * 5 * 4 * 12
        else:
            continue
        count = count.replace(',', '')
        counts = re.findall(r'\d*', count)
        if len(counts) > 0:
            count = int(counts[0])
        else:
            count = 0
        data.append([title, comp, basePay, count])
    return data

def save2mysql(data = [], if_cache = True):
    if if_cache:
        data = pickle.load(open('sss', 'rb'))

    for row in data:
        sql = "INSERT INTO salaries (title, company, base_pay, positions) VALUES "
        sql += '("{}", "{}", {}, {})'.format(row[0], row[1], row[2], row[3])
        try:
            cur.execute(sql)
        except Exception as e:
            print(e)
            print(sql)
            continue

    conn.commit()

if __name__ == "__main__":
    # test_comp = 'Lyft'
    # start(test_comp, glassdoor[test_comp][1])
    # for comp, url in glassdoor.items():
    #     start(comp, url)

    # get_salaries()
    save2mysql(if_cache=True)

