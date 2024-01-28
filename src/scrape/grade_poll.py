def get_poll_grade(poll_data):
    """
       poll_data: {
           '37hard,High 6b+': 0,  # index=1
           '37,Mid 6b+':      1,  # index=2
           '37easy,Low 6b+':  0,  # index=3
           '36hard,High 6b':  0,  # index=4
           '36,Mid 6b':       3,  # index=5
           '36easy,Low 6b':   1,  # index=6
           '35hard,High 6a+': 1,  # index=7
           '35,Mid 6a+':      0,  # index=9
           '35easy,Low 6a+':  0   # index=10
       }

       weighted_mean_index = ( 1*2 + 3*5 + 1*6 + 1*7 )/ ( 1 + 3 + 1 + 1 ) = 5.0
    """
    index_x_votes = 0
    total_votes = 0
    for index, (grade_code, votes) in enumerate(poll_data.items(), start=1):
        index_x_votes += index * votes
        total_votes += votes

    if total_votes == 0:
        return 'No votes', 'No votes', 0.0

    weighted_mean_index = round(index_x_votes / float(total_votes)) - 1  # Subtract one to return to a 0 based index
    poll_grade = list(poll_data.keys())[weighted_mean_index]
    grade_text = poll_grade.split(',')[-1]  # e.g. Mid 6a+
    grade_code_full = poll_grade.split(',')[0]  # e.g. 36easy
    if "easy" in grade_code_full:
        grade_modifier = 0.33
    elif "hard" in grade_code_full:
        grade_modifier = 0.33
    else:
        grade_modifier = 0.00

    grade_code = grade_code_full.removesuffix('easy').removesuffix('hard')  # e.g. 36

    return grade_text, grade_code, grade_modifier
