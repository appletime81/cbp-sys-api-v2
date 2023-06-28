from fastapi import APIRouter, Request, Depends
from fastapi.responses import FileResponse

from crud import *
from get_db import get_db
from sqlalchemy.orm import Session
from utils.utils import *
from utils.log import *
from utils.orm_pydantic_convert import *
from itertools import groupby
from operator import itemgetter

import os
from copy import deepcopy
from docxtpl import DocxTemplate, InlineImage


router = APIRouter()


# region:  ------------------------------ 合併帳單 ------------------------------
@router.get("/getInvoiceMaster&InvoiceDetail/{urlCondition}")
async def getInvoiceMasterAndInvoiceDetail(
    request: Request, urlCondition: str, db: Session = Depends(get_db)
):
    crudInvoiceDetail = CRUD(db, InvoiceDetailDBModel)
    crudInvoiceMaster = CRUD(db, InvoiceMasterDBModel)
    dictCondition = None

    if urlCondition != "all":
        dictCondition = convert_url_condition_to_dict(urlCondition)
    pprint(dictCondition)

    if urlCondition == "all":
        InvoiceDetailDataList = crudInvoiceDetail.get_all()
    elif "InvoiceNo" in urlCondition:
        InvoiceNo = dictCondition.pop("InvoiceNo")
        InvoiceDetailDataList = crudInvoiceDetail.get_with_condition_and_like(
            dictCondition, InvoiceDetailDBModel.InvoiceNo, InvoiceNo
        )
    else:
        InvoiceDetailDataList = crudInvoiceDetail.get_with_condition(dictCondition)

    # 如果為空值，則直接回傳空值
    if not InvoiceDetailDataList:
        return InvoiceDetailDataList

    InvoiceMasterData = crudInvoiceMaster.get_value_if_in_a_list(
        InvoiceMasterDBModel.InvMasterID,
        list(
            set(
                [
                    InvoiceDetailData.InvMasterID
                    for InvoiceDetailData in InvoiceDetailDataList
                ]
            )
        ),
    )[0]

    InvoiceDetailDictDataList = [
        orm_to_dict(InvoiceDetailData) for InvoiceDetailData in InvoiceDetailDataList
    ]

    for i in range(len(InvoiceDetailDictDataList)):
        InvoiceDetailDictDataList[i]["IsPro"] = InvoiceMasterData.IsPro

    return InvoiceDetailDictDataList


# 檢查合併帳單的PartyName、SubmarineCable、WorkTitle是否相同
@router.post("/checkInitBillMaster&BillDetail")
async def checkInitBillMasterAndBillDetail(
    request: Request, db: Session = Depends(get_db)
):
    """
    {
        "InvoiceDetail": [
            {...},
            {...},
            {...}
        ]
    }
    """
    request_data = await request.json()
    PartyList = []
    SubmarineCableList = []
    WorkTitleList = []
    return


async def checkInitBillMasterAndBillDetailFunc(request_data, db):
    """
    {
        "InvoiceDetail": [
            {...},
            {...},
            {...}
        ]
    }
    """
    crudInvoiceMaster = CRUD(db, InvoiceMasterDBModel)

    # --------- get every InvoiceDetail's PartyName, SubmarineCable, WorkTitle and IsPro ---------
    PartyList = []
    SubmarineCableList = []
    WorkTitleList = []
    InvoiceDetailDictDataList = request_data["InvoiceDetail"]
    InvoiceMasterDataList = crudInvoiceMaster.get_value_if_in_a_list(
        InvoiceMasterDBModel.InvMasterID,
        list(
            set(
                [
                    InvoiceDetailDictData["InvMasterID"]
                    for InvoiceDetailDictData in InvoiceDetailDictDataList
                ]
            )
        ),
    )
    IsPro = list(
        set([InvoiceMasterData.IsPro for InvoiceMasterData in InvoiceMasterDataList])
    )
    for InvoiceDetailDictData in InvoiceDetailDictDataList:
        PartyList.append(InvoiceDetailDictData["PartyName"])
        SubmarineCableList.append(InvoiceDetailDictData["SubmarineCable"])
        WorkTitleList.append(InvoiceDetailDictData["WorkTitle"])
    # --------------------------------------------------------------------------------------------

    alert_msg = {}
    if len(set(PartyList)) > 1:
        alert_msg["PartyName"] = "PartyName is not unique"
        record_log(
            f"{user_name} chose the InvoiceDetails, the PartyName is not unique."
        )
    if len(set(SubmarineCableList)) > 1:
        alert_msg["SubmarineCable"] = "SubmarineCable is not unique"
        record_log(
            f"{user_name} chose the InvoiceDetails, the SubmarineCable is not unique."
        )
    if len(set(WorkTitleList)) > 1:
        alert_msg["WorkTitle"] = "WorkTitle is not unique"
        record_log(
            f"{user_name} chose the InvoiceDetails, the WorkTitle is not unique."
        )
    if len(set(IsPro)) > 1:
        alert_msg["IsPro"] = "IsPro is not unique"
        record_log(f"{user_name} chose the InvoiceDetails, the IsPro is not unique.")
    if not alert_msg:
        alert_msg["isUnique"] = True
    return alert_msg


# 待合併(合併預覽)
@router.post("/getBillMaster&BillDetailStream")
async def initBillMasterAndBillDetail(request: Request, db: Session = Depends(get_db)):
    """
    {
        "InvoiceDetail": [
            {...},
            {...},
            {...},
        ]
    }
    """
    crudInvoiceDetail = CRUD(db, InvoiceDetailDBModel)
    crudInvoiceMaster = CRUD(db, InvoiceMasterDBModel)
    InvoiceDetailDictDataList = (await request.json())["InvoiceDetail"]

    alert_msg = await checkInitBillMasterAndBillDetailFunc(
        {"InvoiceDetail": InvoiceDetailDictDataList}, db
    )

    # 檢查合併的發票明細(InvoiceDetail)是否有不同的會員名稱、海纜名稱、海纜作業
    if not alert_msg.get("isUnique"):
        return alert_msg

    InvoiceDetailDataList = crudInvoiceDetail.get_value_if_in_a_list(
        InvoiceDetailDBModel.InvDetailID,
        [
            InvoiceDetailDictData["InvDetailID"]
            for InvoiceDetailDictData in InvoiceDetailDictDataList
        ],
    )
    BillingNo = f"{InvoiceDetailDataList[0].SubmarineCable}-{InvoiceDetailDataList[0].WorkTitle}-CBP-{InvoiceDetailDataList[0].PartyName}-{convert_time_to_str(datetime.now()).replace('-', '').replace(' ', '').replace(':', '')[2:-2]}"

    # change InvoiceDetail status to "MERGED"
    BillDetailDictDataList = list()
    for InvoiceDetailData in InvoiceDetailDataList:
        InvoiceDetailDictData = deepcopy(orm_to_dict(InvoiceDetailData))
        InvoiceDetailDictData["Status"] = "MERGED"
        newBillDetailDictData = {
            "WKMasterID": InvoiceDetailDictData["WKMasterID"],
            "InvoiceNo": InvoiceDetailDictData["InvoiceNo"],
            "InvDetailID": InvoiceDetailDictData["InvDetailID"],
            "PartyName": InvoiceDetailDictData["PartyName"],
            "SupplierName": InvoiceDetailDictData["SupplierName"],
            "SubmarineCable": InvoiceDetailDictData["SubmarineCable"],
            "WorkTitle": InvoiceDetailDictData["WorkTitle"],
            "BillMilestone": InvoiceDetailDictData["BillMilestone"],
            "FeeItem": InvoiceDetailDictData["FeeItem"],
            "OrgFeeAmount": InvoiceDetailDictData["FeeAmountPost"],
            "DedAmount": 0,
            "FeeAmount": InvoiceDetailDictData["FeeAmountPost"],
            "ReceivedAmount": 0,
            "OverAmount": 0,
            "ShortAmount": 0,
            "ToCBAmount": 0,
            "PaidAmount": 0,
            "ShortOverReason": "",
            "WriteOffDate": None,
            "ReceiveDate": None,
            "Note": "",
            "Status": "",
        }
        BillDetailDictDataList.append(newBillDetailDictData)

    # init BillMaster
    BillMasterDictData = {
        "BillingNo": BillingNo,
        "SubmarineCable": InvoiceDetailDataList[0].SubmarineCable,
        "WorkTitle": InvoiceDetailDataList[0].WorkTitle,
        "PartyName": InvoiceDetailDataList[0].PartyName,
        "IssueDate": convert_time_to_str(datetime.now()),
        "DueDate": None,
        "FeeAmountSum": sum(
            [
                InvoiceDetailData.FeeAmountPost
                for InvoiceDetailData in InvoiceDetailDataList
            ]
        ),
        "ReceivedAmountSum": 0,
        "IsPro": crudInvoiceMaster.get_value_if_in_a_list(
            InvoiceMasterDBModel.InvMasterID, [InvoiceDetailDataList[0].InvMasterID]
        )[0].IsPro,
        "Status": "INITIAL",
    }

    return {
        "message": "success",
        "BillMaster": BillMasterDictData,
        "BillDetail": BillDetailDictDataList,
    }


# 待抵扣階段(for 把getBillMaster&BillDetailStream產生的初始化帳單及帳單明細資料存入db)
@router.post("/initBillMaster&BillDetail")
async def generateInitBillMasterAndBillDetail(
    request: Request, db: Session = Depends(get_db)
):
    request_data = await request.json()
    DueDate = request_data["DueDate"]
    crudBillMaster = CRUD(db, BillMasterDBModel)
    crudBillDetail = CRUD(db, BillDetailDBModel)
    crudInvoiceDetail = CRUD(db, InvoiceDetailDBModel)
    BillMasterDictData = request_data["BillMaster"]
    BillDetailDataList = request_data["BillDetail"]
    PONo = request_data["PONo"]

    # convert BillMasterDictData to BillMasterPydanticData and insert to db
    IssueDate = convert_time_to_str(datetime.now())
    if DueDate[:10] == IssueDate[:10]:
        replace_str = DueDate[11:]
        DueDate = DueDate.replace(replace_str, IssueDate[11:])
    BillMasterDictData["IssueDate"] = IssueDate
    BillMasterDictData["DueDate"] = DueDate
    BillMasterDictData["PONo"] = PONo
    BillMasterPydanticData = BillMasterSchema(**BillMasterDictData)
    BillMasterData = crudBillMaster.create(BillMasterPydanticData)

    newBillDetailDataList = []
    for BillDetailData in BillDetailDataList:
        BillDetailData["BillMasterID"] = BillMasterData.BillMasterID
        BillDetailPydanticData = BillDetailSchema(**BillDetailData)
        BillDetailData = crudBillDetail.create(BillDetailPydanticData)
        newBillDetailDataList.append(BillDetailData)

    InvDetailIDList = list(
        set(
            [
                newBillDetailData.InvDetailID
                for newBillDetailData in newBillDetailDataList
            ]
        )
    )
    InvoiceDetailDataList = crudInvoiceDetail.get_value_if_in_a_list(
        InvoiceDetailDBModel.InvDetailID, InvDetailIDList
    )
    for i, newInvoiceDetailData in enumerate(InvoiceDetailDataList):
        newInvoiceDetailData.Status = "MERGED"
        _ = crudInvoiceDetail.update(
            InvoiceDetailDataList[i], orm_to_dict(newInvoiceDetailData)
        )

    # 紀錄使用者操作log
    record_log(
        f"{user_name} initial BillMaster, BillingNo is {BillMasterData.BillingNo}"
    )

    return {
        "message": "success",
        "BillMaster": BillMasterData,
        "BillDetail": newBillDetailDataList,
    }


# 查詢帳單主檔&帳單明細檔
@router.get("/getBillMaster&BillDetail/{urlCondition}")
async def getBillMasterAndBillDetail(urlCondition: str, db: Session = Depends(get_db)):
    print(urlCondition)
    crudBillMaster = CRUD(db, BillMasterDBModel)
    crudBillDetail = CRUD(db, BillDetailDBModel)
    BillingNo = None
    table_name = "BillMaster"
    getResult = []
    if urlCondition == "all":
        BillMasterDataList = crudBillMaster.get_all()
        for BillMasterData in BillMasterDataList:
            BillDetailDataList = crudBillDetail.get_with_condition(
                {"BillMasterID": BillMasterData.BillMasterID}
            )
            getResult.append(
                {
                    "BillMaster": BillMasterData,
                    "BillDetail": BillDetailDataList,
                }
            )
    elif "start" in urlCondition and "end" in urlCondition:
        dictCondition = convert_url_condition_to_dict(urlCondition)
        if "BillingNo" in urlCondition:
            BillingNo = dictCondition.pop("BillingNo")
        sqlCondition = convert_dict_to_sql_condition(dictCondition, table_name)
        BillMasterDataList = crudBillMaster.get_all_by_sql(sqlCondition)
        for BillMasterData in BillMasterDataList:
            BillDetailDataList = crudBillDetail.get_with_condition(
                {"BillMasterID": BillMasterData.BillMasterID}
            )
            getResult.append(
                {
                    "BillMaster": BillMasterData,
                    "BillDetail": BillDetailDataList,
                }
            )
    else:
        dictCondition = convert_url_condition_to_dict(urlCondition)
        if "Status" in dictCondition:
            if "%" in dictCondition["Status"]:
                dictCondition["Status"] = dictCondition["Status"].split("%")[0]
        pprint(dictCondition)
        if "BillingNo" in urlCondition:
            BillingNo = dictCondition.pop("BillingNo")
        BillMasterDataList = crudBillMaster.get_with_condition(dictCondition)
        for BillMasterData in BillMasterDataList:
            BillDetailDataList = crudBillDetail.get_with_condition(
                {"BillMasterID": BillMasterData.BillMasterID}
            )
            getResult.append(
                {
                    "BillMaster": BillMasterData,
                    "BillDetail": BillDetailDataList,
                }
            )

    return getResult


# 待抵扣階段(for 執行抵扣，更新初始化的帳單主檔及帳單明細資料庫)
@router.post("/generateBillMaster&BillDetail")
async def generateBillMasterAndBillDetail(
    request: Request, db: Session = Depends(get_db)
):
    """
    {
        "BillMaster": {...},
        "Deduct": [
            {
                "BillDetailID": 1,
                "CB": [
                    {
                        "CBID": 1,
                        "TransAmount": 1000
                    },
                    {...},
                    {...}
                ]
            },
            {...},
            {...}
        ]
    }
    """
    crudBillMaster = CRUD(db, BillMasterDBModel)
    crudBillDetail = CRUD(db, BillDetailDBModel)
    crudCreditBalance = CRUD(db, CreditBalanceDBModel)
    crudCreditBalanceStatement = CRUD(db, CreditBalanceStatementDBModel)

    BillMasterDictData = (await request.json())["BillMaster"]
    oldBillMasterData = crudBillMaster.get_with_condition(
        {"BillMasterID": BillMasterDictData["BillMasterID"]}
    )[0]
    newBillMasterData = deepcopy(oldBillMasterData)
    pprint((await request.json()))
    deductDataList = (await request.json())["Deduct"]
    deductDataList = sorted(deductDataList, key=lambda x: x["BillDetailID"])

    LastUpDate = CreateDate = convert_time_to_str(datetime.now())
    newBillDetailDataList = []
    for deductData in deductDataList:
        oldBillDetailData = crudBillDetail.get_with_condition(
            {"BillDetailID": deductData["BillDetailID"]}
        )[0]
        newBillDetailData = deepcopy(oldBillDetailData)

        reqCBDataList = deductData["CB"]
        tempTotalDedAmount = 0
        for reqCBData in reqCBDataList:
            oldCBData = crudCreditBalance.get_with_condition(
                {"CBID": reqCBData["CBID"]}
            )[0]
            newCBData = deepcopy(oldCBData)
            newCBDictData = orm_to_dict(newCBData)
            newCBDictData["CurrAmount"] -= reqCBData["TransAmount"]
            newCBDictData["LastUpdDate"] = LastUpDate

            newCBStatementDictData = {
                "CBID": newCBDictData["CBID"],
                "BillingNo": BillMasterDictData["BillingNo"],
                "BLDetailID": newBillDetailData.BillDetailID,
                "TransItem": "DEDUCT",
                "OrgAmount": oldCBData.CurrAmount,
                "TransAmount": reqCBData["TransAmount"] * (-1),
                "Note": "",
                "CreateDate": CreateDate,
            }

            tempTotalDedAmount += reqCBData["TransAmount"]

            # update CreditBalance
            crudCreditBalance.update(oldCBData, newCBDictData)

            # insert CreditBalanceStatement
            crudCreditBalanceStatement.create(
                dict_to_pydantic(CreditBalanceStatementSchema, newCBStatementDictData)
            )

        # update BillDetail
        newBillDetailData.DedAmount = tempTotalDedAmount
        newBillDetailData.FeeAmount = (
            newBillDetailData.OrgFeeAmount - newBillDetailData.DedAmount
        )
        newBillDetailData = crudBillDetail.update(
            oldBillDetailData, orm_to_dict(newBillDetailData)
        )
        newBillDetailDataList.append(newBillDetailData)

    # update BillMaster
    newBillMasterData.FeeAmountSum -= sum(
        [newBillDetailData.DedAmount for newBillDetailData in newBillDetailDataList]
    )
    newBillMasterData.Status = "RATED"
    crudBillMaster.update(oldBillMasterData, orm_to_dict(newBillMasterData))

    # 紀錄使用者操作
    record_log(
        f"{user_name} completed the deduction of the BillMaster: {orm_to_dict(newBillMasterData)}"
    )

    return {
        "message": "success",
        "BillMaster": newBillMasterData,
        "BillDetail": newBillDetailDataList,
    }


# 待抵扣階段(for 執行抵扣，預覽)
# @router.post("/generateBillMaster&BillDetail/preview")
# async def generateBillMasterAndBillDetail(
#     request: Request, db: Session = Depends(get_db)
# ):
#     """
#     {
#         "BillMaster": {...},
#         "Deduct": [
#             {
#                 "BillDetailID": 1,
#                 "CB": [
#                     {
#                         "CBID": 1,
#                         "TransAmount": 1000
#                     },
#                     {...},
#                     {...}
#                 ]
#             },
#             {...},
#             {...}
#         ]
#     }
#     -------------------------------------------------------------
#     dataProcessRecord = {
#         "BillDetail": None,
#         "CBList": [
#             {
#                 "CB": {...},
#                 "CBStatement": {...}
#             },
#             {...}
#         ]
#     }
#     """
#     crudBillMaster = CRUD(db, BillMasterDBModel)
#     crudBillDetail = CRUD(db, BillDetailDBModel)
#     crudCreditBalance = CRUD(db, CreditBalanceDBModel)
#     crudCreditBalanceStatement = CRUD(db, CreditBalanceStatementDBModel)
#
#     BillMasterDictData = (await request.json())["BillMaster"]
#     oldBillMasterData = crudBillMaster.get_with_condition(
#         {"BillMasterID": BillMasterDictData["BillMasterID"]}
#     )[0]
#     newBillMasterData = deepcopy(oldBillMasterData)
#
#     deductDataList = (await request.json())["Deduct"]
#     deductDataList = sorted(deductDataList, key=lambda x: x["BillDetailID"])
#
#     recordDeductProcess = {"BillMaster": None, "BillDetailProcess": []}
#
#     newBillDetailDataList = []
#     for deductData in deductDataList:
#         dataProcessRecord = {
#             "BillDetail": None,
#             "CBList": [],
#         }
#         oldBillDetailData = crudBillDetail.get_with_condition(
#             {"BillDetailID": deductData["BillDetailID"]}
#         )[0]
#         newBillDetailData = deepcopy(oldBillDetailData)
#
#         reqCBDataList = deductData["CB"]
#         tempTotalDedAmount = 0
#         for reqCBData in reqCBDataList:
#             oldCBData = crudCreditBalance.get_with_condition(
#                 {"CBID": reqCBData["CBID"]}
#             )[0]
#             newCBData = deepcopy(oldCBData)
#             newCBDictData = orm_to_dict(newCBData)
#             newCBDictData["CurrAmount"] -= reqCBData["TransAmount"]
#             newCBDictData["LastUpdDate"] = convert_time_to_str(datetime.now())
#             newCBStatementDictData = {
#                 "CBID": newCBDictData["CBID"],
#                 "BillingNo": BillMasterDictData["BillingNo"],
#                 "BLDetailID": newBillDetailData.BillDetailID,
#                 "TransItem": "DEDUCT",
#                 "OrgAmount": oldCBData.CurrAmount,
#                 "TransAmount": reqCBData["TransAmount"] * (-1),
#                 "Note": "",
#                 "CreateDate": convert_time_to_str(datetime.now()),
#             }
#
#             tempTotalDedAmount += reqCBData["TransAmount"]
#
#             # update CreditBalance
#             dataProcessRecord["CBList"].append(
#                 {"CB": newCBDictData, "CBStatement": newCBStatementDictData}
#             )
#
#         # update BillDetail
#         newBillDetailData.DedAmount = tempTotalDedAmount
#         newBillDetailData.FeeAmount = (
#             newBillDetailData.OrgFeeAmount - newBillDetailData.DedAmount
#         )
#         newBillDetailDataList.append(newBillDetailData)
#
#         dataProcessRecord["BillDetail"] = orm_to_dict(newBillDetailData)
#         recordDeductProcess["BillDetailProcess"].append(dataProcessRecord)
#     # update BillMaster
#     newBillMasterData.FeeAmountSum -= sum(
#         [newBillDetailData.DedAmount for newBillDetailData in newBillDetailDataList]
#     )
#     newBillMasterData.Status = "RATED"
#     recordDeductProcess["BillMaster"] = orm_to_dict(newBillMasterData)
#
#     return {"message": "success", "previewData": recordDeductProcess}


# 抓取帳單主檔及可抵扣CB
@router.get("/getBillMaster&BillDetailWithCBData/{urlCondition}")
async def getBillMasterAndBillDetailWithCBData(
    request: Request, urlCondition: str, db: Session = Depends(get_db)
):
    getResult = list()

    table_name = "BillMaster"
    crudBillMaster = CRUD(db, BillMasterDBModel)
    crudBillDetail = CRUD(db, BillDetailDBModel)
    crudCreditBalance = CRUD(db, CreditBalanceDBModel)
    crudCreditBalanceStatement = CRUD(db, CreditBalanceStatementDBModel)

    # ---------- get BillMaster ----------
    BillingNo = None
    dictCondition = None
    if urlCondition != "all":
        dictCondition = convert_url_condition_to_dict(urlCondition)
        if "BillingNo" in dictCondition:
            BillingNo = dictCondition.pop("BillingNo")
    if urlCondition == "all":
        BillMasterDataList = crudBillMaster.get_all()
    elif "start" in urlCondition and "end" in urlCondition:
        sql_condition = convert_dict_to_sql_condition(dictCondition, table_name)
        BillMasterDataList = crudBillMaster.get_all_by_sql(sql_condition)
    else:
        BillMasterDataList = crudBillMaster.get_with_condition(dictCondition)

    for BillMasterData in BillMasterDataList:
        tempDictData = {"BillMaster": BillMasterData}
        tempListData = list()
        tempBillDetailDataList = crudBillDetail.get_with_condition(
            {"BillMasterID": BillMasterData.BillMasterID}
        )
        for tempBillDetailData in tempBillDetailDataList:
            tempCBStatementDataList = crudCreditBalanceStatement.get_with_condition(
                {"BLDetailID": tempBillDetailData.BillDetailID}
            )
            tempCBDictDataList = list()
            for tempCBStatementData in tempCBStatementDataList:
                tempCBData = crudCreditBalance.get_with_condition(
                    {"CBID": tempCBStatementData.CBID}
                )[0]
                tempCBDictData = orm_to_dict(tempCBData)
                tempCBDictDataList.append(tempCBDictData)

            tempListData.append(
                {"BillDetail": tempBillDetailData, "CB": tempCBDictDataList}
            )

        tempDictData["data"] = tempListData
        getResult.append(tempDictData)

    if BillingNo:
        newGetResult = list()
        for result in getResult:
            if BillingNo in result["BillMaster"].BillingNo:
                newGetResult.append(result)
        getResult = newGetResult
    return getResult


# endregion:  -----------------------------------------------------------------


# region: ------------------------------- 產製帳單 -------------------------------
# 產製帳單draft(初始化)


@router.post("/getBillMasterDraftStream")
async def getBillMasterDraftStream(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    {
      "BillMasterID": 1,
      "UserID": "username",
      "GetTemplate": true,
      "IssueDate": "2023/04/01",
      "DueDate": "2023/04/30",
      "WorkTitle": "Construction #11",
      "InvoiceName": "",
      "logo": 1
    }
    """
    crudInvoiceDetail = CRUD(db, InvoiceDetailDBModel)
    crudBillMaster = CRUD(db, BillMasterDBModel)
    crudBillDetail = CRUD(db, BillDetailDBModel)
    crudCB = CRUD(db, CreditBalanceDBModel)
    crudCBStatement = CRUD(db, CreditBalanceStatementDBModel)
    crudCNDetail = CRUD(db, CreditNoteDetailDBModel)
    crudCorporates = CRUD(db, CorporatesDBModel)
    crudParties = CRUD(db, PartiesDBModel)
    crudUsers = CRUD(db, UsersDBModel)

    # --------------------------- 抓取帳單主檔及帳單明細 ---------------------------
    BillMasterData = crudBillMaster.get_with_condition(
        {"BillMasterID": (await request.json())["BillMasterID"]}
    )[0]
    BillDetailDataList = crudBillDetail.get_with_condition(
        {"BillMasterID": BillMasterData.BillMasterID}
    )
    BillDetailDictDataList = [
        orm_to_dict(BillDetailData) for BillDetailData in BillDetailDataList
    ]
    for i, BillDetailDictData in enumerate(BillDetailDictDataList):
        InvDetailID = BillDetailDictData["InvDetailID"]
        InvoiceDetailData = crudInvoiceDetail.get_with_condition(
            {"InvDetailID": InvDetailID}
        )[0]
        BillDetailDictDataList[i]["LBRatio"] = InvoiceDetailData.LBRatio
        BillDetailDictDataList[i]["FeeAmountPre"] = InvoiceDetailData.FeeAmountPre

    # --------------------------- 抓取會員資訊 ---------------------------
    PartyData = crudParties.get_with_condition({"PartyName": BillMasterData.PartyName})[
        0
    ]

    # --------------------------- 抓取聯盟資料表(含金融帳戶資訊) ---------------------------
    CorporateData = crudCorporates.get_with_condition(
        {"SubmarineCable": BillMasterData.SubmarineCable}
    )[0]

    # --------------------------- 抓取使用者資料 ---------------------------
    UserData = crudUsers.get_with_condition(
        {"UserID": (await request.json())["UserID"]}
    )[0]

    ContactWindowAndSupervisorInformationDictData = {
        # give html reponse for company
        "Company": UserData.Company,
        "Address": UserData.Address,
        "Tel": UserData.Tel,
        "Fax": UserData.Fax,
        "DirectorName": UserData.DirectorName,
        "DTel": UserData.DTel,
        "DFax": UserData.DFax,
        "DEmail": UserData.DEmail,
    }

    PartyInformationDictData = {
        "Company": PartyData.CompanyName,
        "Address": PartyData.Address,
        "Contact": PartyData.Contact,
        "Email": PartyData.Email,
        "Tel": PartyData.Tel,
    }

    CorporateDictData = {
        "BankName": CorporateData.BankName,  # Bank Name
        "Branch": CorporateData.Branch,  # Branch Name
        "BranchAddress": CorporateData.BranchAddress,  # Branch Address
        "BankAcctName": CorporateData.BankAcctName,  # Account Name
        "BankAcctNo": CorporateData.BankAcctNo,  # AC No.
        "SavingAcctNo": CorporateData.SavingAcctNo,  # Saving Account No
        "IBAN": CorporateData.IBAN,  # IBAN
        "SWIFTCode": CorporateData.SWIFTCode,  # Swift
        "ACHNo": CorporateData.ACHNo,  # ACH
        "WireRouting": CorporateData.WireRouting,  # Wire/Routing
        "Address": CorporateData.Address,  # Address
    }
    BLDetailIDList = [
        BillDetailDictData["BillDetailID"]
        for BillDetailDictData in BillDetailDictDataList
    ]
    CBStatementDataList = crudCBStatement.get_value_if_in_a_list(
        CreditBalanceStatementDBModel.BLDetailID, BLDetailIDList
    )
    DetailInformationDictData = {
        "Supplier": list(),
        "InvNumber": list(),
        "Description": list(),
        "BilledAmount": list(),
        "Liability": list(),
        "ShareAmount": list(),
    }

    for BillDetailDictData in BillDetailDictDataList:
        InvoiceDetailData = crudInvoiceDetail.get_with_condition(
            {"InvDetailID": BillDetailDictData["InvDetailID"]}
        )[0]
        DetailInformationDictData["Supplier"].append(BillDetailDictData["SupplierName"])
        DetailInformationDictData["InvNumber"].append(BillDetailDictData["InvoiceNo"])
        DetailInformationDictData["Description"].append(BillDetailDictData["FeeItem"])
        DetailInformationDictData["BilledAmount"].append(InvoiceDetailData.FeeAmountPre)
        DetailInformationDictData["Liability"].append(InvoiceDetailData.LBRatio)
        DetailInformationDictData["ShareAmount"].append(
            BillDetailDictData["OrgFeeAmount"]
        )
    if CBStatementDataList:
        for CBStatementData in CBStatementDataList:
            CBData = crudCB.get_with_condition({"CBID": CBStatementData.CBID})[0]
            BillDetailDictData = next(
                filter(
                    lambda x: x["BillDetailID"] == CBStatementData.BLDetailID,
                    BillDetailDictDataList,
                )
            )
            DetailInformationDictData["Supplier"].append(
                BillDetailDictData["SupplierName"]
            )
            DetailInformationDictData["Description"].append(
                BillDetailDictData["FeeItem"]
            )
            DetailInformationDictData["BilledAmount"].append(
                CBStatementData.TransAmount
            )
            DetailInformationDictData["Liability"].append(100)
            DetailInformationDictData["ShareAmount"].append(CBStatementData.TransAmount)
            if CBData.CNNo:
                DetailInformationDictData["InvNumber"].append(CBData.CNNo)
            else:
                DetailInformationDictData["InvNumber"].append(CBData.BillingNo)

    DetailInformationDictDataList = list()
    No = 1
    for supplier, invNumber, description, amountBilled, liability, yourShare in zip(
        DetailInformationDictData["Supplier"],
        DetailInformationDictData["InvNumber"],
        DetailInformationDictData["Description"],
        DetailInformationDictData["BilledAmount"],
        DetailInformationDictData["Liability"],
        DetailInformationDictData["ShareAmount"],
    ):
        DetailInformationDictDataList.append(
            {
                "Supplier": supplier,
                "InvNumber": invNumber if invNumber else "",
                "Description": description,
                "BilledAmount": amountBilled,
                "Liability": liability,
                "ShareAmount": yourShare,
                "No": str(No),
            }
        )
        No += 1

    getResult = {
        "ContactWindowAndSupervisorInformation": ContactWindowAndSupervisorInformationDictData,
        "PartyInformation": PartyInformationDictData,
        "CorporateInformation": CorporateDictData,
        "DetailInformation": DetailInformationDictDataList,
        "InvoiceNo": BillMasterData.BillingNo,
    }
    # if (await request.json())["GetTemplate"]:
    #     return getResult
    if not (await request.json()).get("logo"):
        return getResult

    # ----------- 先清空所有的docx文件 -----------
    docxFiles = os.listdir(os.getcwd())
    for docxFile in docxFiles:
        if docxFile.endswith(".docx"):
            try:
                os.system(f"rm -rf {docxFile}")
            except Exception as e:
                print(e)
    # -----------------------------------------

    # --------- generate word file ---------
    doc = DocxTemplate("templates/bill_draft_tpl.docx")

    logo_path = (
        "images/logo_001.png"
        if (await request.json())["logo"] == 1
        else "images/logo_002.png"
    )

    BillingInfo = getResult["DetailInformation"]
    origBillingInfo = deepcopy(BillingInfo)
    for item in BillingInfo:
        item["BilledAmount"] = convert_number_to_string(
            "{:.2f}".format(item["BilledAmount"]).split(".")
        )
        item["Liability"] = convert_number_to_string(
            "{:.10f}".format(item["Liability"]).split(".")
        )
        item["ShareAmount"] = convert_number_to_string(
            "{:.2f}".format(item["ShareAmount"]).split(".")
        )
    context = {
        "submarinecable": BillMasterData.SubmarineCable,
        "worktitle": (await request.json())["WorkTitle"],
        "invoicename": (await request.json())["InvoiceName"],
        "PartyCompany": getResult["PartyInformation"]["Company"],
        "PartyAddress": getResult["PartyInformation"]["Address"],
        "PartyContact": getResult["PartyInformation"]["Contact"],
        "PartyEmail": getResult["PartyInformation"]["Email"],
        "PartyTel": getResult["PartyInformation"]["Tel"],
        "BillingInfo": BillingInfo,
        "TotalAmount": convert_number_to_string(
            "{:.2f}".format(
                sum([float(i["ShareAmount"]) for i in origBillingInfo])
            ).split(".")
        ),
        "ContactWindowCompany": getResult["ContactWindowAndSupervisorInformation"][
            "Company"
        ],
        "ContactWindowAddress": getResult["ContactWindowAndSupervisorInformation"][
            "Address"
        ],
        "ContactWindowTel": getResult["ContactWindowAndSupervisorInformation"]["Tel"],
        "ContactWindowFax": getResult["ContactWindowAndSupervisorInformation"]["Fax"],
        "ContactWindowDirectorName": getResult["ContactWindowAndSupervisorInformation"][
            "DirectorName"
        ],
        "ContactWindowDTel": getResult["ContactWindowAndSupervisorInformation"]["DTel"],
        "ContactWindowDFax": getResult["ContactWindowAndSupervisorInformation"]["DFax"],
        "ContactWindowDEmail": getResult["ContactWindowAndSupervisorInformation"][
            "DEmail"
        ],
        # "CorporateBankName": getResult["CorporateInformation"]["BankName"],
        "CorporateBankName": f"Bank Name: {getResult['CorporateInformation']['BankName']}"
        if getResult["CorporateInformation"]["BankName"]
        else "",
        # "CorporateBranch": getResult["CorporateInformation"]["Branch"]
        # if getResult["CorporateInformation"]["Branch"]
        # else "n/a",
        "CorporateBranch": f"Branch Name: {getResult['CorporateInformation']['Branch']}"
        if getResult["CorporateInformation"]["Branch"]
        else "",
        # "CorporateBranchAddress": getResult["CorporateInformation"]["BranchAddress"]
        # if getResult["CorporateInformation"]["BranchAddress"]
        # else "n/a",
        "CorporateBranchAddress": f"Branch Address: {getResult['CorporateInformation']['BranchAddress']}"
        if getResult["CorporateInformation"]["BranchAddress"]
        else "",
        # "CorporateBankAcctName": getResult["CorporateInformation"]["BankAcctName"]
        # if getResult["CorporateInformation"]["BankAcctName"]
        # else "n/a",
        "CorporateBankAcctName": f"A/C Name: {getResult['CorporateInformation']['BankAcctName']}"
        if getResult["CorporateInformation"]["BankAcctName"]
        else "",
        # "CorporateBankAcctNo": getResult["CorporateInformation"]["BankAcctNo"]
        # if getResult["CorporateInformation"]["BankAcctNo"]
        # else "n/a",
        "CorporateBankAcctNo": f"A/C No.: {getResult['CorporateInformation']['BankAcctNo']}"
        if getResult["CorporateInformation"]["BankAcctNo"]
        else "",
        # "CorporateSavingAcctNo": getResult["CorporateInformation"]["SavingAcctNo"]
        # if getResult["CorporateInformation"]["SavingAcctNo"]
        # else "n/a",
        "CorporateSavingAcctNo": f"Saving A/C No.: {getResult['CorporateInformation']['SavingAcctNo']}"
        if getResult["CorporateInformation"]["SavingAcctNo"]
        else "",
        # "CorporateIBAN": getResult["CorporateInformation"]["IBAN"]
        # if getResult["CorporateInformation"]["IBAN"]
        # else "n/a",
        "CorporateIBAN": f"IBAN: {getResult['CorporateInformation']['IBAN']}"
        if getResult["CorporateInformation"]["IBAN"]
        else "",
        # "CorporateSWIFTCode": getResult["CorporateInformation"]["SWIFTCode"],
        "CorporateSWIFTCode": f"SWIFT Code: {getResult['CorporateInformation']['SWIFTCode']}"
        if getResult["CorporateInformation"]["SWIFTCode"]
        else "",
        # "CorporateACHNo": getResult["CorporateInformation"]["ACHNo"]
        "CorporateACHNo": f"ACH No.: {getResult['CorporateInformation']['ACHNo']}"
        if getResult["CorporateInformation"]["ACHNo"]
        else "",
        # "CorporateWireRouting": getResult["CorporateInformation"]["WireRouting"]
        "CorporateWireRouting": f"Wire / Routing: {getResult['CorporateInformation']['WireRouting']}"
        if getResult["CorporateInformation"]["WireRouting"]
        else "",
        "IssueDate": (await request.json())["IssueDate"],
        "DueDate": (await request.json())["DueDate"],
        "InvoiceNo": getResult["InvoiceNo"],
        "logo": InlineImage(doc, logo_path),
        "PONo": f"PO No.: {BillMasterData.PONo}" if BillMasterData.PONo else "",
    }
    doc.render(context)
    titleName = f"{context['submarinecable']} Cable Network {context['worktitle']} Central Billing Party"
    titleName = (
        f"{titleName} {context['invoicename']} Invoice"
        if context["invoicename"]
        else f"{titleName} Invoice"
    )
    fileName = getResult["InvoiceNo"]
    doc.save(f"{fileName}.docx")

    # --------- 更新BillMaster IssueDate、DueDate ---------
    newBillMasterDictData = orm_to_dict(deepcopy(BillMasterData))
    newBillMasterDictData["IssueDate"] = (await request.json())["IssueDate"].replace(
        "/", "-"
    ) + " 00:00:00"
    newBillMasterDictData["DueDate"] = (await request.json())["DueDate"].replace(
        "/", "-"
    ) + " 00:00:00"
    crudBillMaster.update(BillMasterData, newBillMasterDictData)

    # 紀錄使用者下載紀錄
    record_log(
        f"{user_name} downloaded {fileName}.docx, title is {titleName}, logo is {(await request.json()).get('logo')}"
    )

    resp = FileResponse(path=f"{fileName}.docx", filename=f"{fileName}.docx")
    return resp


# @router.get("/updateBillMasterByDraftStream")
# async def updateBillMasterByDraftStream(
#     request: Request, db: Session = Depends(get_db)
# ):
#     """
#     {
#         "BillMasterID": 1,
#         "IssueDate": "2020-01-01 00:00:00",
#         "DueDate": "2020-01-01 00:00:00",
#     }
#     """
#     request_data = await request.json()
#     crudBillMaster = CRUD(db, BillMasterDBModel)
#     BillMasterData = crudBillMaster.get_with_condition(
#         {"BillMasterID": request_data["BillMasterID"]}
#     )[0]
#     BillMasterDictData = orm_to_dict(BillMasterData)
#     BillMasterDictData["IssueDate"] = request_data["IssueDate"]
#     BillMasterDictData["DueDate"] = request_data["DueDate"]
#
#     newBillMasterData = crudBillMaster.update(BillMasterData, BillMasterDictData)
#
#     return {"newBillMaster": newBillMasterData}


# endregion: --------------------------------------------------------------------


# region: ------------------------------ 退回及作廢 ------------------------------


# 未抵扣退回
@router.post("/returnBillMaster/beforeduction")
async def returnBillMasterBeforeDeduction(
    request: Request, db: Session = Depends(get_db)
):
    """
    input data:
    {
        "BillMasterID": int,
        "Note": str
    }
    """
    crudInvoiceDetail = CRUD(db, InvoiceDetailDBModel)
    crudBillMaster = CRUD(db, BillMasterDBModel)
    crudBillDetail = CRUD(db, BillDetailDBModel)

    BillMasterID = (await request.json())["BillMasterID"]
    BillDetailDataList = crudBillDetail.get_with_condition(
        {"BillMasterID": BillMasterID}
    )

    InvDetailIDList = list(
        set([BillDetailData.InvDetailID for BillDetailData in BillDetailDataList])
    )

    InvoiceDetailDataList = crudInvoiceDetail.get_value_if_in_a_list(
        InvoiceDetailDBModel.InvDetailID, InvDetailIDList
    )

    # =============================================
    # 刪除BillMaster
    # =============================================
    crudBillMaster.remove(BillMasterID)

    # =============================================
    # 刪除BillDetail
    # =============================================
    for BillDetailData in BillDetailDataList:
        crudBillDetail.remove(BillDetailData.BillDetailID)

    # =============================================
    # 更改InvoiceDetail狀態
    # =============================================
    newInvoiceDetailDictDataList = []
    for InvoiceDetailData in InvoiceDetailDataList:
        newInvoiceDetailDictData = orm_to_dict(deepcopy(InvoiceDetailData))
        newInvoiceDetailDictData["Status"] = "TO_MERGE"
        newInvoiceDetailDictDataList.append(newInvoiceDetailDictData)

    newInvoiceDetailDataList = []
    for newInvoiceDetailDictData, oldInvoiceDetailData in zip(
        newInvoiceDetailDictDataList, InvoiceDetailDataList
    ):
        newInvoiceDetailData = crudInvoiceDetail.update(
            oldInvoiceDetailData, newInvoiceDetailDictData
        )
        newInvoiceDetailDataList.append(newInvoiceDetailData)

    return {"message": "success", "InvoiceDetail": newInvoiceDetailDataList}


# # 未抵扣作廢
# @router.post("/invalidBillMaster/beforededuction")
# async def invlaidBillMasterBeforeDeduction(
#     request: Request, db: Session = Depends(get_db)
# ):
#     """
#     input data:
#     {
#         "BillMasterID": int,
#         "Note": str
#     }
#     """
#     crudBillMaster = CRUD(db, BillMasterDBModel)
#     crudBillDetail = CRUD(db, BillDetailDBModel)
#
#     BillMasterID = (await request.json())["BillMasterID"]
#     Note = None
#     if "Note" in (await request.json()).keys():
#         Note = (await request.json())["Note"]
#
#     BillMasterData = crudBillMaster.get_with_condition({"BillMasterID": BillMasterID})[
#         0
#     ]
#     BillDetailDataList = crudBillDetail.get_with_condition(
#         {"BillMasterID": BillMasterID}
#     )
#
#     # =============================================
#     # 變更BillMaster狀態
#     # =============================================
#     newBillMasterData = deepcopy(BillMasterData)
#     newBillMasterData.Status = "INVALID"
#     newBillMasterData = crudBillMaster.update(
#         BillMasterData, orm_to_dict(newBillMasterData)
#     )
#
#     # =============================================
#     # 變更BillDetail狀態
#     # =============================================
#     newBillDetailDictDataList = []
#     for BillDetailData in BillDetailDataList:
#         newBillDetailData = deepcopy(BillDetailData)
#         newBillDetailData.Status = "INVALID"
#         if Note:
#             newBillDetailData.Note = Note
#         newBillDetailDictDataList.append(orm_to_dict(newBillDetailData))
#
#     newBillDetailDataList = []
#     for newBillDetailDictData, oldBillDetailData in zip(
#         newBillDetailDictDataList, BillDetailDataList
#     ):
#         newBillDetailData = crudBillDetail.update(
#             oldBillDetailData, newBillDetailDictData
#         )
#         newBillDetailDataList.append(newBillDetailData)
#
#     return {
#         "message": "success",
#         "BillMaster": newBillMasterData,
#         "BillDetail": newBillDetailDataList,
#     }


# 已抵扣退回至未抵扣
@router.post("/returnBillMaster/afterdeduction")
async def returnBillMasterAfterDeduction(
    request: Request, db: Session = Depends(get_db)
):
    """
    input data
    {
        "BillMasterID": int,
        "Note": str
    }
    """

    dictCondition = await request.json()
    Note = None
    if dictCondition.get("Note"):
        Note = dictCondition.pop("Note")
    crudBillMaster = CRUD(db, BillMasterDBModel)
    crudBillDetail = CRUD(db, BillDetailDBModel)
    crudInvoiceDetail = CRUD(db, InvoiceDetailDBModel)
    crudCreditBalance = CRUD(db, CreditBalanceDBModel)
    crudCreditBalanceStatement = CRUD(db, CreditBalanceStatementDBModel)

    BillMasterData = crudBillMaster.get_with_condition(dictCondition)[0]
    BillDetailDataList = crudBillDetail.get_with_condition(dictCondition)
    BillDetailDataList.sort(key=lambda x: x.BillDetailID, reverse=True)

    # =============================================
    # 處理CreditBalanceStatement資料               #
    # =============================================
    newCBStatementDictDataList = []
    CBStatementCreateDate = convert_time_to_str(datetime.now())
    for BillDetailData in BillDetailDataList:
        # 抓取對應BillDetail的CreditBalanceStatement
        tempCBStatementDataList = crudCreditBalanceStatement.get_with_condition(
            {"BLDetailID": BillDetailData.BillDetailID}
        )
        tempCBStatementDictDataList = [
            orm_to_dict(tempCBStatementData)
            for tempCBStatementData in tempCBStatementDataList
        ]

        # Filter TransItem is DEDUCT and sort by CreateDate
        tempCBStatementDictDataList = sorted(
            [d for d in tempCBStatementDictDataList if d["TransItem"] == "DEDUCT"],
            key=lambda x: x["CreateDate"],
            reverse=True,
        )
        print(tempCBStatementDictDataList)
        if tempCBStatementDictDataList:
            # Groupby CreateDate and get the first group
            tempCBStatementDictDataList = next(
                iter(
                    [
                        list(group)
                        for key, group in groupby(
                            tempCBStatementDictDataList, key=lambda x: x["CreateDate"]
                        )
                    ]
                )
            )

            tempCBStatementDataList = [
                dict_to_orm(tempCBStatementDictData, CreditBalanceStatementDBModel)
                for tempCBStatementDictData in tempCBStatementDictDataList
            ]

        # 抓取對應BillDetail的CreditBalance主檔(如果有找到該BillDetail對應的CreditBalanceStatement)
        if tempCBStatementDataList:
            tempCBIDList = list(
                set(
                    [
                        tempCBStatementData.CBID
                        for tempCBStatementData in tempCBStatementDataList
                    ]
                )
            )
            tempCBDataList = crudCreditBalance.get_value_if_in_a_list(
                CreditBalanceDBModel.CBID, tempCBIDList
            )
            for tempCBData in tempCBDataList:
                # 處理CreditBalanceStatement資料
                filterCBStatementDataList = list(
                    filter(lambda x: x.CBID == tempCBData.CBID, tempCBStatementDataList)
                )
                filterCBStatementDataList.sort(key=lambda x: x.CBStateID, reverse=True)
                for filterCBStatementData in filterCBStatementDataList:
                    newCBStatementDictData = {
                        "CBID": filterCBStatementData.CBID,
                        "BillingNo": filterCBStatementData.BillingNo,
                        "BLDetailID": filterCBStatementData.BLDetailID,
                        "TransItem": "RETURN",
                        "OrgAmount": filterCBStatementData.OrgAmount
                        + filterCBStatementData.TransAmount,
                        "TransAmount": 0 - filterCBStatementData.TransAmount,
                        "Note": "",
                        "CreateDate": CBStatementCreateDate,
                    }
                    if Note:
                        newCBStatementDictData["Note"] = Note
                    newCBStatementDictDataList.append(newCBStatementDictData)

    # =============================================
    # 處理CreditBalance資料                        #
    # =============================================
    df_CBStatement = pd.DataFrame.from_records(newCBStatementDictDataList)
    newCBDictDataList = []
    if not df_CBStatement.empty:
        df_CBStatement = df_CBStatement[["CBID", "TransAmount"]]
        df_CBStatement_groupby = df_CBStatement.groupby(["CBID"]).sum(["TransAmount"])
        df_CBStatement_groupby = df_CBStatement_groupby.reset_index()  # reset index

        for i in range(len(df_CBStatement_groupby)):
            CBData = crudCreditBalance.get_with_condition(
                {"CBID": df_CBStatement_groupby.iloc[i]["CBID"]}
            )[0]
            CBDictData = orm_to_dict(deepcopy(CBData))
            CBDictData["CurrAmount"] = (
                CBDictData["CurrAmount"] + df_CBStatement_groupby.iloc[i]["TransAmount"]
            )
            CBDictData["LastUpdDate"] = CBStatementCreateDate
            if Note:
                CBDictData["Note"] = Note
            newCBDictDataList.append(CBDictData)

    # =============================================
    # 更新CreditBalance資料                        #
    # =============================================
    newCBDataList = []
    if newCBDictDataList:
        for newCBDictData in newCBDictDataList:
            oldCBData = crudCreditBalance.get_with_condition(
                {"CBID": newCBDictData["CBID"]}
            )[0]
            newCBData = crudCreditBalance.update(oldCBData, newCBDictData)
            newCBDataList.append(newCBData)

    # =============================================
    # 更新CreditBalanceStatement資料               #
    # =============================================
    newCBStatementDataList = []
    for newCBStatementDictData in newCBStatementDictDataList:
        newCBStatementPydanticData = dict_to_pydantic(
            CreditBalanceStatementSchema, newCBStatementDictData
        )
        newCBStatementData = crudCreditBalanceStatement.create(
            newCBStatementPydanticData
        )
        newCBStatementDataList.append(newCBStatementData)

    # =============================================
    # 更改BillDetail資料                           #
    # =============================================
    newBillDetailDataList = []
    for BillDetailData in BillDetailDataList:
        newBillDetailData = deepcopy(BillDetailData)
        newBillDetailData.DedAmount = 0
        newBillDetailData.FeeAmount = newBillDetailData.OrgFeeAmount
        newBillDetailData = crudBillDetail.update(
            BillDetailData, orm_to_dict(newBillDetailData)
        )
        newBillDetailDataList.append(newBillDetailData)

    # =============================================
    # 更改BillMaster資料                           #
    # =============================================
    newBillMasterData = deepcopy(BillMasterData)
    newBillMasterData.Status = "INITIAL"
    newBillMasterData.FeeAmountSum += sum(
        [
            newCBStatementData.TransAmount
            for newCBStatementData in newCBStatementDataList
        ]
    )
    newBillMasterData = crudBillMaster.update(
        BillMasterData, orm_to_dict(newBillMasterData)
    )

    return {
        "CB": newCBDataList,
        "CBStatement": newCBStatementDataList,
        "BillMaster": newBillMasterData,
        "BillDetail": newBillDetailDataList,
    }


# 已簽核作廢
@router.post("/invalidBillMaster/signed")
async def invlaidBillMasterAfterDeduction(
    request: Request, db: Session = Depends(get_db)
):
    """
    input data:
    {
        "BillMasterID": int,
        "Note": str
    }
    """
    crudInvoiceDetail = CRUD(db, InvoiceDetailDBModel)
    crudBillMaster = CRUD(db, BillMasterDBModel)
    crudBillDetail = CRUD(db, BillDetailDBModel)
    crudCreditBalance = CRUD(db, CreditBalanceDBModel)
    crudCreditBalanceStatement = CRUD(db, CreditBalanceStatementDBModel)
    Note = None
    if (await request.json()).get("Note"):
        Note = (await request.json())["Note"]
    BillMasterID = (await request.json())["BillMasterID"]

    BillDetailDataList = crudBillDetail.get_with_condition(
        {"BillMasterID": BillMasterID}
    )
    BillDetailDataList.sort(key=lambda x: x.BillDetailID, reverse=True)
    BillDetailIDList = list(
        set([BillDetailData.BillDetailID for BillDetailData in BillDetailDataList])
    )
    CBStatementDataList = crudCreditBalanceStatement.get_value_if_in_a_list(
        CreditBalanceStatementDBModel.BLDetailID, BillDetailIDList
    )

    InvDetailIDList = list(
        set([BillDetailData.InvDetialID for BillDetailData in BillDetailDataList])
    )
    InvoiceDetailDataList = crudInvoiceDetail.get_value_if_in_a_list(
        InvoiceDetailDBModel.InvDetialID, InvDetailIDList
    )

    newDataCreateDate = convert_time_to_str(datetime.now())

    # =============================================
    # 創建新的CBStatement
    # =============================================
    newCBStatementDictDataList = []
    for BillDetailData in BillDetailDataList:
        # 抓取對應的CBStatement
        filterCBStatementDataList = list(
            filter(
                lambda x: x.BLDetailID == BillDetailData.BillDetailID,
                CBStatementDataList,
            )
        )
        filterCBStatementDataList.sort(key=lambda x: x.CBStateID, reverse=True)
        for filterCBStatementData in filterCBStatementDataList:
            # 新增CBStatement
            newCBStatementDictData = {
                "CBID": filterCBStatementData.CBID,
                "BillingNo": filterCBStatementData.BillingNo,
                "TransItem": "RETURN",
                "OrgAmount": filterCBStatementData.OrgAmount
                + filterCBStatementData.TransAmount,
                "TransAmount": 0 - filterCBStatementData.TransAmount,
                "CreateDate": newDataCreateDate,
            }
            if Note:
                newCBStatementDictData["Note"] = Note
            newCBStatementDictDataList.append(newCBStatementDictData)

    # =============================================
    # 更新CB資料
    # =============================================
    df_CBStatement = pd.DataFrame.from_records(newCBStatementDictDataList)
    newCBDictDataList = []
    if not df_CBStatement.empty:
        df_CBStatement = df_CBStatement[["CBID", "TransAmount"]]
        df_CBStatement_groupby = (
            df_CBStatement.groupby(["CBID"]).sum(["TransAmount"]).reset_index()
        )
        for i in range(len(df_CBStatement_groupby)):
            CBData = crudCreditBalance.get_with_condition(
                {"CBID": df_CBStatement_groupby.loc[i, "CBID"]}
            )[0]
            newCBDictData = orm_to_dict(deepcopy(CBData))
            newCBDictData["LastUpdDate"] = newDataCreateDate
            newCBDictData["CurrAmount"] += df_CBStatement_groupby.loc[i, "TransAmount"]
            newCBDictDataList.append(newCBDictData)

        for newCBDictData in newCBDictDataList:
            CBData = crudCreditBalance.get_with_condition(
                {"CBID": newCBDictData["CBID"]}
            )[0]
            crudCreditBalance.update(CBData, newCBDictData)

    # =============================================
    # 更新InvoiceDetail
    # =============================================
    newInvoiceDetailDataList = []
    for InvoiceDetailData in InvoiceDetailDataList:
        newInvoiceDetailData = deepcopy(InvoiceDetailData)
        newInvoiceDetailData.Status = "TO_MERGE"
        newInvoiceDetailData = crudInvoiceDetail.update(
            InvoiceDetailData, orm_to_dict(newInvoiceDetailData)
        )
        newInvoiceDetailDataList.append(newInvoiceDetailData)

    # =============================================
    # 更新BillDetail
    # =============================================
    newBillDetailDictDataList = []
    for BillDetailData in BillDetailDataList:
        newBillDetailDictData = orm_to_dict(deepcopy(BillDetailData))
        newBillDetailDictData["Status"] = "INVALID"
        newBillDetailDictDataList.append(newBillDetailDictData)

    for oldBillDetailData, newBillDetailDictData in zip(
        BillDetailDataList, newBillDetailDictDataList
    ):
        crudBillDetail.update(oldBillDetailData, newBillDetailDictData)

    # =============================================
    # 更新BillMaster
    # =============================================
    BillMasterData = crudBillMaster.get_with_condition({"BillMasterID": BillMasterID})[
        0
    ]
    newBillMasterDictData = orm_to_dict(deepcopy(BillMasterData))
    newBillMasterDictData["Status"] = "INVALID"
    crudBillMaster.update(BillMasterData, newBillMasterDictData)
    return {
        "CBStatement": newCBStatementDictDataList,
        "CB": newCBDictDataList,
        "InvoiceDetail": newInvoiceDetailDataList,
        "BillDetail": newBillDetailDictDataList,
        "BillMaster": newBillMasterDictData,
    }


# endregion: -------------------------------------------------------------------


# region: ----------------------------------- 銷帳 -----------------------------------


@router.post("/BillMaster&BillDetail/toWriteOff")
async def billWriteOff(request: Request, db: Session = Depends(get_db)):
    """
    {
        "BillMaster": {...},
        "BillDetail": [
            {...},
            {...}
        ]
    }
    """
    # 預設前端是傳一個BillMaster與一個BillDetailList
    BillMasterDictData = (await request.json())["BillMaster"]
    BillDetailDictDataList = (await request.json())["BillDetail"]

    CollectStatementDictData = {
        "BillingNo": BillMasterDictData["BillingNo"],
        "PartyName": BillMasterDictData["PartyName"],
        "SubmarineCable": BillMasterDictData["SubmarineCable"],
        "WorkTitle": BillMasterDictData["WorkTitle"],
        "FeeAmount": BillMasterDictData["FeeAmountSum"],
        "ReceivedAmountSum": 0,
        "BankFee": BillMasterDictData["BankFees"],
        # 整個帳單的收款日期暫時取系統當下時間
        "ReceiveDate": convert_time_to_str(datetime.now()),
        "Note": None,
    }

    crudBillMaster = CRUD(db, BillMasterDBModel)
    crudBillDetail = CRUD(db, BillDetailDBModel)
    crudCollectStatement = CRUD(db, CollectStatementDBModel)

    crudCreditBalance = CRUD(db, CreditBalanceDBModel)
    crudCreditBalanceStatement = CRUD(db, CreditBalanceStatementDBModel)
    newBillDetailDataList = []
    proBankFeeFlag = 0
    for BillDetailDictData in BillDetailDictDataList:
        # DB帳單明細檔舊資訊
        oldBillDetailData = crudBillDetail.get_with_condition(
            {"BillDetailID": BillDetailDictData["BillDetailID"]}
        )[0]

        # 本次帳單收款紀錄實收累加
        CollectStatementDictData["ReceivedAmountSum"] = (
            CollectStatementDictData["ReceivedAmountSum"]
            + BillDetailDictData["ReceivedAmount"]
        )

        # 最新銷帳日期
        BillDetailDictData["WriteOffDate"] = convert_time_to_str(datetime.now())

        # 明細累計實收
        BillDetailDictData["ReceivedAmount"] = (
            BillDetailDictData["ReceivedAmount"] + oldBillDetailData.ReceivedAmount
        )

        # 若有溢繳的明細要進CB帳，有超過已經轉入CB的金額，才會新增CB
        if (
            BillMasterDictData["IsPro"] != 1
            and BillDetailDictData["Status"] == "OVER"
            and BillDetailDictData["OverAmount"] > BillDetailDictData["ToCBAmount"]
        ):
            newCBAmount = (
                BillDetailDictData["OverAmount"] - BillDetailDictData["ToCBAmount"]
            )
            CreditBalanceDictData = {
                "CBType": "OVERPAID",
                "BillingNo": BillMasterDictData["BillingNo"],
                "InvoiceNo": None,
                "BLDetailID": BillDetailDictData["BillDetailID"],
                "SubmarineCable": BillMasterDictData["SubmarineCable"],
                "WorkTitle": BillMasterDictData["WorkTitle"],
                "BillMilestone": BillDetailDictData["BillMilestone"],
                "PartyName": BillMasterDictData["PartyName"],
                "CNNo": None,
                "CurrAmount": newCBAmount,
                "CreateDate": convert_time_to_str(datetime.now()),
                "LastUpdDate": None,
                "Note": None,
            }
            # 新增CB
            CreditBalanceSchemaData = CreditBalanceSchema(**CreditBalanceDictData)
            thisCBRecord = crudCreditBalance.create(CreditBalanceSchemaData)

            # 把BillDetailDictData["OverAmount"] update回BillDetailDictData["ToCBAmount"]
            # 重溢繳的金額理當等於已轉CB的金額
            BillDetailDictData["ToCBAmount"] = BillDetailDictData["OverAmount"]

            CBStatementDictData = {
                "CBID": thisCBRecord.CBID,
                "BillingNo": BillMasterDictData["BillingNo"],
                "BLDetailID": BillDetailDictData["BillDetailID"],
                "TransItem": "BM_ADD",
                "OrgAmount": newCBAmount,
                "TransAmount": 0,
                "Note": None,
                "CreateDate": convert_time_to_str(datetime.now()),
            }
            # 新增CB Statement
            CBStatementSchemaData = CreditBalanceStatementSchema(**CBStatementDictData)
            crudCreditBalanceStatement.create(CBStatementSchemaData)
        # 若Pro-forma帳單明細(通常只會有一筆明細)要進CB帳，累計實收已經轉入CB的金額，才會新增CB
        elif (
            BillMasterDictData["IsPro"] == 1
            and BillDetailDictData["ReceivedAmount"] > BillDetailDictData["ToCBAmount"]
        ):
            newCBAmount = (
                BillDetailDictData["ReceivedAmount"] - BillDetailDictData["ToCBAmount"]
            )
            CreditBalanceDictData = {
                "CBType": "PREPAID",
                "BillingNo": BillMasterDictData["BillingNo"],
                "InvoiceNo": None,
                "BLDetailID": BillDetailDictData["BillDetailID"],
                "SubmarineCable": BillMasterDictData["SubmarineCable"],
                "WorkTitle": BillMasterDictData["WorkTitle"],
                "BillMilestone": BillDetailDictData["BillMilestone"],
                "PartyName": BillMasterDictData["PartyName"],
                "CNNo": None,
                "CurrAmount": newCBAmount,
                "CreateDate": convert_time_to_str(datetime.now()),
                "LastUpdDate": None,
                "Note": None,
            }
            # 新增CB
            CreditBalanceSchemaData = CreditBalanceSchema(**CreditBalanceDictData)
            thisCBRecord = crudCreditBalance.create(CreditBalanceSchemaData)

            # 把BillDetailDictData["ReceivedAmount"] update回BillDetailDictData["ToCBAmount"]
            # 累計實收的金額理當等於已轉CB的金額
            BillDetailDictData["ToCBAmount"] = BillDetailDictData["ReceivedAmount"]

            # Proforma 帳單的CBStatement初始就會拆成兩筆
            # 第一筆為原始金額包含手續費(但兩筆以上的Pro-forma帳單明細，手續費負項只能記錄一次)
            orgAmount = (
                newCBAmount + BillMasterDictData["BankFees"]
                if (proBankFeeFlag == 0)
                else newCBAmount
            )
            CBStatementDictData = {
                "CBID": thisCBRecord.CBID,
                "BillingNo": BillMasterDictData["BillingNo"],
                "BLDetailID": BillDetailDictData["BillDetailID"],
                "TransItem": "BM_ADD",
                "OrgAmount": orgAmount,
                "TransAmount": 0,
                "Note": None,
                "CreateDate": convert_time_to_str(datetime.now()),
            }
            # 新增CB Statement
            CBStatementSchemaData = CreditBalanceStatementSchema(**CBStatementDictData)
            crudCreditBalanceStatement.create(CBStatementSchemaData)

            # 第二筆異動項目為BANK_FEE，異動金額為手續費金額取負值
            if proBankFeeFlag == 0:
                CBStatementDictData["TransItem"] = "BANK_FEE"
                CBStatementDictData["TransAmount"] = -BillMasterDictData["BankFees"]
                CBStatementSchemaData = CreditBalanceStatementSchema(
                    **CBStatementDictData
                )
                crudCreditBalanceStatement.create(CBStatementSchemaData)
                proBankFeeFlag = 1
        # end if

        # 更新帳單明細檔資訊
        newBillDetailData = crudBillDetail.update(oldBillDetailData, BillDetailDictData)
        newBillDetailDataList.append(newBillDetailData)
    # end for BillDetailDictData in BillDetailDictDataList

    # 寫入本次收款紀錄
    # covert CollectStatementDict to Pydantic model
    if CollectStatementDictData["ReceivedAmountSum"] > 0:
        CollectStatementSchemaData = CollectStatementSchema(**CollectStatementDictData)
        crudCollectStatement.create(CollectStatementSchemaData)

    # DB帳單主檔舊資訊
    oldBillMasterData = crudBillMaster.get_with_condition(
        {"BillMasterID": BillMasterDictData["BillMasterID"]}
    )[0]

    # 累計銀行手續費
    BillMasterDictData["BankFees"] = (
        BillMasterDictData["BankFees"] + oldBillMasterData.BankFees
        if oldBillMasterData.BankFees
        else BillMasterDictData["BankFees"]
    )

    # 累計帳單實收
    ReceivedAmountSum = sum(
        [
            newBillDetailData.ReceivedAmount
            for newBillDetailData in newBillDetailDataList
        ]
    )
    BillMasterDictData["ReceivedAmountSum"] = ReceivedAmountSum

    # 更新帳單主檔資訊
    newBillMasterData = crudBillMaster.update(oldBillMasterData, BillMasterDictData)

    # record log
    record_log(
        f"{user_name} writes off {BillMasterDictData['BillingNo']} successfully.",
    )

    return


# endregion: ------------------------------------------------------------------------
