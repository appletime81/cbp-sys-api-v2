from fastapi import APIRouter, Request, Depends
from fastapi.responses import FileResponse

from crud import *
from get_db import get_db
from sqlalchemy.orm import Session
from utils.utils import *
from utils.orm_pydantic_convert import *

import os
from copy import deepcopy
from docxtpl import DocxTemplate, InlineImage


router = APIRouter()

# ---------------------------- 付款函稿管理頁面 --------------------------
@router.get("/payment/{urlCondition}")
async def showPaymentData(request: Request, db: Session = Depends(get_db)):
    
    crudPaymentDraft = CRUD(db, )


    return None



# -----------------------------------------------------------------------




# ------------------------------- 付款功能 -------------------------------
@router.get("/payment/{urlCondition}")
async def getPaymentData(
    request: Request,
    db: Session = Depends(get_db),
):
    # the datas will be shown on the frontend page
    pass
# -----------------------------------------------------------------------




