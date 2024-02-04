import altair as alt
import streamlit as st

from starchaser.utils import get_climb_data, set_common_page_config, get_logbook_data

set_common_page_config()
st.markdown("# Explore Crags")

df = get_climb_data()
df_filtered = df
crag_list = sorted(df['crag'].unique().tolist())
grade_list = sorted(df['grade'].unique().tolist())

with st.sidebar:
    logbook_file = st.file_uploader('Upload UKC logbook (DLOG format)')

    guidebook = st.selectbox(
        'Select area',
        ['Portland']
    )

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

df_filtered = df_filtered.loc[
    (df['crag'].isin(selected_crags)) &
    (df['grade'] >= min_grade) &
    (df['grade'] <= max_grade) &
    (df['stars'].isin(selected_stars))
    ]

exclude_logs = False
with st.sidebar:
    df_logs, f = get_logbook_data(logbook_file)
    if df_logs is not None:
        df_matched = df_filtered.loc[df['name'].isin(df_logs['Name'])]
        n_matched = len(df_matched.index)
        exclude_logs = st.checkbox(f'Exclude climbs in logbook', value=False)
        if exclude_logs:
            st.markdown(f'{n_matched} climbs in {f.name} matched and were excluded')
            df_filtered = df_filtered.loc[~df['name'].isin(df_logs['Name'])]

    n_climbs = len(df_filtered.index)
    total_climbs = len(df.index)
    if n_climbs:
        st.markdown(f'### {n_climbs} / {total_climbs} climbs selected')
    else:
        st.warning('No climbs found at selected grades and crags')
        st.stop()

st.markdown('''
This page helps you pick a crag by showing which crag has the most climbs at each grade.

#### Upload your UKC logbook file
You can upload your UKC logbook to exclude climbs that you have already done.

First, download your logbook file from your account on the UKC website.
Go to Logbooks - "My Logbook". Click "Download" above the list of climbs and select DLOG format.
Next, select this file using the box on the left.
You can then include or exclude climbs you have done using the checkbox on the left.

#### Find your dream crag
Use the filters on the left to filter by grade or focus on particular crags.

:point_left: Hover over the leftmost bar to see which crag has the most climbs for each grade.
The bars get smaller from left to right.
##
''')

c = alt.Chart(
    df_filtered,
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

st.markdown('''
#### List of selected climbs
These are the climbs selected by the filters on the left.
A poll_diff of 1 means that the guidebook grade is 1 grade higher than the poll grade i.e. the climb is "soft".

:point_up_2: Click the column headers to sort by that column.

:mag: Click the magnifier in the top right to search.
''')
st.dataframe(df_filtered.style.format('link', subset='url'), column_config={'url': st.column_config.LinkColumn()})

if exclude_logs:
    st.markdown('#### Climbs in logbook that were excluded')
    st.dataframe(df_matched)
