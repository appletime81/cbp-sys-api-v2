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
    crudInvoiceWKDetail = CRUD(db, InvoiceWKDetailDBModel)
    crudBillDetail = CRUD(db, BillDetailDBModel)
    crudBillMaster = CRUD(db, BillMasterDBModel)

    BillMilestone = requestDictData.pop("BillMilestone", None)
    Status = requestDictData.pop("Status", None)
    InvoiceNo = requestDictData.pop("InvoiceNo", None)
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
        InvoiceWKMasterData.WKMasterID
        for InvoiceWKMasterData in InvoiceWKMasterDataList
    ]

    if BillMilestone:
        InvoiceWKDetailDataList = crudInvoiceWKDetail.get_value_if_in_a_list(
            InvoiceWKDetailDBModel.WKMasterID, WKMasterIDList
        )
        WKMasterIDList = list(
            set(
                [
                    InvoiceWKDetailData.WKMasterID
                    for InvoiceWKDetailData in InvoiceWKDetailDataList
                    if InvoiceWKDetailData.BillMilestone == BillMilestone
                ]
            )
        )

    InvoiceWKMasterDataList = list(
        filter(lambda x: x.WKMasterID in WKMasterIDList, InvoiceWKMasterDataList)
    )

    # =============================================
    # 抓取 BillDetail(by WKMasterID)
    # =============================================
    BillDetailDataList = crudBillDetail.get_value_if_in_a_list(
        BillDetailDBModel.WKMasterID, WKMasterIDList
    )

    # =============================================
    # 組成結果
    # =============================================
    getResult = []
    for InvoiceWKMasterData in InvoiceWKMasterDataList:
        tempBillDetailDataList = list(
            filter(
                lambda x: x.WKMasterID == InvoiceWKMasterData.WKMasterID,
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
        getResult.append(
            {
                "InvoiceWKMaster": InvoiceWKMasterData,
                "BillMaster": crudBillMaster.get_value_if_in_a_list(
                    BillMasterDBModel.BillMasterID, tempBillMasterIDList
                ),
            }
        )

    if InvoiceNo:
        getResult = [
            result
            for result in getResult
            if InvoiceNo in result["InvoiceWKMaster"].InvoiceNo
        ]
    return getResult
