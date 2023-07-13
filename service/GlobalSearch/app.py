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
            "BillMaster": [
                {...},
                {...}
            ]
        },
        {...},
        {...}
    ]
    """

    def parse_date(date_string):
        return datetime.strptime(date_string, "%Y%m%d") if date_string else None

    def increment_day(date):
        return date + timedelta(days=1) if date else None

    requestDictData = await request.json()

    crudInvoiceWKMaster = CRUD(db, InvoiceWKMasterDBModel)
    crudInvoiceWKDetail = CRUD(db, InvoiceWKDetailDBModel)
    crudBillDetail = CRUD(db, BillDetailDBModel)
    crudBillMaster = CRUD(db, BillMasterDBModel)

    BillMilestone = requestDictData.pop("BillMilestone", None)
    Status = requestDictData.pop("Status", None)
    InvoiceNo = requestDictData.pop("InvoiceNo", None)

    date_fields = ["startDueDate", "endDueDate", "startIssueDate", "endIssueDate"]

    startDueDate, endDueDate, startIssueDate, endIssueDate = (
        parse_date(requestDictData.pop(field, None)) for field in date_fields
    )

    endDueDate, endIssueDate = increment_day(endDueDate), increment_day(endIssueDate)

    date_ranges = [
        (startDueDate, endDueDate, "DueDate"),
        (startIssueDate, endIssueDate, "IssueDate"),
    ]

    InvoiceWKMasterDataList = crudInvoiceWKMaster.get_with_condition(requestDictData)

    InvoiceWKDetailDataList = None
    for start, end, attr in date_ranges:
        if start and end:
            InvoiceWKMasterDataList = [
                data
                for data in InvoiceWKMasterDataList
                if start <= getattr(data, attr) < end
            ]

    if Status:
        InvoiceWKMasterDataList = [
            InvoiceWKMasterData
            for InvoiceWKMasterData in InvoiceWKMasterDataList
            if InvoiceWKMasterData.Status in Status
        ]
    if InvoiceNo:
        InvoiceWKMasterDataList = [
            InvoiceWKMasterData
            for InvoiceWKMasterData in InvoiceWKMasterDataList
            if InvoiceNo in InvoiceWKMasterData.InvoiceNo
            or InvoiceNo == InvoiceWKMasterData.InvoiceNo
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

    if not WKMasterIDList:
        return []

    if not InvoiceWKDetailDataList:
        InvoiceWKDetailDataList = crudInvoiceWKDetail.get_value_if_in_a_list(
            InvoiceWKDetailDBModel.WKMasterID, WKMasterIDList
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

        BillMilestoneList = list(
            set(
                [
                    tempInvoiceWKDetailData.BillMilestone
                    for tempInvoiceWKDetailData in list(
                        filter(
                            lambda x: x.WKMasterID == InvoiceWKMasterData.WKMasterID,
                            InvoiceWKDetailDataList,
                        )
                    )
                ]
            )
        )
        BillMilestoneListString = ", ".join(BillMilestoneList)
        InvoiceWKMasterDictData = orm_to_dict(deepcopy(InvoiceWKMasterData))
        InvoiceWKMasterDictData["BillMilestone"] = BillMilestoneListString

        BillMasterDataList = crudBillMaster.get_value_if_in_a_list(
            BillMasterDBModel.BillMasterID, tempBillMasterIDList
        )

        BillMasterDictDataList = []
        for BillMasterData in BillMasterDataList:
            BillMasterDictData = orm_to_dict(deepcopy(BillMasterData))
            tempBillDetailDataList = crudBillDetail.get_with_condition(
                {"BillMasterID": BillMasterData.BillMasterID}
            )
            BillMilestoneString = ", ".join(
                list(
                    set(
                        [
                            tempBillDetailData.BillMilestone
                            for tempBillDetailData in tempBillDetailDataList
                        ]
                    )
                )
            )
            BillMasterDictData["BillMilestone"] = BillMilestoneString
            BillMasterDictDataList.append(BillMasterDictData)

        getResult.append(
            {
                "InvoiceWKMaster": InvoiceWKMasterDictData,
                "BillMaster": BillMasterDictDataList,
            }
        )

    return getResult


@router.post("/searchInvoiceWKMasterByBillMaster", status_code=status.HTTP_200_OK)
async def searchInvoiceWKMasterByBillMaster(
    request: Request, db: Session = Depends(get_db)
):
    """
    input data:
    {
        "PartyName": "str",
        "SubmarineCable": "str",
        "WorkTitle": "str",
        "BillingNo": "str",
        "BillMilestone": "str",
        "startDueDate": "2023XXXX",
        "endDueDate": "2023XXXX",
    }

    Output:
    [
        {
            "BillMaster": {},
            "InvoiceWKMaster": [
                {...},
                {...}
            ]
        },
        {...},
        {...}
    ]
    """

    def parse_date(date_string):
        return datetime.strptime(date_string, "%Y%m%d") if date_string else None

    def increment_day(date):
        return date + timedelta(days=1) if date else None

    requestDictData = await request.json()

    crudInvoiceWKMaster = CRUD(db, InvoiceWKMasterDBModel)
    crudInvoiceWKDetail = CRUD(db, InvoiceWKDetailDBModel)
    crudBillDetail = CRUD(db, BillDetailDBModel)
    crudBillMaster = CRUD(db, BillMasterDBModel)

    BillMilestone = requestDictData.pop("BillMilestone", None)
    BillingNo = requestDictData.pop("BillingNo", None)

    date_fields = ["startDueDate", "endDueDate"]

    startDueDate, endDueDate = (
        parse_date(requestDictData.pop(field, None)) for field in date_fields
    )

    endDueDate = increment_day(endDueDate)

    date_ranges = [(startDueDate, endDueDate, "DueDate")]

    BillMasterDataList = crudBillMaster.get_with_condition(requestDictData)

    BillDetailDataList = None
    for start, end, attr in date_ranges:
        if start and end:
            BillMasterDataList = [
                data
                for data in BillMasterDataList
                if start <= getattr(data, attr) < end
            ]

    if BillingNo:
        BillMasterDataList = [
            BillMasterData
            for BillMasterData in BillMasterDataList
            if BillingNo in BillMasterData.BillingNo
            or BillingNo == BillMasterData.BillingNo
        ]

    BillMasterIDList = [
        BillMasterData.BillMasterID for BillMasterData in BillMasterDataList
    ]

    if BillMilestone:
        BillDetailDataList = crudBillDetail.get_value_if_in_a_list(
            BillDetailDBModel.BillMasterID, BillMasterIDList
        )
        BillMasterIDList = list(
            set(
                [
                    BillDetailData.BillMasterID
                    for BillDetailData in BillDetailDataList
                    if BillDetailData.BillMilestone == BillMilestone
                ]
            )
        )

    if not BillMasterIDList:
        return []

    if not BillDetailDataList:
        BillDetailDataList = crudBillDetail.get_value_if_in_a_list(
            BillDetailDBModel.BillMasterID, BillMasterIDList
        )

    # =============================================
    # 抓取 InvoiceWKMaster(by WKMasterID)
    # =============================================
    InvoiceWKMasterDataList = crudInvoiceWKMaster.get_value_if_in_a_list(
        InvoiceWKMasterDBModel.WKMasterID,
        list(set([BillDetailData.WKMasterID for BillDetailData in BillDetailDataList])),
    )
    InvoiceWKMasterDictIncludeBillMasterIDList = list()
    for InvoiceWKMasterData in InvoiceWKMasterDataList:
        tempInvoiceWKMasterDictData = orm_to_dict(deepcopy(InvoiceWKMasterData))
        tempBillMasterDataList = list(
            set(
                list(
                    filter(
                        lambda x: x.WKMasterID == InvoiceWKMasterData.WKMasterID,
                        BillDetailDataList,
                    )
                )
            )
        )
        tempInvoiceWKMasterDictData["BillMasterIDList"] = list(
            set(
                [
                    tempBillMasterData.BillMasterID
                    for tempBillMasterData in tempBillMasterDataList
                ]
            )
        )
        InvoiceWKMasterDictIncludeBillMasterIDList.append(tempInvoiceWKMasterDictData)

    getResult = []
    InvoiceWKDetailDataList = crudInvoiceWKDetail.get_value_if_in_a_list(
        InvoiceWKDetailDBModel.WKMasterID,
        list(
            set(
                [
                    InvoiceWKMasterData.WKMasterID
                    for InvoiceWKMasterData in InvoiceWKMasterDataList
                ]
            )
        ),
    )
    for BillMasterData in BillMasterDataList:
        tempInvoiceWKMasterDictDataList = list(
            filter(
                lambda x: BillMasterData.BillMasterID in x["BillMasterIDList"],
                InvoiceWKMasterDictIncludeBillMasterIDList,
            )
        )

        tempInvoiceWKMasterDictDataWithBillMilestoneList = list()
        for tempInvoiceWKMasterDictData in tempInvoiceWKMasterDictDataList:
            tempInvoiceWKMasterDictData["BillMilestone"] = ", ".join(
                list(
                    set(
                        [
                            InvoiceWKDetailData.BillMilestone
                            for InvoiceWKDetailData in list(
                                filter(
                                    lambda x: x.WKMasterID
                                    == tempInvoiceWKMasterDictData["WKMasterID"],
                                    InvoiceWKDetailDataList,
                                )
                            )
                        ]
                    )
                )
            )
            tempInvoiceWKMasterDictDataWithBillMilestoneList.append(
                tempInvoiceWKMasterDictData
            )

        tempBillMilestoneString = ", ".join(
            list(
                set(
                    [
                        tempBillDetailData.BillMilestone
                        for tempBillDetailData in list(
                            filter(
                                lambda x: x.BillMasterID == BillMasterData.BillMasterID,
                                BillDetailDataList,
                            )
                        )
                    ]
                )
            )
        )
        BillMasterDictData = orm_to_dict(deepcopy(BillMasterData))
        BillMasterDictData["BillMilestone"] = tempBillMilestoneString
        getResult.append(
            {
                "BillMaster": BillMasterDictData,
                "InvoiceWKMaster": tempInvoiceWKMasterDictDataWithBillMilestoneList,
            }
        )

    return getResult
