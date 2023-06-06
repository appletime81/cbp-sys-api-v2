from fastapi import APIRouter, Request, status, Depends, Body
from crud import *
from get_db import get_db
from sqlalchemy.orm import Session
from utils.utils import *
from utils.orm_pydantic_convert import *
from copy import deepcopy

router = APIRouter()


# ------------------------------ Corporates ------------------------------
@router.get("/Corporates/{urlCondition}")
async def getCorporates(
    request: Request,
    urlCondition: str,
    db: Session = Depends(get_db),
):
    table_name = "Corporates"
    crud = CRUD(db, CorporatesDBModel)
    if urlCondition == "all":
        CorporatesDataList = crud.get_all()
    elif "start" in urlCondition or "end" in urlCondition:
        dictCondition = convert_url_condition_to_dict(urlCondition)
        sql_condition = convert_dict_to_sql_condition(dictCondition, table_name)

        # get data by SQL
        CorporatesDataList = crud.get_all_by_sql(sql_condition)
    else:
        dictCondition = convert_url_condition_to_dict_ignore_date(urlCondition)
        CorporatesDataList = crud.get_with_condition(dictCondition)
    return CorporatesDataList


@router.post("/Corporates", status_code=status.HTTP_201_CREATED)
async def addCorporates(
    request: Request,
    db: Session = Depends(get_db),
):
    CorporatesDictData = await request.json()
    CorporatesDictData["CreateDate"] = convert_time_to_str(datetime.now())
    crud = CRUD(db, CorporatesDBModel)
    CorporatesPydanticData = CorporatesSchema(**CorporatesDictData)
    CorporatesData = crud.create(CorporatesPydanticData)
    return {
        "message": "Corporate successfully created",
        "CorporatesData": CorporatesData,
    }


@router.post("/updateCorporates")
async def updateCorporates(
    request: Request,
    db: Session = Depends(get_db),
):
    CorporatesDictData = await request.json()
    crud = CRUD(db, CorporatesDBModel)
    CorporatesData = crud.get_with_condition({"CorpID": CorporatesDictData["CorpID"]})[
        0
    ]
    updateCorporatesData = crud.update(CorporatesData, CorporatesDictData)
    return {
        "message": "Corporate successfully updated",
        "updateCorporatesData": updateCorporatesData,
    }


@router.post("/deleteCorporates")
async def deleteCorporates(
    request: Request,
    db: Session = Depends(get_db),
):
    CorporatesDictData = await request.json()
    pprint(CorporatesDictData)
    crud = CRUD(db, CorporatesDBModel)
    CorporatesData = crud.get_with_condition({"CorpID": CorporatesDictData["CorpID"]})[
        0
    ]
    crud.remove_with_condition(orm_to_dict(CorporatesData))
    return {"message": "Corporate successfully deleted"}
