from fastapi import APIRouter, Request, Depends
from fastapi.responses import FileResponse

from crud import *
from get_db import get_db
from sqlalchemy.orm import Session
from utils.utils import *
from utils.orm_pydantic_convert import *

import os
from copy import deepcopy
from docxtpl import DocxTemplate, InlineImage


router = APIRouter()


# ------------------------------- 付款功能 -------------------------------
@router.get("/payment/{urlCondition}")
async def getPaymentData(
    request: Request,
    urlCondition: str,
    db: Session = Depends(get_db),
):
    # the datas will be shown on the frontend page
    crudInvoiceWKMaster = CRUD(db, InvoiceWKMasterDBModel)
    crudBillDetail = CRUD(db, BillDetailDBModel)
    print(urlCondition)
    getResult = []
    # if(urlCondition == "Status=PAYING"):
    if "Status" in urlCondition:
        dictCondition = convert_url_condition_to_dict(urlCondition)
        InvoiceWKMasterDataList = crudInvoiceWKMaster.get_with_condition(dictCondition)

        for InvoiceWKMasterData in InvoiceWKMasterDataList:
            receivedAmountSum = 0
            BillDetailDataList = crudBillDetail.get_with_condition(
                {"WKMasterID": InvoiceWKMasterData.WKMasterID}
            )
            for BillDetailData in BillDetailDataList:
                # 要與發票金額對得起來，必須要用抵扣前的金額資訊來對，所以此處已實收要納入已抵扣金額
                BillDetailData.ReceivedAmount = (
                    BillDetailData.ReceivedAmount + BillDetailData.DedAmount
                )
                receivedAmountSum = receivedAmountSum + BillDetailData.ReceivedAmount

            getResult.append(
                {
                    "InvoiceWKMaster": InvoiceWKMasterData,
                    "BillDetailList": BillDetailDataList,
                    "ReceivedAmountSum": receivedAmountSum,
                }
            )
        return getResult
    else:
        return {"message": "failed to get invoice data which is in PAYING"}


# 確認送出此次付款內容
@router.post("/payment/submit")
async def submitPayment(request: Request, db: Session = Depends(get_db)):
    """
    {
        "PaymentList": [
            {
                "InvoiceWKMaster": {...},
                "BillDetailList": [
                    {...},
                    {...},
                    ...
                ],
                "PayAmount":float,
                "Note":str,
                "Status":str
            },
            {...},
            {...},
            ...
        ]
    }
    """
    crudInvoiceWKMaster = CRUD(db, InvoiceWKMasterDBModel)
    crudBillDetail = CRUD(db, BillDetailDBModel)
    crudPayMaster = CRUD(db, PayMasterDBModel)
    crudPayStatement = CRUD(db, PayStatementDBModel)
    crudPayDraft = CRUD(db, PayDraftDBModel)
    crudPayDraftDetail = CRUD(db, PayDraftDetailDBModel)
    PaymentDataList = (await request.json())["PaymentList"]

    # Initial一筆付款紀錄主檔並新增至DB
    PayMasterDictData = {
        "SupplierName": PaymentDataList[0]["InvoiceWKMaster"]["SupplierName"],
        "FeeAmount": 0,
        "PaidAmount": 0,
        "PaidDate": convert_time_to_str(datetime.now()),
        "Note": "",
    }
    PayMasterSchemaData = PayMasterSchema(**PayMasterDictData)
    thisPayMaster = crudPayMaster.create(PayMasterSchemaData)

    # Initial一筆付款函稿主檔並新增至DB
    PayDraftDictData = {
        "PayMID": thisPayMaster.PayMID,
        "Payee": PayMasterDictData["SupplierName"],
        "CableInfo": "",
        "TotalFeeAmount": 0,
        "Subject": "",
        "Address": "",
        "CtactPerson": "",
        "Tel": "",
        "email": "",
        "IssueDate": PayMasterDictData["PaidDate"],
        "IssueNo": "",
        "OriginalTo": "",
        "CBPBankAcctNo": "",
        "BankAcctName": "",
        "BankName": "",
        "BankAddress": "",
        "BankAcctNo": "",
        "IBAN": "",
        "SWIFTCode": "",
        "Status": "TEMPORARY",
        "PayeeType": "SUPPLIER",
        "URI": "",
    }
    PayDraftSchemaData = PayDraftSchema(**PayDraftDictData)
    thisPayDraft = crudPayDraft.create(PayDraftSchemaData)

    for PaymentData in PaymentDataList:
        InvoiceWKMasterDictData = PaymentData["InvoiceWKMaster"]
        oldInvoiceWKMasterData = crudInvoiceWKMaster.get_with_condition(
            {"WKMasterID": InvoiceWKMasterDictData["WKMasterID"]}
        )[0]

        BillDetailDictDataList = PaymentData["BillDetailList"]
        for BillDetailDictData in BillDetailDictDataList:
            oldBillDetailData = crudBillDetail.get_with_condition(
                {"BillDetailID": BillDetailDictData["BillDetailID"]}
            )[0]
            # 更新BillDetail的累計實付與摘要說明,update to DB
            BillDetailDictData["PaidAmount"] = (
                BillDetailDictData["PaidAmount"] + BillDetailDictData["PayAmount"]
            )
            # 因頁面上傳來的累計實收是有加上DedAmount，所以要把它復原成DB原有的值
            # 才能做update BillDetailDictData["PaidAmount"]
            BillDetailDictData["ReceivedAmount"] = oldBillDetailData.ReceivedAmount
            crudBillDetail.update(oldBillDetailData, BillDetailDictData)

        # ----欲更新發票工作主檔的累計實付、付款日與狀態(或許)----
        newInvWKMasterPaidAmount = (
            InvoiceWKMasterDictData["PaidAmount"] + PaymentData["PayAmount"]
        )
        currTotalAmount = (
            InvoiceWKMasterDictData["TotalAmount"]
            - InvoiceWKMasterDictData["PaidAmount"]
        )
        InvoiceWKMasterDictData["PaidDate"] = convert_time_to_str(datetime.now())
        if PaymentData["Status"] == "COMPLETE":
            InvoiceWKMasterDictData["Status"] = PaymentData["Status"]
        InvoiceWKMasterDictData["PaidAmount"] = newInvWKMasterPaidAmount
        # update to DB
        crudInvoiceWKMaster.update(oldInvoiceWKMasterData, InvoiceWKMasterDictData)

        # ----新增付款記錄明細----
        PayStatementDictData = {
            "PayMID": thisPayMaster.PayMID,
            "WKMasterID": InvoiceWKMasterDictData["WKMasterID"],
            "InvoiceNo": InvoiceWKMasterDictData["InvoiceNo"],
            "FeeAmount": currTotalAmount,
            "PaidAmount": PaymentData["PayAmount"],
            "PaidDate": InvoiceWKMasterDictData["PaidDate"],
            "Note": PaymentData["Note"],
            "Status": PaymentData["Status"],
        }
        PayStatementSchemaData = PayStatementSchema(**PayStatementDictData)
        crudPayStatement.create(PayStatementSchemaData)

        # ----新增函稿明細----
        PayDraftDetailDictData = {
            "PayDraftID": thisPayDraft.PayDraftID,
            "InvoiceNo": InvoiceWKMasterDictData["InvoiceNo"],
            "FeeAmount": PaymentData["PayAmount"],
        }
        PayDraftDetailSchemaData = PayDraftDetailSchema(**PayDraftDetailDictData)
        crudPayDraftDetail.create(PayDraftDetailSchemaData)

        # ----累加付款紀錄主檔的資訊-----
        # 此次付款總金額 = 累加每張發票此次付款金額
        PayMasterDictData["PaidAmount"] = (
            PayMasterDictData["PaidAmount"] + PayStatementDictData["PaidAmount"]
        )
        # 此次應付總金額 = 累加每張發票(此次應付金額=總金額-累計實付金額)
        PayMasterDictData["FeeAmount"] = (
            PayMasterDictData["FeeAmount"] + currTotalAmount
        )

        # record log
        record_log(
            f"{user_name} paid to Supplier {InvoiceWKMasterDictData['InvoiceNo']} successfully.",
        )

    # 更新付款紀錄主檔、函稿主檔
    crudPayMaster.update(thisPayMaster, PayMasterDictData)
    PayDraftDictData["TotalFeeAmount"] = PayMasterDictData["PaidAmount"]
    crudPayDraft.update(thisPayDraft, PayDraftDictData)
    return


# -----------------------------------------------------------------------


# ---------------------------- 付款函稿管理頁面 --------------------------
@router.get("/paydraft/{urlCondition}")
async def showPaymentData(
    request: Request, urlCondition: str, db: Session = Depends(get_db)
):
    """
    input data:
    {
        "PayDraftID": int
    }

    output data:
    [
        {
            "PayDraft": {...},
            "PayDraftDetail": [
                {...},
                {...},
                {...}
            ]
        },
        {...},
        {...},
    ]

    """

    def process_data(data_list):
        result = []
        for data in data_list:
            detail_data_list = crudPayDraftDetail.get_with_condition(
                {"PayDraftID": data.PayDraftID}
            )
            result.append({"PayDraft": data, "PayDraftDetail": detail_data_list})
        return result

    crudPayDraft = CRUD(db, PayDraftDBModel)
    crudPayDraftDetail = CRUD(db, PayDraftDetailDBModel)
    table_name = "PayDraft"

    if urlCondition == "all":
        PayDraftDataList = crudPayDraft.get_all()
    elif all(x in urlCondition for x in ["start", "end"]):
        dictCondition = convert_url_condition_to_dict(urlCondition)
        sqlCondition = convert_dict_to_sql_condition(dictCondition, table_name)
        PayDraftDataList = crudPayDraft.get_all_by_sql(sqlCondition)
    else:
        dictCondition = convert_url_condition_to_dict_ignore_date(urlCondition)
        PayDraftDataList = crudPayDraft.get_with_condition(dictCondition)

    return process_data(PayDraftDataList)


# -----------------------------------------------------------------------
