import os

from modules.post_scraping import PostScrapingHandler


def handler(event, context):
    post_scraping_handler = PostScrapingHandler()
    post_scraping_handler.process_scraped()

if __name__ == '__main__':
    handler(None, None)
