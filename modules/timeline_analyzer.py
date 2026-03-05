import pandas as pd

def build_timeline(person_history):

    timeline = person_history[
        [
            "Payroll Month",
            "Longevity Pay",
            "Correct_Long_Pay",
            "LP_Difference"
        ]
    ]

    return timeline