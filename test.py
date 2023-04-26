import json
from pprint import pprint

# load file test1.json
with open("test1.json") as f:
    data = json.load(f)

# print data
InvoiceDetailList = data["InvoiceDetail"]
pprint(InvoiceDetailList)
print(sum([InvoiceDetail["FeeAmountPost"] for InvoiceDetail in InvoiceDetailList]))
