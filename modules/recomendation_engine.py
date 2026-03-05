def recommend_action(row):

    if row["LP_Difference"] > 0:
        return "Possible Overpayment — verify payroll adjustment"

    if row["LP_Difference"] < 0:
        return "Possible Underpayment — issue corrected order"

    return "No action required"