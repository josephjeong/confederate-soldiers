import os
import pickle
from pprint import pprint
from typing import Dict, List

from tqdm import tqdm


# open and unpickle all files in "data/records" directory
def get_all_records() -> List[Dict]:
    records = []
    for filename in tqdm(os.listdir("data/records")[:2], desc="unpickling records"):
        with open(f"data/records/{filename}", "rb") as f:
            records.append(pickle.load(f))
    return records

pprint(get_all_records())