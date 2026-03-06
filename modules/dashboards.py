import streamlit as st
import pandas as pd


# ============================
# DETECTED FINANCIAL IRREGULARITIES
# ============================

def irregularity_summary(merged_df, soi_df, orders_df):

    st.markdown("---")
    st.header("🚨 Detected Financial Irregularities")

    if merged_df is None:
        st.info("Upload files to generate irregularity analysis.")
        return

    # Incorrect LP computation
    incorrect_lp = merged_df[merged_df["Error_Flag"] == True]
    incorrect_count = incorrect_lp["Serial Number"].nunique()

    # LP without order
    if orders_df is not None:
        lp_without_order = merged_df[
            (merged_df["Longevity Pay"] > 0) &
            (~merged_df["Serial Number"].isin(orders_df["Serial Number"]))
        ]
        lp_without_order_count = lp_without_order["Serial Number"].nunique()
    else:
        lp_without_order_count = 0

    # Eligible but no order
    if soi_df is not None and orders_df is not None:

        eligible_df = soi_df[soi_df["Eligible_LP_Level"] > 0]

        missing_orders = eligible_df[
            ~eligible_df["Serial Number"].isin(orders_df["Serial Number"])
        ]

        missing_orders_count = missing_orders["Serial Number"].nunique()

    else:
        missing_orders_count = 0

    # Order issued but payroll not updated
    if orders_df is not None:

        order_not_paid = orders_df[
            ~orders_df["Serial Number"].isin(merged_df["Serial Number"])
        ]

        order_not_paid_count = order_not_paid["Serial Number"].nunique()

    else:
        order_not_paid_count = 0

    st.write("### Status Overview")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Incorrect Longevity Pay Computation",
            incorrect_count
        )

    with col2:
        st.metric(
            "Longevity Pay Without Official Order",
            lp_without_order_count
        )

    col3, col4 = st.columns(2)

    with col3:
        st.metric(
            "Eligible Personnel Without Longevity Order",
            missing_orders_count
        )

    with col4:
        st.metric(
            "Order Issued but Payroll Not Updated",
            order_not_paid_count
        )

def executive_dashboard(summary_df, merged_df, cases_df):

    import streamlit as st

    st.markdown("---")
    st.header("📊 Executive Financial Dashboard")

    if summary_df is None or merged_df is None:
        st.info("Upload files to generate dashboard.")
        return

    # ============================
    # METRICS
    # ============================

    personnel_audited = summary_df["Serial Number"].nunique()

    payroll_records = merged_df.shape[0]

    personnel_errors = cases_df["Serial Number"].nunique() if cases_df is not None else 0

    overpaid_df = cases_df[cases_df["Issue"] == "Overpayment"]
    underpaid_df = cases_df[cases_df["Issue"] == "Underpayment"]
    
    personnel_overpaid = overpaid_df["Serial Number"].nunique() if cases_df is not None else 0
    personnel_underpaid = underpaid_df["Serial Number"].nunique() if cases_df is not None else 0]

    total_overpayment = summary_df["Total_Overpaid"].sum()
    total_underpayment = summary_df["Total_Underpaid"].sum()

    investigation_cases = cases_df.shape[0] if cases_df is not None else 0

    audit_coverage = merged_df["Payroll Month"].nunique()

    # ============================
    # ROW 1
    # ============================

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(f"Personnel Audited\n\n{personnel_audited}", use_container_width=True):
            st.session_state.view = "personnel"

    with col2:
        if st.button(f"Payroll Records\n\n{payroll_records}", use_container_width=True):
            st.session_state.view = "payroll"

    with col3:
        if st.button(f"Personnel with Errors\n\n{personnel_errors}", use_container_width=True):
            st.session_state.view = "errors"

    # ============================
    # ROW 2
    # ============================

    col4, col5, col6 = st.columns(3)

    with col4:
        if st.button(f"Personnel Overpaid\n\n{personnel_overpaid}", use_container_width=True):
            st.session_state.view = "overpayment"

    with col5:
        if st.button(f"Personnel Underpaid\n\n{personnel_underpaid}", use_container_width=True):
            st.session_state.view = "underpayment"

    with col6:
        if st.button(f"Investigation Cases\n\n{investigation_cases}", use_container_width=True):
            st.session_state.view = "cases"

    # ============================
    # ROW 3
    # ============================

    col7, col8, col9 = st.columns(3)

    with col7:
        st.markdown(
            f"""
            <div style="border:1px solid #2c3e50;
                        border-radius:12px;
                        padding:20px;
                        background-color:#0f1c2e;
                        text-align:center;">
                <div>Total Overpayment</div>
                <div style="font-size:32px;font-weight:700;color:red;">
                    ₱{total_overpayment:,.2f}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col8:
        st.markdown(
            f"""
            <div style="border:1px solid #2c3e50;
                        border-radius:12px;
                        padding:20px;
                        background-color:#0f1c2e;
                        text-align:center;">
                <div>Total Underpayment</div>
                <div style="font-size:32px;font-weight:700;color:orange;">
                    ₱{total_underpayment:,.2f}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col9:
        st.metric("Audit Coverage (Months)", audit_coverage)
        

# ============================
# RANK DISCREPANCY SUMMARY
# ============================

def rank_summary(merged_df):

    st.markdown("---")
    st.header("📊 Longevity Pay Discrepancy by Rank")

    if merged_df is None or "Rank" not in merged_df.columns:
        st.info("Upload files to generate rank discrepancy summary.")
        return

    rank_summary = merged_df.groupby("Rank").agg(
        Personnel=("Serial Number", "nunique"),
        With_Error=("Error_Flag", "sum"),
        Overpaid=("LP_Difference", lambda x: x[x > 0].sum()),
        Underpaid=("LP_Difference", lambda x: abs(x[x < 0].sum()))
    ).reset_index()

    st.dataframe(rank_summary)


# ============================
# PERSONNEL INVESTIGATION PANEL
# ============================

def investigation_panel(summary_df, merged_df):

    st.markdown("---")
    st.header("🧑‍⚖️ Personnel Investigation Panel")

    if summary_df is None or merged_df is None:
        st.info("Upload files to investigate personnel records.")
        return

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
