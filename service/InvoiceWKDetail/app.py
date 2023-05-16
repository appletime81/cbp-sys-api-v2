from fastapi import APIRouter, Request, status, Depends, Body
from crud import *
from get_db import get_db
from sqlalchemy.orm import Session
from utils.utils import *
from utils.orm_pydantic_convert import orm_to_pydantic
from copy import deepcopy

router = APIRouter()


# ------------------------------ InvoiceWKDetail ------------------------------
# 查詢發票工作明細檔
@router.get("/InvoiceWKDetail/{InvoiceWKDetailCondition}")
async def getInvoiceWKDetail(
    request: Request, InvoiceWKDetailCondition: str, db: Session = Depends(get_db)
):
    crud = CRUD(db, InvoiceWKDetailDBModel)
    if InvoiceWKDetailCondition == "all":
        InvoiceWKDetailDataList = crud.get_all()
    else:
        InvoiceWKDetailCondition = convert_url_condition_to_dict(
            InvoiceWKDetailCondition
        )
        InvoiceWKDetailDataList = crud.get_with_condition(InvoiceWKDetailCondition)
    return InvoiceWKDetailDataList


# 新增發票工作明細檔
@router.post("/InvoiceWKDetail", status_code=status.HTTP_201_CREATED)
async def addInvoiceWKDetail(
    request: Request,
    InvoiceWKDetailPydanticData: InvoiceWKDetailSchema,
    db: Session = Depends(get_db),
):
    crud = CRUD(db, InvoiceWKDetailDBModel)
    crud.create(InvoiceWKDetailPydanticData)
    return {
        "message": "InvoiceWKDetail successfully created",
    }


@router.post("/deleteInvoiceWKDetail")
async def deleteInvoiceWKDetail(
    request: Request,
    db: Session = Depends(get_db),
):
    request_data = await request.json()
    print("--------------------- WKMasterID ---------------------")
    print(request_data.get("WKMasterID"))
    crud = CRUD(db, InvoiceWKDetailDBModel)
    crud.remove_with_condition({"WKMasterID": request_data.get("WKMasterID")})
    return {"message": "InvoiceWKDetail successfully deleted"}


# -----------------------------------------------------------------------------
