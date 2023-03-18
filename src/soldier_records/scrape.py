from src.soldier_records.ids import scrape_solider_ids
from src.soldier_records.records import get_and_save_soldier_records as solder_records
from src.soldier_records.compile_csv import compile_csv

from src.retry_requests import retry_requests

def scrape():
    soldier_ids = scrape_solider_ids()

    # scrape soldier records
    retry_requests(
        records_dir = "data/regiment_records",
        failed_ids_path = "data/failed_soldier_ids.txt",
        ids = soldier_ids,
        get_and_save_records = solder_records,
    )
    
    # compile all scraped records
    compile_csv()