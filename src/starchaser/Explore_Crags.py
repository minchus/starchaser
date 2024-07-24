import altair as alt
import streamlit as st
import sys

from pathlib import Path

# Add src dir to python path so streamlit can find modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from starchaser.utils import get_climb_data, get_logbook_data, GuidebookInfo, poll_grade_sort_key

st.set_page_config(
    page_title='Starchaser',
    page_icon='⭐',
    layout='wide',
    initial_sidebar_state='expanded'
)

# Hack to fix tooltip hidden behind chart when in full-screen mode
# https://discuss.streamlit.io/t/tool-tips-in-fullscreen-mode-for-charts/6800/9
st.markdown('<style>#vg-tooltip-element{z-index: 1000051}</style>', unsafe_allow_html=True)

st.title('Starchaser')
st.markdown('For the climber obsessed with chasing stars or grades, this page will help you pick a destination.')

st.header('Instructions', divider='gray')
st.markdown('''
Pick an area or crag using the filters on the left. You can also filter by grade (range) or star rating.

#### Upload your UKC logbook file (optional)
You can upload your UKC logbook to exclude climbs that you have already done.

First, download your logbook file from your account on the UKC website.
Go to Logbooks - "My Logbook". Click "Download" above the list of climbs and select DLOG format.

Next, select this file using the box on the left.
You can then include or exclude climbs you have done using the checkbox on the left.
''')

st.header('Explore Crags', divider='gray')

with st.sidebar:
    st.sidebar.markdown('''
    # Sections
    - [Instructions](#instructions)
    - [Explore Crags](#explore-crags)
    - [Explore Climbs by Grade](#explore-climbs-by-grade)
    
    # Options
    ''', unsafe_allow_html=True)

    area = st.selectbox(
        'Select area',
        options=GuidebookInfo.get_area_names(),
        format_func=GuidebookInfo.to_display_name
    )

df = get_climb_data(area)
df_unfiltered = df
total_climbs = len(df.index)
crag_list = sorted(df['crag'].unique().tolist())
grade_list = sorted(df['grade'].unique().tolist())

with st.sidebar:
    selected_crags = st.multiselect(
        'Select crags',
        options=crag_list
    )
    if not selected_crags:
        selected_crags = crag_list

    min_grade, max_grade = st.select_slider(
        'Select grade range',
        options=grade_list,
        value=(min(grade_list), max(grade_list))
    )

    selected_stars = []
    if st.checkbox('No stars', value=True):
        selected_stars.append(0)
    if st.checkbox('⭐', value=True):
        selected_stars.append(1)
    if st.checkbox('⭐⭐', value=True):
        selected_stars.append(2)
    if st.checkbox('⭐⭐⭐', value=True):
        selected_stars.append(3)

    logbook_file = st.file_uploader('Upload UKC logbook (DLOG format)')


df = df.loc[
    (df['crag'].isin(selected_crags)) &
    (df['grade'] >= min_grade) &
    (df['grade'] <= max_grade) &
    (df['stars'].isin(selected_stars))
    ]

exclude_logs = False
with st.sidebar:
    df_logs, f = get_logbook_data(logbook_file)
    if df_logs is None:
        st.markdown('No logbook uploaded')
    else:
        exclude_logs = st.checkbox(f'Exclude climbs in logbook', value=True)
        df_matched = df.loc[df['name'].isin(df_logs['Name'])]
        n_matched = len(df_matched.index)

        if exclude_logs:
            st.markdown(f'{n_matched} climbs in {f.name} matched and were excluded')
            df = df.loc[~df['name'].isin(df_logs['Name'])]
        else:
            st.markdown(f'{n_matched} climbs in {f.name} matched')

    n_climbs = len(df.index)
    if n_climbs:
        st.markdown(f'### {n_climbs} / {total_climbs} climbs selected')
    else:
        st.warning('No climbs found at selected grades and crags')
        st.stop()

st.markdown('''
This chart helps you pick a crag by showing which crag has the most climbs at each grade.

For each grade, the bars are sorted with the biggest on the left.
Hover over the leftmost bar to see which crag has the most climbs for each grade. :point_down: 
''')

c = alt.Chart(
    df,
    title=alt.Title(
        "Number of climbs at each grade by crag",
    )
).mark_bar(
).encode(
    x=alt.X(aggregate='count', type='quantitative').title('number of climbs'),
    y=alt.Y('grade'),
    color=alt.Color('crag:N', legend=alt.Legend(symbolLimit=50)),
    order=alt.Order(
        field='x',  # Sort the segments of the bars by this field
        aggregate='count',
        sort='descending'
    )
).configure_title(
    fontSize=22
)
st.altair_chart(c, use_container_width=True)

st.header('Explore Climbs By Grade', divider='gray')
st.markdown('''

This chart helps you pick a climb by showing the most popular climbs at each grade along with their star rating and
difficulty.

:point_down: Hover over the bars to see details about the climb. Clicking on a bar takes you to the relevant UKC page.
''')

tabs = st.tabs(grade_list)  # Assume tabs returned in same order as grade_list
for tab, tab_name in zip(tabs, grade_list):
    df_climbs_at_grade = df_unfiltered.loc[df_unfiltered['grade'] == tab_name]
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
            title='Top 30 most logged climbs at grade by difficulty'
        ).resolve_scale(
            x='independent'
        )

        c['usermeta'] = {
            'embedOptions': {
                'loader': {'target': '_blank'}
            }
        }

        st.altair_chart(c, use_container_width=True)


st.markdown('''
#### List of selected climbs
These are the climbs selected by the filters on the left.
A poll_diff of 1 means that the guidebook grade is 1 grade higher than the poll grade i.e. the climb is "soft".

:point_down: Click the column headers to sort by that column.

:mag: Click the magnifier in the top right to search.
''')
st.dataframe(df.style.format('link', subset='url'), column_config={'url': st.column_config.LinkColumn()})

if exclude_logs:
    st.markdown('#### Climbs in logbook that were excluded')
    st.dataframe(df_matched)
