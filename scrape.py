from os import getcwd
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

PATH = getcwd() + "/chromedriver.exe"
from selenium.webdriver.support import expected_conditions as EC
from typing import Dict, List
import requests
import re
from urllib.parse import urlencode
from pprint import pprint
import logging
import json

def get_headers_dict() -> Dict[str, str]:
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
    return req_dict

def send_req(req_headers : Dict[str, str]):
    try:
        resp = requests.get(url="https://www.fold3.com/memorial/653971380/a-augustin-bernard-civil-war-stories", headers=req_headers, timeout=120)
    except requests.exceptions.Timeout:
        print("timed out!")
        return
    except requests.exceptions.ConnectionError:
        print("connection error")
        return
    match = re.search(r"\"F3_COMPONENT_DATA\":\s*({(?:.*)})", resp.text)
    if match is None:
        print("no match")
        return
    data = json.loads(match.group(1))
    elements = data["memorialContent"]["elements"]
    mapped_elements = list(filter(lambda x: x is not None, map(extract_elements, elements)))
    return mapped_elements

def extract_elements(data: Dict):
    element = data["element"]
    if "event" not in element.keys():
        return None
    new_dict = {}
    new_dict["type"] = element["type"]
    new_dict["name"] = element["name"]
    new_dict["value"] = element["value"]
    return new_dict

def scrape():
    req_headers = get_headers_dict()
    return send_req(req_headers)

if __name__ == "__main__":
    pprint(scrape())