from fastapi import APIRouter, Request, status, Depends, Body
from crud import *
from get_db import get_db
from sqlalchemy.orm import Session
from utils.utils import *
from utils.orm_pydantic_convert import *
from utils.log import *
from copy import deepcopy

router = APIRouter()


# ------------------------------ Liability ------------------------------
# 查詢Liability
@router.get("/Liability/{LiabilityCondition}")
async def getLiability(
    request: Request,
    LiabilityCondition: str,
    db: Session = Depends(get_db),
):
    crud = CRUD(db, LiabilityDBModel)
    table_name = "Liability"
    origLiabilityCondition = deepcopy(LiabilityCondition)

    EndBool = "Init"
    if "End" in LiabilityCondition:
        LiabilityCondition, EndBool = re_search_url_condition_value(
            LiabilityCondition, "End"
        )
        if not LiabilityCondition:
            LiabilityCondition = "all"

    if LiabilityCondition == "all":
        LiabilityDataList = crud.get_all()
    elif "start" in LiabilityCondition or "end" in LiabilityCondition:
        LiabilityCondition = convert_url_condition_to_dict(LiabilityCondition)
        sql_condition = convert_dict_to_sql_condition(LiabilityCondition, table_name)
        LiabilityDataList = crud.get_all_by_sql(sql_condition)
        LiabilityDictDataList = [
            orm_to_dict(LiabilityData) for LiabilityData in LiabilityDataList
        ]
        for i, LiabilityDictData in enumerate(LiabilityDictDataList):
            if LiabilityDictData["EndDate"] == "NaT":
                LiabilityDictDataList[i]["EndDate"] = None
        pprint(LiabilityDictDataList)
    else:
        LiabilityCondition = convert_url_condition_to_dict(LiabilityCondition)
        LiabilityDataList = crud.get_with_condition(LiabilityCondition)

    if EndBool != "Init" and "start" in origLiabilityCondition:
        # 篩選沒終止的資料
        if EndBool:
            LiabilityDictDataList = [
                LiabilityDictData
                for LiabilityDictData in LiabilityDictDataList
                if LiabilityDictData["EndDate"]
            ]
        # 篩選有終止的資料
        if not EndBool:
            LiabilityDictDataList = [
                LiabilityDictData
                for LiabilityDictData in LiabilityDictDataList
                if not LiabilityDictData["EndDate"]
            ]
        return LiabilityDictDataList
    elif EndBool == "Init" and "start" in origLiabilityCondition:
        return LiabilityDictDataList

    if EndBool != "Init":
        # 篩選沒終止的資料
        if EndBool:
            LiabilityDataList = [
                LiabilityData
                for LiabilityData in LiabilityDataList
                if LiabilityData.EndDate
            ]

        # 篩選有終止的資料
        if not EndBool:
            LiabilityDataList = [
                LiabilityData
                for LiabilityData in LiabilityDataList
                if not LiabilityData.EndDate
            ]

    return LiabilityDataList


@router.post("/addLiability", status_code=status.HTTP_201_CREATED)
async def addLiability(
    request: Request,
    LiabilityPydanticData: LiabilitySchema,
    db: Session = Depends(get_db),
):
    crud = CRUD(db, LiabilityDBModel)

    # give CreateDate
    LiabilityPydanticData.CreateDate = convert_time_to_str(datetime.now())

    # add into database
    crud.create(LiabilityPydanticData)
    return {"message": "Liability successfully created"}


@router.post("/updateLiability")
async def updateLiability(
    request: Request,
    db: Session = Depends(get_db),
):
    LiabilityDictData = await request.json()
    LBRawID = LiabilityDictData.get("LBRawID")
    Note = LiabilityDictData.get("Note")
    ModifyNote = LiabilityDictData.get("ModifyNote")
    crud = CRUD(db, LiabilityDBModel)
    LiabilityData = crud.get_with_condition({"LBRawID": LBRawID})[0]

    # update LiabilityData
    LiabilityDictData = orm_to_dict(deepcopy(LiabilityData))
    LiabilityDictData["Note"] = Note
    LiabilityDictData["ModifyNote"] = ModifyNote
    crud.update(LiabilityData, LiabilityDictData)

    return {"message": "Liability successfully updated"}


@router.post("/deleteLiability")
async def deleteLiability(
    request: Request,
    db: Session = Depends(get_db),
):
    LiabilityDictData = await request.json()
    LBRawID = LiabilityDictData.get("LBRawID")
    ModifyNote = LiabilityDictData.get("ModifyNote")
    EndDate = convert_time_to_str(datetime.now())
    crud = CRUD(db, LiabilityDBModel)
    LiabilityData = crud.get_with_condition({"LBRawID": LBRawID})[0]
    LiabilityDataList = crud.get_with_condition(
        {
            "BillMilestone": LiabilityData.BillMilestone,
            "WorkTitle": LiabilityData.WorkTitle,
            "SubmarineCable": LiabilityData.SubmarineCable,
        }
    )

    # terminate LiabilityData
    for LiabilityData in LiabilityDataList:
        LiabilityDictData = orm_to_dict(deepcopy(LiabilityData))
        LiabilityDictData["EndDate"] = EndDate
        LiabilityDictData["ModifyNote"] = ModifyNote
        crud.update(LiabilityData, LiabilityDictData)
        record_log(
            f"{user_name} terminate LiabilityData, LBRawID: {LiabilityData.LBRawID}"
        )

    return {"message": "Liability successfully terminated"}


# for dropdown list
# 會員名稱
# @router.get("/dropdownmenuParties")
# async def getDropdownMenuParties(
#     request: Request,
#     db: Session = Depends(get_db),
# ):
#     crud = CRUD(db, LiabilityDBModel)
#     LiabilityDataList = crud.get_all()
#     PartyNameList = []
#     for LiabilityData in LiabilityDataList:
#         PartyNameList.append(LiabilityData.PartyName)
#     PartyNameList = list(set(PartyNameList))
#     return PartyNameList


# 記帳段號(BillMilestone)
@router.get("/dropdownmenuBillMilestone")
async def getDropdownMenuBillMilestone(
    request: Request,
    db: Session = Depends(get_db),
):
    crud = CRUD(db, LiabilityDBModel)
    LiabilityDataList = crud.get_all()
    BillMilestoneList = [
        # if LiabilityData.EndDate have value, then put it into list
        LiabilityData.BillMilestone
        for LiabilityData in LiabilityDataList
        if not LiabilityData.EndDate
    ]
    BillMilestoneList = list(set(BillMilestoneList))
    return BillMilestoneList


# 海纜名稱(SubmarineCable)
@router.get("/dropdownmenuSubmarineCable")
async def getDropdownMenuSubmarineCable(
    request: Request,
    db: Session = Depends(get_db),
):
    crud = CRUD(db, LiabilityDBModel)
    LiabilityDataList = crud.get_all()
    SubmarineCableList = []
    for LiabilityData in LiabilityDataList:
        SubmarineCableList.append(LiabilityData.SubmarineCable)
    SubmarineCableList = list(set(SubmarineCableList))
    return SubmarineCableList


# 海纜作業(WorkTitle)
@router.get("/dropdownmenuWorkTitle")
async def getDropdownMenuWorkTitle(
    request: Request,
    db: Session = Depends(get_db),
):
    crud = CRUD(db, LiabilityDBModel)
    LiabilityDataList = crud.get_all()
    WorkTitleList = []
    for LiabilityData in LiabilityDataList:
        WorkTitleList.append(LiabilityData.WorkTitle)
    WorkTitleList = list(set(WorkTitleList))
    return WorkTitleList


# -----------------------------------------------------------------------
