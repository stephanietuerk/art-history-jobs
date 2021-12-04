import os

from modules import utils


class Config():
    def __init__(self):
        self.base_config = utils.load_base_config()

    def get_base_config(self):
        return self.base_config
    
    def get_out_path(self):
        return self.base_config['OUT_FOLDER']

    def get_scraping_config(self):
        return self.base_config['WIKIA']

    def get_parsing_config(self):
        return self.base_config['TEXT_PARSING']

    def get_existing_path(self):
        return self.base_config['EXISTING_FOLDER']

    def get_post_scraping_config(self):
        return self.base_config['POST_SCRAPING']
