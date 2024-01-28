# SPDX-FileCopyrightText: 2024-present Ming Chung <73884404+minchus@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
import click
import logging

from starchaser.__about__ import __version__
from scrape.scrape import scrape_guidebook, write_climbs_csv


logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s [%(filename)s:%(lineno)d] %(levelname)-8s %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO)


@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.version_option(version=__version__, prog_name="Starchaser Scraper")
def do_scrape():
    guidebook_url = 'https://www.ukclimbing.com/logbook/books/dorset-2348/'
    crag_list = scrape_guidebook(guidebook_url)
    write_climbs_csv(crag_list, out_path='./data/climbs.csv')

