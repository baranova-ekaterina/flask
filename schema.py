import pydantic
from typing import Type, Optional  
from errors import HttpError


def validate(
        json_data: dict,
        model_class: Type['CreateAdModel'] | Type['UpdateAdModel']
        ):

    try:
        model_item = model_class(**json_data) 
        return model_item.dict(exclude_none=True) 
    except pydantic.ValidationError as error:
        raise HttpError(400, error.errors()) 


class CreateAdModel(pydantic.BaseModel):
    title: str
    description: Optional[str]
    owner: str


class UpdateAdModel(pydantic.BaseModel):
    title: str
    description: Optional[str]
