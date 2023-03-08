import json
import pickle
import re
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import requests
import numpy as np

import src.auth as auth
import src.config as config

def send_record_req(id : int):
    # copy request headers so we don't modify the original
    req_headers = auth.REQ_HEADERS.copy()

    try:
        # send request to get record
        resp = requests.get(url=f"https://www.fold3.com/memorial/{id}/", headers=req_headers, timeout=600)

        # send data in html webpage received
        match = re.search(r"\"F3_COMPONENT_DATA\":\s*({(?:.*)})", resp.text)
        if match is None:
            raise Exception("no match")
        data = json.loads(match.group(1))

        # check if memorialContent is a key and reject if not
        if "memorialContent" not in data.keys():
            raise Exception("no memorialContent")

        # pickle and save file in "data/records" directory
        with open(f"data/records/{id}.pkl", "wb") as f:
            pickle.dump(data, f)

        # refresh cookie to refresh session token
        if id % 1000 == 0:
            auth.REQ_HEADERS["cookie"] = resp.headers.get("Set-Cookie")

    except Exception as e:
        # append id to text file so we can scrape it later
        with open("data/failed_ids.txt", "a") as f:
            f.write(f"{id}\n")

def get_and_save_records(ids: np.ndarray):
    with ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as executor:
        list(tqdm(executor.map(send_record_req, ids),
            total=len(ids),
            desc= "scraping all confederate soldier records"
        ))
