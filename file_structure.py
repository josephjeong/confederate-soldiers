import os
import pickle
import numpy as np

from tqdm import tqdm

# open soldier_ids.pickle
with open("data/regiment_ids.pickle", "rb") as f:
    soldier_ids = pickle.load(f)
print(len(soldier_ids))

# # exit
# exit()

# get list of files in data/soldier_records
filenames = os.listdir("data/soldier_records")

regiment_ids = set()

for filename in tqdm(filenames):
    # open the pickle file
    with open("data/soldier_records/" + filename, "rb") as f:
        # read the file
        data = pickle.load(f)

        # extract regiment id from json object
        relations = data["relations"]
        for relation in relations:
            if relation["id"]["contentType"] == "REGIMENT":
                regiment_ids.add(relation["id"]["objectId"])

print(regiment_ids)

# save to pickle file in data/
with open("data/regiment_ids.pickle", "wb") as f:
    pickle.dump(regiment_ids, f)


