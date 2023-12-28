import os
from modules import utils

class Config():
    def __init__(self):
        self.base_config = utils.load_base_config()

    def get_base_config(self):
        return self.base_config
    
    def get_out_config(self):
        return self.base_config['OUT_FOLDER']

    def get_main_config(self):
        return self.base_config['MAIN_FOLDER']

    def get_processed_config(self):
        return self.base_config['PROCESSED_FOLDER']

    def get_scraping_config(self):
        return self.base_config['WIKIA']

    def get_parsing_config(self):
        return self.base_config['TEXT_PARSING']
