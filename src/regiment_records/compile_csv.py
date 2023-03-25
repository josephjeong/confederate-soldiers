import pandas as pd
import pickle
import re
import json
import os

from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor

def modify_record_to_include_metadata(record : dict, id : str, name : str, event_type : str) -> dict:
    record["id"] = id
    record["name"] = name
    record["event_type"] = event_type
    return record

def process_regiment_file(filename : str) -> pd.DataFrame:
    with open(f"data/regiment_records/{filename}", "rb") as f:
        data = pickle.load(f)

    regimentContent = data["regimentContent"]

    documents = regimentContent["document"]

    companies = documents["companies"]
    battles = documents["battles"]

    # muster in
    try:
        start_date = documents["startDate"] 
    except:
        start_date = None

    # muster out
    try:
        end_date = documents["endDate"]
    except:
        end_date = None
    # endPlace = documents["endPlace"]

    # get commander list
    history = documents["history"]
    matches = re.findall(r"<li><a href=\"https://www\.fold3\.com/memorial/.+?/.*?\">(.+?)</a> \((.*?)\)</li>", history)
    commanders = [{
        "name": match[0],
        "info": match[1]
    } for match in matches]

    id = filename.split(".")[0]
    name = documents["name"]

    # add metadata to data types
    start_date = modify_record_to_include_metadata({"start_date": start_date}, id, name, "start_date")
    end_date = modify_record_to_include_metadata({"end_date": end_date}, id, name, "end_date")
    commanders = list(map(lambda commander: modify_record_to_include_metadata(commander, id, name, "commander"), commanders))
    companies = list(map(lambda company: modify_record_to_include_metadata(company, id, name, "company"), companies))
    battles = list(map(lambda battle: modify_record_to_include_metadata(battle, id, name, "battle"), battles))

    # combine into one list
    records = [start_date, end_date] + commanders + companies + battles

    # turn records into dataframe
    return pd.DataFrame(records)

def process_all_regiment_files() -> pd.DataFrame:
    filenames = os.listdir("data/regiment_records")
    with ProcessPoolExecutor() as executor:
        records = pd.concat(tqdm(
            executor.map(process_regiment_file, filenames), 
            total=len(filenames), 
            desc="unpickling records"
        ))
    return records

def compile_regiment_csv():
    df = process_all_regiment_files()

    print("compiling csv")
    df.to_csv("data/regiment_records.csv", index=False)

    df.reset_index(inplace=True, drop=True)
    print(df)