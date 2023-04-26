from fastapi import APIRouter, Request, Depends
from fastapi.responses import FileResponse

from crud import *
from get_db import get_db
from sqlalchemy.orm import Session
from utils.utils import *
from utils.log import *
from utils.orm_pydantic_convert import *

import os
from copy import deepcopy
from docxtpl import DocxTemplate, InlineImage


router = APIRouter()


# region:  ------------------------------ 合併帳單 ------------------------------
# 顯示InvoiceMaster、InvoiceDetail資料


@router.get("/getInvoiceMaster&InvoiceDetail/{urlCondition}")
async def getInvoiceMasterAndInvoiceDetail(
    request: Request, urlCondition: str, db: Session = Depends(get_db)
):
    crudInvoiceMaster = CRUD(db, InvoiceMasterDBModel)
    crudInvoiceDetail = CRUD(db, InvoiceDetailDBModel)
    getResult = []
    if "BillMilestone" in urlCondition:
        newUrlCondition, BillMilestone = re_search_url_condition_value(
            urlCondition, "BillMilestone"
        )
        dictCondition = convert_url_condition_to_dict(newUrlCondition)
        InvoiceMasterDataList = crudInvoiceMaster.get_with_condition(dictCondition)
        for InvoiceMasterData in InvoiceMasterDataList:
            InvoiceDetailDataList = crudInvoiceDetail.get_with_condition(
                {"InvMasterID": InvoiceMasterData.InvMasterID}
            )
            checkBillMilestone = list(
                filter(
                    lambda x: x.BillMilestone == BillMilestone, InvoiceDetailDataList
                )
            )
            if checkBillMilestone:
                getResult.append(
                    {
                        "InvoiceMaster": InvoiceMasterData,
                        "InvoiceDetail": InvoiceDetailDataList,
                    }
                )
    else:
        dictCondition = convert_url_condition_to_dict(urlCondition)
        InvoiceMasterDataList = crudInvoiceMaster.get_with_condition(dictCondition)
        for InvoiceMasterData in InvoiceMasterDataList:
            InvoiceDetailDataList = crudInvoiceDetail.get_with_condition(
                {"InvMasterID": InvoiceMasterData.InvMasterID}
            )
            getResult.append(
                {
                    "InvoiceMaster": InvoiceMasterData,
                    "InvoiceDetail": InvoiceDetailDataList,
                }
            )

    return getResult


# 檢查合併帳單的PartyName、SubmarineCable、WorkTitle是否相同
@router.post("/checkInitBillMaster&BillDetail")
async def checkInitBillMasterAndBillDetail(
    request: Request, db: Session = Depends(get_db)
):
    """
    {
        "InvoiceMaster": [
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
    InvoiceMasterDictDataList = request_data["InvoiceMaster"]
    for InvoiceMasterDictData in InvoiceMasterDictDataList:
        PartyList.append(InvoiceMasterDictData["PartyName"])
        SubmarineCableList.append(InvoiceMasterDictData["SubmarineCable"])
        WorkTitleList.append(InvoiceMasterDictData["WorkTitle"])

    alert_msg = {}
    if len(set(PartyList)) > 1:
        alert_msg["PartyName"] = "PartyName is not unique"
    if len(set(SubmarineCableList)) > 1:
        alert_msg["SubmarineCable"] = "SubmarineCable is not unique"
    if len(set(WorkTitleList)) > 1:
        alert_msg["WorkTitle"] = "WorkTitle is not unique"
    if not alert_msg:
        alert_msg["isUnique"] = True
    return alert_msg


# 待抵扣階段(for 點擊合併帳單button後，初始化帳單及帳單明細，顯示預覽畫面)
@router.post("/getBillMaster&BillDetailStream")
async def initBillMasterAndBillDetail(request: Request, db: Session = Depends(get_db)):
    """
    {
        "InvoiceMaster": [
            {...},
            {...},
            {...}
        ]
    }
    """
    request_data = await request.json()
    InvoiceMasterIdList = [
        InvoiceMasterDictData["InvMasterID"]
        for InvoiceMasterDictData in request_data["InvoiceMaster"]
    ]

    crudInvoiceDetail = CRUD(db, InvoiceDetailDBModel)
    crudInvoiceMaster = CRUD(db, InvoiceMasterDBModel)
    crudBillMaster = CRUD(db, BillMasterDBModel)
    crudBillDetail = CRUD(db, BillDetailDBModel)

    InvoiceMasterDataList = crudInvoiceMaster.get_value_if_in_a_list(
        InvoiceMasterDBModel.InvMasterID, InvoiceMasterIdList
    )

    InvoiceDetailDataList = crudInvoiceDetail.get_value_if_in_a_list(
        InvoiceDetailDBModel.InvMasterID, InvoiceMasterIdList
    )
    InvoiceDetailDataList = list(
        filter(
            lambda x: x.PartyName == InvoiceMasterDataList[0].PartyName,
            InvoiceDetailDataList,
        )
    )

    BillingNo = f"{InvoiceMasterDataList[0].SubmarineCable}-{InvoiceMasterDataList[0].WorkTitle}-CBP-{InvoiceMasterDataList[0].PartyName}-{convert_time_to_str(datetime.now()).replace('-', '').replace(' ', '').replace(':', '')[2:-2]}"

    # change InvoiceMaster status to "MERGED"
    for InvoiceMasterData in InvoiceMasterDataList:
        InvoiceMasterDictData = orm_to_dict(InvoiceMasterData)
        InvoiceMasterDictData["Status"] = "MERGED"

    # cal FeeAmountSum
    FeeAmountSum = 0
    for InvoiceDetailData in InvoiceDetailDataList:
        FeeAmountSum += InvoiceDetailData.FeeAmountPost

    # init BillMaster
    BillMasterDictData = {
        "BillingNo": BillingNo,
        "SubmarineCable": InvoiceMasterDataList[0].SubmarineCable,
        "WorkTitle": InvoiceMasterDataList[0].WorkTitle,
        "PartyName": InvoiceMasterDataList[0].PartyName,
        "IssueDate": convert_time_to_str(datetime.now()),
        "DueDate": None,
        "FeeAmountSum": FeeAmountSum,
        "ReceivedAmountSum": 0,
        "IsPro": InvoiceMasterDataList[0].IsPro,
        "Status": "INITIAL",
    }

    # init BillDetail
    BillDetailDataList = []
    for InvoiceDetailData in InvoiceDetailDataList:
        """
        BillDetailData keys:
        BillDetailID
        BillMasterID
        WKMasterID
        InvDetailID
        PartyName
        SupplierName
        SubmarineCable
        WorkTitle
        BillMilestone
        FeeItem
        OrgFeeAmount
        DedAmount(抵扣金額)
        FeeAmount(應收(會員繳)金額)
        ReceivedAmount(累計實收(會員繳)金額(初始為0))
        OverAmount(重溢繳金額 銷帳介面會自動計算帶出)
        ShortAmount(短繳金額 銷帳介面會自動計算帶出)
        ShortOverReason(短繳原因 自行輸入)
        WriteOffDate(銷帳日期)
        ReceiveDate(最新收款日期 自行輸入)
        Note
        ToCB(金額是否已存在 null or Done)
        Status
        """
        BillDetailDictData = {
            # "BillMasterID": BillMasterData.BillMasterID,
            "WKMasterID": InvoiceDetailData.WKMasterID,
            "InvDetailID": InvoiceDetailData.InvDetailID,
            "InvoiceNo": InvoiceDetailData.InvoiceNo,
            "PartyName": InvoiceDetailData.PartyName,
            "SupplierName": InvoiceDetailData.SupplierName,
            "SubmarineCable": InvoiceDetailData.SubmarineCable,
            "WorkTitle": InvoiceDetailData.WorkTitle,
            "BillMilestone": InvoiceDetailData.BillMilestone,
            "FeeItem": InvoiceDetailData.FeeItem,
            "OrgFeeAmount": InvoiceDetailData.FeeAmountPost,
            "DedAmount": 0,
            "FeeAmount": InvoiceDetailData.FeeAmountPost,
            "ReceivedAmount": 0,
            "OverAmount": 0,
            "ShortAmount": 0,
            "ShortOverReason": None,
            "WriteOffDate": None,
            "ReceiveDate": None,
            "Note": None,
            "ToCBAmount": None,
            "Status": "INCOMPLETE",
        }
        # BillDetailData = crudBillDetail.create(BillDetailSchema(**BillDetailDictData))
        BillDetailDataList.append(BillDetailDictData)

    return {
        "message": "success",
        "BillMaster": BillMasterDictData,
        "BillDetail": BillDetailDataList,
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
    crudInvoiceMaster = CRUD(db, InvoiceMasterDBModel)
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
    InvoiceMasterDataList = crudInvoiceMaster.get_value_if_in_a_list(
        InvoiceDetailDBModel.InvDetailID, InvDetailIDList
    )
    InvoiceMasterDataList = list(
        filter(lambda x: x.PartyName == BillMasterData.PartyName, InvoiceMasterDataList)
    )

    newInvoiceMasterDataList = []
    for InvoiceMasterData in InvoiceMasterDataList:
        InvoiceMasterData.Status = "MERGED"
        newInvoiceMasterDataList.append(InvoiceMasterData)

    for oldInvoiceMasterData, newInvoiceMasterData in zip(
        InvoiceMasterDataList, newInvoiceMasterDataList
    ):
        crudInvoiceMaster.update(
            oldInvoiceMasterData, orm_to_dict(newInvoiceMasterData)
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
    crudBillMaster = CRUD(db, BillMasterDBModel)
    crudBillDetail = CRUD(db, BillDetailDBModel)
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

    deductDataList = (await request.json())["Deduct"]
    deductDataList = sorted(deductDataList, key=lambda x: x["BillDetailID"])

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
            newCBDictData["LastUpdDate"] = convert_time_to_str(datetime.now())

            newCBStatementDictData = {
                "CBID": newCBDictData["CBID"],
                "BillingNo": BillMasterDictData["BillingNo"],
                "BLDetailID": newBillDetailData.BillDetailID,
                "TransItem": "DEDUCT",
                "OrgAmount": oldCBData.CurrAmount,
                "TransAmount": reqCBData["TransAmount"] * (-1),
                "Note": "",
                "CreateDate": convert_time_to_str(datetime.now()),
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
@router.post("/generateBillMaster&BillDetail/preview")
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
    -------------------------------------------------------------
    dataProcessRecord = {
        "BillDetail": None,
        "CBList": [
            {
                "CB": {...},
                "CBStatement": {...}
            },
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

    deductDataList = (await request.json())["Deduct"]
    deductDataList = sorted(deductDataList, key=lambda x: x["BillDetailID"])

    recordDeductProcess = {"BillMaster": None, "BillDetailProcess": []}

    newBillDetailDataList = []
    for deductData in deductDataList:
        dataProcessRecord = {
            "BillDetail": None,
            "CBList": [],
        }
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
            newCBDictData["LastUpdDate"] = convert_time_to_str(datetime.now())
            newCBStatementDictData = {
                "CBID": newCBDictData["CBID"],
                "BillingNo": BillMasterDictData["BillingNo"],
                "BLDetailID": newBillDetailData.BillDetailID,
                "TransItem": "DEDUCT",
                "OrgAmount": oldCBData.CurrAmount,
                "TransAmount": reqCBData["TransAmount"] * (-1),
                "Note": "",
                "CreateDate": convert_time_to_str(datetime.now()),
            }

            tempTotalDedAmount += reqCBData["TransAmount"]

            # update CreditBalance
            dataProcessRecord["CBList"].append(
                {"CB": newCBDictData, "CBStatement": newCBStatementDictData}
            )

        # update BillDetail
        newBillDetailData.DedAmount = tempTotalDedAmount
        newBillDetailData.FeeAmount = (
            newBillDetailData.OrgFeeAmount - newBillDetailData.DedAmount
        )
        newBillDetailDataList.append(newBillDetailData)

        dataProcessRecord["BillDetail"] = orm_to_dict(newBillDetailData)
        recordDeductProcess["BillDetailProcess"].append(dataProcessRecord)
    # update BillMaster
    newBillMasterData.FeeAmountSum -= sum(
        [newBillDetailData.DedAmount for newBillDetailData in newBillDetailDataList]
    )
    newBillMasterData.Status = "RATED"
    recordDeductProcess["BillMaster"] = orm_to_dict(newBillMasterData)

    return {"message": "success", "previewData": recordDeductProcess}


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
    if urlCondition == "all":
        BillMasterDataList = crudBillMaster.get_all()
    elif "start" in urlCondition and "end" in urlCondition:
        dictCondition = convert_url_condition_to_dict(urlCondition)
        sql_condition = convert_dict_to_sql_condition(dictCondition, table_name)
        BillMasterDataList = crudBillMaster.get_all_by_sql(sql_condition)
    else:
        dictCondition = convert_url_condition_to_dict(urlCondition)
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
            }
        )

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
        if docxFile.endswith(".docx") and "Network" in docxFile:
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
        "CorporateBankName": getResult["CorporateInformation"]["BankName"],
        "CorporateBranch": getResult["CorporateInformation"]["Branch"]
        if getResult["CorporateInformation"]["Branch"]
        else "n/a",
        "CorporateBranchAddress": getResult["CorporateInformation"]["BranchAddress"]
        if getResult["CorporateInformation"]["BranchAddress"]
        else "n/a",
        "CorporateBankAcctName": getResult["CorporateInformation"]["BankAcctName"]
        if getResult["CorporateInformation"]["BankAcctName"]
        else "n/a",
        "CorporateBankAcctNo": getResult["CorporateInformation"]["BankAcctNo"]
        if getResult["CorporateInformation"]["BankAcctNo"]
        else "n/a",
        "CorporateSavingAcctNo": getResult["CorporateInformation"]["SavingAcctNo"]
        if getResult["CorporateInformation"]["SavingAcctNo"]
        else "n/a",
        "CorporateIBAN": getResult["CorporateInformation"]["IBAN"]
        if getResult["CorporateInformation"]["IBAN"]
        else "n/a",
        "CorporateSWIFTCode": getResult["CorporateInformation"]["SWIFTCode"],
        "CorporateACHNo": getResult["CorporateInformation"]["ACHNo"]
        if getResult["CorporateInformation"]["ACHNo"]
        else "n/a",
        "CorporateWireRouting": getResult["CorporateInformation"]["WireRouting"]
        if getResult["CorporateInformation"]["WireRouting"]
        else "n/a",
        "IssueDate": (await request.json())["IssueDate"],
        "DueDate": (await request.json())["DueDate"],
        "InvoiceNo": getResult["InvoiceNo"],
        "logo": InlineImage(doc, logo_path),
        "PONo": f"PO No.: {BillMasterData.PONo}" if BillMasterData.PONo else "n/a",
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
# 待抵扣階段退回


@router.post("/returnBillMaster&BillDetail/beforeDeduct")
async def returnBillMasterAndBillDetail(
    request: Request, db: Session = Depends(get_db)
):
    """
    {
        "BillMaster": {},
        "ReturnStage": "VALIDATED" or "TO_MERGE"
    }
    """
    crudBillMaster = CRUD(db, BillMasterDBModel)
    crudBillDetail = CRUD(db, BillDetailDBModel)
    crudInvoiceMaster = CRUD(db, InvoiceMasterDBModel)
    crudInvoiceDetail = CRUD(db, InvoiceDetailDBModel)

    InvDetailIDList = []
    BillMasterDictData = (await request.json())["BillMaster"]
    ReturnStage = (await request.json())["ReturnStage"]

    # get BillDetailDataList
    BillDetailDataList = crudBillDetail.get_with_condition(
        {"BillMasterID": BillMasterDictData["BillMasterID"]}
    )
    for BillDetailData in BillDetailDataList:
        InvDetailIDList.append(BillDetailData.InvDetailID)

    InvoiceMasterDataList = crudInvoiceMaster.get_value_if_in_a_list(
        InvoiceMasterDBModel.InvDetailID, InvDetailIDList
    )

    if ReturnStage == "TO_MERGE":
        # 更新發票主檔狀態為"TO_MERGE"
        for InvoiceMasterData in InvoiceMasterDataList:
            InvoiceMasterDictData = orm_to_dict(InvoiceMasterData)
            InvoiceMasterDictData["Status"] = "TO_MERGE"
            newInvoiceMasterData = crudInvoiceMaster.update(
                InvoiceMasterData, InvoiceMasterDictData
            )
    elif ReturnStage == "VALIDATED":
        # 刪除發票主檔、發票明細檔
        for InvoiceMasterData in InvoiceMasterDataList:
            InvoiceDetailDataList = crudInvoiceDetail.get_with_condition(
                {"InvMasterID": InvoiceMasterData.InvMasterID}
            )
            for InvoiceDetailData in InvoiceDetailDataList:
                crudInvoiceDetail.remove(InvoiceDetailData.InvDetailID)
            crudInvoiceMaster.remove(InvoiceMasterData.InvMasterID)

    # 刪除BillMaster、BillDetail
    crudBillMaster.remove(BillMasterDictData["BillMasterID"])
    for BillDetailData in BillDetailDataList:
        crudBillDetail.remove(BillDetailData.BillDetailID)

    if ReturnStage == "TO_MERGE":
        return {"message": "success to return to TO_MERGE stage"}
    elif ReturnStage == "VALIDATED":
        return {"message": "success return to VALIDATED stage"}
    else:
        return {"message": "fail to return"}


# 已抵扣階段退回(選擇帳單)
@router.post("/returnToValidatedBillMaster&BillDetail/afterDeduct/choiceBillMaster")
async def returnToValidatedBillMasterAndBillDetailChoiceBillMaster(
    request: Request, db: Session = Depends(get_db)
):
    """
    {
        "BillMaster": {},
    }
    """
    crudInvoiceWKMaster = CRUD(db, InvoiceWKMasterDBModel)
    crudBillMaster = CRUD(db, BillMasterDBModel)
    crudBillDetail = CRUD(db, BillDetailDBModel)

    BillMasterDictData = (await request.json())["BillMaster"]
    BillMasterData = crudBillMaster.get_with_condition(
        {"BillMasterID": BillMasterDictData["BillMasterID"]}
    )[0]
    BillDetailDataList = crudBillDetail.get_with_condition(
        {"BillMasterID": BillMasterData.BillMasterID}
    )
    InvoiceWKMasterIDList = [
        BillDetailData.WKMasterID for BillDetailData in BillDetailDataList
    ]
    InvoiceWKMasterDataList = crudInvoiceWKMaster.get_value_if_in_a_list(
        InvoiceWKMasterDBModel.WKMasterID, InvoiceWKMasterIDList
    )
    return {
        "BillMaster": BillMasterData,
        "InvoiceWKMaster": InvoiceWKMasterDataList,
    }


# 已抵扣階段退回(選擇發票工作主檔)
@router.post(
    "/returnToValidatedBillMaster&BillDetail/afterDeduct/choiceInvoiceWKMaster"
)
async def returnToValidatedBillMasterAndBillDetailChoiceInvoiceWKMaster(
    request: Request, db: Session = Depends(get_db)
):
    """
    input:
    {
        InvoiceWKMaster: [
            {...},
            {...},
        ]
        "Confirm": True / False
        "Note": "string"
    }

    output:
    streamResponse = [
        {
            InvoiceWKMasterData: {},
            BillMasterDataList: [
                {
                    "BillMaster": {},
                    "BillDetail": [],
                    "TotalBillDetailAmount": 123.45,
                },
                {...}
            ]
        }
    ]
    """
    crudInvoiceWKMaster = CRUD(db, InvoiceWKMasterDBModel)
    crudInvoiceMaster = CRUD(db, InvoiceMasterDBModel)
    crudInvoiceDetail = CRUD(db, InvoiceDetailDBModel)
    crudBillDetail = CRUD(db, BillDetailDBModel)
    crudBillMaster = CRUD(db, BillMasterDBModel)
    crudCreditBalance = CRUD(db, CreditBalanceDBModel)
    crudCreditBalanceStatement = CRUD(db, CreditBalanceStatementDBModel)
    confirm = (await request.json())["Confirm"]
    note = (await request.json())["Note"]

    InvoiceWKMasterDictDataList = (await request.json())["InvoiceWKMaster"]
    InvoiceWKMasterIDList = [
        InvoiceWKMasterData["WKMasterID"]
        for InvoiceWKMasterData in InvoiceWKMasterDictDataList
    ]
    BillDetailDataList = crudBillDetail.get_value_if_in_a_list(
        BillDetailDBModel.WKMasterID, InvoiceWKMasterIDList
    )
    BillDetailIDList = list(
        set([BillDetailData.BillDetailID for BillDetailData in BillDetailDataList])
    )
    BillMasterIDList = list(
        set([BillDetailData.BillMasterID for BillDetailData in BillDetailDataList])
    )
    pprint(BillDetailIDList)
    BillMasterDataList = crudBillMaster.get_value_if_in_a_list(
        BillMasterDBModel.BillMasterID, BillMasterIDList
    )
    for BillMasterData in BillMasterDataList:
        pprint(orm_to_dict(BillMasterData))
    CBStatementDataList = crudCreditBalanceStatement.get_value_if_in_a_list(
        CreditBalanceStatementDBModel.BLDetailID, BillDetailIDList
    )

    streamResponse = []
    for InvoiceWKMasterDictData in InvoiceWKMasterDictDataList:
        streamDictData = {
            "InvoiceWKMaster": InvoiceWKMasterDictData,
            "BillMasterDataList": [],
        }
        tempBillDetailDataList = list(
            filter(
                lambda x: x.WKMasterID == InvoiceWKMasterDictData["WKMasterID"],
                BillDetailDataList,
            )
        )
        tempBillMasterIDList = list(
            set(
                [
                    tempBillDetailData.BillMasterID
                    for tempBillDetailData in tempBillDetailDataList
                ]
            )
        )
        print(tempBillMasterIDList)
        for tempBillMasterID in tempBillMasterIDList:
            print(tempBillMasterID)
            tempBillMasterData = list(
                filter(lambda x: x.BillMasterID == tempBillMasterID, BillMasterDataList)
            )[0]
            tempBillDetailDataList = list(
                filter(lambda x: x.BillMasterID == tempBillMasterID, BillDetailDataList)
            )
            streamDictData["BillMasterDataList"].append(
                {
                    "BillMaster": tempBillMasterData,
                    "BillDetail": tempBillDetailDataList,
                }
            )
        streamResponse.append(streamDictData)
    if not confirm:
        return streamResponse
    if confirm:
        dataToBeProcessed = {
            # --------------------------
            "oldInvoiceWKMasterDataList": [],
            "newInvoiceWKMasterDataList": [],
            # --------------------------
            "oldBillMasterDataList": [],
            "newBillMasterDataList": [],
            # --------------------------
            "oldBillDetailDataList": [],
            "newBillDetailDataList": [],
            # --------------------------
            "newCBStatementDataList": [],
        }
        for tempOldBillMasterData in BillMasterDataList:
            dataToBeProcessed["oldBillMasterDataList"].append(tempOldBillMasterData)
            tempNewBillMasterDictData = orm_to_dict(tempOldBillMasterData)
            tempOldBillDetailDataList = list(
                filter(
                    lambda x: x.BillMasterID == tempOldBillMasterData.BillMasterID,
                    BillDetailDataList,
                )
            )
            for tempOldBillDetailData in tempOldBillDetailDataList:
                dataToBeProcessed["oldBillDetailDataList"].append(tempOldBillDetailData)
                tempNewBillDetailDictData = orm_to_dict(tempOldBillDetailData)
                tempOldCBStatementDataList = list(
                    filter(
                        lambda x: x.BLDetailID == tempOldBillDetailData.BillDetailID
                        and x.TransItem == "DEDUCT",
                        CBStatementDataList,
                    )
                )
                if tempOldCBStatementDataList:
                    tempTotalTransAmount = 0
                    for tempOldCBStatementData in tempOldCBStatementDataList:
                        tempOldCBData = crudCreditBalance.get_with_condition(
                            {"CBID": tempOldCBStatementData.CBID}
                        )[0]

                        tempTotalTransAmount += tempOldCBStatementData.TransAmount

                        # --------------- 更新CB ---------------
                        tempNewCBDictData = orm_to_dict(tempOldCBData)
                        tempNewCBDictData[
                            "CurrAmount"
                        ] -= tempOldCBStatementData.TransAmount
                        tempNewCBDictData["LastUpDate"] = convert_time_to_str(
                            datetime.now()
                        )
                        tempNewCBData = crudCreditBalance.update(
                            tempOldCBData, tempNewCBDictData
                        )

                        # --------------- 建立CBStatement ---------------
                        newCBStatementDictData = {
                            "CBID": tempOldCBStatementData.CBID,
                            "BillingNo": tempOldBillMasterData.BillingNo,
                            "BLDetailID": tempOldBillDetailData.BillDetailID,
                            "TransItem": "RETURN",
                            "OrgAmount": tempOldCBStatementData.OrgAmount
                            + tempOldCBStatementData.TransAmount,
                            "TransAmount": tempOldCBStatementData.TransAmount,
                            "Note": "tempOldBillMasterData.BillingNo 帳單退回至發票工作主檔VALIDATED階段",
                            "CreateDate": convert_time_to_str(datetime.now()),
                        }
                        newCBStatementPydanticData = dict_to_pydantic(
                            CreditBalanceStatementSchema, newCBStatementDictData
                        )
                        newCBStatementData = crudCreditBalanceStatement.create(
                            newCBStatementPydanticData
                        )
                        dataToBeProcessed["newCBStatementDataList"].append(
                            newCBStatementData
                        )

                        # --------------- 更新BillMaster的FeeAmountSum ---------------
                        tempNewBillMasterDictData[
                            "FeeAmountSum"
                        ] -= tempOldCBStatementData.TransAmount

                    # --------------- 更新BillDetail ---------------
                    tempNewBillDetailDictData["DedAmount"] += tempTotalTransAmount
                    tempNewBillDetailDictData["FeeAmount"] = (
                        tempNewBillDetailDictData["OrgFeeAmount"]
                        - tempNewBillDetailDictData["DedAmount"]
                    )
                    dataToBeProcessed["newBillDetailDataList"].append(
                        tempNewBillDetailDictData
                    )
            # --------------- 更新BillMaster ---------------
            tempNewBillMasterDictData["Status"] = "INITIAL"
            dataToBeProcessed["newBillMasterDataList"].append(tempNewBillMasterDictData)

        # 刪除InvoiceDetail、BillMaster、BillDetail，並更新InvoiceWKMaster的Status
        # --------------- 刪除InvoiceWKMaster ---------------
        InvoiceWKMasterDataList = crudInvoiceWKMaster.get_value_if_in_a_list(
            InvoiceWKMasterDBModel.WKMasterID, InvoiceWKMasterIDList
        )
        for InvoiceWKMasterData in InvoiceWKMasterDataList:
            dataToBeProcessed["oldInvoiceWKMasterDataList"].append(InvoiceWKMasterData)
            newInvoiceWKMasterData = deepcopy(InvoiceWKMasterData)
            newInvoiceWKMasterData.Status = "VALIDATED"
            newInvoiceWKMasterData = crudInvoiceWKMaster.update(
                InvoiceWKMasterData, orm_to_dict(newInvoiceWKMasterData)
            )
            dataToBeProcessed["newInvoiceWKMasterDataList"].append(
                newInvoiceWKMasterData
            )

        # --------------- 刪除InvoiceDetail ---------------
        InvoiceDetailDataList = crudInvoiceDetail.get_value_if_in_a_list(
            InvoiceDetailDBModel.WKMasterID, InvoiceWKMasterIDList
        )
        for InvoiceDetailData in InvoiceDetailDataList:
            crudInvoiceDetail.remove(InvoiceDetailData.InvDetailID)

        # --------------- 刪除BillMaster ---------------
        for BillMasterData in BillMasterDataList:
            crudBillMaster.remove(BillMasterData.BillMasterID)

        # --------------- 刪除BillDetail ---------------
        for BillDetailData in BillDetailDataList:
            crudBillDetail.remove(BillDetailData.BillDetailID)

        return {"message": "success", "changed_data": dataToBeProcessed}


@router.post("/returnToMergeBillMaster&BillDetail/afterDeduct")
async def returnToMergeBillMasterAndBillDetailAfterDeduct(
    request: Request, db: Session = Depends(get_db)
):
    """
    input:
    {
        "BillMasterID": 1,
    }

    output:
    {
        "newCBStatement": [
            {...},
            {...}
        ]
    }
    """
    response = {
        "message": "success",
        "newCBStatement": [],
        "newBillDetail": [],
        "newInvoiceMaster": [],
    }

    crudInvoiceMaster = CRUD(db, InvoiceMasterDBModel)
    crudInvoiceDetail = CRUD(db, InvoiceDetailDBModel)
    crudBillMaster = CRUD(db, BillMasterDBModel)
    crudBillDetail = CRUD(db, BillDetailDBModel)
    crudCreditBalance = CRUD(db, CreditBalanceDBModel)
    crudCreditBalanceStatement = CRUD(db, CreditBalanceStatementDBModel)

    oldBillMasterData = crudBillMaster.get_with_condition(
        {"BillMasterID": (await request.json())["BillMasterID"]}
    )[0]

    oldBillDetailDataList = crudBillDetail.get_with_condition(
        {"BillMasterID": oldBillMasterData.BillMasterID}
    )
    oldBillDetailDataList.reverse()

    for oldBillDetailData in oldBillDetailDataList:
        newBillDetailDictData = orm_to_dict(deepcopy(oldBillDetailData))
        oldCBStatementDataList = crudCreditBalanceStatement.get_with_condition(
            {"BLDetailID": oldBillDetailData.BillDetailID}
        )
        oldCBStatementDataList = list(
            filter(lambda x: x.TransItem == "DEDUCT", oldCBStatementDataList)
        )
        if oldCBStatementDataList:
            totalDedAmount = 0
            for oldCBStatementData in oldCBStatementDataList:
                oldCBData = crudCreditBalance.get_with_condition(
                    {"CBID": oldCBStatementData.CBID}
                )[0]

                totalDedAmount += oldCBStatementData.TransAmount

                newCBDictData = orm_to_dict(deepcopy(oldCBData))

                # --------------- 新增CBStatement ---------------
                newCBStatementDictData = {
                    "CBID": oldCBStatementData.CBID,
                    "BillingNo": oldBillMasterData.BillingNo,
                    "BLDetailID": oldBillDetailData.BillDetailID,
                    "TransItem": "RETURN",
                    "OrgAmount": oldCBStatementData.OrgAmount
                    + oldCBStatementData.TransAmount,
                    "TransAmount": oldCBStatementData.TransAmount * (-1),
                    "Note": "",
                    "CreateDate": convert_time_to_str(datetime.now()),
                }
                newCBStatementData = crudCreditBalanceStatement.create(
                    dict_to_pydantic(
                        CreditBalanceStatementSchema, newCBStatementDictData
                    )
                )
                response["newCBStatement"].append(newCBStatementData)

                # --------------- 更新CB ---------------
                newCBDictData["CurrAmount"] -= oldCBStatementData.TransAmount
                newCBDictData["LastUpdDate"] = convert_time_to_str(datetime.now())
                crudCreditBalance.update(oldCBData, newCBDictData)

            # --------------- 更新BillDetail ---------------
            newBillDetailDictData["DedAmount"] += totalDedAmount
            newBillDetailDictData["FeeAmount"] = (
                newBillDetailDictData["OrgFeeAmount"]
                - newBillDetailDictData["DedAmount"]
            )
            newBillDetailData = crudBillDetail.update(
                oldBillDetailData, newBillDetailDictData
            )
            response["newBillDetail"].append(newBillDetailData)

    InvDetailIDList = list(
        set(
            [
                oldBillDetailData.InvDetailID
                for oldBillDetailData in oldBillDetailDataList
            ]
        )
    )

    InvoiceDetailDataList = crudInvoiceDetail.get_value_if_in_a_list(
        InvoiceDetailDBModel.InvDetailID, InvDetailIDList
    )

    InvMasterIDList = list(
        set(
            [
                InvoiceDetailData.InvMasterID
                for InvoiceDetailData in InvoiceDetailDataList
            ]
        )
    )

    InvoiceMasterDataList = crudInvoiceMaster.get_value_if_in_a_list(
        InvoiceMasterDBModel.InvMasterID, InvMasterIDList
    )
    InvoiceMasterDataList = list(
        filter(
            lambda x: x.PartyName == oldBillMasterData.PartyName, InvoiceMasterDataList
        )
    )

    for InvoiceMasterData in InvoiceMasterDataList:
        newInvoiceMasterDictData = orm_to_dict(deepcopy(InvoiceMasterData))
        newInvoiceMasterDictData["Status"] = "TO_MERGE"
        newInvoiceMasterData = crudInvoiceMaster.update(
            InvoiceMasterData, newInvoiceMasterDictData
        )
        response["newInvoiceMaster"].append(newInvoiceMasterData)

    # --------------- 刪除BillMaster ---------------
    crudBillMaster.remove(oldBillMasterData.BillMasterID)

    # --------------- 刪除BillDetail ---------------
    for oldBillDetailData in oldBillDetailDataList:
        crudBillDetail.remove(oldBillDetailData.BillDetailID)

    return response


@router.post("/returnToInitialBillMaster&BillDetail/afterDeduct")
async def returnToInitialBillMasterAndBillDetailAfterDeduct(
    request: Request, db: Session = Depends(get_db)
):
    dataToBeProcessed = {
        "oldBillMasterDataList": [],
        "newBillMasterDataList": [],
        # --------------------------
        "oldBillDetailDataList": [],
        "newBillDetailDataList": [],
        # --------------------------
        "oldCBDataList": [],
        "newCBDataList": [],
        # --------------------------
        "newCBStatementDataList": [],
    }
    crudBillMaster = CRUD(db, BillMasterDBModel)
    crudBillDetail = CRUD(db, BillDetailDBModel)
    crudCreditBalance = CRUD(db, CreditBalanceDBModel)
    crudCreditBalanceStatement = CRUD(db, CreditBalanceStatementDBModel)

    BillMasterDictData = await request.json()
    BillMasterData = crudBillMaster.get_with_condition(
        {"BillMasterID": BillMasterDictData["BillMasterID"]}
    )[0]
    dataToBeProcessed["oldBillMasterDataList"].append(BillMasterData)
    BillDetailDataList = crudBillDetail.get_with_condition(
        {"BillMasterID": BillMasterData.BillMasterID}
    )
    BillDetailIDList = [
        BillDetailData.BillDetailID for BillDetailData in BillDetailDataList
    ]
    CBDataList = crudCreditBalance.get_value_if_in_a_list(
        CreditBalanceDBModel.BLDetailID, BillDetailIDList
    )
    CBIDList = [CBData.CBID for CBData in CBDataList]
    CBStatementDataList = crudCreditBalanceStatement.get_value_if_in_a_list(
        CreditBalanceStatementDBModel.CBID, CBIDList
    )
    dataToBeProcessed["oldBillDetailDataList"].extend(BillDetailDataList)
    FeeAmountSum = 0
    for BillDetailData in BillDetailDataList:
        tempOldCBDataList = list(
            filter(lambda x: x.BLDetailID == BillDetailData.BillDetailID, CBDataList)
        )
        for tempOldCBData in tempOldCBDataList:
            tempOldCBStatementDataList = list(
                filter(lambda x: x.CBID == tempOldCBData.CBID, CBStatementDataList)
            )
            tempOldCBStatementData = max(
                tempOldCBStatementDataList, key=lambda x: x.CreateDate
            )
            newCBStatementTransAmount = tempOldCBStatementData.TransAmount * (-1)
            newCBStatementData = CreditBalanceStatementDBModel(
                CBID=tempOldCBData.CBID,
                BillingNo=BillMasterData.BillingNo,
                BLDetailID=BillDetailData.BillDetailID,
                TransItem="RETURN",
                OrgAmount=tempOldCBData.CurrAmount + newCBStatementTransAmount,
                TransAmount=newCBStatementTransAmount,
                Note="",
                CreateDate=convert_time_to_str(datetime.now()),
            )
            tempNewCBData = deepcopy(tempOldCBData)
            tempNewCBData.CurrAmount = (
                newCBStatementData.OrgAmount + newCBStatementData.TransAmount
            )
            # ---------------------------- BillDetail更新 ----------------------------
            BillDetailData.DedAmount -= newCBStatementTransAmount
            BillDetailData.FeeAmount = (
                BillDetailData.OrgFeeAmount - BillDetailData.DedAmount
            )
            BillDetailData.Status = "INCOMPLETE"

            # ---------------------------- record data to be processed ----------------------------
            dataToBeProcessed["oldCBDataList"].append(tempOldCBData)
            dataToBeProcessed["newCBDataList"].append(tempNewCBData)
            dataToBeProcessed["newCBStatementDataList"].append(newCBStatementData)
        dataToBeProcessed["newBillDetailDataList"].append(BillDetailData)
        FeeAmountSum += BillDetailData.FeeAmount

    BillMasterData.Status = "INITIAL"
    if FeeAmountSum:
        BillMasterData.FeeAmountSum = FeeAmountSum
    dataToBeProcessed["newBillMasterDataList"].append(BillMasterData)

    # ---------------------------- 更新BillMaster -------------------------------
    for oldBillMasterData, newBillMasterData in zip(
        dataToBeProcessed["oldBillMasterDataList"],
        dataToBeProcessed["newBillMasterDataList"],
    ):
        crudBillMaster.update(oldBillMasterData, orm_to_dict(newBillMasterData))

    # ---------------------------- 更新BillDetail -------------------------------
    for oldBillDetailData, newBillDetailData in zip(
        dataToBeProcessed["oldBillDetailDataList"],
        dataToBeProcessed["newBillDetailDataList"],
    ):
        crudBillDetail.update(oldBillDetailData, orm_to_dict(newBillDetailData))

    # ---------------------------- 更新CB -------------------------------
    for oldCBData, newCBData in zip(
        dataToBeProcessed["oldCBDataList"], dataToBeProcessed["newCBDataList"]
    ):
        crudCreditBalance.update(oldCBData, orm_to_dict(newCBData))

    # ---------------------------- 新增CBStatement -------------------------------
    for newCBStatementData in dataToBeProcessed["newCBStatementDataList"]:
        newCBStatementPydanticData = orm_to_pydantic(
            newCBStatementData, CreditBalanceStatementSchema
        )
        crudCreditBalanceStatement.create(newCBStatementPydanticData)
    return {"message": "success"}


# endregion: -------------------------------------------------------------------


# region: ----------------------------------- 銷帳 -----------------------------------


# @router.post("/BillMaster&BillDetail/toWriteOff")
# async def billWriteOff(request: Request, db: Session = Depends(get_db)):
#     """
#     {
#         "BillMaster": {...},
#         "BillDetail": [
#             {...},
#             {...}
#         ]
#     }
#     """
#     BillMasterDictData = (await request.json())["BillMaster"]
#     BillDetailDictDataList = (await request.json())["BillDetail"]
#
#     crudBillMaster = CRUD(db, BillMasterDBModel)
#     crudBillDetail = CRUD(db, BillDetailDBModel)
#     crudCreditBalance = CRUD(db, CreditBalanceDBModel)
#     crudCreditBalanceStatement = CRUD(db, CreditBalanceStatementDBModel)
#
#     newBillDetailDataList = []
#
#     for BillDetailDictData in BillDetailDictDataList:
#         oldBillDetailData = crudBillDetail.get_with_condition(
#             {"BillDetailID": BillDetailDictData["BillDetailID"]}
#         )[0]
#
#         if BillMasterDictData["Status"] == "COMPLETE":
#             BillDetailDictData["WriteOffDate"] = convert_time_to_str(datetime.now())
#
#         newBillDetailData = crudBillDetail.update(oldBillDetailData, BillDetailDictData)
#         newBillDetailDataList.append(newBillDetailData)
#
#     oldBillMasterData = crudBillMaster.get_with_condition(
#         {"BillMasterID": BillMasterDictData["BillMasterID"]}
#     )[0]
#     ReceivedAmountSum = sum(
#         [
#             newBillDetailData.ReceivedAmount
#             for newBillDetailData in newBillDetailDataList
#         ]
#     )
#     BillMasterDictData["ReceivedAmountSum"] = ReceivedAmountSum
#
#     newBillMasterData = crudBillMaster.update(oldBillMasterData, BillMasterDictData)
#
#     # ---------------------------- 溢繳 -------------------------------
#     for newBillDetailData in newBillDetailDataList:
#         if newBillDetailData.OverAmount > 0:
#             newCBDictData = {
#                 "BLDetailID": newBillDetailData.BillDetailID,
#             }
#
#     return


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

    CollectStatmentDictData = {
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
        CollectStatmentDictData["ReceivedAmountSum"] = (
            CollectStatmentDictData["ReceivedAmountSum"]
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
    CollectStatementSchemaData = CollectStatementSchema(**CollectStatmentDictData)
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
    return


# endregion: ------------------------------------------------------------------------
