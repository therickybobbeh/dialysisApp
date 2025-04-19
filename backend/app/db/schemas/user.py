from pydantic import BaseModel, EmailStr

from pydantic import BaseModel, EmailStr
from typing import List, Optional

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str
    notifications: Optional[dict] = {}
    patients: Optional[List[int]] = []
    sex: str
    height: float
    birth_date: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
    
class LoginData(BaseModel):
    email: str
    password: str

class ProviderPatientsResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    patients: list[int]
    #
    model_config = {
        "from_attributes": True
    }
