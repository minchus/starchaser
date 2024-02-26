from starchaser.utils import poll_grade_sort_key


def test_poll_grade_sort_key():

    grade_list = [
        'High 7a+',
        'Low 7a',
        'Low 7a+',
        'Mid 7a',
        'Mid 7a+',
        'High 7a',
        'project',
        'Mid 5b',
    ]

    sorted_grades = sorted(grade_list, key=poll_grade_sort_key)

    assert sorted_grades == [
        'Mid 5b',
        'Low 7a',
        'Mid 7a',
        'High 7a',
        'Low 7a+',
        'Mid 7a+',
        'High 7a+',
        'project'
    ]
