from os import getcwd

from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire import webdriver

PATH = getcwd() + "/chromedriver.exe"
import json
import os
import pickle
import re
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
from pprint import pprint
from typing import Dict, List, Optional, Any

import numpy as np
import requests
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm

MAX_WORKERS = 36

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

def get_military_entities(req_headers : Dict[str, str]) -> List[Dict[str, Any]]:
    payload = {
        "facetRequests": [
            {
            "type": "military.service",
            "maxCount": 10000
            }
        ],
        "filters": [
            {
            "type": "military.conflict",
            "values": [
                "Civil War (Confederate)"
            ]
            },
            {
            "type": "general.title.content.sub-type",
            "values": [
                "SERVICEPERSON"
            ]
            },
            {
            "type": "general.title.content.collection",
            "values": [
                "us-civil-war-confederate"
            ]
            }
        ],
        "maxCount": 0
    }

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
    facets = resp_json["facets"][0]["facets"]

    # get all the facet names
    entities = [{
        "name": facet["v"],
        "count": facet["c"]
        } for facet in facets]
    return entities


def generate_doc_search_payloads(entities : List[Dict]) -> List[Dict]:
    payloads = []
    max_results_per_req = 5000

    for entity in entities:
        entity_name = entity["name"]
        entity_count = entity["count"]
        num_reqs = entity_count // max_results_per_req + 1

        for i in range(num_reqs):
            offset = i * max_results_per_req
            
            payload = {
                'environment': {'origin': 'regiment'},
                'facetRequests': [
                    {
                        'maxCount': max_results_per_req, 
                        'placeLevel': 'COUNTRY', 
                        'type': 'place'
                    },
                    {
                        'maxCount': max_results_per_req,
                        'placeLevel': 'STATE',
                        'placeParents': ['rel.148838'],
                        'type': 'place'
                    },
                    {
                        'maxCount': max_results_per_req, 
                        'type': 'military.service.branch'
                    },       
                    {
                        'maxCount': max_results_per_req, 
                        'type': 'general.title.content.type'
                    },    
                    {
                        'maxCount': max_results_per_req, 
                        'type': 'general.title.provider.id'
                    }
                ],    
                'filters': [
                    {
                        'type': 'military.conflict',
                        'values': ['Civil War (Confederate)']
                    },
                    {
                        'type': 'general.title.content.sub-type',
                        'values': ['SERVICEPERSON']
                    },
                    {
                        'type': 'general.title.content.collection',
                        'values': ['us-civil-war-confederate']
                    },
                    # removing this to check if this works - and if this creates the diff in num records
                    {
                        'type': 'general.title.id', 
                        'values': ['1087']
                    },
                    {
                    "type": "military.service",
                    "values": [entity_name]
                    }
                ],
                'highlight': {'highlight': True},
                'maxCount': max_results_per_req,
                'offset': offset,
            }

            payloads.append(payload)

    return payloads

def get_id(resp_body) -> int:
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

def get_record_ids(req_headers : Optional[Dict[str, str]], entities : List[Dict]) -> np.ndarray:
    # if ids are already cached, use them instead of scraping
    if os.path.exists("data/confederate_ids.npy"):
        print("using cached ids")
        return np.load("data/confederate_ids.npy")

    payloads = generate_doc_search_payloads(entities)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        ids = list(tqdm(executor.map(send_docsearch_req, repeat(req_headers), payloads), 
            total=len(payloads),
            desc= "scraping all confederate soldier ids"
        ))

    flattened_ids = np.array([item for sublist in ids for item in sublist])
    sorted_flattened_ids = np.sort(flattened_ids)

    # cache ids for future use
    save_record_ids(sorted_flattened_ids)

    return sorted_flattened_ids

def save_record_ids(ids : np.ndarray):
    np.save("data/confederate_ids.npy", ids)

def send_record_req(req_headers : Dict[str, str], id : int):
    try:
        resp = requests.get(url=f"https://www.fold3.com/memorial/{id}/", headers=req_headers, timeout=600)
    except Exception as e:
        print(id, e)
        return
    match = re.search(r"\"F3_COMPONENT_DATA\":\s*({(?:.*)})", resp.text)
    if match is None:
        print("no match")
        return
    data = json.loads(match.group(1))
    try:
        elements = data["memorialContent"]["elements"]
    except:
        print(data)
        return
    mapped_elements = list(filter(lambda x: x is not None, map(extract_record_elements, elements)))
    # pickle and save file in "data/records" directory
    with open(f"data/records/{id}.pkl", "wb") as f:
        pickle.dump(mapped_elements, f)
    return

def extract_record_elements(data: Dict):
    element = data["element"]
    if "event" not in element.keys():
        return None
    new_dict = {}
    new_dict["type"] = element["type"]
    new_dict["name"] = element["name"]
    new_dict["value"] = element["value"]
    return new_dict

def get_and_save_records(ids: np.ndarray, req_headers : Dict[str, str], start : int=0, number : int=100_000):
    # if scrape fails somewhere, start from where it left off
    if start != 0:
        ids = ids[ids > start]
    
    # only scrape a certain number of records (negative number scrapes all records)
    if number >= 0:
        ids = ids[:number]

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        list(tqdm(executor.map(send_record_req, repeat(req_headers), ids),
            total=len(ids),
            desc= "scraping all confederate soldier ids"
        ))

def scrape():
    req_headers = get_headers_dict()
    entities = get_military_entities(req_headers)
    ids =  get_record_ids(req_headers, entities)
    get_and_save_records(ids, req_headers, number=-1)

    # add a check to make sure directories exist
    # problem with expiring authentication tokens

if __name__ == "__main__":
    scrape()