from fastapi import APIRouter, Request, Depends

from fastapi.responses import FileResponse

from crud import *
from get_db import get_db
from sqlalchemy.orm import Session
from utils.utils import *
from utils.log import *
from utils.orm_pydantic_convert import *

from docxtpl import DocxTemplate

import os
from copy import deepcopy


router = APIRouter()


@router.post("/getPayDraftStream")
async def getPayDraftStream(request: Request, db: Session = Depends(get_db)):
    """
    input data:
    {
        "PayDraftID": int,
        "PaymentUSerInput": str,
        "PaidAmountChinese": str,
        "SubmarineCableInfo": str,
    }
    """
    PayDraftID = (await request.json())["PayDraftID"]

    crudInvoiceWKMaster = CRUD(db, InvoiceWKMasterDBModel)
    crudCorporates = CRUD(db, CorporatesDBModel)
    crudPayDraft = CRUD(db, PayDraftDBModel)
    crudPayMaster = CRUD(db, PayMasterDBModel)
    crudPayStatement = CRUD(db, PayStatementDBModel)
    crudSuppliers = CRUD(db, SuppliersDBModel)

    PayDraftData = crudPayDraft.get_with_condition({"PayDraftID": PayDraftID})[0]

    # =============================================
    # 利用PayDraft取得PayMaster
    # =============================================
    PayMasterData = crudPayMaster.get_with_condition({"PayMID": PayDraftData.PayMID})[0]

    # =============================================
    # 利用PayMaster取得PayStatement
    # =============================================
    PayStatementDataList = crudPayStatement.get_with_condition(
        {"PayMID": PayMasterData.PayMID}
    )

    # =============================================
    # 利用其中一個PayStatement取得InvoiceNo
    # 再利用InvoiceNo取得InvoiceWKMaster
    # 並從InvoiceWKMaster取得SubmarineCable和WorkTitle
    # =============================================
    InvoiceWKMasterData = crudInvoiceWKMaster.get_with_condition(
        {"InvoiceNo": PayStatementDataList[0].InvoiceNo}
    )[0]
    SupplierData = crudSuppliers.get_with_condition(
        {
            "SupplierName": InvoiceWKMasterData.SupplierName,
            "WorkTitle": InvoiceWKMasterData.WorkTitle,
            "SubmarineCable": InvoiceWKMasterData.SubmarineCable,
        }
    )[0]
    # =============================================
    # 抓取Corporate資料
    # =============================================
    CorporateData = crudCorporates.get_with_condition(
        {
            "SubmarineCable": InvoiceWKMasterData.SubmarineCable,
            "WorkTitle": InvoiceWKMasterData.WorkTitle,
        }
    )[0]

    # =============================================
    # 提取Template需要的資料
    # =============================================
    CorporateAccountNo = (
        CorporateData.BankAcctName
        if CorporateData.BankAcctName
        else CorporateData.SavingAcctNo
    )

    InvoiceNo = "/".join(
        [PayStatementData.InvoiceNo for PayStatementData in PayStatementDataList]
    )

    SubmarineCableInfo = (await request.json())["SubmarineCableInfo"]

    PaidAmount = convert_number_to_string(str(PayDraftData.TotalFeeAmount).split("."))

    SupplierName = SupplierData.SupplierName
    SupplierAccountName = SupplierData.BankAcctName
    SupplierAccountNo = (
        SupplierData.BankAcctNo
        if SupplierData.BankAcctNo
        else SupplierData.SavingAcctNo
    )
    SupplierBankName = SupplierData.BankName
    SupplierBankAddress = SupplierData.BankAddress
    SupplierIBAN = SupplierData.IBAN
    SupplierSWIFT = SupplierData.SWIFTCode
    SupplierACHNo = SupplierData.ACHNo
    SupplierWireRouting = SupplierData.WireRouting

    if (await request.json())["GetTemplate"]:
        context = {
            "CorporateAccountNo": CorporateAccountNo if CorporateAccountNo else "n/a",
            "InvoiceNo": InvoiceNo if InvoiceNo else "n/a",
            "PaymentUSerInput": (await request.json())["PaymentUSerInput"],
            "PaidAmountChinese": (await request.json())["PaidAmountChinese"],
            "SubmarineCableInfo": SubmarineCableInfo if SubmarineCableInfo else "n/a",
            "PaidAmount": PaidAmount if PaidAmount else "n/a",
            "SupplierName": SupplierName if SupplierName else "n/a",
            "SupplierAccountName": (
                SupplierAccountName if SupplierAccountName else "n/a"
            ),
            "SupplierAccountNo": SupplierAccountNo if SupplierAccountNo else "n/a",
            "SupplierBankName": SupplierBankName if SupplierBankName else "n/a",
            "SupplierBankAddress": (
                SupplierBankAddress if SupplierBankAddress else "n/a"
            ),
            "SupplierIBAN": SupplierIBAN if SupplierIBAN else "n/a",
            "SupplierSWIFT": SupplierSWIFT if SupplierSWIFT else "n/a",
            "SupplierACHNo": SupplierACHNo if SupplierACHNo else "n/a",
            "SupplierWireRouting": (
                SupplierWireRouting if SupplierWireRouting else "n/a"
            ),
        }

        doc = DocxTemplate("templates/payment-supplier-letter-template.docx")
        doc.render(context)
        fileName = "payment-supplier-letter-template.docx"
        doc.save(f"{fileName}")

        return context


# @router.post("/getPayDraftStream")
# async def getPayDraftStream(request: Request, db: Session = Depends(get_db)):
#     """
#     input data:
#     {
#         "PayDraftID": int,
#         "PaymentUSerInput": str,
#         "PaidAmountChinese": str,
#         "SubmarineCableInfo": str,
#     }
#     """
#     CorporateAccountNo = "007-53-110022"
#
#     InvoiceNo = "/".join(["15328", "15428"])
#
#     PaidAmount = convert_number_to_string(str(48576.00).split("."))
#
#     SupplierName = "CIENA JP"
#     SupplierAccountName = "Ciena Communications Japan Co. Ltd."
#     SupplierAccountNo = "6550207141"
#     SupplierBankName = "JPMorgan Chase Bank Luxembourg S.A."
#     SupplierBankAddress = "6 route de Treves, Senningerberg, 2633, Luxembourg"
#     SupplierIBAN = "LU290670006550207141"
#     SupplierSWIFT = "CHASLULX"
#     SupplierACHNo = "xxxxxxxxxx"
#     SupplierWireRouting = "xxxxxxxxxxx"
#
#     if (await request.json())["GetTemplate"]:
#         context = {
#             "CorporateAccountNo": CorporateAccountNo,
#             "InvoiceNo": InvoiceNo,
#             "PaymentUSerInput": (await request.json())["PaymentUSerInput"],
#             "PaidAmountChinese": (await request.json())["PaidAmountChinese"],
#             "SubmarineCableInfo": (await request.json())["SubmarineCableInfo"],
#             "PaidAmount": PaidAmount,
#             "SupplierName": SupplierName,
#             "SupplierAccountName": SupplierAccountName,
#             "SupplierAccountNo": SupplierAccountNo,
#             "SupplierBankName": SupplierBankName,
#             "SupplierBankAddress": SupplierBankAddress,
#             "SupplierIBAN": SupplierIBAN,
#             "SupplierSWIFT": SupplierSWIFT,
#             "SupplierACHNo": SupplierACHNo,
#             "SupplierWireRouting": SupplierWireRouting,
#         }
#
#         doc = DocxTemplate("templates/payment-supplier-letter-template.docx")
#         doc.render(context)
#         fileName = "payment-supplier-letter-template.docx"
#         doc.save(f"{fileName}")
#         return FileResponse(path=fileName, filename=fileName)
