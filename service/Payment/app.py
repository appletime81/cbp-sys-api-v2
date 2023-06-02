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


# ---------------------------- 付款函稿管理頁面 --------------------------
@router.get("/payment/{urlCondition}")
async def showPaymentData(
    request: Request, urlCondition: str, db: Session = Depends(get_db)
):
    """
    input data:
    {
        "PayDraftID": int
    }

    output data:
    [
        {
            "PayDraft": {...},
            "PayDraftDetail": [
                {...},
                {...},
                {...}
            ]
        },
        {...},
        {...},
    ]

    """

    def process_data(data_list):
        result = []
        for data in data_list:
            detail_data_list = crudPayDraftDetail.get_with_condition(
                {"PayDraftID": data.PayDraftID}
            )
            result.append({"PayDraft": data, "PayDraftDetail": detail_data_list})
        return result

    crudPayDraft = CRUD(db, PayDraftDBModel)
    crudPayDraftDetail = CRUD(db, PayDraftDetailDBModel)
    table_name = "PayDraft"

    if urlCondition == "all":
        PayDraftDataList = crudPayDraft.get_all()
    elif all(x in urlCondition for x in ["start", "end"]):
        dictCondition = convert_url_condition_to_dict(urlCondition)
        sqlCondition = convert_dict_to_sql_condition(dictCondition, table_name)
        PayDraftDataList = crudPayDraft.get_all_by_sql(sqlCondition)
    else:
        dictCondition = convert_url_condition_to_dict_ignore_date(urlCondition)
        PayDraftDataList = crudPayDraft.get_with_condition(dictCondition)

    return process_data(PayDraftDataList)


# -----------------------------------------------------------------------


# ------------------------------- 付款功能 -------------------------------
@router.get("/payment/{urlCondition}")
async def getPaymentData(
    request: Request,
    db: Session = Depends(get_db),
):
    # the datas will be shown on the frontend page
    pass


# -----------------------------------------------------------------------
