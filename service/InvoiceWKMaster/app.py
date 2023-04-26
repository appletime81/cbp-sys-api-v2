from fastapi import APIRouter, Request, status, Depends
from crud import *
from get_db import get_db
from sqlalchemy.orm import Session
from utils.utils import *
from utils.log import *
from utils.orm_pydantic_convert import orm_to_pydantic
from copy import deepcopy

router = APIRouter()


# 查詢發票工作主檔
@router.get(f"/InvoiceWKMaster/" + "{InvoiceWKMasterCondition}")
async def getInvoiceWKMaster(
    request: Request, InvoiceWKMasterCondition: str, db: Session = Depends(get_db)
):
    crud = CRUD(db, InvoiceWKMasterDBModel)
    table_name = "InvoiceWKMaster"
    if InvoiceWKMasterCondition == "all":
        InvoiceWKMasterDataList = crud.get_all()
    elif "start" in InvoiceWKMasterCondition or "end" in InvoiceWKMasterCondition:
        InvoiceWKMasterCondition = convert_url_condition_to_dict(
            InvoiceWKMasterCondition
        )
        sql_condition = convert_dict_to_sql_condition(
            InvoiceWKMasterCondition, table_name
        )

        # get all InvoiceWKMaster by sql
        InvoiceWKMasterDataList = crud.get_all_by_sql(sql_condition)
    else:
        InvoiceWKMasterCondition = convert_url_condition_to_dict(
            InvoiceWKMasterCondition
        )
        InvoiceWKMasterDataList = crud.get_with_condition(InvoiceWKMasterCondition)
    return InvoiceWKMasterDataList


# 新增發票工作主檔
@router.post(f"/InvoiceWKMaster", status_code=status.HTTP_201_CREATED)
async def addInvoiceWKMaster(
    request: Request,
    InvoiceWKMasterPydanticData: InvoiceWKMasterSchema,
    db: Session = Depends(get_db),
):
    crud = CRUD(db, InvoiceWKMasterDBModel)
    crud.create(InvoiceWKMasterPydanticData)
    return {
        "message": "InvoiceWKMaster successfully created",
    }


@router.post(f"/deleteInvoiceWKMaster")
async def deleteInvoiceWKMaster(
    request: Request,
    db: Session = Depends(get_db),
):
    print(
        "-------------------------------------------------------- deleteInvoiceWKMaster --------------------------------------------------------"
    )
    request_data = await request.json()
    print("WKMasterID: ", request_data.get("WKMasterID"))
    crud = CRUD(db, InvoiceWKMasterDBModel)
    crud.remove({"WKMasterID": request_data.get("WKMasterID")})
    record_log(f"{user_name} delete InvoiceWKMaster: {request_data.get('WKMasterID')}")
    return {"message": "InvoiceWKMaster successfully deleted"}


@router.post(f"/updateInvoiceWKMaster")
async def updateInvoiceWKMasterStatusAndInvoiceMasterStatus(
    request: Request,
    db: Session = Depends(get_db),
):
    update_dict_condition = await request.json()
    crud = CRUD(db, InvoiceWKMasterDBModel)
    InvoiceWKMasterDataList = crud.get_with_condition(
        {"WKMasterID": update_dict_condition["WKMasterID"]}
    )
    for InvoiceWKMasterData in InvoiceWKMasterDataList:
        crud.update(InvoiceWKMasterData, update_dict_condition)

    record_log(f"{user_name} update InvoiceWKMaster: {update_dict_condition}")

    return {"message": "InvoiceWKMaster status successfully updated"}
