from src.regiment_records.ids import get_regiment_ids_from_solider_records
from src.regiment_records.records import get_and_save_regiment_records as regiment_records
from src.retry_requests import retry_requests
from src.regiment_records.compile_csv import compile_regiment_csv

def scrape():
    regiment_ids = get_regiment_ids_from_solider_records()

    # scrape regiment records
    retry_requests(
        records_dir = "data/regiment_records",
        failed_ids_path = "data/failed_regiment_ids.txt",
        ids = regiment_ids,
        get_and_save_records = regiment_records,
    )

    # compile all scraped records
    compile_regiment_csv()