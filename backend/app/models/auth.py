from pydantic import BaseModel

class UserRegister(BaseModel):
    email: str
    password: str
    preferred_name: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    mcp_slug: str