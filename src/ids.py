import os
import sys
import time
import requests

import numpy as np

from tqdm import tqdm
from itertools import repeat
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any

from src.auth import REQ_HEADERS
from src.config import MAX_WORKERS

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
        sys.exit(1)
        return []
    except requests.exceptions.ConnectionError as e:
        print("connection error", e)
        sys.exit(1)
        return []
    except Exception as e:
        print(e)
        sys.exit(1)
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
    NUM_RETRIES = 3
    WAIT_TIME = 0 # 1 min wait before retry

    exc_reason = None
    
    for _ in range(NUM_RETRIES):
        try:
            resp = requests.post(url="https://www.fold3.com/fold31-search/doc-search", 
                json=payload, 
                headers=req_headers, 
                timeout=120
            )
        except requests.exceptions.Timeout as e:
            exc_reason = e
            time.sleep(WAIT_TIME)
            continue
        except requests.exceptions.ConnectionError as e:
            exc_reason = e
            time.sleep(WAIT_TIME)
            continue
        except Exception as e:
            exc_reason = e
            time.sleep(WAIT_TIME)
            continue
        resp_json = resp.json()
        if "hits" not in resp_json.keys():
            exc_reason = "hits"
            time.sleep(WAIT_TIME)
            continue
        ids = list(map(get_id, resp_json["hits"]))    
        return ids
    print("failed to get ids for payload", payload)
    print("reason:", exc_reason)
    sys.exit(1)

def save_record_ids(ids : np.ndarray):
    np.save("data/confederate_ids.npy", ids)

def get_record_ids() -> np.ndarray:
    # if ids are already cached, use them instead of scraping
    if os.path.exists("data/confederate_ids.npy"):
        print("using cached ids")
        return np.load("data/confederate_ids.npy")

    req_headers = REQ_HEADERS.copy()

    # get all the entities that are military service
    entities = get_military_entities(req_headers)

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