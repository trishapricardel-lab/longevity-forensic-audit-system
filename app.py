import streamlit as st
import pandas as pd
import math
import sqlite3
from datetime import datetime
import os

st.set_page_config(page_title="Integrated Longevity Audit System", layout="wide")

st.markdown("""
<style>

/* METRIC CARDS */
[data-testid="stMetric"] {
    background-color: #1C1F26;
    border: 1px solid #2E3138;
    padding: 15px;
    border-radius: 10px;
}

/* METRIC VALUE */
[data-testid="stMetricValue"] {
    color: #C9A227;
    font-size: 32px;
    font-weight: bold;
}

/* SECTION HEADERS */
h2 {
    border-bottom: 2px solid #C9A227;
    padding-bottom: 5px;
}

/* ALERT BOX */
.stAlert {
    border-left: 6px solid red;
}

/* DATAFRAME */
[data-testid="stDataFrame"] {
    border: 1px solid #2E3138;
}

</style>
""", unsafe_allow_html=True)

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

def log_action(user, action, filename):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO audit_log (username, action, filename, timestamp)
    VALUES (?, ?, ?, ?)
    """, (user, action, filename, timestamp))

    conn.commit()

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

cursor.execute("""
CREATE TABLE IF NOT EXISTS audit_log (
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
action TEXT,
filename TEXT,
timestamp TEXT
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

    st.title("🛡️ Integrated Longevity Audit System")

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
# ADMIN FILE CONTROL PANEL
# ============================

st.sidebar.markdown("## ⚙️ Admin Controls")

if st.session_state.role == "Admin":

    st.sidebar.markdown("---")
    st.sidebar.header("Admin File Control Panel")

    # ==================================
    # DELETE SOI FILE
    # ==================================

    st.sidebar.subheader("Delete SOI File")

    soi_files = os.listdir("data/soi")

    if len(soi_files) > 0:

        soi_to_delete = st.sidebar.selectbox(
            "Select SOI File",
            soi_files,
            key="delete_soi"
        )

        confirm_soi = st.sidebar.checkbox(
            "Confirm SOI deletion",
            key="confirm_soi"
        )

        if confirm_soi and st.sidebar.button("Delete SOI File"):

            os.remove(f"data/soi/{soi_to_delete}")

            log_action(
                st.session_state.username,
                "Delete SOI File",
                soi_to_delete
            )

            st.sidebar.success("SOI file deleted successfully")
            st.rerun()

    else:
        st.sidebar.write("No SOI files found")

    # ==================================
    # DELETE ORDER FILE
    # ==================================

    st.sidebar.subheader("Delete Order File")

    order_files = os.listdir("data/orders")

    if len(order_files) > 0:

        order_to_delete = st.sidebar.selectbox(
            "Select Order File",
            order_files,
            key="delete_order"
        )

        confirm_order = st.sidebar.checkbox(
            "Confirm order deletion",
            key="confirm_order"
        )

        if confirm_order and st.sidebar.button("Delete Order File"):

            os.remove(f"data/orders/{order_to_delete}")

            log_action(
                st.session_state.username,
                "Delete Order File",
                order_to_delete
            )

            st.sidebar.success("Order file deleted successfully")
            st.rerun()

    else:
        st.sidebar.write("No order files found")

    # ==================================
    # DELETE PAYROLL FILE
    # ==================================

    st.sidebar.subheader("Delete Payroll File")

    payroll_repo_files = os.listdir("data/payroll")

    if len(payroll_repo_files) > 0:

        payroll_to_delete = st.sidebar.selectbox(
            "Select Payroll File",
            payroll_repo_files,
            key="delete_payroll"
        )

        confirm_payroll = st.sidebar.checkbox(
            "Confirm payroll deletion",
            key="confirm_payroll"
        )

        if confirm_payroll and st.sidebar.button("Delete Payroll File"):

            os.remove(f"data/payroll/{payroll_to_delete}")

            log_action(
                st.session_state.username,
                "Delete Payroll File",
                payroll_to_delete
            )

            st.sidebar.success("Payroll file deleted successfully")
            st.rerun()

    else:
        st.sidebar.write("No payroll files found")

    # ============================
    # DELETE AUDIT LOG ENTRY
    # ============================

    st.sidebar.subheader("Delete Audit Log Entry")

    log_df = pd.read_sql_query(
        "SELECT id, username, action, filename, timestamp FROM audit_log ORDER BY id DESC",
        conn
    )

    if len(log_df) > 0:

        selected_log = st.sidebar.selectbox(
            "Select Log ID",
            log_df["id"]
        )

        confirm_log = st.sidebar.checkbox("Confirm log deletion")

        if confirm_log and st.sidebar.button("Delete Log Entry"):

            cursor.execute(
                "DELETE FROM audit_log WHERE id=?",
                (selected_log,)
            )

            conn.commit()

            st.sidebar.success("Log entry deleted")
            st.rerun()

    else:
        st.sidebar.write("No logs available")

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
# MAIN PAGE HEADER
# ============================

st.title("🛡️ Integrated Longevity Audit System")
st.caption("Personnel–Finance Validation Engine| Philippine Army Financial Audit Tool")

st.markdown("---")

# COMMAND DASHBOARD

st.header("📊 Command Dashboard")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Personnel Audited", "0")

with col2:
    st.metric("Overpayment Detected", "₱0")

with col3:
    st.metric("Underpayment Detected", "₱0")

with col4:
    st.metric("Risk Alerts", "0")

st.markdown("---")

# ============================
# FILE UPLOAD
# ============================

st.header("📤 Upload Required Files")

# ============================
# SOI SOURCE
# ============================

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

        log_action(st.session_state.username, "Upload SOI", uploaded_soi.name)

        soi_file = path


# ============================
# Orders Upload
# ============================

orders_file = None

if st.session_state.role in ["Admin", "Adjutant"]:

    orders_file = st.file_uploader(
        "Upload Longevity Orders",
        type=["csv"]
    )

    if orders_file is not None:

        path = f"data/orders/{orders_file.name}"

        with open(path, "wb") as f:
            f.write(orders_file.getbuffer())

        st.success("Orders saved")
        log_action(st.session_state.username, "Upload Longevity Order", orders_file.name)


# ============================
# Payroll Upload
# ============================

payroll_files = []

if st.session_state.role in ["Admin", "Finance"]:

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

            log_action(st.session_state.username, "Upload Payroll", file.name)

        st.success("Payroll files saved")

# ============================
# LOAD ORDERS FROM REPOSITORY
# ============================

orders_files = os.listdir("data/orders")

orders_list = []

for file in orders_files:

    path = f"data/orders/{file}"

    df = pd.read_csv(path)

    df.columns = df.columns.str.strip()

    df["Effective Date"] = pd.to_datetime(
        df["Effective Date"],
        errors="coerce"
    )

    orders_list.append(df)

if len(orders_list) > 0:
    orders_df = pd.concat(orders_list, ignore_index=True)
    orders_df["Upload_Time"] = datetime.now()
else:
    orders_df = None

# ============================
# LONGEVITY ORDER ARCHIVE
# ============================

st.markdown("---")
st.header("📑 Longevity Order Archive")

orders_files = os.listdir("data/orders")
soi_files = os.listdir("data/soi")

orders_list = []

# Load orders
for file in orders_files:

    path = f"data/orders/{file}"

    df = pd.read_csv(path)

    df.columns = df.columns.str.strip()

    df["Source_File"] = file

    orders_list.append(df)

if len(orders_list) > 0:

    orders_df = pd.concat(orders_list, ignore_index=True)

    # Load SOI for Rank and Name
    if len(soi_files) > 0:

        soi_path = f"data/soi/{sorted(soi_files)[-1]}"

        soi_df = pd.read_csv(soi_path)

        soi_df.columns = soi_df.columns.str.strip()

        orders_df = pd.merge(
            orders_df,
            soi_df[["Serial Number","Rank","Name"]],
            on="Serial Number",
            how="left"
        )

    # Filters
    col1, col2 = st.columns(2)

    with col1:
        rank_filter = st.selectbox(
            "Filter by Rank",
            ["All"] + sorted(orders_df["Rank"].dropna().unique().tolist())
        )

    with col2:
        order_filter = st.selectbox(
            "Filter by Order Number",
            ["All"] + sorted(orders_df["Order Number"].dropna().unique().tolist())
        )

    filtered_df = orders_df.copy()

    if rank_filter != "All":
        filtered_df = filtered_df[filtered_df["Rank"] == rank_filter]

    if order_filter != "All":
        filtered_df = filtered_df[filtered_df["Order Number"] == order_filter]

    display_columns = [
        "Rank",
        "Name",
        "Serial Number",
        "LP Level",
        "Order Number",
        "Effective Date",
        "Source_File"
    ]

    display_columns = [c for c in display_columns if c in filtered_df.columns]

    st.dataframe(filtered_df[display_columns])

else:

    st.info("No orders uploaded yet.")

# ============================
# SOI ARCHIVE
# ============================

st.markdown("---")
st.header("📂 SOI Archive")

soi_files = os.listdir("data/soi")

if len(soi_files) > 0:

    selected_soi = st.selectbox(
        "Filter by SOI File",
        soi_files
    )

    path = f"data/soi/{selected_soi}"

    soi_archive_df = pd.read_csv(path)

    soi_archive_df.columns = soi_archive_df.columns.str.strip()

    soi_archive_df["Source_File"] = selected_soi
    soi_archive_df["Upload_Date"] = datetime.fromtimestamp(os.path.getmtime(path))

    # Rank filter
    if "Rank" in soi_archive_df.columns:

        rank_options = ["All"] + sorted(
            soi_archive_df["Rank"].dropna().unique().tolist()
        )

        selected_rank = st.selectbox(
            "Filter by Rank",
            rank_options
        )

        if selected_rank != "All":
            soi_archive_df = soi_archive_df[
                soi_archive_df["Rank"] == selected_rank
            ]

    display_columns = [
        "Rank",
        "Name",
        "Serial Number",
        "Date of Entry",
        "Source_File",
        "Upload_Date"
    ]

    display_columns = [c for c in display_columns if c in soi_archive_df.columns]

    st.dataframe(soi_archive_df[display_columns])

else:

    st.info("No SOI files uploaded yet.")
    
# ============================
# PROCESSING
# ============================

if soi_file is not None and payroll_files:

    try:

        # ============================
        # LOAD SOI
        # ============================

        soi_files = os.listdir("data/soi")

        if len(soi_files) == 0:
            st.error("No SOI files uploaded yet.")
            st.stop()

        latest_soi = sorted(soi_files)[-1]

        soi_path = f"data/soi/{latest_soi}"

        soi_df = pd.read_csv(soi_path)

        # Clean column names
        soi_df.columns = soi_df.columns.str.strip()

        soi_df["Date of Entry"] = pd.to_datetime(
            soi_df["Date of Entry"],
            errors="coerce"
        )

        today = datetime.today()

        soi_df["Years_of_Service"] = (
            (today - soi_df["Date of Entry"]).dt.days / 365.25
        )

        soi_df["Eligible_LP_Level"] = soi_df["Years_of_Service"].apply(
            lambda x: min(math.floor(x / 5), 5)
        )

        # ============================
        # LOAD PAYROLL FILES FROM REPOSITORY
        # ============================

        payroll_files_repo = os.listdir("data/payroll")

        payroll_list = []

        for file in payroll_files_repo:

            path = f"data/payroll/{file}"

            df = pd.read_csv(path)

            df.columns = df.columns.str.strip()

            payroll_list.append(df)

        if len(payroll_list) == 0:
            st.error("No payroll files uploaded yet.")
            st.stop()

        payroll_df = pd.concat(payroll_list, ignore_index=True)

        payroll_df["Basic Salary"] = pd.to_numeric(
            payroll_df["Basic Salary"], errors="coerce"
        )

        payroll_df["Longevity Pay"] = pd.to_numeric(
            payroll_df["Longevity Pay"], errors="coerce"
        )

        payroll_df["Payroll_Date"] = pd.to_datetime(
            payroll_df["Payroll Month"] + "-01",
            errors="coerce"
        )

        # ============================
        # MERGE SOI + PAYROLL
        # ============================

        merged_df = pd.merge(
            payroll_df,
            soi_df,
            on="Serial Number",
            how="inner"
        )

        # ============================
        # IRREGULARITY DETECTION
        # ============================

        st.markdown("---")
        st.header("🚨 Longevity Pay Irregularity Detection")

        if orders_df is not None:

            # Personnel receiving LP but no order
            lp_without_order = merged_df[
                (merged_df["Longevity Pay"] > 0) &
                (~merged_df["Serial Number"].isin(orders_df["Serial Number"]))
            ]

            if len(lp_without_order) > 0:

                st.subheader("⚠ Personnel Receiving LP but NO Official Order")

                st.metric("Cases Detected", len(lp_without_order))

                st.dataframe(
                    lp_without_order[
                        [
                            "Serial Number",
                            "Payroll Month",
                            "Longevity Pay"
                        ]
                    ]
                )

            else:
                st.success("No unauthorized longevity payments detected.")

        # ============================
        # ELIGIBLE BUT NO ORDER
        # ============================

        eligible_df = soi_df[soi_df["Eligible_LP_Level"] > 0]

        if orders_df is not None:

            missing_orders = eligible_df[
                ~eligible_df["Serial Number"].isin(orders_df["Serial Number"])
            ]

            if len(missing_orders) > 0:

                st.subheader("⚠ Personnel Eligible but No Longevity Order Issued")

                st.metric(
                    "Personnel Eligible Without Order",
                    len(missing_orders)
                )

                st.dataframe(
                    missing_orders[
                        [
                            "Serial Number",
                            "Years_of_Service",
                            "Eligible_LP_Level"
                        ]
                    ]
                )

            else:
                st.success("All eligible personnel have orders issued.")

        # ============================
        # ORDER ISSUED BUT PAYROLL NOT UPDATED
        # ============================

        if orders_df is not None:

            order_not_paid = orders_df[
                ~orders_df["Serial Number"].isin(merged_df["Serial Number"])
            ]

            if len(order_not_paid) > 0:

                st.subheader("⚠ Orders Issued but Payroll Not Updated")

                st.metric(
                    "Personnel With Order but No LP Payment",
                    len(order_not_paid)
                )

                st.dataframe(order_not_paid)

            else:
                st.success("All issued orders reflected in payroll.")

        # ============================
        # CORRECT LP COMPUTATION
        # ============================

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


        # ============================
        # PERSONNEL SUMMARY
        # ============================

        summary_df = merged_df.groupby("Serial Number").agg(
            Months_Incorrect=("Error_Flag", "sum"),
            Total_Variance=("LP_Difference", "sum"),
            Total_Overpaid=("LP_Difference", lambda x: x[x > 0].sum()),
            Total_Underpaid=("LP_Difference", lambda x: abs(x[x < 0].sum()))
        ).reset_index()

        # ============================
        # ORGANIZATIONAL SUMMARY
        # ============================

        total_overpayment = summary_df["Total_Overpaid"].sum()
        total_underpayment = summary_df["Total_Underpaid"].sum()

        st.header("📊 Organizational Financial Summary")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Total Overpayment", f"₱{total_overpayment:,.2f}")

        with col2:
            st.metric("Total Underpayment", f"₱{total_underpayment:,.2f}")


        # ============================
        # PERSONNEL INVESTIGATION PANEL
        # ============================

        st.markdown("---")
        st.header("🧑‍⚖️ Personnel Investigation Panel")

        if len(summary_df) > 0:

            selected_serial = st.selectbox(
                "Select Personnel Serial Number",
                summary_df["Serial Number"]
            )

            person_summary = summary_df[
                summary_df["Serial Number"] == selected_serial
            ]

            person_history = merged_df[
                merged_df["Serial Number"] == selected_serial
            ]

            st.subheader("Personnel Financial Summary")
            st.dataframe(person_summary)

            st.subheader("Monthly Payroll History")

            st.dataframe(
                person_history[
                    [
                        "Payroll Month",
                        "Basic Salary",
                        "Longevity Pay",
                        "Correct_Long_Pay",
                        "LP_Difference"
                    ]
                ]
            )

        else:
            st.info("No personnel records available.")


        # ============================
        # INDIVIDUAL DISCREPANCY SUMMARY
        # ============================

        st.markdown("---")
        st.header("🔍 Individual Discrepancy Summary")
        st.dataframe(summary_df)


        # ============================
        # DETAILED MONTHLY AUDIT
        # ============================

        st.markdown("---")
        st.header("📑 Detailed Monthly Audit")

        st.dataframe(merged_df)

        st.download_button(
            label="Download Audit Report",
            data=merged_df.to_csv(index=False).encode("utf-8"),
            file_name="longevity_audit_report.csv",
            mime="text/csv",
        )

    except Exception as e:
        st.error(f"Processing Error: {e}")

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
