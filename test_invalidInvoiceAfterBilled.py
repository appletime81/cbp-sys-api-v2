import pandas as pd
import numpy as np
from pprint import pprint

# df = pd.read_csv("BillDetailData.csv")
#
#
# df_RATED = df[df["Status"] == "RATED"]
# print("-" * 100)
# print(df_RATED)

# convert df_RATED to List[Dict]
# df_RATED_list = df_RATED.to_dict("records")
# pprint(df_RATED_list)


# df_NAN = df[df["Status"].isnull()]
# print("-" * 100)
# print(df_NAN)

# convert df_NAN to List[Dict]
# df_NAN_list = df_NAN.to_dict("records")
# pprint(df_NAN_list)
# print(np.isnan(df_NAN_list[0]["Status"]))


"""
{
    "ifReturn": False,
    "BillMaster": {
        "INITIAL": [],
        "RATED": [],
        "SIGNED": [],
        "TO_WRITEOFF": [],
        "COMPLETE": [],
    }
}
"""

status_list = ["INITIAL", "RATED", "SIGNED", "TO_WRITEOFF", "COMPLETE"]
df_BillDetailData = pd.read_csv("BillDetailData.csv")
df_BillDetailData_INITIAL = df_BillDetailData[df_BillDetailData["Status"].isnull()]
df_BillDetailData_INITIAL_list = df_BillDetailData_INITIAL.to_dict("records")


df_BillDetailData_COMPLETE = df_BillDetailData[
    df_BillDetailData["Status"] == "COMPLETE"
]
df_BillDetailData_COMPLETE_list = df_BillDetailData_COMPLETE.to_dict("records")

df_BillDetailData_RATED = df_BillDetailData[df_BillDetailData["Status"] == "RATED"]
df_BillDetailData_RATED_list = df_BillDetailData_RATED.to_dict("records")

df_BillDetailData_SIGNED = df_BillDetailData[df_BillDetailData["Status"] == "SIGNED"]
df_BillDetailData_SIGNED_list = df_BillDetailData_SIGNED.to_dict("records")

df_BillDetailData_TO_WRITEOFF = df_BillDetailData[
    df_BillDetailData["Status"] == "TO_WRITEOFF"
]
df_BillDetailData_TO_WRITEOFF_list = df_BillDetailData_TO_WRITEOFF.to_dict("records")
