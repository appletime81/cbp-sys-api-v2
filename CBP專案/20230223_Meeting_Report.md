# 20230223 Metting Report



## 作廢
- 全部退回到發票工作主檔，並提示有哪些"發票工作主檔"需要處理
- "帳單"作廢 -> BillMaster、CB、CBStatement、InvoiceWKMaster、InvoiceMaster
- 做待抵扣前，合併後，退回到待抵扣，就要刪掉BillMaster及BillDetail
- 已抵扣退回，
---

## 帳單簽核
- 已產製draft後只可以更改的內容為
  * 時間(BillMaster.IssueDate、BillMaster.DueDate)
---