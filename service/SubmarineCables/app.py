from fastapi import APIRouter, Request, status, Depends
from crud import *
from get_db import get_db
from sqlalchemy.orm import Session
from utils.utils import *
from utils.orm_pydantic_convert import *
from copy import deepcopy

router = APIRouter()


# ------------------------------ SubmarineCables ------------------------------
# 查詢SubmarineCables
@router.get("/SubmarineCables/{SubmarineCablesCondition}")
async def getSubmarineCables(
    request: Request,
    SubmarineCablesCondition: str,
    db: Session = Depends(get_db),
):
    crud = CRUD(db, SubmarineCablesDBModel)
    if SubmarineCablesCondition == "all":
        SubmarineCablesDataList = crud.get_all()
    else:
        SubmarineCablesDictCondition = convert_url_condition_to_dict_ignore_date(
            SubmarineCablesCondition
        )
        SubmarineCablesDataList = crud.get_with_condition(SubmarineCablesDictCondition)

    return SubmarineCablesDataList


# C
@router.post("/SubmarineCables", status_code=status.HTTP_201_CREATED)
async def addSubmarineCables(
    request: Request,
    SubmarineCablesPydanticData: SubmarineCablesSchema,
    db: Session = Depends(get_db),
):
    pprint(await request.json())
    crud = CRUD(db, SubmarineCablesDBModel)
    SubmarineCablesData = crud.create(SubmarineCablesPydanticData)

    return {
        "message": "SubmarineCable successfully created",
        "SubmarineCablesData": SubmarineCablesData,
    }


# U
@router.post("/updateSubmarineCables")
async def updateSubmarineCables(
    request: Request,
    db: Session = Depends(get_db),
):
    pprint((await request.json()))
    SubmarineCablesDictData = await request.json()
    crud = CRUD(db, SubmarineCablesDBModel)
    SubmarineCablesData = crud.get_with_condition(
        {"CableID": SubmarineCablesDictData.get("CableID")}
    )[0]
    newSubmarineCablesData = crud.update(SubmarineCablesData, SubmarineCablesDictData)
    return {
        "message": "SubmarineCable successfully updated",
        "newSubmarineCablesData": newSubmarineCablesData,
    }


# D
@router.post("/deleteSubmarineCables")
async def deleteSubmarineCables(
    request: Request,
    db: Session = Depends(get_db),
):
    SubmarineCablesDictData = await request.json()
    crud = CRUD(db, SubmarineCablesDBModel)
    crud.remove(SubmarineCablesDictData["CableID"])
    return {"message": "SubmarineCable successfully deleted"}


# -----------------------------------------------------------------------------
