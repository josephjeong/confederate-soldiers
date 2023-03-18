from src.auth import get_headers_dict
import src.soldier_records.scrape as soldiers
import src.regiment_records.scrape as regiments

if __name__ == "__main__":
    # get initial auth headers for use in subsequent operations
    get_headers_dict()

    # scrape solider reocrds
    # soldiers.scrape()

    # scrape regiment records
    regiments.scrape()
