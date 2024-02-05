# SPDX-FileCopyrightText: 2024-present Ming Chung <73884404+minchus@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
import click
import logging


from starchaser.__about__ import __version__
from starchaser.utils import GuidebookInfo
from scrape.scrape import Scraper


logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s [%(filename)s:%(lineno)d] %(levelname)-8s %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO)


@click.command(context_settings={'help_option_names': ['-h', '--help']})
@click.option('--area', '-a',
              default='dorset', show_default=True,
              type=click.Choice(GuidebookInfo.get_area_names()))
@click.version_option(version=__version__, prog_name="Starchaser Scraper")
def main(area):
    s = Scraper()
    crag_data = s.scrape_guidebook_and_contents(GuidebookInfo.get_url(area))
    out_file = f"{area}.csv"
    s.write_climbs_csv(crag_data, out_file)

