from fastapi import APIRouter, Request, status, Depends, Body
from crud import *
from get_db import get_db
from sqlalchemy.orm import Session
from utils.utils import *
from utils.orm_pydantic_convert import *
from copy import deepcopy

router = APIRouter()


# ------------------------------ BillMilestone ------------------------------
# 查詢BillMilestone
@router.get("/BillMilestone/{BillMilestoneCondition}")
async def getBillMilestone(
    request: Request,
    BillMilestoneCondition: str,
    db: Session = Depends(get_db),
):
    """
    BillMilestoneCondition: str
    Example: "SubmarineCable={SubmarineCableName}&WorkTitle={WorkTitleName}"
    """

    BillMilestoneDictCondition = convert_url_condition_to_dict_ignore_date(
        BillMilestoneCondition
    )

    crudLiability = CRUD(db, LiabilityDBModel)
    LiabilityDataList = crudLiability.get_with_condition(BillMilestoneDictCondition)
    LiabilityDictDataList = [
        orm_to_dict(LiabilityData) for LiabilityData in LiabilityDataList
    ]
    BillMilestoneDictDataList = list(
        set(
            [
                LiabilityDictData["BillMilestone"]
                for LiabilityDictData in LiabilityDictDataList
            ]
        )
    )

    return BillMilestoneDictDataList


# ---------------------------------------------------------------------------
