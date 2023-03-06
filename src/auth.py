from os import getcwd

from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire import webdriver
from selenium.webdriver.support import expected_conditions as EC

PATH = getcwd() + "/chromedriver.exe"
REQ_HEADERS = {}

def get_headers_dict():
    driver = webdriver.Chrome(PATH)
    driver.get("https://www.fold3.com/login")

    # wait to be redirected to the home page
    WebDriverWait(driver, 60).until(   
        EC.title_contains("Historical"),
        "Authentication Did Not Succeed Before Timeout"
    )
    reqs = driver.requests
    driver.quit()
 
    # get the last request that has a cookie (the authenticated request)
    reqs_with_cookies = list(filter(lambda req: "cookie" in req.headers , reqs))
    req_header = list(map(lambda req: req.headers, reqs_with_cookies))[-1]

    # create a dictionary of headers
    req_dict = {key: value for key, value in req_header.raw_items()}
    global REQ_HEADERS
    REQ_HEADERS = req_dict
