import streamlit as st
import pandas as pd
import os

from modules.auth import login
from modules.database import connect_db, create_tables
from modules.file_manager import create_directories
from modules.audit import log_action
from modules.admin_panel import admin_controls

from modules.uploads import handle_soi_upload
from modules.uploads import handle_orders_upload
from modules.uploads import handle_payroll_upload

from modules.processing import load_soi
from modules.processing import load_payroll
from modules.processing import merge_datasets
from modules.processing import compute_longevity
from modules.processing import create_summary

from modules.dashboards import executive_dashboard
from modules.dashboards import rank_summary
from modules.dashboards import organizational_summary
from modules.dashboards import investigation_panel
from modules.dashboards import irregularity_summary

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
if "view" not in st.session_state:
    st.session_state.view = None
st.markdown("""
<style>
.metric-card button {
    width: 100%;
    height: 90px;
    border-radius: 10px;
    border: 1px solid #2c3e50;
    background-color: #0f1c2e;
    color: white;
    font-size: 16px;
    font-weight: 600;
}
.metric-card button:hover {
    border-color: #C9A227;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

/* METRIC CARD STYLE */
[data-testid="stMetric"] {
    background-color: #0f1c2e;
    border: 1px solid #2c3e50;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
}

/* METRIC LABEL */
[data-testid="stMetricLabel"] {
    font-size: 15px;
    font-weight: 600;
}

/* METRIC VALUE */
[data-testid="stMetricValue"] {
    font-size: 32px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

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

soi_files = handle_soi_upload(cursor, conn)

orders_files = handle_orders_upload(cursor, conn)

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

st.markdown("### ⚙️ Run Audit Analysis")

if st.button("🚀 Generate Audit Analysis"):

    if not soi_files:
        st.error("Please upload or select SOI files.")
        st.stop()

    if not payroll_files:
        st.error("Please upload or select payroll files.")
        st.stop()

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

        st.success("Audit analysis completed successfully.")

    except Exception as e:

        st.error(f"Processing Error: {e}")

# ============================
# DASHBOARDS
# ============================

if cases_df is not None:

    st.header("📁 Case Tracking")

    st.dataframe(
        cases_df.sort_values("Amount", ascending=False)
    )

# ----------------------------

if merged_df is not None:

    irregularity_summary(merged_df, soi_df, orders_df)

# ----------------------------

if summary_df is not None and merged_df is not None:

    executive_dashboard(summary_df, merged_df, cases_df)

# ----------------------------

# ============================
# DATA VIEW (DRILL DOWN)
# ============================

if "view" in st.session_state:

    st.markdown("---")
    st.subheader("📂 Data View")

    if st.session_state.view == "personnel":
        st.dataframe(summary_df)

    elif st.session_state.view == "payroll":
        st.dataframe(merged_df)

    elif st.session_state.view == "errors":
        st.dataframe(summary_df[summary_df["Months_Incorrect"] > 0])

    elif st.session_state.view == "overpayment":
        st.dataframe(summary_df[summary_df["Total_Overpaid"] > 0])

    elif st.session_state.view == "underpayment":
        st.dataframe(summary_df[summary_df["Total_Underpaid"] > 0])
        
    elif st.session_state.view == "cases":
        st.dataframe(cases_df)

# ----------------------------

if merged_df is not None:

    rank_summary(merged_df)

# ----------------------------

if summary_df is not None:

    pass

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
