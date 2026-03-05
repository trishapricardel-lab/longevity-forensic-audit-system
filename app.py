import streamlit as st
import pandas as pd
import os

from modules.auth import login
from modules.database import connect_db, create_tables
from modules.file_manager import create_directories
from modules.audit import log_action
from modules.admin_panel import admin_controls

from modules.uploads import (
    handle_soi_upload,
    handle_orders_upload,
    handle_payroll_upload
)

from modules.processing import (
    load_soi,
    load_payroll,
    merge_datasets,
    compute_longevity,
    create_summary
)

from modules.dashboards import (
    command_dashboard,
    rank_summary,
    organizational_summary,
    investigation_panel,
    irregularity_summary,
    financial_impact_panel
)

from modules.irregularity_engine import detect_mismatch
from modules.case_tracker import generate_cases
from modules.recommendation_engine import recommend_action
from modules.timeline_analyzer import build_timeline


# ============================
# LOGIN
# ============================

login()

# ============================
# PAGE CONFIG
# ============================

st.set_page_config(
    page_title="Integrated Longevity Audit System",
    layout="wide"
)

# ============================
# SYSTEM SETUP
# ============================

create_directories()

conn, cursor = connect_db()
create_tables(cursor, conn)

# ============================
# SYSTEM HEADER
# ============================

st.title("🛡️ Integrated Longevity Audit System")
st.caption("Personnel–Finance Validation Engine | Philippine Army Financial Audit Tool")

st.markdown("---")

# ============================
# SIDEBAR USER PANEL
# ============================

st.sidebar.header("User Session")

st.sidebar.write("User:", st.session_state.username)
st.sidebar.write("Role:", st.session_state.role)

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

# ============================
# ADMIN PANEL
# ============================

admin_controls(cursor, conn)

# ============================
# FILE UPLOAD SECTION
# ============================

st.header("📤 Upload Required Files")

soi_file = handle_soi_upload(cursor, conn)

orders_file = handle_orders_upload(cursor, conn)

payroll_files = handle_payroll_upload(cursor, conn)

# ============================
# INITIALIZE VARIABLES
# ============================

summary_df = None
merged_df = None
soi_df = None
orders_df = None
cases_df = None

# ============================
# LOAD ORDERS FROM REPOSITORY
# ============================

orders_files = os.listdir("data/orders")

orders_list = []

for file in orders_files:

    path = f"data/orders/{file}"

    df = pd.read_csv(path)

    df.columns = df.columns.str.strip()

    orders_list.append(df)

if len(orders_list) > 0:
    orders_df = pd.concat(orders_list, ignore_index=True)

# ============================
# PROCESSING
# ============================

if soi_file is not None and payroll_files:

    try:

        soi_df = load_soi()

        payroll_df = load_payroll()

        if soi_df is None:
            st.error("No SOI file available.")
            st.stop()

        if payroll_df is None:
            st.error("No payroll files uploaded.")
            st.stop()

        merged_df = merge_datasets(soi_df, payroll_df)

        merged_df = compute_longevity(merged_df)

        summary_df = create_summary(merged_df)

        # ============================
        # IRREGULARITY ENGINE
        # ============================

        mismatch_df = detect_mismatch(merged_df)

        cases_df = generate_cases(mismatch_df)

    except Exception as e:

        st.error(f"Processing Error: {e}")

# ============================
# DASHBOARDS
# ============================

if cases_df is not None:

    st.header("📁 Case Tracking")

    st.dataframe(cases_df)

# ----------------------------

if merged_df is not None:

    irregularity_summary(merged_df, soi_df, orders_df)

# ----------------------------

if summary_df is not None:

    financial_impact_panel(summary_df)

# ----------------------------

if summary_df is not None:

    command_dashboard(summary_df)

# ----------------------------

if merged_df is not None:

    rank_summary(merged_df)

# ----------------------------

if summary_df is not None:

    organizational_summary(summary_df)

# ----------------------------

if summary_df is not None and merged_df is not None:

    investigation_panel(summary_df, merged_df)

# ============================
# INDIVIDUAL SUMMARY
# ============================

if summary_df is not None:

    st.markdown("---")
    st.header("🔍 Individual Discrepancy Summary")

    st.dataframe(summary_df)

# ============================
# DETAILED AUDIT TABLE
# ============================

if merged_df is not None:

    st.markdown("---")
    st.header("📑 Detailed Monthly Audit")

    st.dataframe(merged_df)

    st.download_button(
        label="Download Audit Report",
        data=merged_df.to_csv(index=False).encode("utf-8"),
        file_name="longevity_audit_report.csv",
        mime="text/csv",
    )

# ============================
# SYSTEM AUDIT LOG
# ============================

st.markdown("---")
st.header("📜 System Audit Log")

audit_df = pd.read_sql_query(
    "SELECT * FROM audit_log ORDER BY id DESC",
    conn
)

st.dataframe(audit_df)
