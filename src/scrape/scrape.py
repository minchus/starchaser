import json
import logging
import numpy as np
import os
import pandas as pd
import re
import warnings

from bs4 import BeautifulSoup as bs, MarkupResemblesLocatorWarning
from io import StringIO
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit
from requests import Session
from requests_cache import CacheMixin
from requests_ratelimiter import LimiterMixin

from scrape.grade_poll import get_poll_grade

# import scrape.block_network  # Uncomment to test caching
# from line_profiler_pycharm import profile  # Uncomment to use profiling


logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)


class CachedLimiterSession(CacheMixin, LimiterMixin, Session):
    pass


def get_base_url(url):
    url_parts = urlsplit(url)
    return urlunsplit((url_parts.scheme, url_parts.netloc, '', '', ''))


class Scraper:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)

        self.session = CachedLimiterSession(
            cache_name=os.path.join(self.data_dir, 'ukc-cache'),
            per_second=5,
            backend='filesystem'
        )

    def scrape_guidebook_and_contents(self, guidebook_url: str, refresh: bool = False) -> list[dict]:
        """

        :param guidebook_url:
        :param refresh: Force refresh of the cache
        :return: A list of dict, each dict is info for a crag
        """

        logger.info(f'Scraping guidebook {guidebook_url}')
        crag_list = self.scrape_guidebook(guidebook_url, refresh)

        for n_crag, crag in enumerate(crag_list, start=1):
            logger.info(f'Scraping crag {n_crag}/{len(crag_list)} {crag["url"]}')
            crag_data = self.scrape_crag(crag['url'], refresh)
            crag.update(crag_data)

        # Sport climbing only
        for crag in crag_list:
            crag['climbs'] = list(filter(lambda x: x['gradetype'] == 3, crag['climbs']))

        # crag_list = crag_list[0:1]  # Uncomment for testing (scrape only first crag)
        total_climbs = sum(len(crag['climbs']) for crag in crag_list)
        total_done = 0.0

        for n_crag, crag in enumerate(crag_list, start=1):
            for n_climb, climb in enumerate(crag['climbs']):
                total_done += 1
                climb_url = urljoin(crag['url'], climb['slug'])
                climb['url'] = climb_url
                logger.info(f'{total_done * 100 / total_climbs:.1f}% - Scraping climb {n_climb}/{len(crag["climbs"])}, '
                            f'crag {n_crag}/{len(crag_list)} {climb_url}')

                if poll_data := self.scrape_grade_poll(climb_url, refresh):
                    grade_dict = crag['grade_list'][str(climb['gradetype'])]
                    guidebook_grade_score = grade_dict[str(climb['grade'])]['score']
                    poll_grade_text, poll_grade_code, score_modifier = get_poll_grade(poll_data)
                    climb['poll_grade_text'] = poll_grade_text

                    if poll_grade_code in grade_dict:
                        climb['poll_diff'] = guidebook_grade_score - (grade_dict[poll_grade_code]['score'] + score_modifier)
                    else:
                        climb['poll_diff'] = -0.01
                else:
                    climb['poll_grade_text'] = "Bad poll data"
                    climb['poll_diff'] = -0.01

        return crag_list

    def scrape_guidebook(self, guidebook_url: str, refresh: bool) -> list[dict]:
        """Return a list of dict, where each dict is crag info"""
        response = self.session.get(guidebook_url, refresh=refresh)
        base_url = get_base_url(guidebook_url)

        df_scraped_tables = pd.read_html(StringIO(response.text), extract_links='all')

        # El-chorro guidebook has an initial table that we're not interested in
        if 'chorro' in guidebook_url:
            df_scraped_tables = df_scraped_tables[1:]

        df_crags = pd.DataFrame(np.vstack(df_scraped_tables), columns=df_scraped_tables[0].columns)
        df_crags.columns = ['crag', 'nclimbs', 'rocktype', 'aspect']

        # read_html extract_links makes each cell a tuple (link_text, link_path)
        # Extract the elements of the tuple into separate columns
        df_crags['name'] = df_crags['crag'].apply(pd.Series)[0]
        df_crags['url'] = base_url + df_crags['crag'].apply(pd.Series)[1] + "/"

        # The crag table may contain title rows that we are not interested in
        n_crags_before = len(df_crags.index)
        df_crags = df_crags.dropna()
        n_rows_with_nan = abs(n_crags_before - len(df_crags.index))
        if n_rows_with_nan:
            logging.warning(f'{n_rows_with_nan} guidebook crag rows contained NaN and were dropped')

        df_crags['nclimbs'] = df_crags['nclimbs'].apply(pd.Series)[0].apply(int)
        df_crags['rocktype'] = df_crags['rocktype'].apply(pd.Series)[0]
        df_crags['aspect'] = df_crags['aspect'].apply(pd.Series)[0]
        df_crags['id'] = df_crags.url.str.extract('(\d+)')
        df_crags['id'] = df_crags.id.apply(int)
        df_crags = df_crags[['name', 'nclimbs', 'rocktype', 'aspect', 'url', 'id']]

        crag_list = df_crags.to_dict(orient='records')
        return crag_list

    def scrape_crag(self, crag_url: str, refresh: bool) -> dict:
        """
        Return a dict containing crag data
        The crag data is contained in javascript variables in <script> section
        """

        response = self.session.get(crag_url, refresh=refresh)
        soup = bs(response.content, 'lxml')
        script = [x for x in soup.find_all('script') if 'cragId' in x.text][0]

        crag = {
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
                if key in crag.keys():
                    crag[key] = json.loads(value)

        crag['climbs'] = crag.pop('table_data')
        return crag

    def scrape_grade_poll(self, climb_url: str, refresh: bool) -> dict:
        response = self.session.get(climb_url, refresh=refresh)

        # Get grade poll vote count - we assume that find_all preserves order
        poll_data = dict()
        soup = bs(response.content, 'html.parser')
        poll_divs = soup.find_all('div', {'class': 'progress-bar bg-success polltype1 progress-bar-striped'})
        for div in poll_divs:
            poll_data[div.attrs['data-val']] = int(div.attrs['data-n'])

        # Get grade poll grade names
        grade_name_list = []
        poll_grade_name_divs = soup.find_all('div', {'class': 'col-4 small text-right'})
        for div in poll_grade_name_divs:
            grade_name = div.text.strip()
            if grade_name:
                grade_name_list.append(grade_name)

        if len(poll_data) != len(grade_name_list):
            return None

        # Return a dict { '37hard,High 6b+': 0, ... }
        ret = {f"{grade_code},{grade_name}": votes for (grade_code, votes), grade_name in
               zip(poll_data.items(), grade_name_list)}
        return ret

    def write_climbs_csv(self, crag_list: list[dict], out_file: str) -> None:
        # Flatten data and extract fields of interest

        list_of_climbs = list()
        for crag in crag_list:
            for climb in crag['climbs']:

                c = dict()
                c['name'] = climb['name']
                c['url'] = climb['url']
                # Convert grade to text e.g. 36 (int) => 6a (str)
                c['grade'] = crag['grade_list'][str(climb['gradetype'])][str(climb['grade'])]['name']
                c['stars'] = climb['stars']
                c['logs'] = climb['logs']
                c['poll_grade'] = climb['poll_grade_text']
                c['poll_diff'] = climb['poll_diff']
                c['crag'] = crag['name']

                # Sometimes there is no buttress data
                buttress_id_str = str(climb['buttress_id'])
                if buttress_id_str in crag['buttress_data']:
                    c['buttress'] = crag['buttress_data'][buttress_id_str]['name']

                c['desc'] = (bs(climb['desc'], 'lxml').get_text()
                             .removeprefix('Rockfax Description')
                             .removeprefix('UKClimbing Description'))
                c['symbols'] = ', '.join([crag['climb_symbols'][str(s)]['name'] for s in climb['symbols']
                                          if str(s) in crag['climb_symbols']])

                c['approach_time'] = 0
                if buttress_id_str in crag['buttress_data']:
                    if 'approach_time' in crag['buttress_data'][buttress_id_str]['meta']:
                        c['approach_time'] = crag['buttress_data'][buttress_id_str]['meta']['approach_time']

                c['rocktype'] = crag['rocktype']
                c['aspect'] = crag['aspect']

                list_of_climbs.append(c)

        df_climbs = pd.DataFrame(list_of_climbs)
        out_path = os.path.join(self.data_dir, out_file)
        df_climbs.to_csv(out_path, index=False)
        logging.info(f'CSV written to {out_path}')


