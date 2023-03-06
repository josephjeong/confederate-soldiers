import os
import pickle
from pprint import pprint
from typing import Dict, List
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
import pandas as pd

# some files are a list, some files are a dict
def record_element_list_to_dict(elements):
    return_dict = {}
    for element in elements:

        if element is None:
            continue

        if element["type"] not in return_dict.keys():
            return_dict[element["type"]] = element["value"]
        elif element["type"] == "full-name": # for full-name, keep the longest full name
            if len(element["type"]) > len(return_dict[element["type"]]):
                return_dict[element["type"]] = element["value"]
        else:
            return_dict[element["type"]] = return_dict[element["type"]] + " - " + element["value"]
    return return_dict

def unpickle_record(filename: str) -> pd.DataFrame:
    record = None
    with open(f"data/records/{filename}", "rb") as f:
        try:
            record = pickle.load(f)
        except:
            print(f"Error unpickling {filename}")
            # return empty df
            return pd.DataFrame()
    if isinstance(record, list):
        record = record_element_list_to_dict(record)
    id = filename.split(".")[0]
    record["id"] = id
    return pd.DataFrame(record, index=[0])

# open and unpickle all files in "data/records" directory
def get_all_records() -> pd.DataFrame:
    filenames = os.listdir("data/records")
    with ProcessPoolExecutor() as executor:
        records = pd.concat(tqdm(executor.map(unpickle_record, filenames), total=len(filenames), desc="unpickling records"))
    return records

def compile_csv():
    df = get_all_records()
    df.to_csv("data/records.csv", index=False)
    print(df)
