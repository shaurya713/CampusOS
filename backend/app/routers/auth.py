from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import CurrentUser, DatabaseSession
from app.config import get_settings
from app.core.security import create_access_token, create_refresh_token, decode_token, hash_password, token_hash, verify_password
from app.models.user import RefreshToken, Role, StudentProfile, User
<<<<<<< HEAD
from app.schemas.auth import LoginRequest, ProfileUpdateRequest, RefreshRequest, RegisterRequest, TokenResponse, UserResponse
=======
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse, UserResponse
>>>>>>> 1b8878ef404f483e7609ab1c87da6c2e8c648546
from app.schemas.common import APIResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])
settings = get_settings()


def issue_token_pair(user: User, db: DatabaseSession) -> TokenResponse:
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    db.add(RefreshToken(user_id=user.id, token_hash=token_hash(refresh_token), expires_at=datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_token_expire_days)))
<<<<<<< HEAD
    return TokenResponse(access_token=access_token, refresh_token=refresh_token, role=user.role)
=======
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)
>>>>>>> 1b8878ef404f483e7609ab1c87da6c2e8c648546


@router.post("/register", response_model=APIResponse[UserResponse], status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: DatabaseSession):
    existing = db.scalar(select(User).where(User.email == payload.email.lower()))
    if existing:
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    existing_student_id = db.scalar(select(StudentProfile).where(StudentProfile.student_id == payload.student_id))
    if existing_student_id:
        raise HTTPException(status_code=409, detail="An account with this student ID already exists")
<<<<<<< HEAD
    existing_government_id = db.scalar(select(User).where(User.government_id == payload.government_id))
    if existing_government_id:
        raise HTTPException(status_code=409, detail="An account with this government ID already exists")
    user = User(full_name=payload.full_name, email=payload.email.lower(), phone=payload.phone, government_id=payload.government_id, permanent_address=payload.permanent_address, profile_photo_url=payload.profile_photo_url, password_hash=hash_password(payload.password), role=Role.STUDENT, is_verified=False)
=======
    user = User(full_name=payload.full_name, email=payload.email.lower(), phone=payload.phone, password_hash=hash_password(payload.password), role=Role.STUDENT)
>>>>>>> 1b8878ef404f483e7609ab1c87da6c2e8c648546
    db.add(user)
    db.flush()
    db.add(StudentProfile(user_id=user.id, student_id=payload.student_id, department_name=payload.department, year=payload.year, section=payload.section))
    db.commit()
    db.refresh(user)
    return {"data": user}


@router.post("/login", response_model=APIResponse[TokenResponse])
def login(payload: LoginRequest, db: DatabaseSession):
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="This account has been suspended")
<<<<<<< HEAD
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Your registration is awaiting administrator approval")
=======
>>>>>>> 1b8878ef404f483e7609ab1c87da6c2e8c648546
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    token_pair = issue_token_pair(user, db)
    db.commit()
    return {"data": token_pair}


@router.post("/refresh", response_model=APIResponse[TokenResponse])
def refresh(payload: RefreshRequest, db: DatabaseSession):
    try:
        token_payload = decode_token(payload.refresh_token, "refresh")
        user_id = UUID(str(token_payload["sub"]))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    stored_token = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash(payload.refresh_token), RefreshToken.revoked_at.is_(None)))
    user = db.get(User, user_id)
    if not stored_token or stored_token.user_id != user_id or stored_token.expires_at < datetime.now(timezone.utc) or not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    stored_token.revoked_at = datetime.now(timezone.utc)
    token_pair = issue_token_pair(user, db)
    db.commit()
    return {"data": token_pair}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: RefreshRequest, current_user: CurrentUser, db: DatabaseSession):
    token = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash(payload.refresh_token), RefreshToken.user_id == current_user.id, RefreshToken.revoked_at.is_(None)))
    if token:
        token.revoked_at = datetime.now(timezone.utc)
        db.commit()
    return None


@router.get("/me", response_model=APIResponse[UserResponse])
def me(current_user: CurrentUser):
    return {"data": current_user}
<<<<<<< HEAD


@router.patch("/me", response_model=APIResponse[UserResponse])
def update_me(payload: ProfileUpdateRequest, db: DatabaseSession, current_user: CurrentUser):
    current_user.full_name = payload.full_name
    current_user.phone = payload.phone
    current_user.permanent_address = payload.permanent_address
    current_user.profile_photo_url = payload.profile_photo_url
    db.commit()
    db.refresh(current_user)
    return {"data": current_user}
=======
>>>>>>> 1b8878ef404f483e7609ab1c87da6c2e8c648546
