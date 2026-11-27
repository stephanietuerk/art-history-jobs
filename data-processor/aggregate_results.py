import os

from modules.aggregate import AggregationHandler


def handler(event, context):
    aggregation_handler = AggregationHandler()
    aggregation_handler.aggregate_main_jobs()
    aggregation_handler.aggregate_main_jobs_by_school()

if __name__ == '__main__':
    handler(None, None)
