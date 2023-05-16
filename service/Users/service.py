from fastapi import APIRouter, Request, Depends

from crud import *
from get_db import get_db
from sqlalchemy.orm import Session
from utils.utils import *
from utils.orm_pydantic_convert import *
from copy import deepcopy
import configparser

router = APIRouter()


@router.post("/login")
async def login(
    request: Request, LogonPydanticData: LoginSchema, db: Session = Depends(get_db)
):
    """
    {"username": xxx}
    """
    crud = CRUD(db, UsersDBModel)
    error_message = {"status": False, "message": "error username or password"}

    config = configparser.ConfigParser()
    config.read("userinfo.ini")

    userInfo = await request.json()
    username = userInfo.get("username")
    inputPassword = userInfo.get("password")

    correctPassword = config[f"{username}"]["password"]

    userData = crud.get_with_condition({"UserID": username})
    if userData and inputPassword == correctPassword:
        return {"status": True, "user": userData[0].UserID}
    return error_message
