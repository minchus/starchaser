import json
import logging
import numpy as np
import pandas as pd
import re
import requests_cache
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin

BASE_URL = 'https://www.ukclimbing.com/'
logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s [%(filename)s:%(lineno)d] %(levelname)-8s %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO)


# Scrape guidebook
session = requests_cache.CachedSession('ukc-cache', backend='filesystem')
url = urljoin(BASE_URL, '/logbook/books/dorset-2348')
logger.info(f"Scraping {url}")
response = session.get(url)

dfs = pd.read_html(response.text, extract_links="all")
df_crag = pd.DataFrame(np.vstack(dfs), columns=dfs[0].columns)
df_crag.columns = ['crag', 'nclimbs', 'rocktype', 'aspect']

# read_html extract_links makes each element a tuple - expand to columns
df_crag['name'] = df_crag['crag'].apply(pd.Series)[0]
df_crag['path'] = df_crag['crag'].apply(pd.Series)[1]
df_crag['nclimbs'] = df_crag['nclimbs'].apply(pd.Series)[0]
df_crag['rocktype'] = df_crag['rocktype'].apply(pd.Series)[0]
df_crag['aspect'] = df_crag['aspect'].apply(pd.Series)[0]
df_crag = df_crag[['name', 'nclimbs', 'rocktype', 'aspect', 'path']]

# Scrape crags
for path in df_crag['path']:
    url = urljoin(BASE_URL, path)
    logger.info(f"Scraping {url}")
    response = session.get(url)
    soup = bs(response.content, "html.parser")
    scripts = [x for x in soup.find_all("script") if "cragId" in x.text]

    crag_vars = {}
    crag_keys = ["table_data", "grade_type_list", "grade_list", "buttress_data", "climb_symbols", "butress_symbols"]
    for script in scripts:
        script_lines = script.text.lstrip().rstrip().lstrip("let").rstrip(";").splitlines()
        for line in script_lines:
            ret = re.match(r"^([^=]*)=(.*)", line.lstrip().rstrip(","))
            if ret:
                key = ret.group(1).strip()
                value = ret.group(2).strip()
                if key in crag_keys:
                    crag_vars[key] = json.loads(value)

        print("got here")

