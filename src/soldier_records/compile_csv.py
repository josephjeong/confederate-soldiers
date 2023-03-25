import os
import pickle

import pandas as pd

from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
from collections import defaultdict

def process_soldier_file(filename: str) -> pd.DataFrame:
    with open(f"data/soldier_records/{filename}", "rb") as f:
        data = pickle.load(f)
    
    facts = defaultdict(lambda : defaultdict(str)) 
    prev_military_service_type = "" # to detect when event type changes
    counter = defaultdict(int) # to append event types
    name = ""
    
    for datum in data["memorialContent"]["elements"]:
        element = datum["element"]
        # if not an event, not relevant to us
        if "event" not in element.keys():
            continue
        event_type = element["event"][0]["type"]

        # if custom event, make event type the name of the event
        if event_type == "CUSTOM":
            event_type = element["event"][0]["name"].upper()

        # if military service, make event type the name of the military service
        elif event_type == "MILITARY_SERVICE": 
            # if military service is general, make event type military service general
            if len(element["event"]) == 1:
                event_type = "MILITARY_SERVICE_GENERAL"
            else:
                event_type = "MILITARY_SERVICE_" + element["event"][1]["type"]
            
            # if military service is custom, make event type military service custom military
            if event_type == "MILITARY_SERVICE_CUSTOM_MILITARY":
                event_type = "MILITARY_SERVICE_" + element["event"][1]["name"].upper()

            # if event_type is not the same, increment counter
            if event_type != prev_military_service_type:
                counter[prev_military_service_type] += 1
                prev_military_service_type = event_type
            
            # if counter is greater than 0, append counter to event type
            if counter[event_type] > 0 and event_type != "MILITARY_SERVICE_GENERAL":
                event_type = event_type + "_" + str(counter[event_type])

        # if internal people, this is just the name
        elif event_type == "INTERNAL_PEOPLE":
            name = element["value"]
            continue

        event_type = event_type.replace(" ", "_")

        # only append to string when there is already a value
        if not facts[event_type][element["name"]]:
            facts[event_type][element["name"]] = str(element["value"])
        else:
            facts[event_type][element["name"]] += ", " + str(element["value"])
    df = pd.DataFrame.from_dict(facts, orient="index")

    df.reset_index(inplace=True)
    df.rename(columns={"index": "event_type"}, inplace=True)
    df["id"] = filename.split(".")[0] 
    df["name"] = name 

    return df

# open and unpickle all files in "data/soldier_records" directory
def process_all_soldier_records() -> pd.DataFrame:
    filenames = os.listdir("data/soldier_records")
    with ProcessPoolExecutor() as executor:
        records = pd.concat(tqdm(
            executor.map(process_soldier_file, filenames), 
            total=len(filenames), 
            desc="unpickling records"
        ))
    return records

def compile_soldier_csv():
    df = process_all_soldier_records()

    print("compiling csv")
    df.to_csv("data/soldier_records.csv", index=False)

    df.reset_index(inplace=True, drop=True)
    print(df)