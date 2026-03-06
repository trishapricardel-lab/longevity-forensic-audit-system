import pandas as pd
from datetime import datetime


# ============================
# GENERATE CASES
# ============================

def generate_cases(mismatch_df):

    if mismatch_df is None or mismatch_df.empty:
        return pd.DataFrame()

    cases = []

    for _, row in mismatch_df.iterrows():

        serial = row["Serial Number"]
        diff = row["LP_Difference"]

        # Determine issue type
        if diff > 1:

            issue = "Incorrect Longevity Pay (Overpayment)"
            amount = round(diff, 2)

        elif diff < -1:

            issue = "Incorrect Longevity Pay (Underpayment)"
            amount = round(abs(diff), 2)

        else:
            continue

        case_id = f"LP-{serial}"

        cases.append({
            "Case_ID": case_id,
            "Serial Number": serial,
            "Issue": issue,
            "Amount": amount,
            "Status": "Open",
            "Date Detected": datetime.today().strftime("%Y-%m-%d")
        })

    cases_df = pd.DataFrame(cases)

    return cases_df
