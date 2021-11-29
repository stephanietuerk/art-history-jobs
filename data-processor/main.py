import os

from modules.wikia_handler import WikiaHandler


def handler(event, context):
    wikia_handler = WikiaHandler()
    wikia_handler.create_jobs_file()

if __name__ == '__main__':
    handler(None, None)
