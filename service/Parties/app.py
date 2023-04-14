from fastapi import APIRouter, Request, status, Depends, Body
from crud import *
from get_db import get_db
from sqlalchemy.orm import Session
from utils.utils import *
from utils.orm_pydantic_convert import orm_to_pydantic
from copy import deepcopy
from sqlalchemy.sql import func

router = APIRouter()


# ------------------------------ Parties ------------------------------
# 查詢Parties
@router.get("/Parties/{urlCondition}")
async def getParties(
    request: Request,
    urlCondition: str,
    db: Session = Depends(get_db),
):
    crud = CRUD(db, PartiesDBModel)
    if urlCondition == "all":
        PartiesDataList = crud.get_all()
    else:
        dictCondition = convert_url_condition_to_dict_ignore_date(urlCondition)
        PartiesDataList = crud.get_with_condition(dictCondition)
    newPartiesDataList = []

    # get unique PartyName
    for i, PartiesData in enumerate(PartiesDataList):
        if i == 0:
            newPartiesDataList.append(PartiesData)
        else:
            filter_result = list(
                filter(
                    lambda x: x.PartyName == PartiesData.PartyName, newPartiesDataList
                )
            )
            if not filter_result:
                newPartiesDataList.append(PartiesData)

    return newPartiesDataList


@router.post("/Parties", status_code=status.HTTP_201_CREATED)
async def addParties(
    request: Request,
    PartiesPydanticData: PartiesSchema,
    db: Session = Depends(get_db),
):
    crud = CRUD(db, PartiesDBModel)
    PartiesData = crud.create(PartiesPydanticData)
    return {"message": "Party successfully created", "PartiesData": PartiesData}


@router.post("/deleteParties")
async def deletePartiesList(
    request: Request,
    db: Session = Depends(get_db),
):
    PartiesDictData = await request.json()
    crud = CRUD(db, PartiesDBModel)
    crud.remove_with_condition(PartiesDictData)
    return {"message": "Party successfully deleted"}


@router.post("/updateParties")
async def updateParties(
    request: Request,
    db: Session = Depends(get_db),
):
    PartiesDictData = await request.json()
    crud = CRUD(db, PartiesDBModel)
    PartiesData = crud.get_with_condition({"PartyID": PartiesDictData["PartyID"]})[0]
    newPartiesData = crud.update(PartiesData, PartiesDictData)

    return {"message": "Party successfully updated", "newPartiesData": newPartiesData}


# ---------------------------------------------------------------------
