import altair as alt
import streamlit as st

from starchaser.utils import get_climb_data, set_common_page_config, get_logbook_data


set_common_page_config()
st.markdown('''
# Explore Climbs By Grade

This page helps you pick a climb by showing the most popular climbs at each grade along with their star rating and
difficulty.

If you uploaded a logbook file on the "Explore Crags" page, those climbs can be excluded using the checkbox on the left.

:point_right: Hover over the bars to see details about the climb. Clicking on a bar takes you to the relevant UKC page.
''')


def poll_grade_sort_key(x):
    if x == "No votes":
        return "0", "0"

    # Low 6a, Mid 6a, High 6a => 6a0, 6a1, 6a2
    m = {
        'Low': '0',
        'Mid': '1',
        'High': '2'
    }
    x_modifier, x_grade = x.split()
    return x_grade, m[x_modifier]


df = get_climb_data()
crag_list = sorted(df['crag'].unique().tolist())
grade_list = sorted(df['grade'].unique().tolist())


with st.sidebar:
    exclude_climbs = st.checkbox('Exclude climbs in logbook')
    df_logs, f = get_logbook_data()
    if exclude_climbs and df_logs is not None:
        df_matched = df.loc[df['name'].isin(df_logs['Name'])]
        n_matched = len(df_matched.index)
        st.markdown(f'{n_matched} climbs in {f.name} matched and were excluded')
        df = df.loc[~df['name'].isin(df_logs['Name'])]


tabs = st.tabs(grade_list)  # Assume tabs returned in same order as grade_list
for tab, tab_name in zip(tabs, grade_list):
    df_climbs_at_grade = df.loc[df['grade'] == tab_name]
    df_climbs_at_grade = df_climbs_at_grade.sort_values('logs').tail(30)
    poll_grade_sort_order = sorted(df_climbs_at_grade['poll_grade'].unique().tolist(), key=poll_grade_sort_key)

    with (tab):
        c = alt.Chart(
            df_climbs_at_grade
        ).mark_bar(
        ).encode(
            x=alt.X('name:N', sort='-y').title(None),
            y=alt.Y('logs:Q'),
            color='stars:N',
            tooltip=['name:N', 'logs:Q', 'stars:N', 'crag:N', 'desc:N'],
            href='url'
        ).facet(
            column=alt.Column('poll_grade:N', sort=poll_grade_sort_order, title=None),
            title="Top 30 most logged climbs at grade by difficulty"
        ).resolve_scale(
            x='independent'
        )

        c['usermeta'] = {
            "embedOptions": {
                'loader': {'target': '_blank'}
            }
        }

        st.altair_chart(c, use_container_width=True)

