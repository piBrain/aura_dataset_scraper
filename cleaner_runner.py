import data_cleaner
import json
import os



def main():
    root_dir = os.path.dirname(__file__)
    cleaner = data_cleaner.DataCleaner()
    print('Starting clean...')
    with open('data/scrape_file.jl','r') as f:
        for line in f:
            cleaner.process_row(json.loads(line))
    cleaner.flush_row_cache()
    print('Clean data ready.')
if __name__ == '__main__':
    main()
