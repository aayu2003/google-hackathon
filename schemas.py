from pydantic import BaseModel
from typing import List, Optional


class City(BaseModel):
    name:str