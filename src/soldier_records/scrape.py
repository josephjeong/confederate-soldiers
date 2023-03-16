from src.soldier_records.ids import get_record_ids as soldier_ids
from src.soldier_records.records import get_and_save_records as solder_records
from src.soldier_records.compile_csv import compile_csv

from src.retry_requests import retry_requests

def scrape():
    # scrape soldier records
    retry_requests(
        records_dir = "data/soldier_records",
        failed_ids_path = "data/failed_ids.txt",
        get_record_ids = soldier_ids,
        get_and_save_records = solder_records,
    )
    
    # compile all scraped records
    compile_csv()