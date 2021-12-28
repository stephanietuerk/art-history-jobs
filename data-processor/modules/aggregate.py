import csv

import pandas as pd

from modules.config import Config


class AggregationHandler():
    def __init__(self):
        config = Config()
        self.main_config = config.get_main_config()
        self.scraping_config = config.get_scraping_config()
        self.main_file = f"{self.main_config['path']}/{self.main_config['main_file']}"
        self.aggregated_file = f"{self.main_config['path']}/{self.main_config['aggregated_file']}"
    
    def aggregate_main_jobs(self):
        sig_figs = 2
        headers = ['year', 'field', 'is_tt', 'rank', 'count']
        aggregated = []
        main_jobs = self.get_main_jobs()
        main = pd.DataFrame(main_jobs)
        main = main[headers]
        main['count'] = main['count'].astype(float)
        year_options = [str(i) for i in self.scraping_config['years']]
        field_options = list(main['field'].unique())
        is_tt_options = list(main['is_tt'].unique())
        rank_options = list(main['rank'].unique())
        data_by_years = main.groupby(['year'])
        for year in year_options:
            year_count = 0
            year_has_data = year in data_by_years.groups
            if year_has_data:
                year_group = data_by_years.get_group(year)  
                year_count = year_group['count'].sum().round(sig_figs)
                data_by_fields = year_group.groupby(['field'])
            year_row = [year, 'all', 'all', 'all', year_count]
            aggregated.append(year_row)
            for field in field_options:
                field_count = 0
                field_has_data = field in data_by_fields.groups
                if year_has_data and field_has_data:
                    field_group = data_by_fields.get_group(field)
                    field_count = field_group['count'].sum().round(sig_figs)
                    data_by_is_tt = field_group.groupby(['is_tt'])
                field_row = [year, field, 'all', 'all', field_count]
                aggregated.append(field_row)
                for is_tt in is_tt_options:
                    is_tt_count = 0
                    is_tt_has_data = is_tt in data_by_is_tt.groups
                    if year_has_data and field_has_data and is_tt_has_data:
                        is_tt_group = data_by_is_tt.get_group(is_tt)
                        is_tt_count = is_tt_group['count'].sum().round(sig_figs)
                        data_by_ranks = is_tt_group.groupby(['rank'])
                    is_tt_row = [year, field, is_tt, 'all', is_tt_count]
                    aggregated.append(is_tt_row)
                    for rank in rank_options:
                        rank_count = 0
                        rank_has_data = rank in data_by_ranks.groups
                        if year_has_data and field_has_data and is_tt_has_data and rank_has_data:
                            rank_group = data_by_ranks.get_group(rank)
                            rank_count = rank_group['count'].sum().round(sig_figs)
                        rank_row = [year, field, is_tt, rank, rank_count]
                        aggregated.append(rank_row)

        # print(pd.DataFrame(aggregated, columns=headers).head(100))
        self.write_df_to_csv(pd.DataFrame(aggregated, columns=headers), self.aggregated_file)

    def get_main_jobs(self):
        with open(self.main_file, mode='r', encoding='utf-8-sig') as infile:
            return list(csv.DictReader(infile))

    def write_df_to_csv(self, df, file_path):
        df.to_csv(file_path, index=False, encoding='utf-8')
