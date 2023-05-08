import re
import urllib3


url = "?startIssueDate=20230425&BillMilestone=BM9a&InvoiceNo=g.sj!?8&endIssueDate=20230425"

print(urllib3.util.parse_url(url).query.split("&"))
