# @router.post("/getBillMaster&BillDetailStream")
# async def initBillMasterAndBillDetail(request: Request, db: Session = Depends(get_db)):
#     """
#     {
#         "InvoiceMaster": [
#             {...},
#             {...},
#             {...}
#         ]
#     }
#     """
#     request_data = await request.json()
#     InvoiceMasterIdList = [
#         InvoiceMasterDictData["InvMasterID"]
#         for InvoiceMasterDictData in request_data["InvoiceMaster"]
#     ]
#
#     crudInvoiceDetail = CRUD(db, InvoiceDetailDBModel)
#     crudInvoiceMaster = CRUD(db, InvoiceMasterDBModel)
#     crudBillMaster = CRUD(db, BillMasterDBModel)
#     crudBillDetail = CRUD(db, BillDetailDBModel)
#
#     InvoiceMasterDataList = crudInvoiceMaster.get_value_if_in_a_list(
#         InvoiceMasterDBModel.InvMasterID, InvoiceMasterIdList
#     )
#
#     # check PartName or SubmarineCable or WorkTitle is not unique
#     try:
#         _ = await checkInitBillMasterAndBillDetailFunc(
#             {
#                 "InvoiceMaster": [
#                     orm_to_dict(InvoiceMasterData)
#                     for InvoiceMasterData in InvoiceMasterDataList
#                 ]
#             }
#         )
#     except Exception as e:
#         print(e)
#
#     InvoiceDetailDataList = crudInvoiceDetail.get_value_if_in_a_list(
#         InvoiceDetailDBModel.InvMasterID, InvoiceMasterIdList
#     )
#     InvoiceDetailDataList = list(
#         filter(
#             lambda x: x.PartyName == InvoiceMasterDataList[0].PartyName,
#             InvoiceDetailDataList,
#         )
#     )
#
#     BillingNo = f"{InvoiceMasterDataList[0].SubmarineCable}-{InvoiceMasterDataList[0].WorkTitle}-CBP-{InvoiceMasterDataList[0].PartyName}-{convert_time_to_str(datetime.now()).replace('-', '').replace(' ', '').replace(':', '')[2:-2]}"
#
#     # change InvoiceMaster status to "MERGED"
#     for InvoiceMasterData in InvoiceMasterDataList:
#         InvoiceMasterDictData = orm_to_dict(InvoiceMasterData)
#         InvoiceMasterDictData["Status"] = "MERGED"
#
#     # cal FeeAmountSum
#     FeeAmountSum = 0
#     for InvoiceDetailData in InvoiceDetailDataList:
#         FeeAmountSum += InvoiceDetailData.FeeAmountPost
#
#     # init BillMaster
#     BillMasterDictData = {
#         "BillingNo": BillingNo,
#         "SubmarineCable": InvoiceMasterDataList[0].SubmarineCable,
#         "WorkTitle": InvoiceMasterDataList[0].WorkTitle,
#         "PartyName": InvoiceMasterDataList[0].PartyName,
#         "IssueDate": convert_time_to_str(datetime.now()),
#         "DueDate": None,
#         "FeeAmountSum": FeeAmountSum,
#         "ReceivedAmountSum": 0,
#         "IsPro": InvoiceMasterDataList[0].IsPro,
#         "Status": "INITIAL",
#     }
#
#     # init BillDetail
#     BillDetailDataList = []
#     for InvoiceDetailData in InvoiceDetailDataList:
#         """
#         BillDetailData keys:
#         BillDetailID
#         BillMasterID
#         WKMasterID
#         InvDetailID
#         PartyName
#         SupplierName
#         SubmarineCable
#         WorkTitle
#         BillMilestone
#         FeeItem
#         OrgFeeAmount
#         DedAmount(抵扣金額)
#         FeeAmount(應收(會員繳)金額)
#         ReceivedAmount(累計實收(會員繳)金額(初始為0))
#         OverAmount(重溢繳金額 銷帳介面會自動計算帶出)
#         ShortAmount(短繳金額 銷帳介面會自動計算帶出)
#         ShortOverReason(短繳原因 自行輸入)
#         WriteOffDate(銷帳日期)
#         ReceiveDate(最新收款日期 自行輸入)
#         Note
#         ToCB(金額是否已存在 null or Done)
#         Status
#         """
#         BillDetailDictData = {
#             # "BillMasterID": BillMasterData.BillMasterID,
#             "WKMasterID": InvoiceDetailData.WKMasterID,
#             "InvDetailID": InvoiceDetailData.InvDetailID,
#             "InvoiceNo": InvoiceDetailData.InvoiceNo,
#             "PartyName": InvoiceDetailData.PartyName,
#             "SupplierName": InvoiceDetailData.SupplierName,
#             "SubmarineCable": InvoiceDetailData.SubmarineCable,
#             "WorkTitle": InvoiceDetailData.WorkTitle,
#             "BillMilestone": InvoiceDetailData.BillMilestone,
#             "FeeItem": InvoiceDetailData.FeeItem,
#             "OrgFeeAmount": InvoiceDetailData.FeeAmountPost,
#             "DedAmount": 0,
#             "FeeAmount": InvoiceDetailData.FeeAmountPost,
#             "ReceivedAmount": 0,
#             "OverAmount": 0,
#             "ShortAmount": 0,
#             "ShortOverReason": None,
#             "WriteOffDate": None,
#             "ReceiveDate": None,
#             "Note": None,
#             "ToCBAmount": 0,
#             "Status": "INCOMPLETE",
#         }
#         # BillDetailData = crudBillDetail.create(BillDetailSchema(**BillDetailDictData))
#         BillDetailDataList.append(BillDetailDictData)
#
#     return {
#         "message": "success",
#         "BillMaster": BillMasterDictData,
#         "BillDetail": BillDetailDataList,
#     }
class MyObject:
    def __init__(self, id, other_attributes):
        self.id = id
        self.other_attributes = other_attributes


objects = [
    MyObject(1, "foo"),
    MyObject(2, "bar"),
    MyObject(1, "baz"),
    MyObject(3, "qux"),
]

# 使用字典來確保id的唯一性
unique_objects = {obj.id: obj for obj in objects}
print(unique_objects)
# 獲得唯一物件的列表
unique_objects_list = list(unique_objects.values())

print(unique_objects_list[0].other_attributes)
