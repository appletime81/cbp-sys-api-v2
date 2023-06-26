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
        "PayDraftCableInfo": str(使用者輸入),
        "PayDraftSubject": str(主旨),
        "PayDraftChineseTotalFeeAmount": str(中文總金額),
        "DownloadTemplate": true,
        "Preview": true,
        "Save": true,
        "Confirm": true,
    }

    example:
    {
        "PayDraftID": 2,
        "PayDraftCableInfo": "(使用者輸入CableInfo)",
        "PayDraftSubject": "(使用者輸入Subject)",
        "PayDraftChineseTotalFeeAmount": "二〇八四九四．五二",
        "DownloadTemplate": true,
        "Preview": false,
        "Save": false,
        "Confirm": false,
    }
    """
    requestDictData = await request.json()
    pprint(requestDictData)
    crudPayDraft = CRUD(db, PayDraftDBModel)
    crudSuppliers = CRUD(db, SuppliersDBModel)
    crudCorporates = CRUD(db, CorporatesDBModel)

    PayDraftData = crudPayDraft.get_with_condition(
        {"PayDraftID": requestDictData.get("PayDraftID")}
    )[0]
    newPayDraftData = deepcopy(PayDraftData)

    SuppliersData = crudSuppliers.get_with_condition(
        {
            "SubmarineCable": PayDraftData.SubmarineCable,
            "WorkTitle": PayDraftData.WorkTitle,
            "SupplierName": PayDraftData.Payee,
        }
    )[0]

    CorporatesData = crudCorporates.get_with_condition(
        {
            "SubmarineCable": PayDraftData.SubmarineCable,
            "WorkTitle": PayDraftData.WorkTitle,
        }
    )[0]
    newPayDraftData.CBPBankAcctNo = (
        CorporatesData.BankAcctNo
        if CorporatesData.BankAcctNo
        else CorporatesData.SavingAcctNo
    )
    newPayDraftData.OriginalTo = " ".join(
        [
            CorporatesData.BankName,
            CorporatesData.Branch if CorporatesData.Branch else "",
        ]
    )
    newPayDraftData.BankAcctName = SuppliersData.BankAcctName
    newPayDraftData.BankName = SuppliersData.BankName
    newPayDraftData.BankAcctNo = (
        SuppliersData.BankAcctNo
        if SuppliersData.BankAcctNo
        else SuppliersData.SavingAcctNo
    )
    newPayDraftData.IBAN = SuppliersData.IBAN if SuppliersData.IBAN else ""
    newPayDraftData.SWIFTCode = (
        SuppliersData.SWIFTCode if SuppliersData.SWIFTCode else ""
    )
    newPayDraftData.ACHNo = SuppliersData.ACHNo if SuppliersData.ACHNo else ""
    newPayDraftData.WireRouting = (
        SuppliersData.WireRouting if SuppliersData.WireRouting else ""
    )
    newPayDraftData.Subject = (
        requestDictData.get("Subject") if requestDictData.get("Subject") else ""
    )
    newPayDraftData.CableInfo = (
        requestDictData.get("CableInfo") if requestDictData.get("CableInfo") else ""
    )
    newPayDraftData.BankAddress = (
        SuppliersData.BankAddress if SuppliersData.BankAddress else ""
    )
    # =============================================
    # 拚湊 template context
    # =============================================
    context = {
        "PayDraftOriginalTo": newPayDraftData.OriginalTo,
        "PayDraftPayee": newPayDraftData.Payee,
        "PayDraftSubject": newPayDraftData.Subject,
        "PayDraftCableInfo": newPayDraftData.CableInfo,
        "PayDraftTotalFeeAmount": convert_number_to_string(
            str(newPayDraftData.TotalFeeAmount).split(".")
        ),
        "PayDraftCBPBankAcctNo": newPayDraftData.CBPBankAcctNo,
        "PayDraftBankAcctName": newPayDraftData.BankAcctName,
        "PayDraftBankName": newPayDraftData.BankName,
        "PayDraftBankAcctNo": newPayDraftData.BankAcctNo,
        "PayDraftIBAN": newPayDraftData.IBAN,
        "PayDraftSWIFTCode": newPayDraftData.SWIFTCode,
        "PayDraftACHNo": newPayDraftData.ACHNo,
        "PayDraftWireRouting": newPayDraftData.WireRouting,
        "PayDraftInvoiceNo": newPayDraftData.InvoiceNo,
        "PayDraftBankAddress": newPayDraftData.BankAddress,
    }

    if requestDictData.get("DownloadTemplate"):
        context["PayDraftSubject"] = PayDraftData.Subject
        context["PayDraftCableInfo"] = PayDraftData.CableInfo
        context["PayDraftBankAddress"] = PayDraftData.BankAddress
        context["PayDraftBankAcctName"] = PayDraftData.BankAcctName
        context["PayDraftCBPBankAcctNo"] = PayDraftData.CBPBankAcctNo
        context["PayDraftOriginalTo"] = PayDraftData.OriginalTo
        context["PayDraftBankName"] = PayDraftData.BankName
        context["PayDraftBankAcctNo"] = PayDraftData.BankAcctNo
        context["PayDraftIBAN"] = PayDraftData.IBAN
        context["PayDraftSWIFTCode"] = PayDraftData.SWIFTCode
        context["PayDraftWireRouting"] = PayDraftData.WireRouting
        context["PayDraftACHNo"] = PayDraftData.ACHNo
        context[
            "PayDraftChineseTotalFeeAmount"
        ] = convert_arabic_numerals_to_chinese_numerals(
            convert_number_to_string(str(PayDraftData.TotalFeeAmount).split("."))
        )
        fileName = "payment-supplier-letter-template-output"
        doc = DocxTemplate("templates/payment-supplier-letter-template.docx")
        doc.render(context)
        doc.save(f"{fileName}.docx")
        return FileResponse(path=f"{fileName}.docx", filename=f"{fileName}.docx")
    if requestDictData.get("Preview"):
        PayDraftDictData = orm_to_dict(PayDraftData)
        PayDraftDictData[
            "PayDraftChineseTotalFeeAmount"
        ] = convert_arabic_numerals_to_chinese_numerals(
            convert_number_to_string(str(PayDraftData.TotalFeeAmount).split("."))
        )
        return PayDraftDictData
    if requestDictData.get("Save"):
        newPayDraftData = crudPayDraft.update(
            PayDraftData, orm_to_dict(newPayDraftData)
        )
        return {"message": "temp save success", "PayDraft": newPayDraftData}
