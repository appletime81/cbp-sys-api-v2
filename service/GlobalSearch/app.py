import os
from datetime import timedelta

from fastapi import APIRouter, Request, status, Depends
from crud import *
from get_db import get_db
from sqlalchemy.orm import Session
from utils.utils import *
from utils.orm_pydantic_convert import *
from copy import deepcopy


router = APIRouter()


@router.post("/searchBillMasterByInvoiceWKMaster", status_code=status.HTTP_200_OK)
async def searchBillMasterByInvoiceWKMaster(
    request: Request, db: Session = Depends(get_db)
):
    """
    input data:
    {
        "SupplierName": "str",
        "SubmarineCable": "str",
        "WorkTitle": "str",
        "InvoiceNo": "str",
        "BillMilestone": "str"
        "startDueDate": "2023XXXX",
        "endDueDate": "2023XXXX",
        "Status": ["str1", "str2",...,"strn"]
    }

    Output:
    [
        {
            "InvoiceWKMaster": {},
            "BillMaster": {}
        },
        {...},
        {...}
    ]
    """
    requestDictData = await request.json()

    crudInvoiceWKMaster = CRUD(db, InvoiceWKMasterDBModel)

    BillMilestone = requestDictData.pop("BillMilestone", None)
    Status = requestDictData.pop("Status", None)
    startDueDateString = requestDictData.pop("startDueDate", None)
    endDueDateString = requestDictData.pop("endDueDate", None)
    startDueDate = (
        datetime.strptime(startDueDateString, "%Y%m%d") if startDueDateString else None
    )
    endDueDate = (
        datetime.strptime(endDueDateString, "%Y%m%d") if endDueDateString else None
    )
    if startDueDate == endDueDate:
        endDueDate = endDueDate + timedelta(days=1)

    pprint(requestDictData)

    InvoiceWKMasterDataList = crudInvoiceWKMaster.get_with_condition(requestDictData)

    if startDueDate and endDueDate:
        InvoiceWKMasterDataList = [
            InvoiceWKMasterData
            for InvoiceWKMasterData in InvoiceWKMasterDataList
            if startDueDate <= InvoiceWKMasterData.DueDate < endDueDate
        ]
    if Status:
        InvoiceWKMasterDataList = [
            InvoiceWKMasterData
            for InvoiceWKMasterData in InvoiceWKMasterDataList
            if InvoiceWKMasterData.Status in Status
        ]

    WKMasterIDList = [
        InvoiceWKMasterData.WKMasterID for InvoiceWKMasterData in InvoiceWKMasterDataList
    ]

    