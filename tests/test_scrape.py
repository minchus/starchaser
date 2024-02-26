from scrape.scrape import Scraper
from scrape.grade_poll import get_poll_grade


def test_scrape():
    s = Scraper()
    poll_data = s.scrape_grade_poll('https://www.ukclimbing.com/logbook/crags/las_encantadas-2485/redders-112975',
                                    refresh=False)
    poll_grade_text, poll_grade_code, score_modifier = get_poll_grade(poll_data)
    assert True