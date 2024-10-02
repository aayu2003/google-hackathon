from pydantic import BaseModel
from typing import List, Optional


class City(BaseModel):
    name:str


class demand(BaseModel):
    category:str
    city:str
    quantity:int
class products(BaseModel):
    model_name:str
    specifications:str
    target_customer:str
    trending_level:str
    no_of_units_forcasted:int
    price:int


class OutputModel(BaseModel):
    city: str
    city_type: str
    demand_summary: str
    products: List[products]


    