import csv
import re
import unicodedata

import bs4
import wikia

from modules import utils
from modules.config import Config


class WikiaHandler():
    def __init__(self):
        config = Config()
        self.scraping_config = config.get_scraping_config()
        self.parsing_config = config.get_parsing_config()
        self.out_path = config.get_out_path()
        self.make_page_names()

    def make_page_names(self):
        years = self.scraping_config['years']
        page_name = self.scraping_config['sub_page']
        names = [f'{page_name} {year}-{year+1}' for year in years]
        names = [x.replace('Art History 2018-2019','Art History 2018-19') for x in names]
        names = [x.replace('Art History 2019-2020','Art History Jobs 2019-20') for x in names]
        names = [x.replace('Art History 2020-2021','Art History 2020-21') for x in names]
        names = [x.replace('Art History 2021-2022','Art History 2021-22') for x in names]
        self.page_names = names

    def create_fields_file(self):
        data = []
        for page_name in self.page_names:
            print(f'Begin processing {page_name}')
            year = self.get_year_from_page_name(page_name)
            html = self.get_html_for_page(page_name)
            sections = utils.get_sections_for_tag(html, 'h2')
            fields_in_page = []
            for section in sections:
                soup = bs4.BeautifulSoup(section, 'html.parser')
                section_title_list = soup.select('h2 .mw-headline')
                if self.is_field_title(section_title_list):
                    field = self.clean_text(section_title_list[0].text)
                    if field not in fields_in_page:
                        fields_in_page.append(field)
                        if len(data) > 0:
                            fields_in_list = []
                            for item in data:
                                fields_in_list.append(item['field'])
                            fields_in_list = set(fields_in_list)
                            if field not in fields_in_list:
                                item = {'field': field, 'years': year}
                                data.append(item)
                            else:
                                for item in data:
                                    if field == item['field']:
                                        item['years'] = item['years'] + ',' + year
                        else:
                            item = {'field': field, 'years': year} 
                            data.append(item)
        self.write_fields_file(data)

    def get_year_from_page_name(self, page_name):
        year_regex = re.compile(r'\d{4,}(?=-)')
        return year_regex.search(page_name).group()

    def get_html_for_page(self, page_name):
        page_content = wikia.page(self.scraping_config['main_wiki'], page_name)
        return page_content.html()

    def get_sections_for_tag(self, html, tag):
        sections = html.split(f'<{tag}>')
        sections = [f'<{tag}>' + section for section in sections][1:]
        return sections

    def write_fields_file(self, data):
        keys = data[0].keys()
        with open(f"{self.out_path}/{self.parsing_config['fields_file']}", 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, keys)
            writer.writeheader()
            writer.writerows(data)

    def is_field_title(self, section_title_list):
        return len(section_title_list) > 0 and not self.section_is_excluded(section_title_list[0].text) and not self.scraping_config['tt_key'] in section_title_list[0].text and not self.scraping_config['non_tt_key'] in section_title_list[0].text

    def create_jobs_file(self):
        self.get_fields_dict()
        data = []
        for page in self.page_names:
            print(f'Begin processing {page}')
            page_data = self.get_page_data(page)
            data.extend(page_data)
        keys = data[0].keys()
        print(keys)
        print(data[0])
        self.weight_jobs(data)
        with open(f"{self.out_path}/{self.parsing_config['jobs_file']}", 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, keys)
            writer.writeheader()
            writer.writerows(data)
    
    def get_fields_dict(self):
        with open(self.parsing_config['fields_dictionary'], mode='r') as infile:
            reader = csv.reader(infile)
            self.fields_dict = {rows[0]:rows[1] for rows in reader}

    def get_page_data(self, page_name):
        html = self.get_html_for_page(page_name)
        self.current_year = self.get_year_from_page_name(page_name)
        if self.page_is_segmented_by_tt_status(html):
            data = self.process_page_segmented_by_tt_status(html)
        else:
            data = self.process_unsegmented_page(html)
        return data

    def page_is_segmented_by_tt_status(self, html):
        soup = bs4.BeautifulSoup(html, 'html.parser')
        return soup.find(id='TENURE_TRACK_JOBS') is not None

    def process_page_segmented_by_tt_status(self, html):
        sections = utils.get_sections_for_tag(html, 'h2')
        jobs = []
        grouped_sections = self.group_sections_by_tt_status(sections)
        for section in grouped_sections['tt']:
            tt_jobs = self.get_jobs_from_field_section(section, True)
            jobs.extend(tt_jobs)
        for section in grouped_sections['non_tt']:
            non_tt_jobs = self.get_jobs_from_field_section(section, False)
            jobs.extend(non_tt_jobs)
        return jobs

    def process_unsegmented_page(self, html):
        sections = utils.get_sections_for_tag(html, 'h2')
        jobs = []
        for section in sections:
            section_title_list = utils.get_selection_from_content(section, 'h2 .mw-headline')
            if len(section_title_list) > 0 and not self.section_is_excluded(section_title_list[0].text):
                data = self.get_jobs_from_field_section(section)
                jobs.extend(data)
        return jobs

    def group_sections_by_tt_status(self, sections):
        tt_sections = []
        non_tt_sections = []
        section_type = None
        for section in sections:
            section_title_list = utils.get_selection_from_content(section, 'h2 .mw-headline')
            if len(section_title_list) > 0 and not self.section_is_excluded(section_title_list[0].text):
                section_title = section_title_list[0].text
                if self.scraping_config['tt_key'] in section_title or self.scraping_config['non_tt_key'] in section_title:
                    if self.scraping_config['tt_key'] in section_title:
                        section_type = 'tt'
                    if self.scraping_config['non_tt_key'] in section_title:
                        section_type = 'non_tt'
                else:
                    if section_type == 'tt':
                        tt_sections.append(section)
                    if section_type == 'non_tt':
                        non_tt_sections.append(section)
        return {'tt': tt_sections, 'non_tt': non_tt_sections}

    def section_is_excluded(self, section_title):
        excluded_sections = self.scraping_config['excluded_sections']
        for excluded_section in excluded_sections:
            if excluded_section in section_title:
                return True
        return False

    def get_jobs_from_field_section(self, html, isTt = None):
        original_field = self.get_field(html)
        normalized_field = self.normalize_field(original_field)
        job_listings = utils.get_sections_for_tag(html, 'h3')
        jobs = []
        if len(job_listings) > 0:
            for job in job_listings:
                title_list = utils.get_selection_from_content(job, 'h3 .mw-headline')
                body = bs4.BeautifulSoup(job, 'html.parser').get_text()
                if self.scraping_config['end_marker'] in body:
                    body = body.split(self.scraping_config['end_marker'])[0]
                if len(title_list) > 0:
                    headline = self.clean_text(title_list[0].get_text())
                    if not 'see also' in headline.lower():
                        body = self.clean_text(body)
                        job_type_keys = self.get_job_type_keys(headline, body)
                        # print('job_type_keys', job_type_keys)
                        if len(job_type_keys) == 0:
                            print('No job type keys found', headline)
                        if original_field is 'Fellowships':
                            isTt = False
                        data = {
                            'year': self.current_year,
                            'field': normalized_field,
                            'original_field': self.clean_text(original_field),
                            'keys': ', '.join(job_type_keys),                           
                            'is_tt': self.get_tenure_status(job_type_keys, isTt),
                            'rank': self.get_rank(job_type_keys),
                            'headline': headline,
                            # 'school': None,
                            # 'department': None,
                            # 'location': self.get_location_from_headline(headline),
                            'text': self.clean_body(body),
                        }
                        jobs.append(data)
        return jobs    
    
    def get_field(self, section):
        field_header = utils.get_selection_from_content(section, 'h2 .mw-headline')
        return self.clean_text(field_header[0].text)

    def normalize_field(self, field):
        return self.fields_dict[field]

    def clean_text(self, text):
        for string in self.parsing_config['strip']:
            if string == '\xa0':
                print(text, string)
            text = text.replace(string, ' ')
            text = unicodedata.normalize('NFKD', text)
        return text

    def clean_body(self, body):
        weird_stuff_regex = r'[][[:cntrl:]]'
        return re.sub(weird_stuff_regex, '', body)

    def get_location_from_headline(self, headline):
        location_regex = re.compile(r'\([^\n)]*[A-Z]{2}\)')
        return location_regex.search(headline).group().replace('(', '').replace(')', '') if location_regex.search(headline) else None
    
    def get_job_type_keys(self, headline, body):
        title_keys = self.get_matching_keys(headline, self.parsing_config['HEADLINE'])
        text_keys = self.get_matching_keys(body, self.parsing_config['BODY'])
        return title_keys + text_keys
    
    def get_tenure_status(self, keys, isTt):
        if isTt == False:
            return False
        elif len(keys) == 0:
            return 'manual'
        elif 'tt' in keys or isTt == True:
            if 'non_tt' in keys or 'vap' in keys or 'lecturer' in keys or 'postdoc' in keys or 'contract' in keys or isTt == False:
                return 'manual'
            else:
                return True
        elif ('tt' not in keys) and ('assistant_prof' in keys or 'associate_prof' in keys or 'full_prof' in keys):
            if ('vap' not in keys and 'lecturer' not in keys and 'postdoc' not in keys and 'contract' not in keys):
                return True
            else: 
                return 'manual'
        elif len(keys) == 1 and 'open_rank' in keys:
            return 'manual'
        else: 
            return False

    def get_rank(self, keys):
        keys = list(set(keys))
        if 'tt' in keys:
            keys.remove('tt')
        if 'non_tt' in keys:
            keys.remove('non_tt')
        return ', '.join(keys)

    def get_matching_keys(self, text, job_type_dict):
        types = []
        for key, value in job_type_dict.items():
            if self.any_in_list_in_text(value, text):
                types.append(key)
        return types

    def any_in_list_in_text(self, list, text):
        match = False
        for word in list:
            if word in text.lower():
                match = True
        return match

    def weight_jobs(self, jobs):
        for job in jobs:
            matches = []
            matches.append(job)
            for job_to_compare in jobs:
                if job_to_compare['year'] == job['year'] and job_to_compare['headline'] == job['headline'] and job_to_compare['text'] == job['text'] and job_to_compare['original_field'] is not job['original_field']:
                    matches.append(job_to_compare)
            if len(matches) > 1:
                print('matches', len(matches))
            job['count'] = 1 / len(matches)
            