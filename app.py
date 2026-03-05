import streamlit as st
import pandas as pd
import math
from datetime import datetime

st.set_page_config(page_title="Longevity Forensic Audit System", layout="wide")

st.title("Longevity Pay Forensic Audit System")
st.markdown("### Multi-Month Personnel–Finance Validation Engine")

st.markdown("---")

# ============================
# FILE UPLOAD
# ============================

st.header("1. Upload Required Files")

soi_file = st.file_uploader(
    "Upload SOI File (S1) - CSV",
    type=["csv"]
)

orders_file = st.file_uploader(
    "Upload Longevity Orders (Adjutant) - CSV",
    type=["csv"]
)

payroll_files = st.file_uploader(
    "Upload Monthly Payroll Files (Finance) - CSV",
    type=["csv"],
    accept_multiple_files=True
)
if orders_file is not None:

    orders_df = pd.read_csv(orders_file)

    orders_df["Effective Date"] = pd.to_datetime(
        orders_df["Effective Date"]
    )

    orders_df["Upload_Time"] = datetime.now()

st.markdown("---")

# ============================
# PROCESSING
# ============================

if soi_file is not None and payroll_files:

    try:

        # ------------------------
        # LOAD SOI
        # ------------------------

        soi_df = pd.read_csv(soi_file)

        required_soi_cols = ["Serial Number", "Date of Entry"]

        if not all(col in soi_df.columns for col in required_soi_cols):
            st.error("SOI must contain: Serial Number, Date of Entry")
            st.stop()

        soi_df["Date of Entry"] = pd.to_datetime(
            soi_df["Date of Entry"],
            format="%m/%d/%Y"
        )

        # ------------------------
        # LOAD PAYROLL FILES
        # ------------------------

        payroll_list = []

        for file in payroll_files:

            df = pd.read_csv(file)

            required_payroll_cols = [
                "Serial Number",
                "Basic Salary",
                "Longevity Pay",
                "Payroll Month"
            ]

            if not all(col in df.columns for col in required_payroll_cols):
                st.error(f"Payroll file {file.name} missing required columns.")
                st.stop()

            payroll_list.append(df)

        payroll_df = pd.concat(payroll_list, ignore_index=True)

        payroll_df["Basic Salary"] = pd.to_numeric(payroll_df["Basic Salary"])
        payroll_df["Longevity Pay"] = pd.to_numeric(payroll_df["Longevity Pay"])

        payroll_df["Payroll_Date"] = pd.to_datetime(
            payroll_df["Payroll Month"] + "-01"
        )

        # ------------------------
        # MERGE DATA
        # ------------------------

        merged_df = pd.merge(
            payroll_df,
            soi_df,
            on="Serial Number",
            how="inner"
        )

        # ------------------------
        # YEARS OF SERVICE PER MONTH
        # ------------------------

        merged_df["Years_of_Service"] = (
            (merged_df["Payroll_Date"] - merged_df["Date of Entry"]).dt.days / 365.25
        )

        merged_df["LP_Count"] = merged_df["Years_of_Service"].apply(
            lambda x: min(math.floor(x / 5), 5)
        )

        # ------------------------
        # LONG PAY FORMULA
        # ------------------------

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

        # ------------------------
        # VARIANCE
        # ------------------------

        merged_df["LP_Difference"] = (
            merged_df["Longevity Pay"] - merged_df["Correct_Long_Pay"]
        ).round(2)

        merged_df["Error_Flag"] = merged_df["LP_Difference"].abs() > 1

        # ------------------------
        # INDIVIDUAL SUMMARY
        # ------------------------

        summary_df = merged_df.groupby("Serial Number").agg(
            Months_Incorrect=("Error_Flag", "sum"),

            Months_Overpaid=("LP_Difference", lambda x: (x > 0).sum()),
            Months_Underpaid=("LP_Difference", lambda x: (x < 0).sum()),

            Total_Variance=("LP_Difference", "sum"),
            Total_Overpaid=("LP_Difference", lambda x: x[x > 0].sum()),
            Total_Underpaid=("LP_Difference", lambda x: abs(x[x < 0].sum()))
        ).reset_index()
        def risk_level(months):
            
            if months == 0:
                return "🟢 Compliant"

            elif months <= 2:
                return "🟡 Low Risk"

            elif months <= 4:
                return "🟠 Medium Risk"

            else:
                return "🔴 High Risk"


        summary_df["Risk_Level"] = summary_df["Months_Incorrect"].apply(risk_level)
        # ------------------------
        # DASHBOARD
        # ------------------------

        total_overpayment = summary_df["Total_Overpaid"].sum()
        total_underpayment = summary_df["Total_Underpaid"].sum()
        net_exposure = total_underpayment - total_overpayment

        st.header("2. Organizational Financial Summary")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Overpayment", f"₱{total_overpayment:,.2f}")

        with col2:
            st.metric("Total Underpayment", f"₱{total_underpayment:,.2f}")

        with col3:
            st.metric("Net Organizational Liability", f"₱{net_exposure:,.2f}")

        st.markdown("---")

        # ------------------------
        # PERSONNEL SUMMARY
        # ------------------------

        st.header("3. Individual Discrepancy Summary")

        st.dataframe(
        summary_df[
            [
                "Serial Number",
                "Months_Incorrect",
                "Months_Overpaid",
                "Months_Underpaid",
                "Total_Overpaid",
                "Total_Underpaid",
                "Total_Variance"
                ]
            ]
        )

        st.markdown("---")

        # ------------------------
        # FULL MONTHLY AUDIT
        # ------------------------

        st.header("4. Detailed Monthly Audit")

        st.dataframe(merged_df)

        # ------------------------
        # DOWNLOAD REPORT
        # ------------------------

        st.markdown("### Export Full Audit Report")

        csv_report = merged_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download Full Multi-Month Audit Report",
            data=csv_report,
            file_name="longevity_forensic_audit.csv",
            mime="text/csv",
        )

    except Exception as e:
        st.error(f"Processing Error: {e}")

else:
    st.info("Upload SOI file and at least one monthly payroll file to begin.")
