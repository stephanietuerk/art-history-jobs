import csv

from modules.config import Config


class PostScrapingHandler(): 
    def __init__(self):
        config = Config()
        self.out_path = config.get_out_path()
        self.existing_path = config.get_existing_path()
        self.post_scraping_config = config.get_post_scraping_config()

    def diff_scraped_with_existing(self):
        self.get_existing_jobs()
        print(self.existing_jobs[0])
        # scraped_jobs = self.get_scraped_jobs()
        # newly_scraped_jobs = []
        # for job in scraped_jobs:
        #     for existing_job in existing_jobs:
        #         if job['year'] == existing_job['year'] and job['headline'] == existing_job['headline'] and job['original_field'] == existing_job['original_field'] and job['text'] == existing_job['text']:
        #             newly_scraped_jobs.append(job)
        # self.write_out_new_jobs(newly_scraped_jobs)
        
    def get_scraped_jobs(self):
        with open(f"{self.out_path}/{self.post_scraping_config['newly_scraped_file']}", mode='r', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            return {rows[0]:rows[1] for rows in reader}

    def get_existing_jobs(self):
        with open('data/out/jobs_all_years.csv', mode='r', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            self.existing_jobs = {rows[0]:rows[1] for rows in reader}

    def write_out_new_jobs(self, data):
        keys = data[0].keys()
        with open(f"{self.out_path}/{self.post_scraping_config['new_jobs_file']}", 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, keys)
            writer.writeheader()
            writer.writerows(data)
