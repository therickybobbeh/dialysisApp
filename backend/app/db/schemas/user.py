from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str
    height = float
    sex = str

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
