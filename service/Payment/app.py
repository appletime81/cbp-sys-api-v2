from fastapi import APIRouter, Request, Depends
from fastapi.responses import FileResponse

from crud import *
from get_db import get_db
from sqlalchemy.orm import Session
from utils.utils import *
from utils.orm_pydantic_convert import *

import os
from copy import deepcopy
from docxtpl import DocxTemplate, InlineImage


router = APIRouter()


# ------------------------------- 付款功能 -------------------------------
@router.get("/payment/datastream")
async def getPaymentDatastream(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    [
        {
            "InvoiceWKMaster": {...},
            "InvoiceDetail": {...},
            "BillDetail": {...}
        },
        {...},
    ]
    """
    getResult = []
    crudInvoiceWKMaster = CRUD(db, InvoiceWKMasterDBModel)
    crudInvoiceWKDetail = CRUD(db, InvoiceWKDetailDBModel)
    crudInvoiceMaster = CRUD(db, InvoiceMasterDBModel)
    crudInvoiceDetail = CRUD(db, InvoiceDetailDBModel)
    crudBillMaster = CRUD(db, BillMasterDBModel)
    crudBillDetail = CRUD(db, BillDetailDBModel)

    InvoiceWKMasterDataList = crudInvoiceWKMaster.get_with_condition(
        {"Status": "PAYING"}
    )
    for InvoiceWKMasterData in InvoiceWKMasterDataList:
        # ------------------------ 抓取 InvoiceDetail ------------------------
        InvoiceDetailDataList = crudInvoiceDetail.get_with_condition(
            {"WKMasterID": InvoiceWKMasterData.WKMasterID}
        )
        # -------------------------------------------------------------------

        for InvoiceDetailData in InvoiceDetailDataList:
            # ------------------------ 抓取 BillDetail ------------------------
            BillDetailDataList = crudBillDetail.get_with_condition(
                {"InvDetailID": InvoiceDetailData.InvDetailID}
            )
            # ----------------------------------------------------------------
            if BillDetailDataList:
                BillDetailData = BillDetailDataList[0]
                data = {
                    "InvoiceWKMaster": InvoiceWKMasterData,
                    "InvoiceDetail": InvoiceDetailData,
                    "BillDetail": BillDetailData,
                }

                getResult.append(data)

    # ------------------------ test part ------------------------
    df_dict = {}
    for data in getResult:
        for k, v in orm_to_dict(data["InvoiceWKMaster"]).items():
            if "InvoiceWKMaster_" + k not in df_dict:
                df_dict["InvoiceWKMaster_" + k] = []
            df_dict["InvoiceWKMaster_" + k].append(v)
        for k, v in orm_to_dict(data["InvoiceDetail"]).items():
            if "InvoiceDetail_" + k not in df_dict:
                df_dict["InvoiceDetail_" + k] = []
            df_dict["InvoiceDetail_" + k].append(v)
        for k, v in orm_to_dict(data["BillDetail"]).items():
            if "BillDetail_" + k not in df_dict:
                df_dict["BillDetail_" + k] = []
            df_dict["BillDetail_" + k].append(v)

    df = pd.DataFrame(df_dict)
    df.to_excel("test.xlsx", index=False)

    return getResult


@router.post("/InvoiceWKMaster/payment")
async def paymentForInvWKMaster(
    request: Request,
    db: Session = Depends(get_db),
):
    pass


def test():
    df = pd.read_excel("test.xlsx")
    # if the "PP_NAME" column's value is string called "FALSE", it will be converted to False
    df["PP_NAME"] = df["PP_NAME"].apply(lambda x: False if x == "FALSE" else True)
