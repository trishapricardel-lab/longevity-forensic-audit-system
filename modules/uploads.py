import streamlit as st
import os
from modules.audit import log_action


# ============================
# SOI UPLOAD
# ============================

def handle_soi_upload(cursor, conn):

    st.subheader("SOI Source")

    soi_option = st.radio(
        "SOI Data Source",
        ["Use Existing SOI File", "Upload New SOI File"]
    )

    soi_file = None

    if soi_option == "Use Existing SOI File":

        soi_files = os.listdir("data/soi")

        if len(soi_files) > 0:

            selected_soi = st.selectbox("Select SOI File", soi_files)

            soi_file = f"data/soi/{selected_soi}"

        else:
            st.info("No SOI files available in repository.")

    else:

        uploaded_soi = st.file_uploader("Upload SOI CSV", type=["csv"])

        if uploaded_soi is not None:

            path = f"data/soi/{uploaded_soi.name}"

            with open(path, "wb") as f:
                f.write(uploaded_soi.getbuffer())

            st.success("SOI saved to repository")

            log_action(
                cursor,
                conn,
                st.session_state.username,
                "Upload SOI",
                uploaded_soi.name
            )

            soi_file = path

    return soi_file


# ============================
# ORDERS UPLOAD
# ============================

def handle_orders_upload(cursor, conn):

    st.subheader("Longevity Orders Source")

    orders_option = st.radio(
        "Orders Data Source",
        ["Use Existing Orders", "Upload New Orders"]
    )

    orders_file = None

    if orders_option == "Use Existing Orders":

        orders_files = os.listdir("data/orders")

        if len(orders_files) > 0:

            selected_orders = st.selectbox("Select Orders File", orders_files)

            orders_file = f"data/orders/{selected_orders}"

        else:
            st.info("No order files available.")

    else:

        uploaded_orders = st.file_uploader("Upload Orders CSV", type=["csv"])

        if uploaded_orders is not None:

            path = f"data/orders/{uploaded_orders.name}"

            with open(path, "wb") as f:
                f.write(uploaded_orders.getbuffer())

            st.success("Orders saved")

            log_action(
                cursor,
                conn,
                st.session_state.username,
                "Upload Orders",
                uploaded_orders.name
            )

            orders_file = path

    return orders_file


# ============================
# PAYROLL UPLOAD
# ============================

def handle_payroll_upload(cursor, conn):

    st.subheader("Payroll Source")

    payroll_option = st.radio(
        "Payroll Data Source",
        ["Use Existing Payroll Files", "Upload New Payroll Files"]
    )

    payroll_files = []

    if payroll_option == "Use Existing Payroll Files":

        payroll_repo = os.listdir("data/payroll")

        if len(payroll_repo) > 0:

            selected_payroll = st.multiselect(
                "Select Payroll Files",
                payroll_repo
            )

            payroll_files = [f"data/payroll/{f}" for f in selected_payroll]

        else:
            st.info("No payroll files available.")

    else:

        uploaded_payroll = st.file_uploader(
            "Upload Payroll CSV Files",
            type=["csv"],
            accept_multiple_files=True
        )

        if uploaded_payroll:

            for file in uploaded_payroll:

                path = f"data/payroll/{file.name}"

                with open(path, "wb") as f:
                    f.write(file.getbuffer())

                log_action(
                    cursor,
                    conn,
                    st.session_state.username,
                    "Upload Payroll",
                    file.name
                )

                payroll_files.append(path)

            st.success("Payroll files saved to repository")

    return payroll_files
