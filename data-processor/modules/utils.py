import os
import unicodedata

import bs4
import yaml


def get_project_root():
    this_file_path = os.path.abspath(__file__)
    # Go up 2 directories from this file
    project_dir = os.path.dirname(this_file_path)
    project_dir = os.path.dirname(project_dir)
    return project_dir

def load_base_config(file_path_name='config.yml'):
    project_dir = get_project_root()
    config_file = os.path.join(project_dir, file_path_name)
    with open(config_file, 'r') as stream:
        base_config = yaml.safe_load(stream)
    return base_config

def get_sections_for_tag(html, tag):
    sections = html.split(f'<{tag}>')
    sections = [f'<{tag}>' + section for section in sections][1:]
    return sections

def get_selection_from_content(content, selector):
    soup = bs4.BeautifulSoup(content, 'html.parser')
    return soup.select(selector)

