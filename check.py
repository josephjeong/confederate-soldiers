import pickle
import json
from pprint import pprint

from collections import defaultdict

import pandas as pd
import numpy as np

# read pickle file based on id 
id = 653619202
filename = f"{id}.pkl"

def process_file(filename: str) -> pd.DataFrame:
    with open(f"data/records/{filename}", "rb") as f:
        data = pickle.load(f)
        
        facts = defaultdict(lambda : defaultdict(str)) 
        
        prev_military_service_type = "" # to detect when event type changes
        counter = defaultdict(int) # to append event types

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
                facts["name"] = element["value"]
                continue
            
            event_type = event_type.replace(" ", "_")

            # only append to string when there is already a value
            if not facts[event_type][element["name"]]:
                facts[event_type][element["name"]] = str(element["value"])
            else:
                facts[event_type][element["name"]] += ", " + str(element["value"])

        facts["id"] = id # type: ignore

    id = facts.pop("id") # type: ignore
    name = facts.pop("name")

    df = pd.DataFrame.from_dict(facts, orient="index")
    df.reset_index(inplace=True)
    df.rename(columns={"index": "event_type"}, inplace=True)
    df["id"] = id
    df["name"] = name

    return df

if __name__ == "__main__":
    # read confederate_ids.npy
    ids = np.load("data/confederate_ids.npy", allow_pickle=True)
    ids = ids.tolist()[:10]

    # get all dfs from ids
    dfs = []
    for id in ids:
        dfs.append(process_file(id))
    
    # concat all dfs
    df = pd.concat(dfs, ignore_index=True)

    print(df)

    # save to csv
    df.to_csv(f"data/responses/results.csv", index=False)