import altair as alt
import streamlit as st
import pandas as pd
import numpy as np

from streamlit_gsheets import GSheetsConnection

st.set_page_config(
    page_title="Starchaser - Reach for the stars",
    page_icon="⭐",
    layout="wide",
    initial_sidebar_state="expanded"
)

conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read()

crag_list = sorted(df['crag'].unique().tolist())
grade_list = sorted(df['grade'].unique().tolist())

with st.sidebar:
    st.markdown('# Explore the climbs')
    guidebook = st.selectbox(
        'Select area',
        ['Portland']
    )

    min_grade, max_grade = st.select_slider(
        'Select grade range',
        options=grade_list,
        value=(min(grade_list), max(grade_list))
    )

    selected_crags = st.multiselect(
        'Select crags',
        options=crag_list
    )
    if not selected_crags:
        selected_crags = crag_list

df_filtered = df.loc[
    (df['crag'].isin(selected_crags)) &
    (df['grade'] >= min_grade) &
    (df['grade'] <= max_grade)
    ]

n_climbs = len(df_filtered.index)
if n_climbs:
    st.markdown(f'#### Number of climbs: {n_climbs}')
else:
    st.warning('No climbs found at selected grades and crags')
    st.stop()


st.markdown('Clicking the column header will sort by that column')
st.markdown('A poll_diff of 1 indicates that the guidebook grade is 1 grade higher than the poll results '
            'i.e. the climb is "soft"')
st.dataframe(df_filtered)
st.markdown('#')

c = (
    alt.Chart(
        df_filtered,
        title=alt.Title(
            "Climbs by grade at crag",
            subtitle="Hover over bars for crag info (largest bar on left)"
        )
    )
    .mark_bar()
    .encode(
        x=alt.X(aggregate='count', type='quantitative').title('number of climbs'),
        y=alt.Y('grade'),
        color=alt.Color('crag:N', legend=alt.Legend(symbolLimit=50)),
        order=alt.Order(
            field='x',  # Sort the segments of the bars by this field
            aggregate='count',
            sort='descending'
        )
    )
    .configure_title(fontSize=22)
)

st.altair_chart(c, use_container_width=True)
