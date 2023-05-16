from fastapi import APIRouter, Request, status, Depends
from crud import *
from get_db import get_db
from sqlalchemy.orm import Session
from utils.utils import *
from utils.orm_pydantic_convert import *
from copy import deepcopy

router = APIRouter()


@router.post("/User")
async def create_user(
    request: Request, User: UsersSchema, db: Session = Depends(get_db)
):
    crud = CRUD(db, UsersDBModel)
    new_user = crud.create(User)
    return new_user


# 刪
@router.post("/deleteUser")
async def get_user(request: Request, db: Session = Depends(get_db)):
    """
    Request body content
    {
        "UserID": int,
        "UserName": str,
        "UserPassword": str,
        "CreateDate": str,
        ...
    }
    """
    UserDictData = await request.json()
    crud = CRUD(db, UsersDBModel)
    crud.remove(UserDictData["UserID"])


# 改
@router.post("/updateUser")
async def update_user(request: Request, db: Session = Depends(get_db)):
    """
    Request body content
    {
        "UserID": int,
        "UserName": str,
        "UserPassword": str,
        "CreateDate": str,
        ...
    }
    """
    UserDictData = await request.json()
    crud = CRUD(db, UsersDBModel)
    UserDBData = crud.get_with_condition({"UserID": UserDictData["UserID"]})[0]
    new_user = crud.update(UserDBData, UserDictData)
    return new_user


# 查
@router.get("/User/{urlCondition}")
async def get_user(request: Request, urlCondition: str, db: Session = Depends(get_db)):
    if urlCondition == "all":
        crud = CRUD(db, UsersDBModel)
        UserDBDataList = crud.get_all()
    elif "start" in urlCondition or "end" in urlCondition:
        urlCondition = convert_url_condition_to_dict(urlCondition)
        sql_condition = convert_dict_to_sql_condition(urlCondition, "User")
        crud = CRUD(db, UsersDBModel)
        UserDBDataList = crud.get_all_by_sql(sql_condition)
    else:
        urlConditionDict = convert_url_condition_to_dict(urlCondition)
        crud = CRUD(db, UsersDBModel)
        UserDBDataList = crud.get_with_condition(urlConditionDict)
    return UserDBDataList
