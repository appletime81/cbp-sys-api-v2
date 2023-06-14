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
        "CableInfo": str(使用者輸入),
        "Subject": str(主旨),
        "ChineseTotalFeeAmount": str(中文總金額),
        "DownloadTemplate": true / false
    }
    """
    requestDictData = await request.json()
    crudPayMaster = CRUD(db, PayMasterDBModel)
    crudPayStatement = CRUD(db, PayStatementDBModel)
    crudPayDraft = CRUD(db, PayDraftDBModel)
    crudPayDraftDetail = CRUD(db, PayDraftDetailDBModel)
    crudSuppliers = CRUD(db, SuppliersDBModel)

    PayDraftData = crudPayDraft.get(requestDictData.get("PayDraftID"))[0]

    # =============================================
    # 拚湊 template context
    # =============================================
    context = {
        "PayDraftPayee": "",
        "PayDraftSubject": requestDictData.get("Subject")
        if requestDictData.get("Subject")
        else "",
        "PayDraftChineseTotalFeeAmount": requestDictData.get("ChineseTotalFeeAmount")
        if requestDictData.get("ChineseTotalFeeAmount")
        else "",
        "PayDraftCableInfo": requestDictData.get("CableInfo")
        if requestDictData.get("CableInfo")
        else "",
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
    }

    if requestDictData.get("DownloadTemplate"):
        pass

    return None
