from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.user import Role


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=160)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=32)
<<<<<<< HEAD
    government_id: str = Field(min_length=4, max_length=100)
    permanent_address: str = Field(min_length=10, max_length=500)
    profile_photo_url: str | None = Field(default=None, max_length=500)
=======
>>>>>>> 1b8878ef404f483e7609ab1c87da6c2e8c648546
    password: str = Field(min_length=8, max_length=128)
    student_id: str = Field(min_length=1, max_length=64)
    department: str = Field(min_length=1, max_length=100)
    year: int = Field(ge=1, le=10)
    section: str = Field(min_length=1, max_length=20)

    @field_validator("password")
    @classmethod
    def strong_password(cls, value: str) -> str:
        if not any(char.islower() for char in value) or not any(char.isupper() for char in value) or not any(char.isdigit() for char in value):
            raise ValueError("Password must include uppercase, lowercase, and a number")
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


<<<<<<< HEAD
class ProfileUpdateRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=160)
    phone: str | None = Field(default=None, max_length=32)
    permanent_address: str | None = Field(default=None, max_length=500)
    profile_photo_url: str | None = Field(default=None, max_length=500)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    role: Role
=======
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
>>>>>>> 1b8878ef404f483e7609ab1c87da6c2e8c648546
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    full_name: str
    email: EmailStr
    phone: str | None
<<<<<<< HEAD
    profile_photo_url: str | None
    government_id: str | None
    permanent_address: str | None
    role: Role
    is_active: bool
    is_verified: bool
=======
    role: Role
    is_active: bool
    is_verified: bool

>>>>>>> 1b8878ef404f483e7609ab1c87da6c2e8c648546
