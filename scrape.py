import numpy as np
import os

from src.auth import get_headers_dict
from src.ids import get_record_ids
from src.records import get_and_save_records
from src.compile_csv import compile_csv

def scrape():
    get_headers_dict()

    while True:
        
        # read all ids
        ids = get_record_ids()

        # get all files in data/soldier_records
        filenames = os.listdir("data/soldier_records")
        if filenames:
            filename_ids = np.array([int(filename.split(".")[0]) for filename in filenames])

            result = ids[~np.isin(ids, filename_ids)]
            print("failed results: " + str(result.shape[0]))

            if result.shape[0] == 0:
                break

            print("re-scraping failed results")
            ids = result

        # clear existing failed_ids.txt
        open("data/failed_ids.txt", "w").close()

        get_and_save_records(ids)

if __name__ == "__main__":
    scrape()
    compile_csv()

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--scrape", action="store_true")
    args = parser.parse_args()