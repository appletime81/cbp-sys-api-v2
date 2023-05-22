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


router = APIRouter()


@router.post("/InvoiceWKMaster/billedReturn")
async def invoiceWKMasterBilledReturn(
    request: Request, db: Session = Depends(get_db)
):
    """
    {
        "WKMasterID": int,
    }
    """

    crudBillMaster = CRUD(db, BillMasterDBModel)
    crudBillDetail = CRUD(db, BillDetailDBModel)
    crudInvoiceWKMaster = CRUD(db, InvoiceWKMasterDBModel)
    crudInvoiceMaster = CRUD(db, InvoiceMasterDBModel)
    crudInvoiceDetail = CRUD(db, InvoiceDetailDBModel)

    WKMasterID = (await request.json())["WKMasterID"]
    return
