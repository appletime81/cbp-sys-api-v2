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


@router.post("/getPayDraftStream")
async def getPayDraftStream(request: Request, db: Session = Depends(get_db)):
    """
    input data:
    {
        "PayDraftID": int,
        "IssueDate": "2023/01/01",
        "SubmarineCablePayment": "海纜款項",
        "username": "string"(預留)
        "GetTemplate": bool
    }
    """
    PayDraftID = (await request.json())["PayDraftID"]
    crudPayDraft = CRUD(db, PayDraftDBModel)
    crudPayDraftDetail = CRUD(db, PayDraftDetailDBModel)
    crudPayMaster = CRUD(db, PayMasterDBModel)

    PayDraftData = crudPayDraft.get_with_condition({"PayDraftID": PayDraftID})[0]
    PayDraftDetailDataList = crudPayDraftDetail.get_with_condition(
        {"PayDraftID": PayDraftID}
    )
    PayMasterData = crudPayMaster.get_with_condition(
        {"PayMasterID": PayDraftData.PayMasterID}
    )[0]
    SupplierName = PayMasterData.SupplierName

    if (await request.json())["GetTemplate"]:
        PostingDate = convert_time_to_str(PayDraftData.IssueDate)
        print(PostingDate)
        print(type(PostingDate))
        context = {
            "PostingYear": PostingDate[:4],
            "PostingMonth": PostingDate[5:7],
            "PostingDay": PostingDate[8:10],
        }
        return context
