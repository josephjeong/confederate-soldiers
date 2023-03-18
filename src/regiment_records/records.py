import re
import json
import pickle
import requests

import numpy as np

from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

import src.auth as auth
import src.config as config

from pprint import pprint

def send_regiment_record_req(id : int):
    req_headers = auth.REQ_HEADERS.copy()

    try:
        resp = requests.get(url=f"https://www.fold3.com/regiment/{id}/", headers=req_headers, timeout=600)

        match = re.search(r"\"F3_COMPONENT_DATA\":\s*({(?:.*)})", resp.text)
        if match is None:
            raise Exception("no match")
        data = json.loads(match.group(1))

        if "regimentContent" not in data.keys():
            raise Exception("no regimentContent")

        with open(f"data/regiment_records/{id}.pkl", "wb") as f:
            pickle.dump(data, f)

    except Exception as e:
        # append id to text file so we can scrape it later
        with open("data/failed_regiment_ids.txt", "a") as f:
            f.write(f"{id}\n")


def get_and_save_regiment_records(ids: np.ndarray):
    ids = ids[:1]

    with ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as executor:
        list(tqdm(executor.map(send_regiment_record_req, ids),
            total=len(ids),
            desc= "scraping all confederate regiment records"
        ))