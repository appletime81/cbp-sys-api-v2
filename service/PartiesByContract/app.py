from fastapi import APIRouter, Request, status, Depends
from crud import *
from get_db import get_db
from sqlalchemy.orm import Session
from utils.utils import *
from utils.orm_pydantic_convert import *
from copy import deepcopy

router = APIRouter()


# ------------------------------ PartiesByContract ------------------------------
# 查詢PartiesByContract
@router.get("/PartiesByContract/{urlCondition}")
async def getPartiesByContract(
    request: Request,
    urlCondition: str,
    db: Session = Depends(get_db),
):
    crud = CRUD(db, PartiesByContractDBModel)
    if urlCondition == "all":
        PartiesByContractDataList = crud.get_all()
    else:
        PartiesByContractDictCondition = convert_url_condition_to_dict_ignore_date(
            urlCondition
        )
        PartiesByContractDataList = crud.get_with_condition(
            PartiesByContractDictCondition
        )

    return PartiesByContractDataList


# C
@router.post("/PartiesByContract", status_code=status.HTTP_201_CREATED)
async def addPartiesByContract(
    request: Request,
    PartiesByContractPydanticData: PartiesByContractSchema,
    db: Session = Depends(get_db),
):
    crud = CRUD(db, PartiesByContractDBModel)
    PartiesByContractData = crud.create(PartiesByContractPydanticData)
    return {
        "message": "PartiesByContract successfully created",
        "PartiesByContractData": PartiesByContractData,
    }


# U
@router.post("/updatePartiesByContract")
async def updatePartiesByContract(
    request: Request,
    db: Session = Depends(get_db),
):
    PartiesByContractDictData = await request.json()
    crud = CRUD(db, PartiesByContractDBModel)
    PartiesByContractData = crud.get_with_condition(
        {"ContractID": PartiesByContractDictData.get("ContractID")}
    )[0]
    newPartiesByContractData = crud.update(
        PartiesByContractData, PartiesByContractDictData
    )
    return {
        "message": "PartiesByContract successfully updated",
        "newPartiesByContractData": newPartiesByContractData,
    }


# D
@router.post("/deletePartiesByContract/{ContractID}")
async def deletePartiesByContract(
    request: Request,
    db: Session = Depends(get_db),
):
    PartiesByContractDictData = await request.json()
    crud = CRUD(db, PartiesByContractDBModel)
    crud.remove(PartiesByContractDictData.get("ContractID"))
    return {"message": "PartiesByContract successfully deleted"}
