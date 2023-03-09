import os
import sys
import requests

import numpy as np

from tqdm import tqdm
from itertools import repeat
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any

import src.auth as auth
import src.config as config

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

        resp_json = resp.json()
        facets = resp_json["facets"][0]["facets"]

        # get all the facet names
        entities = [{
            "name": facet["v"],
            "count": facet["c"]
            } for facet in facets]
        return entities

    except Exception as e:
        print(e)
        sys.exit(1)
    
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

def send_docsearch_req(req_headers : Dict[str, str], payload : Dict)-> List[int]:
    NUM_RETRIES = 3
    exc_reason = None
    
    for _ in range(NUM_RETRIES):
        try:
            resp = requests.post(url="https://www.fold3.com/fold31-search/doc-search", 
                json=payload, 
                headers=req_headers, 
                timeout=120
            )
        except Exception as e:
            exc_reason = e
            continue
        resp_json = resp.json()
        if "hits" not in resp_json.keys():
            exc_reason = "hits"
            continue

        # extract id from json
        ids = list(map(lambda x: int(x["doc"]["id"]["id"]), resp_json["hits"]))    
        return ids

    print("failed to get ids for payload:", payload)
    print("reason:", exc_reason)
    sys.exit(1)

def get_record_ids() -> np.ndarray:
    # if ids are already cached, use them instead of scraping
    if os.path.exists("data/confederate_ids.npy"):
        print("using cached ids")
        return np.load("data/confederate_ids.npy", allow_pickle=True)

    req_headers = auth.REQ_HEADERS.copy()

    # get all the entities that are military service
    entities = get_military_entities(req_headers)

    # generate payloads to get ids from each entity
    payloads = generate_doc_search_payloads(entities)

    # get all ids in one file
    with ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as executor:
        ids = list(tqdm(executor.map(send_docsearch_req, repeat(req_headers), payloads), 
            total=len(payloads),
            desc= "scraping all confederate soldier ids"
        ))

    # flatten results
    flattened_ids = np.array([item for sublist in ids for item in sublist])
    unique_flattened_ids = np.unique(flattened_ids) # only have unique ids
    sorted_flattened_ids = np.sort(unique_flattened_ids)

    # these don't seem to be real ids
    # remove 655288166, and 654162824 from array
    sorted_flattened_ids = sorted_flattened_ids[sorted_flattened_ids != 655288166]
    sorted_flattened_ids = sorted_flattened_ids[sorted_flattened_ids != 654162824]

    # cache ids for future use
    np.save("data/confederate_ids.npy", sorted_flattened_ids)

    return sorted_flattened_ids