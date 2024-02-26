import pandas as pd
import streamlit as st

from streamlit_gsheets import GSheetsConnection


class GuidebookInfo:
    data = {
        'dorset': {
            'url': 'https://www.ukclimbing.com/logbook/books/dorset-2348/',
            'display_name': 'Dorset'
        },
        'el-chorro': {
            'url': 'https://www.ukclimbing.com/logbook/books/el_chorro-526',
            'display_name': 'El Chorro'
        },
        'kalymnos': {
            'url': 'https://www.ukclimbing.com/logbook/books/kalymnos-1669',
            'display_name': 'Kalymnos'
        }
    }

    @staticmethod
    def get_area_names():
        return list(GuidebookInfo.data.keys())

    @staticmethod
    def get_url(area_name):
        return GuidebookInfo.data[area_name]['url']

    @staticmethod
    def to_display_name(area_name):
        return GuidebookInfo.data[area_name]['display_name']


def get_climb_data(area):
    if 'df' not in st.session_state or area != st.session_state.area:
        conn = st.connection(area, type=GSheetsConnection)
        df = conn.read()
        st.session_state.df = df
        st.session_state.area = area
    return st.session_state.df


def get_logbook_data(logbook_file: str = ''):
    if logbook_file:
        if 'logbook_file' not in st.session_state or logbook_file != st.session_state.logbook_file:
            df_logs = pd.read_csv(logbook_file)
            st.session_state.logbook_file = logbook_file
            st.session_state.df_logs = df_logs

    if 'df_logs' not in st.session_state:
        return None, None

    return st.session_state.df_logs, st.session_state.logbook_file


def poll_grade_sort_key(x):
    tokens = x.split()

    if len(tokens) != 2:  # e.g. 'project' or '?'
        return '9d', '0'

    modifier = tokens[0]
    grade = tokens[1]

    if not grade[0].isdigit():  # e.g. 'No votes'
        return '9d', '0'

    # Low 6a, Mid 6a, High 6a => 6a0, 6a1, 6a2
    m = {
        'Low': '0',
        'Mid': '1',
        'High': '2'
    }
    return grade, m[modifier]
