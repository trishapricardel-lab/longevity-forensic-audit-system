import os
import streamlit as st
from modules.audit import log_action


def upload_soi(cursor, conn):

    uploaded_soi = st.file_uploader("Upload SOI CSV", type=["csv"])

    if uploaded_soi is not None:

        path = f"data/soi/{uploaded_soi.name}"

        with open(path, "wb") as f:
            f.write(uploaded_soi.getbuffer())

        log_action(cursor, conn, st.session_state.username, "Upload SOI", uploaded_soi.name)

        st.success("SOI uploaded")

        return path

    return None
