from fastapi import APIRouter, Request, status, Depends
from crud import *
from get_db import get_db
from sqlalchemy.orm import Session
from utils.utils import *
from utils.orm_pydantic_convert import *
from copy import deepcopy

router = APIRouter()


# ------------------------------ SuppliersByContract ------------------------------
# 查詢SuppliersByContract R
@router.get("/SuppliersByContract/{urlCondition}")
async def getSuppliersByContract(
    request: Request,
    urlCondition: str,
    db: Session = Depends(get_db),
):
    table_name = "SuppliersByContract"
    crud = CRUD(db, SuppliersByContractDBModel)
    if urlCondition == "all":
        SuppliersByContractDataList = crud.get_all()
    else:
        dictCondition = convert_url_condition_to_dict(urlCondition)
        SuppliersByContractDataList = crud.get_with_condition(dictCondition)
    return SuppliersByContractDataList


# C
@router.post("/SuppliersByContract", status_code=status.HTTP_201_CREATED)
async def addSuppliersByContract(
    request: Request,
    SuppliersByContractPydanticData: SuppliersByContractSchema,
    db: Session = Depends(get_db),
):
    crud = CRUD(db, SuppliersByContractDBModel)
    SuppliersByContractData = crud.create(SuppliersByContractPydanticData)
    return {
        "message": "SuppliersByContract successfully created",
        "SuppliersByContractData": SuppliersByContractData,
    }


# U
@router.post("/updateSuppliersByContract")
async def updateSuppliersByContract(
    request: Request,
    db: Session = Depends(get_db),
):
    SuppliersByContractDictData = await request.json()
    crud = CRUD(db, SuppliersByContractDBModel)
    SuppliersByContractData = crud.get_with_condition(
        {"ContractID": SuppliersByContractDictData["ContractID"]}
    )[0]
    newSuppliersByContractData = crud.update(
        SuppliersByContractData, SuppliersByContractDictData
    )
    return {
        "message": "SuppliersByContract successfully updated",
        "newSuppliersByContractData": newSuppliersByContractData,
    }


# D
@router.post("/SuppliersByContract/{ContractID}")
async def deleteSuppliersByContract(
    request: Request,
    db: Session = Depends(get_db),
):
    SuppliersByContractDictData = await request.json()
    crud = CRUD(db, SuppliersByContractDBModel)
    crud.remove(SuppliersByContractDictData["ContractID"])
    return {"message": "SuppliersByContract successfully deleted"}
