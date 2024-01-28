# SPDX-FileCopyrightText: 2024-present Ming Chung <73884404+minchus@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
import click
import logging


from starchaser.__about__ import __version__
from scrape.scrape import Scraper


logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s [%(filename)s:%(lineno)d] %(levelname)-8s %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO)


@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.version_option(version=__version__, prog_name="Starchaser Scraper")
def do_scrape():
    s = Scraper()
    guidebook_url = 'https://www.ukclimbing.com/logbook/books/dorset-2348/'
    crag_data = s.scrape_guidebook_and_contents(guidebook_url)
    s.write_climbs_csv(crag_data)

