from fastapi import APIRouter, Request, status, Depends, Body
from crud import *
from get_db import get_db
from sqlalchemy.orm import Session
from utils.utils import *
from utils.orm_pydantic_convert import orm_to_pydantic
from copy import deepcopy

router = APIRouter()


# ------------------------------ InvoiceMaster ------------------------------
# 查詢發票主檔
@router.get("/InvoiceMaster/{InvoiceMasterCondition}")
async def getInvoiceMaster(
    request: Request, InvoiceMasterCondition: str, db: Session = Depends(get_db)
):
    crud = CRUD(db, InvoiceMasterDBModel)
    table_name = "InvoiceMaster"
    if InvoiceMasterCondition == "all":
        InvoiceMasterDataList = crud.get_all()
    elif "start" in InvoiceMasterCondition or "end" in InvoiceMasterCondition:
        InvoiceMasterCondition = convert_url_condition_to_dict(InvoiceMasterCondition)
        sql_condition = convert_dict_to_sql_condition(
            InvoiceMasterCondition, table_name
        )

        # get all InvoiceMaster by sql
        InvoiceMasterDataList = crud.get_all_by_sql(sql_condition)
    else:
        InvoiceMasterCondition = convert_url_condition_to_dict(InvoiceMasterCondition)
        InvoiceMasterDataList = crud.get_with_condition(InvoiceMasterCondition)
    return InvoiceMasterDataList


@router.get("/InvoiceMasterWithInvoiceDetail/{InvoiceMasterCondition}")
async def getInvoiceMasterWithInvoiceDetail(
    request: Request, InvoiceMasterCondition: str, db: Session = Depends(get_db)
):
    """
    getResult element:
    {
        "InvoiceMaster": InvoiceMasterData,
        "InvoiceDetail": InvoiceDetailDataList
    }
    """
    getResult = []
    crud = CRUD(db, InvoiceDetailDBModel)
    InvoiceMasterDataList = await getInvoiceMaster(request, InvoiceMasterCondition, db)

    for InvoiceMasterData in InvoiceMasterDataList:
        InvoiceDetailDataList = crud.get_with_condition(
            {"InvMasterID": InvoiceMasterData.InvMasterID}
        )
        getResult.append(
            {
                "InvoiceMaster": InvoiceMasterData,
                "InvoiceDetail": InvoiceDetailDataList,
            }
        )
    return getResult


# 新增發票主檔
@router.post("/InvoiceMaster", status_code=status.HTTP_201_CREATED)
async def addInvoiceMaster(
    request: Request,
    InvoiceMasterPydanticData: InvoiceMasterSchema,
    db: Session = Depends(get_db),
):
    crud = CRUD(db, InvoiceMasterDBModel)
    crud.create(InvoiceMasterPydanticData)
    return {
        "message": "InvoiceMaster successfully created",
    }


@router.post("/deleteInvoiceMaster")
async def deleteInvoiceMaster(
    request: Request,
    db: Session = Depends(get_db),
):
    request_data = await request.json()
    crud = CRUD(db, InvoiceMasterDBModel)
    crud.remove_with_condition(request_data)
    return {"message": "InvoiceMaster successfully deleted"}


@router.post("/updateInvoiceMaster")
async def updateInvoiceMaster(
    request: Request,
    db: Session = Depends(get_db),
):
    update_dict_condition = await request.json()
    update_dict_condition_copy = deepcopy(update_dict_condition)
    if "Status" in update_dict_condition:
        update_dict_condition.pop("Status")
    crud = CRUD(db, InvoiceMasterDBModel)
    InvoiceMasterDataList = crud.get_with_condition(update_dict_condition)
    for InvoiceMasterData in InvoiceMasterDataList:
        crud.update(InvoiceMasterData, update_dict_condition_copy)
    return {"message": "InvoiceMaster status successfully updated"}


# ---------------------------------------------------------------------------
