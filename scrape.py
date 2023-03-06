from src.auth import get_headers_dict
from src.ids import get_record_ids
from src.records import get_and_save_records

# TODO: don't scrape if file already exists

def scrape():
    get_headers_dict()
    ids =  get_record_ids()
    get_and_save_records(ids, number=-1)

    # add a check to make sure directories exist

if __name__ == "__main__":
    scrape()