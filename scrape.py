import numpy as np
import pandas as pd
import re
import requests_cache
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin

BASE_URL = 'https://www.ukclimbing.com/'


session = requests_cache.CachedSession('ukc-cache', backend='filesystem')
response = session.get(urljoin(BASE_URL, '/logbook/books/dorset-2348'))

dfs = pd.read_html(response.content, extract_links="all")

df_crag = pd.DataFrame(np.vstack(dfs), columns=dfs[0].columns)
df_crag.columns = ['crag', 'nclimbs', 'rocktype', 'aspect']
df_crag['name'] = df_crag['crag'].apply(pd.Series)[0]
df_crag['url'] = df_crag['crag'].apply(pd.Series)[1]
df_crag['nclimbs'] = df_crag['nclimbs'].apply(pd.Series)[0]
df_crag['rocktype'] = df_crag['rocktype'].apply(pd.Series)[0]
df_crag['aspect'] = df_crag['aspect'].apply(pd.Series)[0]
df_crag = df_crag[['name', 'nclimbs', 'rocktype', 'aspect', 'url']]

print("got here")
