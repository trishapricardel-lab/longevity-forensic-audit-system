import streamlit as st
import pandas as pd
import math
import sqlite3
from datetime import datetime
import os

st.set_page_config(page_title="Longevity Forensic Audit System", layout="wide")

# ============================
# CREATE STORAGE DIRECTORIES
# ============================

os.makedirs("data", exist_ok=True)
os.makedirs("data/soi", exist_ok=True)
os.makedirs("data/orders", exist_ok=True)
os.makedirs("data/payroll", exist_ok=True)

# ============================
# DATABASE CONNECTION
# ============================

conn = sqlite3.connect("longevity_system.db", check_same_thread=False)
cursor = conn.cursor()

# ============================
# CREATE TABLES
# ============================

cursor.execute("""
CREATE TABLE IF NOT EXISTS soi (
serial_number TEXT PRIMARY KEY,
rank TEXT,
name TEXT,
date_of_entry TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
id INTEGER PRIMARY KEY AUTOINCREMENT,
order_number TEXT,
serial_number TEXT,
lp_level INTEGER,
effective_date TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS payroll (
id INTEGER PRIMARY KEY AUTOINCREMENT,
serial_number TEXT,
payroll_month TEXT,
basic_salary REAL,
longevity_pay REAL
)
""")

conn.commit()

# ============================
# LOGIN SYSTEM
# ============================

users = {
    "admin": {"password": "masterpass", "role": "Admin"},
    "adjutant": {"password": "admin123", "role": "Adjutant"},
    "s1": {"password": "s1pass", "role": "S1"},
    "finance": {"password": "finpass", "role": "Finance"},
    "commander": {"password": "viewonly", "role": "Command"}
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    st.title("Longevity Pay Forensic Audit System")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if username in users and users[username]["password"] == password:

            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = users[username]["role"]

            st.success("Login successful")
            st.rerun()

        else:

            st.error("Invalid credentials")

    st.stop()

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
# SIDEBAR DATA REPOSITORY
# ============================

st.sidebar.header("Data Repository")

st.sidebar.subheader("SOI Files")

soi_list = os.listdir("data/soi")
for file in soi_list:
    st.sidebar.write(file)

st.sidebar.subheader("Longevity Orders")

order_list = os.listdir("data/orders")
for file in order_list:
    st.sidebar.write(file)

st.sidebar.subheader("Payroll Files")

payroll_list = os.listdir("data/payroll")
for file in payroll_list:
    st.sidebar.write(file)

# ============================
# MAIN PAGE
# ============================

st.title("Longevity Pay Forensic Audit System")
st.markdown("### Multi-Month Personnel–Finance Validation Engine")

st.markdown("---")

# ============================
# FILE UPLOAD
# ============================

st.header("1. Upload Required Files")

# SOI Upload

if st.session_state.role in ["Admin", "S1", "Adjutant"]:

    soi_file = st.file_uploader(
        "Upload SOI File (S1) - CSV",
        type=["csv"]
    )

    if soi_file is not None:

        path = f"data/soi/{soi_file.name}"

        with open(path, "wb") as f:
            f.write(soi_file.getbuffer())

        st.success("SOI saved to repository")

else:
    st.info("Only S1 can upload SOI files.")
    soi_file = None

# Orders Upload

if st.session_state.role in ["Admin","Adjutant"]:

    orders_file = st.file_uploader(
        "Upload Longevity Orders",
        type=["csv"]
    )

    if orders_file is not None:

        path = f"data/orders/{orders_file.name}"

        with open(path, "wb") as f:
            f.write(orders_file.getbuffer())

        st.success("Orders saved")

else:
    orders_file = None

# Payroll Upload

if st.session_state.role in ["Admin","Finance"]:

    payroll_files = st.file_uploader(
        "Upload Monthly Payroll Files",
        type=["csv"],
        accept_multiple_files=True
    )

    if payroll_files:

        for file in payroll_files:

            path = f"data/payroll/{file.name}"

            with open(path, "wb") as f:
                f.write(file.getbuffer())

        st.success("Payroll files saved")

else:
    payroll_files = []

# ============================
# LOAD ORDERS
# ============================

orders_df = None

if orders_file is not None:

    orders_df = pd.read_csv(orders_file)

    orders_df["Effective Date"] = pd.to_datetime(
        orders_df["Effective Date"]
    )

    orders_df["Upload_Time"] = datetime.now()

# ============================
# LONGEVITY ORDER ARCHIVE
# ============================

st.markdown("---")
st.header("Longevity Order Archive")

if orders_df is not None:

    st.dataframe(
        orders_df[
            [
                "Order Number",
                "Serial Number",
                "LP Level",
                "Effective Date",
                "Upload_Time"
            ]
        ]
    )

else:

    st.info("No longevity orders uploaded yet.")

# ============================
# PROCESSING
# ============================

if soi_file is not None and payroll_files:

    try:

        soi_df = pd.read_csv(soi_file)

        soi_df["Date of Entry"] = pd.to_datetime(
            soi_df["Date of Entry"],
            format="%m/%d/%Y"
        )

        today = datetime.today()

        soi_df["Years_of_Service"] = (
            (today - soi_df["Date of Entry"]).dt.days / 365.25
        )

        soi_df["Eligible_LP_Level"] = soi_df["Years_of_Service"].apply(
            lambda x: min(math.floor(x / 5), 5)
        )

        payroll_list = []

        for file in payroll_files:

            df = pd.read_csv(file)

            payroll_list.append(df)

        payroll_df = pd.concat(payroll_list, ignore_index=True)

        payroll_df["Basic Salary"] = pd.to_numeric(payroll_df["Basic Salary"])
        payroll_df["Longevity Pay"] = pd.to_numeric(payroll_df["Longevity Pay"])

        payroll_df["Payroll_Date"] = pd.to_datetime(
            payroll_df["Payroll Month"] + "-01"
        )

        merged_df = pd.merge(
            payroll_df,
            soi_df,
            on="Serial Number",
            how="inner"
        )

        merged_df["Years_of_Service"] = (
            (merged_df["Payroll_Date"] - merged_df["Date of Entry"]).dt.days / 365.25
        )

        merged_df["LP_Count"] = merged_df["Years_of_Service"].apply(
            lambda x: min(math.floor(x / 5), 5)
        )

        def compute_correct_lp(base_salary, lp_count):

            if lp_count <= 0:
                return 0

            elif lp_count == 5:
                return base_salary * 0.50

            else:
                return base_salary * (1.1 ** lp_count - 1)

        merged_df["Correct_Long_Pay"] = merged_df.apply(
            lambda row: compute_correct_lp(
                row["Basic Salary"],
                row["LP_Count"]
            ),
            axis=1
        )

        merged_df["LP_Difference"] = (
            merged_df["Longevity Pay"] - merged_df["Correct_Long_Pay"]
        ).round(2)

        merged_df["Error_Flag"] = merged_df["LP_Difference"].abs() > 1

        summary_df = merged_df.groupby("Serial Number").agg(
            Months_Incorrect=("Error_Flag", "sum"),
            Total_Variance=("LP_Difference", "sum"),
            Total_Overpaid=("LP_Difference", lambda x: x[x > 0].sum()),
            Total_Underpaid=("LP_Difference", lambda x: abs(x[x < 0].sum()))
        ).reset_index()

        total_overpayment = summary_df["Total_Overpaid"].sum()
        total_underpayment = summary_df["Total_Underpaid"].sum()

        st.header("2. Organizational Financial Summary")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Total Overpayment", f"₱{total_overpayment:,.2f}")

        with col2:
            st.metric("Total Underpayment", f"₱{total_underpayment:,.2f}")

        st.markdown("---")

        st.header("3. Individual Discrepancy Summary")

        st.dataframe(summary_df)

        st.markdown("---")

        st.header("4. Detailed Monthly Audit")

        st.dataframe(merged_df)

        st.download_button(
            label="Download Audit Report",
            data=merged_df.to_csv(index=False).encode("utf-8"),
            file_name="longevity_audit_report.csv",
            mime="text/csv",
        )

    except Exception as e:
        st.error(f"Processing Error: {e}")

else:
    st.info("Upload SOI and Payroll files to start audit.")
