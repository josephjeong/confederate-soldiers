import os
import pickle
from pprint import pprint
from typing import Dict, List
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
import pandas as pd

def unpickle_record(filename: str) -> pd.DataFrame:
    record = None
    with open(f"data/records/{filename}", "rb") as f:
        record = pickle.load(f)
    record_dict = {}
    for column in record:
        record_dict[column["type"]] = column["value"]
    id = filename.split(".")[0]
    record_dict["id"] = id
    return pd.DataFrame(record_dict, index=[0])

# open and unpickle all files in "data/records" directory
def get_all_records() -> pd.DataFrame:
    filenames = os.listdir("data/records")
    with ProcessPoolExecutor() as executor:
        records = pd.concat(tqdm(executor.map(unpickle_record, filenames), total=len(filenames), desc="unpickling records"))
    return records
if __name__ == "__main__":
    df = get_all_records()
    df.to_csv("data/records.csv", index=False)
    print(df)