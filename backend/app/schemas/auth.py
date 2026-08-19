from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from app.models.user import Role
class RegisterRequest(BaseModel):
    full_name:str=Field(min_length=2,max_length=160); email:EmailStr; phone:str=Field(min_length=7,max_length=32); government_id:str=Field(min_length=4,max_length=100); permanent_address:str=Field(min_length=10,max_length=500); profile_photo_url:str|None=None; password:str=Field(min_length=8,max_length=128); student_id:str=Field(min_length=1,max_length=64); department:str=Field(min_length=1,max_length=100); year:int=Field(ge=1,le=10); section:str=Field(min_length=1,max_length=20)
    @field_validator("password")
    @classmethod
    def strong_password(cls,v:str)->str:
        if not(any(c.islower() for c in v) and any(c.isupper() for c in v) and any(c.isdigit() for c in v)): raise ValueError("Password must include uppercase, lowercase, and a number")
        return v
class LoginRequest(BaseModel): email:EmailStr; password:str=Field(min_length=1,max_length=128)
class ProfileUpdateRequest(BaseModel): full_name:str=Field(min_length=2,max_length=160); phone:str=Field(min_length=7,max_length=32); permanent_address:str=Field(min_length=10,max_length=500); profile_photo_url:str|None=None
class TokenResponse(BaseModel): access_token:str; refresh_token:str; role:Role; token_type:str="bearer"
class RefreshRequest(BaseModel): refresh_token:str
class UserResponse(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id:UUID; full_name:str; email:EmailStr; phone:str|None; profile_photo_url:str|None; government_id:str|None; permanent_address:str|None; role:Role; is_active:bool; is_verified:bool
