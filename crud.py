import pandas as pd

from pprint import pprint
from copy import deepcopy
from sqlalchemy.orm import Session
from sqlalchemy.orm.sync import update
from sqlalchemy.sql import func, text
from database.engine import engine
from database.models import *
from schemas import *

user_name = "Eva Change"


class CRUD:
    def __init__(self, db: Session, model):
        self.db = db
        self.model = model

    def get_with_condition(self, filter_condition: dict):
        return self.db.query(self.model).filter_by(**filter_condition).all()

    def get_with_condition_and_like(
        self, filter_condition: dict, col_name=None, like_condition_value=None
    ):
        if col_name and like_condition_value:
            return (
                self.db.query(self.model)
                .filter_by(**filter_condition)
                .filter(col_name.like(f"%{like_condition_value}%"))
                .all()
            )
        else:
            return self.db.query(self.model).filter_by(**filter_condition).all()

    def get_value_if_in_a_list(self, value, list_of_values):
        return self.db.query(self.model).filter(value.in_(list_of_values)).all()

    def get_all(self):
        return self.db.query(self.model).all()

    def get_all_distinct(self, distinct_field):
        return self.db.query(distinct_field).distinct().all()

    def get_all_by_sql(self, sql: str):
        print(sql)
        with engine.begin() as conn:
            df = pd.read_sql_query(sql=text(f"""{sql}"""), con=conn)
        getResult = [
            self.model(**row_dict) for row_dict in df.to_dict(orient="records")
        ]
        return getResult

    def get_all_by_sql_with_like(
        self, sql: str, col_name=None, like_condition_value=None
    ):
        print(sql)
        with engine.begin() as conn:
            df = pd.read_sql_query(sql=text(f"""{sql}"""), con=conn)
        if col_name and like_condition_value:
            df = df[df[col_name].str.contains(like_condition_value, na=False)]
        getResult = [
            self.model(**row_dict) for row_dict in df.to_dict(orient="records")
        ]
        return getResult

    def get_max_id(self, model_id):
        return self.db.query(func.max(model_id)).scalar()

    def create(self, obj_in):
        db_obj = self.model(**obj_in.dict())
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, db_obj, obj_in: dict):
        for field in obj_in:
            setattr(db_obj, field, obj_in[field])
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def remove(self, id):
        obj = self.db.query(self.model).get(id)
        self.db.delete(obj)
        self.db.commit()
        return obj

    def remove_with_condition(self, condition: dict):
        objs = self.db.query(self.model).filter_by(**condition).all()
        for obj in objs:
            self.db.delete(obj)
            self.db.commit()
