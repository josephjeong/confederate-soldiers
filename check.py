import pickle
import json
from pprint import pprint

from collections import defaultdict

import pandas as pd

# read pickle file based on id 
id = 653619202
with open(f"data/responses/{id}.pkl", "rb") as f:
    data = pickle.load(f)
    
    facts = defaultdict(lambda : defaultdict(str))
    
    prev_military_service_type = ""
    counter = defaultdict(int)

    for datum in data["memorialContent"]["elements"]:
        element = datum["element"]
        if "event" not in element.keys():
            continue
        event_type = element["event"][0]["type"]

        if event_type == "CUSTOM":
            event_type = element["event"][0]["name"].upper()

        elif event_type == "MILITARY_SERVICE": 
            if len(element["event"]) == 1:
                event_type = "MILITARY_SERVICE_GENERAL"
            else:
                event_type = "MILITARY_SERVICE_" + element["event"][1]["type"]
            
            if event_type == "MILITARY_SERVICE_CUSTOM_MILITARY":
                event_type = "MILITARY_SERVICE_" + element["event"][1]["name"].upper()

            if event_type != prev_military_service_type:
                counter[prev_military_service_type] += 1
                prev_military_service_type = event_type
            
            if counter[event_type] > 0 and event_type != "MILITARY_SERVICE_GENERAL":
                event_type = event_type + "_" + str(counter[event_type])

        elif event_type == "INTERNAL_PEOPLE":
            facts["name"] = element["value"]
            continue

        if not facts[event_type][element["name"]]:
            facts[event_type][element["name"]] = str(element["value"])
        else:
            facts[event_type][element["name"]] += ", " + str(element["value"])

    facts["id"] = id # type: ignore

    # output to json file
    with open(f"data/responses/{id}.json", "w") as f:
        json.dump(facts, f, indent=4)

id = facts.pop("id")
name = facts.pop("name")

df = pd.DataFrame.from_dict(facts, orient="index")
df.reset_index(inplace=True)
df.rename(columns={"index": "event_type"}, inplace=True)
df["id"] = id
df["name"] = name

df.to_csv(f"data/responses/{id}.csv", index=False)