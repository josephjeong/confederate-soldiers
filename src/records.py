import json
import pickle
import re
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List
from tqdm import tqdm
import requests
import numpy as np

from src.auth import REQ_HEADERS
from src.config import MAX_WORKERS

def send_record_req(id : int):
        # copy request headers so we don't modify the original
        req_headers = REQ_HEADERS.copy()

        try:
            # send request to get record
            resp = requests.get(url=f"https://www.fold3.com/memorial/{id}/", headers=req_headers, timeout=600)

            # send data in html webpage received
            match = re.search(r"\"F3_COMPONENT_DATA\":\s*({(?:.*)})", resp.text)
            if match is None:
                raise Exception("no match")
            data = json.loads(match.group(1))

            # extrate elements from json string extracted
            elements = data["memorialContent"]["elements"]
            mapped_elements = list(filter(lambda x: x is not None, map(extract_record_elements, elements)))

            # pickle and save file in "data/records" directory
            with open(f"data/records/{id}.pkl", "wb") as f:
                pickle.dump(mapped_elements, f)

            # refresh cookie to refresh session token
            if id % 1000 == 0:
                REQ_HEADERS["cookie"] = resp.headers.get("Set-Cookie")

        except Exception as e:
            # append id to text file so we can scrape it later
            with open("data/failed_ids.txt", "a") as f:
                f.write(f"{id}\n")

def extract_record_elements(data: Dict) -> Dict | None:
    element = data["element"]
    if "event" not in element.keys():
        return None
    new_dict = {}
    new_dict["type"] = element["type"]
    new_dict["name"] = element["name"]
    new_dict["value"] = element["value"]
    return new_dict

def get_and_save_records(ids: np.ndarray,  start : int=0, number : int=100_000):
    # if scrape fails somewhere, start from where it left off
    if start != 0:
        ids = ids[ids > start]
    
    # only scrape a certain number of records (negative number scrapes all records)
    if number >= 0:
        ids = ids[:number]

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        list(tqdm(executor.map(send_record_req, ids),
            total=len(ids),
            desc= "scraping all confederate soldier records"
        ))