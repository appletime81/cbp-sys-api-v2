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
        "TempSave": true,
        "Confirm": true,
    }
    """
    requestDictData = await request.json()
    pprint(requestDictData)
    crudPayMaster = CRUD(db, PayMasterDBModel)
    crudPayStatement = CRUD(db, PayStatementDBModel)
    crudPayDraft = CRUD(db, PayDraftDBModel)
    crudPayDraftDetail = CRUD(db, PayDraftDetailDBModel)
    crudSuppliers = CRUD(db, SuppliersDBModel)
    crudCorporates = CRUD(db, CorporatesDBModel)

    PayDraftData = crudPayDraft.get_with_condition(
        {"PayDraftID": requestDictData.get("PayDraftID")}
    )[0]
    oldPayDraftData = deepcopy(PayDraftData)

    SuppliersData = crudSuppliers.get_with_condition(
        {
            "SubmarineCable": PayDraftData.SubmarineCable,
            "WorkTitle": PayDraftData.WorkTitle,
            "SupplierName": PayDraftData.Payee,
        }
    )[0]

    CBPBankAcctNoDictCondition = {
        "SubmarineCable": PayDraftData.SubmarineCable,
        "WorkTitle": PayDraftData.WorkTitle,
    }
    PayDraftData.CBPBankAcctNo = (
        crudCorporates.get_with_condition(CBPBankAcctNoDictCondition)[0].BankAcctNo
        if crudCorporates.get_with_condition(CBPBankAcctNoDictCondition)[0].BankAcctNo
        else crudCorporates.get_with_condition(CBPBankAcctNoDictCondition)[
            0
        ].SavingAcctNo
    )
    PayDraftData.BankAcctName = SuppliersData.BankAcctName
    PayDraftData.BankName = SuppliersData.BankName
    PayDraftData.AcctNo = (
        SuppliersData.BankAcctNo
        if SuppliersData.BankAcctNo
        else SuppliersData.SavingAcctNo
    )
    PayDraftData.IBAN = SuppliersData.IBAN if SuppliersData.IBAN else ""
    PayDraftData.SWIFTCode = SuppliersData.SWIFTCode if SuppliersData.SWIFTCode else ""
    PayDraftData.ACHNo = SuppliersData.ACHNo if SuppliersData.ACHNo else ""
    PayDraftData.WireRouting = (
        SuppliersData.WireRouting if SuppliersData.WireRouting else ""
    )
    PayDraftData.Subject = (
        requestDictData.get("PayDraftSubject")
        if requestDictData.get("PayDraftSubject")
        else ""
    )
    PayDraftData.CableInfo = (
        requestDictData.get("PayDraftCableInfo")
        if requestDictData.get("PayDraftCableInfo")
        else ""
    )
    # =============================================
    # 拚湊 template context
    # =============================================
    context = {
        "PayDraftPayee": "",
        "PayDraftSubject": PayDraftData.Subject,
        "PayDraftChineseTotalFeeAmount": requestDictData.get(
            "PayDraftChineseTotalFeeAmount"
        )
        if requestDictData.get("PayDraftChineseTotalFeeAmount")
        else "",
        "PayDraftCableInfo": PayDraftData.CableInfo,
        "PayDraftTotalFeeAmount": PayDraftData.TotalFeeAmount,
        "PayDraftCBPBankAcctNo": PayDraftData.CBPBankAcctNo,
        "PayDraftBankAcctName": PayDraftData.BankAcctName,
        "PayDraftBankName": PayDraftData.BankName,
        "PayDraftAcctNo": PayDraftData.AcctNo,
        "PayDraftIBAN": PayDraftData.IBAN,
        "PayDraftSWIFTCode": PayDraftData.SWIFTCode,
        "PayDraftACHNo": PayDraftData.ACHNo,
        "PayDraftWireRouting": PayDraftData.WireRouting,
        "PayDraftInvoiceNo": PayDraftData.InvoiceNo,
        "PayDraftBankAddress": SuppliersData.BankAddress
        if SuppliersData.BankAddress
        else "",
    }

    if requestDictData.get("DownloadTemplate"):
        fileName = "payment-supplier-letter-template-output"
        doc = DocxTemplate("templates/payment-supplier-letter-template.docx")
        doc.render(context)
        doc.save(f"{fileName}.docx")
        return FileResponse(path=f"{fileName}.docx", filename=f"{fileName}.docx")
    if requestDictData.get("Preview"):
        return context
    if requestDictData.get("TempSave"):
        newPayDraftData = crudPayDraft.update(
            oldPayDraftData, orm_to_dict(PayDraftData)
        )
        return {"message": "temp save success", "PayDraft": newPayDraftData}
