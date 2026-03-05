import pandas as pd

def detect_mismatch(merged_df):

    mismatches = merged_df[
        merged_df["Error_Flag"] == True
    ]

    return mismatches

def recompute_longevity(merged_df):

    merged_df["Corrected"] = merged_df["LP_Difference"].apply(
        lambda x: "Incorrect" if abs(x) > 1 else "Correct"
    )

    return merged_df
