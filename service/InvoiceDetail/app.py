from fastapi import APIRouter, Request, status, Depends, Body
from crud import *
from get_db import get_db
from sqlalchemy.orm import Session
from utils.utils import *
from utils.orm_pydantic_convert import orm_to_pydantic
from copy import deepcopy

router = APIRouter()


# ------------------------------ InvoiceDetail ------------------------------
# 建立InvoiceDetail
@router.post("/InvoiceDetail", status_code=status.HTTP_201_CREATED)
async def addInvoiceDetail(
    request: Request,
    InvoiceDetailPydanticData: InvoiceDetailSchema,
    db: Session = Depends(get_db),
):
    crud = CRUD(db, InvoiceDetailDBModel)
    crud.create(InvoiceDetailPydanticData)
    return {
        "message": "InvoiceDetail successfully created",
    }


@router.get("/InvoiceDetail/{InvoiceDetailCondition}")
async def getInvoiceDetail(
    request: Request, InvoiceDetailCondition: str, db: Session = Depends(get_db)
):
    crud = CRUD(db, InvoiceDetailDBModel)
    table_name = "InvoiceDetail"
    if InvoiceDetailCondition == "all":
        InvoiceDetailDataList = crud.get_all()
    elif "start" in InvoiceDetailCondition or "end" in InvoiceDetailCondition:
        InvoiceDetailCondition = convert_url_condition_to_dict(InvoiceDetailCondition)
        sql_condition = convert_dict_to_sql_condition(
            InvoiceDetailCondition, table_name
        )
        InvoiceDetailDataList = crud.get_all_by_sql(sql_condition)
    else:
        InvoiceDetailConditionDict = convert_url_condition_to_dict(
            InvoiceDetailCondition
        )
        InvoiceDetailDataList = crud.get_with_condition(InvoiceDetailConditionDict)
    return InvoiceDetailDataList


@router.post("/deleteInvoiceDetail")
async def deleteInvoiceDetail(
    request: Request,
    db: Session = Depends(get_db),
):
    request_data = await request.json()
    crud = CRUD(db, InvoiceDetailDBModel)
    crud.remove_with_condition(request_data)
    return {"message": "InvoiceDetail successfully deleted"}


# ---------------------------------------------------------------------------
