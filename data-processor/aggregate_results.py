import os

from modules.aggregate import AggregationHandler


def handler(event, context):
    aggregation_handler = AggregationHandler()
    aggregation_handler.aggregate_main_jobs()

if __name__ == '__main__':
    handler(None, None)
