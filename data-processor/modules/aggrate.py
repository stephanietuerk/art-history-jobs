import csv
from os.path import exists

from modules.config import Config


class PostScrapingHandler(): 
    def __init__(self):
        config = Config()
