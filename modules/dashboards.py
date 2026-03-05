import streamlit as st
import pandas as pd


# ============================
# IRREGULARITY SUMMARY
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

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Incorrect LP Computation", incorrect_count)

    with col2:
        st.metric("LP Without Order", lp_without_order_count)

    with col3:
        st.metric("Eligible Without Order", missing_orders_count)

    with col4:
        st.metric("Order Not in Payroll", order_not_paid_count)


# ============================
# FINANCIAL IMPACT ANALYSIS
# ============================

def financial_impact_panel(summary_df):

    st.markdown("---")
    st.header("💰 Financial Impact Analysis")

    if summary_df is None:
        st.info("Upload files to generate financial impact analysis.")
        return

    personnel = summary_df["Serial Number"].nunique()
    overpayment = summary_df["Total_Overpaid"].sum()
    underpayment = summary_df["Total_Underpaid"].sum()
    variance = summary_df["Total_Variance"].sum()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Personnel Affected", personnel)

    with col2:
        st.metric("Total Overpayment", f"₱{overpayment:,.2f}")

    with col3:
        st.metric("Total Underpayment", f"₱{underpayment:,.2f}")

    with col4:
        st.metric("Total Variance", f"₱{variance:,.2f}")


# ============================
# PERSONNEL STATUS PANEL
# ============================

def personnel_status_panel(merged_df, soi_df, orders_df):

    st.markdown("---")
    st.header("📌 Personnel Longevity Status")

    if merged_df is None or soi_df is None:
        st.info("Upload files to analyze personnel longevity status.")
        return

    # LP without order
    if orders_df is not None:

        lp_without_order = merged_df[
            (merged_df["Longevity Pay"] > 0) &
            (~merged_df["Serial Number"].isin(orders_df["Serial Number"]))
        ]

        st.subheader("⚠ Personnel Receiving Longevity Pay WITHOUT Official Order")

        st.metric(
            "Cases Detected",
            lp_without_order["Serial Number"].nunique()
        )

        st.dataframe(
            lp_without_order[
                ["Serial Number", "Payroll Month", "Longevity Pay"]
            ]
        )

    # Eligible but no order

    if orders_df is not None:

        eligible_df = soi_df[soi_df["Eligible_LP_Level"] > 0]

        missing_orders = eligible_df[
            ~eligible_df["Serial Number"].isin(orders_df["Serial Number"])
        ]

        st.subheader("⚠ Personnel Eligible but NO Longevity Order Issued")

        st.metric(
            "Personnel Eligible Without Order",
            missing_orders["Serial Number"].nunique()
        )

        st.dataframe(
            missing_orders[
                ["Serial Number", "Years_of_Service", "Eligible_LP_Level"]
            ]
        )

    # Order but not paid

    if orders_df is not None:

        order_not_paid = orders_df[
            ~orders_df["Serial Number"].isin(merged_df["Serial Number"])
        ]

        st.subheader("⚠ Orders Issued but Payroll NOT Updated")

        st.metric(
            "Cases Detected",
            order_not_paid["Serial Number"].nunique()
        )

        st.dataframe(order_not_paid)


# ============================
# COMMAND DASHBOARD
# ============================

def command_dashboard(summary_df):

    st.markdown("---")
    st.header("📊 Command Dashboard")

    if summary_df is None:
        st.info("Upload files to generate command dashboard.")
        return

    personnel = summary_df["Serial Number"].nunique()

    risk_cases = (summary_df["Months_Incorrect"] > 0).sum()

    highest_variance = summary_df["Total_Variance"].abs().max()

    avg_variance = summary_df["Total_Variance"].mean()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Personnel Audited", personnel)

    with col2:
        st.metric("Personnel With Errors", risk_cases)

    with col3:
        st.metric("Highest Financial Variance", f"₱{highest_variance:,.2f}")

    with col4:
        st.metric("Average Variance", f"₱{avg_variance:,.2f}")


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
# INVESTIGATION PANEL
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
