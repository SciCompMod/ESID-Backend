from pydantic import BaseModel
from typing import Union

class IdNotAvailable(BaseModel): 
    status: str
    message: str
