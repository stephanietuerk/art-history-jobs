This is a simple data processor designed to grab and parse data from Academic Jobs Wiki pages on Wikia.

to run locally:
cd data-processor

then  
_to scrape data from the wiki:_  
pipenv run python main.py

_to diff a new scrape with an existing list of jobs:_  
pipenv run python process_scrape.py

_to get a list of fields in the scrape with years they appear:_  
pipenv run python fields.py

_to aggregate the list of jobs:_  
pipenv run python aggregate.py

### Proposed workflow

`data/main/main_data.csv` is the working and long-term archive of processed and manually-validated jobs. It should never be (over)written programatically.

To update `main_data.csv`:

1. Scrape data from Wiki with `pipenv run python main.py`
    - This will create or update `data/out/jobs_all_years.csv` with the results of the scrape.
2. Get newly added jobs with `pipenv run python process_scrape.py`
    - This will diff `data/out/jobs_all_years.csv` with an existing, processed file of jobs.
    - Jobs not in the existing processed file will be written to `data/out/newly_scraped_jobs.csv`
    - At the end of the script, `jobs_all_years.csv` will be duplicated as `data/processed/processed_scraped_jobs.csv`.
    - If there are no new jobs, no file will be written and a message will appear that no new jobs were found.
    - When `newly_scraped_jobs.csv` does not exist, this will serve as a log of unedited/uncorrected jobs which have validated entries in `main_data.csv`.
3. Manually inspect `newly_scraped_jobs` and validate / correct `field` property.
4. Manually add corrected new jobs to `main_data.csv`
5. Delete `newly_scraped_jobs`.
    - Deleting will allow the script to compare the new scrape (`jobs_all_years.csv`) to unedited jobs (`processed_scraped_jobs.csv`) next time the `process_scrape.py` script is run.
    - Otherwise `process_scrape.py` will diff against `main_data.csv` and jobs that have been manually edited will show up in `newly_scraped_jobs.csv`. (This isn't the end of the world, they will just have to be manually ignored.)
