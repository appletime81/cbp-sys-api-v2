from fastapi import APIRouter, Request, Depends

from crud import *
from get_db import get_db
from sqlalchemy.orm import Session
from utils.utils import *
from utils.log import *
from utils.orm_pydantic_convert import *

import os
from copy import deepcopy


router = APIRouter()


@router.post("/payment/getPaymentDraft")
async def getPaymentDraft(request: Request, db: Session = Depends(get_db)):
    return {"message": "success"}
