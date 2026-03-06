import pandas as pd
from datetime import datetime


def generate_cases(mismatch_df):

    cases = []

    for i, row in mismatch_df.iterrows():

        serial = row["Serial Number"]

        difference = row["LP_Difference"]

        # Determine issue type
        if difference > 0:
            issue = "Overpayment"
            amount = difference

        elif difference < 0:
            issue = "Underpayment"
            amount = abs(difference)

        else:
            continue

        case = {
            "Case_ID": f"LP-{serial}",
            "Serial Number": serial,
            "Issue": issue,
            "Amount": round(amount, 2),
            "Status": "Open",
            "Date_Detected": datetime.now()
        }

        cases.append(case)

    cases_df = pd.DataFrame(cases)

    return cases_df