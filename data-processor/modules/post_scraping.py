import csv
from os.path import exists

from modules.config import Config


class PostScrapingHandler(): 
    def __init__(self):
        config = Config()
        self.out_config = config.get_out_config()
        self.main_config = config.get_main_config()
        self.processed_config = config.get_processed_config()
        self.main_file = f"{self.main_config['path']}/{self.main_config['main_file']}"
        self.newly_retrieved_file = f"{self.out_config['path']}/{self.out_config['newly_retrieved_file']}"
        self.processed_file = f"{self.processed_config['path']}/{self.processed_config['processed_file']}"
        self.scraped_file = f"{self.out_config['path']}/{self.out_config['new_scrape_file']}"
    
    def process_scraped(self):
        scraped_jobs = self.get_scraped_jobs()
        if (exists(self.processed_file) and not exists(self.newly_retrieved_file)):
            processed_jobs = self.get_processed_jobs()
            print('diffing with processed jobs file')
        else:
            print('diffing with main jobs file')
            processed_jobs = self.get_main_jobs()
            print('writing scraped jobs to processed jobs file')
            self.write_processed_jobs(scraped_jobs)
        self.diff_jobs(scraped_jobs, processed_jobs)

    def diff_jobs(self, scraped_jobs, jobs_to_diff):
        newly_scraped_jobs = []
        for job in scraped_jobs:
            match = False
            for existing_job in jobs_to_diff:
                if job['year'] == existing_job['year'] and job['headline'] == existing_job['headline'] and job['original_field'] == existing_job['original_field'] and job['text']:
                    match = True
            if not match:
                newly_scraped_jobs.append(job)
        if len(newly_scraped_jobs) > 0:
            self.write_new_jobs(newly_scraped_jobs)
        else:
            print('No new jobs found')
        
    def get_scraped_jobs(self):
        with open(self.scraped_file, mode='r', encoding='utf-8-sig') as infile:
            return list(csv.DictReader(infile))

    def get_file_to_diff(self):
        processed_jobs = self.get_processed_jobs()
        if (processed_jobs):
            print('diffing with processed jobs file')
            return processed_jobs
        else:
            print('diffing with main jobs file')
            return self.get_main_jobs()

    def get_processed_jobs(self):
        with open(f"{self.processed_file}", mode='r', encoding='utf-8-sig') as infile:
            return list(csv.DictReader(infile))

    
    def get_main_jobs(self):
        with open(self.main_file, mode='r', encoding='utf-8-sig') as infile:
            return list(csv.DictReader(infile))

    def write_new_jobs(self, data):
        path = self.newly_retrieved_file
        self.write_file(path, data)

    def write_processed_jobs(self, data):
        path = self.processed_file
        self.write_file(path, data)

    def write_file(self, path, data):
        keys = data[0].keys() 
        with open(f"{path}", 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, keys)
            writer.writeheader()
            writer.writerows(data)
