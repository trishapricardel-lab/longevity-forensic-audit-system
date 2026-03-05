import pandas as pd
from datetime import datetime

def generate_cases(mismatches):

    cases = []

    for i, row in mismatches.iterrows():

        case = {
            "Case_ID": f"LP-{row['Serial Number']}",
            "Serial Number": row["Serial Number"],
            "Issue": "Incorrect Longevity Pay Computation",
            "Status": "Open",
            "Date_Detected": datetime.now()
        }

        cases.append(case)

    return pd.DataFrame(cases)
