from src.auth import get_headers_dict
from src.ids import get_record_ids
from src.records import get_and_save_records
from src.compile_csv import compile_csv

# TODO: don't scrape if file already exists

def scrape():
    get_headers_dict()
    ids =  get_record_ids()
    get_and_save_records(ids, number=-1)
    compile_csv()

if __name__ == "__main__":
    scrape()