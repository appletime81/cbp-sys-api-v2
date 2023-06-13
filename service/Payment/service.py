from fastapi import APIRouter, Request, Depends

from fastapi.responses import FileResponse

from crud import *
from get_db import get_db
from sqlalchemy.orm import Session
from utils.utils import *
from utils.log import *
from utils.orm_pydantic_convert import *

from docxtpl import DocxTemplate

import os
from copy import deepcopy


router = APIRouter()


@router.post("/getPayDraftStream")
async def getPayDraftStream(request: Request, db: Session = Depends(get_db)):
    """
    input data:
    {
        "PayDraftID": int,
        "CableInfo": str(使用者輸入),
        "Subject": str(主旨),
        "DownloadTemplate": true / false
        "CacheData": true / false
    }
    """
    requestDictData = await request.json()
    crudPayMaster = CRUD(db , PayMasterDBModel)
    crudPayDraft = CRUD(db , PayDraftDBModel)
    if requestDictData.get("CacheData"):
        pass

