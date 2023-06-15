# 新增發票工作主檔(使用者新增發票)
* http://xxx/api/v1/generateInvoiceWKMaster&InvoiceWKDetail

# 立帳(發票工作主檔狀態變為BILLED)
* http://xxx/api/v1/addInvoiceMaster&InvoiceDetail

# 下載已簽核帳單(pdf file)
* http://xxx/api/v1/BillMaster/signedDraft/{BillMasterID}