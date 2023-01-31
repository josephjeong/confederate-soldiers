from os import getcwd
from seleniumwire import webdriver
from selenium.webdriver.support.ui import WebDriverWait

PATH = getcwd() + "/chromedriver.exe"
from selenium.webdriver.support import expected_conditions as EC
from typing import Dict, List
import requests
import re
from pprint import pprint
import json
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from itertools import repeat

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

def generate_doc_search_payloads(start : int, end : int) -> List[Dict]:
    payloads = []
    
    increment = 5000
    for i in range(start, end, increment):
        offset = i

        payload = {
            'environment': {'origin': 'regiment'},
            'facetRequests': [{'maxCount': 5000, 'placeLevel': 'COUNTRY', 'type': 'place'},
                            {'maxCount': 5000,
                                'placeLevel': 'STATE',
                                'placeParents': ['rel.148838'],
                                'type': 'place'},
                            {'maxCount': 5000, 'type': 'military.service.branch'},       
                            {'maxCount': 5000, 'type': 'general.title.content.type'},    
                            {'maxCount': 5000, 'type': 'general.title.provider.id'}],    
            'filters': [{'type': 'military.conflict',
                        'values': ['Civil War (Confederate)']},
                        {'type': 'general.title.content.sub-type',
                        'values': ['SERVICEPERSON']},
                        {'type': 'general.title.content.collection',
                        'values': ['us-civil-war-confederate']},
                        {'type': 'general.title.id', 'values': ['1087']}],
            'highlight': {'highlight': True},
            'maxCount': increment,
            'offset': offset,
        }

        payloads.append(payload)

    return payloads

def get_id(resp_body) -> List[int]:
    return int(resp_body["doc"]["id"]["id"])

def send_docsearch_req(req_headers : Dict[str, str], payload : Dict)-> List[int]:
    try:
        resp = requests.post(url="https://www.fold3.com/fold31-search/doc-search", 
            json=payload, 
            headers=req_headers, 
            timeout=120
        )
    except requests.exceptions.Timeout as e:
        print("timed out!", e)
        return []
    except requests.exceptions.ConnectionError as e:
        print("connection error", e)
        return []
    except Exception as e:
        print(e)
        return []
    resp_json = resp.json()
    if "hits" not in resp_json.keys():
        print(resp.text)
        pprint(payload)
        return []
    ids = list(map(get_id, resp_json["hits"]))
    return ids

def get_record_ids(req_headers : Dict[str, str]) -> List[int]:
    # record_count = 1_300_000 # 1.3 million (round up 1.2 million+)
    payloads = generate_doc_search_payloads(0, 10000)

    with ThreadPoolExecutor(max_workers=25) as executor:
        # map preserves order of the transcripts
        ids = list(tqdm(executor.map(send_docsearch_req, repeat(req_headers), payloads), 
            total=len(payloads),
            desc= "scraping all confederate soldier ids"
        ))

    return ids

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
    ids =  get_record_ids(req_headers)
    return ids

    # return send_req(req_headers)

if __name__ == "__main__":
    pprint(scrape())