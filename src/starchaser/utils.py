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


def get_logbook_data(logbook_file: str = ""):
    if logbook_file:
        if 'logbook_file' not in st.session_state or logbook_file != st.session_state.logbook_file:
            df_logs = pd.read_csv(logbook_file)
            st.session_state.logbook_file = logbook_file
            st.session_state.df_logs = df_logs

    if 'df_logs' not in st.session_state:
        return None, None

    return st.session_state.df_logs, st.session_state.logbook_file


def set_common_page_config():
    st.set_page_config(
        page_title="Starchaser - Reach for the stars",
        page_icon="⭐",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Hack to fix tooltip hidden behind chart when in full-screen mode
    # https://discuss.streamlit.io/t/tool-tips-in-fullscreen-mode-for-charts/6800/9
    st.markdown('<style>#vg-tooltip-element{z-index: 1000051}</style>', unsafe_allow_html=True)

