import json
import logging
import numpy as np
import pandas as pd
import re
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
from requests import Session
from requests_cache import CacheMixin
from requests_ratelimiter import LimiterMixin

BASE_URL = 'https://www.ukclimbing.com/'
logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s [%(filename)s:%(lineno)d] %(levelname)-8s %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO)


# Test if cache is being used by blocking network
# import socket
# class BlockNetwork(socket.socket):
#     def __init__(self, *args, **kwargs):
#         raise Exception('Network call blocked')
# socket.socket = BlockNetwork

class CachedLimiterSession(CacheMixin, LimiterMixin, Session):
    pass


session = CachedLimiterSession(
    'ukc-cache',
    per_second=5,
    backend='filesystem'
)

# Scrape guidebook
url = urljoin(BASE_URL, '/logbook/books/dorset-2348')
logger.info(f'Scraping guidebook {url}')
response = session.get(url)

df_scraped_tables = pd.read_html(response.text, extract_links='all')
df_crags = pd.DataFrame(np.vstack(df_scraped_tables), columns=df_scraped_tables[0].columns)
df_crags.columns = ['crag', 'nclimbs', 'rocktype', 'aspect']

# read_html extract_links makes each element a tuple - expand to columns
df_crags['name'] = df_crags['crag'].apply(pd.Series)[0]
df_crags['path'] = df_crags['crag'].apply(pd.Series)[1]
df_crags['nclimbs'] = df_crags['nclimbs'].apply(pd.Series)[0]
df_crags['rocktype'] = df_crags['rocktype'].apply(pd.Series)[0]
df_crags['aspect'] = df_crags['aspect'].apply(pd.Series)[0]
df_crags['crag_id'] = df_crags.path.str.split('-', expand=True)[1]
df_crags = df_crags[['name', 'nclimbs', 'rocktype', 'aspect', 'path', 'crag_id']]

# Scrape crags data from javascript variables in script tag
crag_data_by_id = dict()
for crag in df_crags.to_dict(orient='records'):
    url = urljoin(BASE_URL, crag['path'])

    logger.info(f'Scraping crag {url}')
    response = session.get(url)
    soup = bs(response.content, 'html.parser')
    script = [x for x in soup.find_all('script') if 'cragId' in x.text][0]

    crag_data = {
        'info': crag,
        'cragId': None,
        'table_data': None,
        'grade_type_list': None,
        'grade_list': None,
        'buttress_data': None,
        'climb_symbols': None,
        'buttress_symbols': None
    }
    lines = script.text.strip().lstrip('let').rstrip(';').splitlines()
    for line in lines:
        ret = re.match(r'^([^=]*)=(.*)', line.lstrip().rstrip(','))
        if ret:
            key = ret.group(1).strip()
            value = ret.group(2).strip()
            if key in crag_data.keys():
                crag_data[key] = json.loads(value)
    crag_data_by_id[crag_data['cragId']] = crag_data


def get_consensus_grade(climb_local):
    sum_of_scores = 0
    total_votes = 0
    guidebook_index = None
    for index, (poll_grade, vote_count_str) in enumerate(climb_local['grade_poll'].items()):
        sum_of_scores += index * int(vote_count_str)
        total_votes += int(vote_count_str)
        text_grade = climb_local['poll_grade_name_list'][index]
        if 'Mid' in text_grade and climb_local['grade'] in text_grade:
            guidebook_index = index

    if total_votes == 0:
        return 'No votes', 0.0, 0

    index = round(sum_of_scores / total_votes)
    diff = 0 if guidebook_index is None else guidebook_index - sum_of_scores / total_votes
    consensus_grade = climb_local['poll_grade_name_list'][index]
    return consensus_grade, diff, total_votes


# Scrape climbs
# NOTE: all keys are strings in crag_data
list_of_climbs = list()
ncrag = 0
for crag_id, crag_data in crag_data_by_id.items():
    ncrag += 1
    nclimb = 0
    for climb in crag_data['table_data']:
        nclimb += 1
        url = urljoin(BASE_URL, crag_data['info']['path'] + '/' + climb['slug'])
        climb['url'] = url
        logger.info(f'Scraping climb {nclimb}/{len(crag_data["table_data"])}'
                    f' crag {ncrag}/{len(crag_data_by_id.items())} {url}')
        response = session.get(url)

        # Get grade as text
        climb['grade'] = crag_data['grade_list'][str(climb['gradetype'])][str(climb['grade'])]['name']

        # Get grade poll vote count - we assume that find_all preserves order
        climb['grade_poll'] = dict()
        soup = bs(response.content, 'html.parser')
        poll_divs = soup.find_all('div', {'class': 'progress-bar bg-success polltype1 progress-bar-striped'})
        for div in poll_divs:
            climb['grade_poll'][div.attrs['data-val']] = div.attrs['data-n']

        # Get grade poll grade names
        poll_grade_name_list = []
        poll_grade_name_divs = soup.find_all('div', {'class': 'col-4 small text-right'})
        for div in poll_grade_name_divs:
            poll_grade_name = div.text.strip()
            if poll_grade_name:
                poll_grade_name_list.append(poll_grade_name)
        climb['poll_grade_name_list'] = poll_grade_name_list

        # Convert grade poll to consensus grade
        climb['consensus_grade'], climb['consensus_diff'], climb['nvotes'] = get_consensus_grade(climb)

        # Flatten
        climb['crag'] = crag_data['info']['name']
        climb['buttress'] = crag_data['buttress_data'][str(climb['buttress_id'])]['name']

        buttress_meta = crag_data['buttress_data'][str(climb['buttress_id'])]['meta']
        if buttress_meta and 'approach_time' in buttress_meta:
            climb['approach_time'] = crag_data['buttress_data'][str(climb['buttress_id'])]['meta']['approach_time']
        else:
            climb['approach_time'] = 0
        climb['rocktype'] = crag_data['info']['rocktype']
        climb['aspect'] = crag_data['info']['aspect']
        climb['symbols'] = ', '.join([crag_data['climb_symbols'][str(s)]['name'] for s in climb['symbols']
                                      if str(s) in crag_data['climb_symbols']])
        climb['desc'] = bs(climb['desc'], 'html.parser').get_text().replace('Description', 'Description: ')

        for key in [
            'buttress_id',
            'buttress_ordering',
            'climb_ordering',
            'ok',
            'rockfax',
            'gradesystem',
            'slug',
            'has_topo',
            'rf_crag',
            'n_photos',
            'n_videos',
            'grade_poll',
            'poll_grade_name_list'
        ]:
            climb.pop(key, None)

        list_of_climbs.append(climb)

df_climbs = pd.DataFrame(list_of_climbs)
df_climbs.to_csv('climbs.csv')
