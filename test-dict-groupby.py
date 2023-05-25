from pprint import pprint
from itertools import groupby
from operator import itemgetter

df_dict = [
    {
        "CBStateID": 1,
        "CBID": 1,
        "BillingNo": "test billing no",
        "BLDetailID": None,
        "TransItem": "USER_ADD",
        "OrgAmount": 200000.0,
        "TransAmount": 0.0,
        "Note": None,
        "CreateDate": "2023-05-25 17:33:31",
    },
    {
        "CBStateID": 2,
        "CBID": 1,
        "BillingNo": "02CO-CI2305251730",
        "BLDetailID": 1.0,
        "TransItem": "DEDUCT",
        "OrgAmount": 200000.0,
        "TransAmount": -30.0,
        "Note": None,
        "CreateDate": "2023-05-25 17:35:41",
    },
    {
        "CBStateID": 3,
        "CBID": 1,
        "BillingNo": "02CO-CI2305251730",
        "BLDetailID": 2.0,
        "TransItem": "DEDUCT",
        "OrgAmount": 199970.0,
        "TransAmount": -20.0,
        "Note": None,
        "CreateDate": "2023-05-25 17:35:41",
    },
    {
        "CBStateID": 4,
        "CBID": 1,
        "BillingNo": "02CO-CI2305251730",
        "BLDetailID": 2.0,
        "TransItem": "RETURN",
        "OrgAmount": 199950.0,
        "TransAmount": 20.0,
        "Note": None,
        "CreateDate": "2023-05-25 17:40:34",
    },
    {
        "CBStateID": 5,
        "CBID": 1,
        "BillingNo": "02CO-CI2305251730",
        "BLDetailID": 1.0,
        "TransItem": "RETURN",
        "OrgAmount": 199970.0,
        "TransAmount": 30.0,
        "Note": None,
        "CreateDate": "2023-05-25 17:40:34",
    },
    {
        "CBStateID": 6,
        "CBID": 1,
        "BillingNo": "02CO-CI2305251730",
        "BLDetailID": 1.0,
        "TransItem": "DEDUCT",
        "OrgAmount": 200000.0,
        "TransAmount": -50.0,
        "Note": None,
        "CreateDate": "2023-05-25 17:47:03",
    },
    {
        "CBStateID": 7,
        "CBID": 1,
        "BillingNo": "02CO-CI2305251730",
        "BLDetailID": 2.0,
        "TransItem": "DEDUCT",
        "OrgAmount": 199950.0,
        "TransAmount": -40.0,
        "Note": None,
        "CreateDate": "2023-05-25 17:47:03",
    },
]

# # filter TransItem is DEDUCT
# df_dict = [x for x in df_dict if x["TransItem"] == "DEDUCT"]
# pprint(df_dict)
# print("-" * 50)
#
# # sort by CreateDate
# df_dict_sorted = sorted(df_dict, key=itemgetter("CreateDate"), reverse=True)
#
# # groupby CreateDate
# df_dict_sorted_grouped = groupby(df_dict_sorted, key=itemgetter("CreateDate"))
#
#
# df_dict_sorted_grouped = [
#     list(v)
#     for i, (k, v) in enumerate(groupby(df_dict_sorted, key=itemgetter("CreateDate")))
#     if i == 0
# ][0]
# print("*" * 100)
# pprint(df_dict_sorted_grouped)

# Filter TransItem is DEDUCT and sort by CreateDate
df_dict = sorted(
    [d for d in df_dict if d["TransItem"] == "DEDUCT"],
    key=lambda x: x["CreateDate"],
    reverse=True,
)

# pprint(df_dict)
# print("-" * 50)

# Groupby CreateDate and get the first group
df_dict_grouped = next(
    iter(
        [list(group) for key, group in groupby(df_dict, key=lambda x: x["CreateDate"])]
    )
)

print("*" * 100)
pprint(df_dict_grouped)
