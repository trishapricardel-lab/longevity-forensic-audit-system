import streamlit as st


# ============================
# COMMAND DASHBOARD
# ============================

def command_dashboard(summary_df):

    st.header("📊 Command Dashboard")

    if summary_df is None or len(summary_df) == 0:

        total_personnel = 0
        total_overpayment = 0
        total_underpayment = 0
        risk_alerts = 0

    else:

        total_personnel = summary_df["Serial Number"].nunique()
        total_overpayment = summary_df["Total_Overpaid"].sum()
        total_underpayment = summary_df["Total_Underpaid"].sum()
        risk_alerts = (summary_df["Months_Incorrect"] > 0).sum()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Personnel Audited", total_personnel)

    with col2:
        st.metric("Overpayment Detected", f"₱{total_overpayment:,.2f}")

    with col3:
        st.metric("Underpayment Detected", f"₱{total_underpayment:,.2f}")

    with col4:
        st.metric("Risk Alerts", risk_alerts)


# ============================
# RANK DISCREPANCY SUMMARY
# ============================

def rank_summary(merged_df):

    st.subheader("📊 Longevity Pay Discrepancy by Rank")

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
# ORGANIZATIONAL SUMMARY
# ============================

def organizational_summary(summary_df):

    if summary_df is None:
        return

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

def investigation_panel(summary_df, merged_df):

    st.markdown("---")
    st.header("🧑‍⚖️ Personnel Investigation Panel")

    if summary_df is None or len(summary_df) == 0:

        st.info("No personnel records available.")
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
