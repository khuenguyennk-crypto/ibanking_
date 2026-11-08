from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class UserBrief(BaseModel):
    user_id: int
    full_name: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserBrief


class UserMe(BaseModel):
    user_id: int
    username: str
    full_name: str
    phone: str
    email: str

    model_config = {"from_attributes": True}


class UserInternal(BaseModel):
    user_id: int
    full_name: str
    phone: str
    email: str

    model_config = {"from_attributes": True}
    