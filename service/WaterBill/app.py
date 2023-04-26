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


@router.post("/uploadWaterBill")
async def uploadWaterBill(request: Request, db: Session = Depends(get_db)):
    fake_invoice_detail_dict_data = {
        "InvDetailID": 1,
        "InvMasterID": 2,
        "WKMasterID": 1,
        "WKDetailID": 2,
        "InvoiceNo": "test-inv-no",
        "PartyName": "test-party-name",
        "SupplierName": "test-supplier-name",
        "SubmarineCable": "test-submarine-cable",
        "WorkTitle": "test-work-title",
        "BillMilestone": "test-bill-milestone",
        "FeeItem": "test-fee-item",
        "FeeAmountPre": 1.0,
        "LBRatio": 1.0,
        "FeeAmountPost": 1.0,
        "Difference": 1.0,
        "Status": "test-status",
    }
    fake_invoice_detail_pydantic_data_lst = [InvoiceDetailSchema(**fake_invoice_detail_dict_data)]

    crud = CRUD(db, WaterBillDBModel)

    fake_water_bill_dict_data = {
        "InvoiceDetailList": fake_invoice_detail_pydantic_data_lst
    }

    newWaterBillPydanticData = WaterBillSchema(**fake_water_bill_dict_data)

    newWaterBillData = crud.create(newWaterBillPydanticData)

    return newWaterBillData
