from fastapi import APIRouter, Request, status, Depends
from crud import *
from get_db import get_db
from sqlalchemy.orm import Session
from utils.utils import *
from utils.orm_pydantic_convert import *
from copy import deepcopy

router = APIRouter()


# ------------------------------ Contracts ------------------------------
# 查詢Contracts R
@router.get("/Contracts/{urlCondition}")
async def getContracts(
    request: Request,
    urlCondition: str,
    db: Session = Depends(get_db),
):
    table_name = "Contracts"
    crud = CRUD(db, ContractsDBModel)
    if urlCondition == "all":
        ContractsDataList = crud.get_all()
    elif "start" in urlCondition or "end" in urlCondition:
        dictCondition = convert_url_condition_to_dict(urlCondition)
        sql_condition = convert_dict_to_sql_condition(dictCondition, table_name)

        # get all Contracts by sql
        ContractsDataList = crud.get_all_by_sql(sql_condition)
    else:
        dictCondition = convert_url_condition_to_dict(urlCondition)
        ContractsDataList = crud.get_with_condition(dictCondition)
    return ContractsDataList


# C
@router.post("/Contracts", status_code=status.HTTP_201_CREATED)
async def addContracts(
    request: Request,
    ContractsPydanticData: ContractsSchema,
    db: Session = Depends(get_db),
):
    crud = CRUD(db, ContractsDBModel)
    ContractsData = crud.create(ContractsPydanticData)
    return {"message": "Contracts successfully created", "ContractsData": ContractsData}


# U
@router.post("/updateContracts")
async def updateContracts(
    request: Request,
    db: Session = Depends(get_db),
):
    ContractsDictData = await request.json()
    crud = CRUD(db, ContractsDBModel)
    ContractsData = crud.get_with_condition(
        {"ContractID": ContractsDictData["ContractID"]}
    )[0]
    updateContractData = crud.update(ContractsData, ContractsDictData)
    return {
        "message": "Contracts successfully updated",
        "updateContractData": updateContractData,
    }


# D
@router.post("/deleteContracts")
async def deleteContracts(
    request: Request,
    db: Session = Depends(get_db),
):
    ContractsDictData = await request.json()
    crud = CRUD(db, ContractsDBModel)
    crud.remove(ContractsDictData["ContractID"])
    return {"message": "Contracts successfully deleted"}
