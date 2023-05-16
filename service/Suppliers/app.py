from fastapi import APIRouter, Request, status, Depends, Body
from crud import *
from get_db import get_db
from sqlalchemy.orm import Session
from utils.utils import *
from utils.orm_pydantic_convert import orm_to_pydantic
from copy import deepcopy

router = APIRouter()


# ------------------------------ Suppliers ------------------------------
# 查詢Suppliers
@router.get("/Suppliers/{urlCondition}")
async def getSuppliers(
    request: Request,
    urlCondition: str,
    db: Session = Depends(get_db),
):
    crud = CRUD(db, SuppliersDBModel)
    if urlCondition == "all":
        SuppliersDataList = crud.get_all()
    else:
        dictCondition = convert_url_condition_to_dict(urlCondition)
        SuppliersDataList = crud.get_with_condition(dictCondition)
    return SuppliersDataList


@router.post("/Suppliers", status_code=status.HTTP_201_CREATED)
async def addSuppliers(
    request: Request,
    SuppliersPydanticData: SuppliersSchema,
    db: Session = Depends(get_db),
):
    crud = CRUD(db, SuppliersDBModel)
    SupplierData = crud.create(SuppliersPydanticData)
    return {"message": "Supplier successfully created", "SupplierData": SupplierData}


@router.post("/deleteSuppliers")
async def deleteSuppliers(
    request: Request,
    db: Session = Depends(get_db),
):
    request_data = await request.json()
    SupplierID = request_data.get("SupplierID")
    crud = CRUD(db, SuppliersDBModel)
    crud.remove(SupplierID)
    return {"message": "Supplier successfully deleted"}


@router.post("/updateSuppliers")
async def updateSuppliers(
    request: Request,
    db: Session = Depends(get_db),
):
    SuppliersDictData = await request.json()
    crud = CRUD(db, SuppliersDBModel)
    SupplierData = crud.get_with_condition(
        {"SupplierID": SuppliersDictData.get("SupplierID")}
    )[0]
    updateSupplierData = crud.update(SupplierData, SuppliersDictData)
    return {
        "message": "Supplier successfully updated",
        "updateSupplierData": updateSupplierData,
    }


# -----------------------------------------------------------------------
