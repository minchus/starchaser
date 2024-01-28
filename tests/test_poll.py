from scrape.grade_poll import get_poll_grade
from math import isclose


def test_get_poll_grade():
    poll_data = {
        '37hard,High 6b+': 0,
        '37,Mid 6b+': 1,
        '37easy,Low 6b+': 0,
        '36hard,High 6b': 0,
        '36,Mid 6b': 3,
        '36easy,Low 6b': 1,
        '35hard,High 6a+': 1,
        '35,Mid 6a+': 0,
        '35easy,Low 6a+': 0
    }

    grade_text, grade_code, score_modifier = get_poll_grade(poll_data)
    assert grade_text == 'Mid 6b'
    assert grade_code == '36'
    assert isclose(score_modifier, 0.0, abs_tol=1e-6)


def test_get_poll_grade_no_votes():
    poll_data = {
        '37hard,High 6b+': 0,
        '37,Mid 6b+': 0,
        '37easy,Low 6b+': 0,
        '36hard,High 6b': 0,
    }

    grade_text, grade_code, score_modifier = get_poll_grade(poll_data)
    assert grade_text == 'No votes'
    assert grade_code == 'No votes'
    assert isclose(score_modifier, 0.0, abs_tol=1e-6)
