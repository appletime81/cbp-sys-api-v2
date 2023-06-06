import os

from docxtpl import DocxTemplate
from fastapi import APIRouter, Request, status, Depends, Body
from fastapi.responses import FileResponse
from crud import *
from get_db import get_db
from sqlalchemy.orm import Session
from utils.utils import *
from utils.orm_pydantic_convert import orm_to_pydantic
from copy import deepcopy


router = APIRouter()


# ------------------------------ Letter ------------------------------
@router.get("/Letter")
async def getLetter(
    request: Request,
    db: Session = Depends(get_db),
):
    doc = DocxTemplate("templates/template.docx")
    context = {
        "file_num": "TPE112013001",
        "conteact_person ": "張增懿",
        "contact_num": "02-23445280",
        "email": "chang_ty@cht.com.tw",
        "recipient": "兆豐國際商業銀行國外部匯兌科",
        "year": "112",
        "month": "01",
        "day": "30",
        "text_number": "TPE112013001",
        "topic_bank_name": "CIENA JP",
        "payment_name": "TPE海纜款項",
        "chinese_payment": "美金四八、五七六．○○",
        "arabic_payment": "48,576.00",
        "account_no_1": "007-53-110022",
        "account_name": "Ciena Communications Japan Co. Ltd.",
        "bank": "JPMorgan Chase Bank Luxembourg S.A.",
        "bank_address": "6 route de Treves, Senningerberg, 2633, Luxembourg",
        "account_no_2": "6550207141",
        "iban": "LU290670006550207141",
        "swift": "CHASLULX",
        "invoice_num": "Invoice No.15328/15428",
        "work_title": "TPE UPG#11(BM1/BM2)",
        "foreign_currency_demand_deposit_no": "007-53-110022",
    }
    file_name = "output.docx"
    # DEPENDS ON WHERE YOUR FILE LOCATES
    file_path = f"{os.getcwd()}/output.docx"
    doc.render(context)
    doc.save(file_path)
    return FileResponse(path=file_path, filename="output.docx")
