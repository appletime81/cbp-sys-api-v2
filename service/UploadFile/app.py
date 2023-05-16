import os
import shutil
import time
from fastapi import APIRouter, Request, status, Depends, File, UploadFile
from crud import *
from get_db import get_db
from sqlalchemy.orm import Session
from utils.utils import *
from utils.orm_pydantic_convert import *
from utils.log import *
from copy import deepcopy

router = APIRouter()


# ------------------------------ Upload file ------------------------------


@router.post("/uploadfile")
async def uploadfile(
    request: Request, db: Session = Depends(get_db), file: UploadFile = File(...)
):
    with open(file.filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"file_name": file.filename}


@router.post("/uploadSignedBillMaster/{BillMasterID}")
async def uploadSignedBillMaster(
    request: Request,
    BillMasterID: str,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
):
    """
    {
        "BillMasterID": int
    }
    """
    BillMasterID = int(BillMasterID)
    crudBillMaster = CRUD(db, BillMasterDBModel)
    BillMasterData = crudBillMaster.get_with_condition({"BillMasterID": BillMasterID})[
        0
    ]

    with open(file.filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    try:
        os.system(
            f"aws s3 cp '{file.filename}' 's3://cht-deploy-bucket-1/{file.filename}'"
        )
    except Exception as e:
        print(e)

    # update BillMaster
    newBillMasterData = deepcopy(BillMasterData)
    newBillMasterData.URI = f"s3://cht-deploy-bucket-1/{file.filename}"
    newBillMasterData.Status = "SIGNED"

    newBillMasterData = crudBillMaster.update(
        BillMasterData, orm_to_dict(newBillMasterData)
    )

    record_log(f"{user_name} upload signed bill master, BillMasterID: {BillMasterID}")

    return {
        "message": "success",
        "file_name": file.filename,
        "URI": newBillMasterData.URI,
    }


# -------------------------------------------------------------------------
