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
    newPayDraftData.AcctNo = (
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
        requestDictData.get("PayDraftSubject")
        if requestDictData.get("PayDraftSubject")
        else ""
    )
    newPayDraftData.CableInfo = (
        requestDictData.get("PayDraftCableInfo")
        if requestDictData.get("PayDraftCableInfo")
        else ""
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
        "PayDraftChineseTotalFeeAmount": requestDictData.get(
            "PayDraftChineseTotalFeeAmount"
        )
        if requestDictData.get("PayDraftChineseTotalFeeAmount")
        else "",
        "PayDraftCableInfo": newPayDraftData.CableInfo,
        "PayDraftTotalFeeAmount": newPayDraftData.TotalFeeAmount,
        "PayDraftCBPBankAcctNo": newPayDraftData.CBPBankAcctNo,
        "PayDraftBankAcctName": newPayDraftData.BankAcctName,
        "PayDraftBankName": newPayDraftData.BankName,
        "PayDraftAcctNo": newPayDraftData.AcctNo,
        "PayDraftIBAN": newPayDraftData.IBAN,
        "PayDraftSWIFTCode": newPayDraftData.SWIFTCode,
        "PayDraftACHNo": newPayDraftData.ACHNo,
        "PayDraftWireRouting": newPayDraftData.WireRouting,
        "PayDraftInvoiceNo": newPayDraftData.InvoiceNo,
        "PayDraftBankAddress": newPayDraftData.BankAddress,
    }

    if requestDictData.get("DownloadTemplate"):
        fileName = "payment-supplier-letter-template-output"
        doc = DocxTemplate("templates/payment-supplier-letter-template.docx")
        doc.render(context)
        doc.save(f"{fileName}.docx")
        return FileResponse(path=f"{fileName}.docx", filename=f"{fileName}.docx")
    if requestDictData.get("Preview"):
        return PayDraftData
    if requestDictData.get("Save"):
        newPayDraftData = crudPayDraft.update(
            PayDraftData, orm_to_dict(newPayDraftData)
        )
        return {"message": "temp save success", "PayDraft": newPayDraftData}

