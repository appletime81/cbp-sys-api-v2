from fastapi.encoders import jsonable_encoder


def orm_to_pydantic(db_model, pydantic_model):
    db_model_dict = jsonable_encoder(db_model)
    return pydantic_model(**db_model_dict)


def orm_to_dict(db_model):
    return jsonable_encoder(db_model)


def pydantic_to_orm(pydantic_model, db_model):
    return db_model(**pydantic_model.dict())


def dict_to_pydantic(pydantic_model, dict_model):
    return pydantic_model(**dict_model)


def dict_to_orm(dict_obj, db_model):
    return db_model(**dict_obj)
