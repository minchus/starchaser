import pandas as pd
import streamlit as st

from streamlit_gsheets import GSheetsConnection


def get_climb_data():
    if 'df' not in st.session_state:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read()
        st.session_state.df = df
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

