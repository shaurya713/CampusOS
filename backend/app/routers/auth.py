from datetime import datetime,timedelta,timezone
from uuid import UUID
from fastapi import APIRouter,HTTPException,status
from sqlalchemy import select
from app.config import get_settings
from app.core.dependencies import CurrentUser,DatabaseSession
from app.core.security import create_access_token,create_refresh_token,decode_token,hash_password,token_hash,verify_password
from app.models.user import RefreshToken,Role,StudentProfile,User
from app.schemas.auth import LoginRequest,ProfileUpdateRequest,RefreshRequest,RegisterRequest,TokenResponse,UserResponse
from app.schemas.common import APIResponse
router=APIRouter(prefix="/auth",tags=["Authentication"]);settings=get_settings()
def issue_pair(user:User,db:DatabaseSession)->TokenResponse:
    access=create_access_token(str(user.id));refresh=create_refresh_token(str(user.id));db.add(RefreshToken(user_id=user.id,token_hash=token_hash(refresh),expires_at=datetime.now(timezone.utc)+timedelta(days=settings.jwt_refresh_token_expire_days)));return TokenResponse(access_token=access,refresh_token=refresh,role=user.role)
@router.post("/register",response_model=APIResponse[UserResponse],status_code=status.HTTP_201_CREATED)
def register(p:RegisterRequest,db:DatabaseSession):
    if db.scalar(select(User).where(User.email==p.email.lower())):raise HTTPException(409,"An account with this email already exists")
    if db.scalar(select(User).where(User.government_id==p.government_id)):raise HTTPException(409,"An account with this government ID already exists")
    if db.scalar(select(StudentProfile).where(StudentProfile.student_id==p.student_id)):raise HTTPException(409,"An account with this student ID already exists")
    user=User(full_name=p.full_name,email=p.email.lower(),phone=p.phone,government_id=p.government_id,permanent_address=p.permanent_address,profile_photo_url=p.profile_photo_url,password_hash=hash_password(p.password),role=Role.STUDENT,is_verified=False);db.add(user);db.flush();db.add(StudentProfile(user_id=user.id,student_id=p.student_id,department_name=p.department,year=p.year,section=p.section));db.commit();db.refresh(user);return {"data":user}
@router.post("/login",response_model=APIResponse[TokenResponse])
def login(p:LoginRequest,db:DatabaseSession):
    user=db.scalar(select(User).where(User.email==p.email.lower()))
    if not user or not verify_password(p.password,user.password_hash):raise HTTPException(401,"Incorrect email or password")
    if not user.is_active:raise HTTPException(403,"This account has been suspended")
    if not user.is_verified:raise HTTPException(403,"Your registration is awaiting administrator approval")
    user.last_login=datetime.now(timezone.utc);pair=issue_pair(user,db);db.commit();return {"data":pair}
@router.post("/refresh",response_model=APIResponse[TokenResponse])
def refresh(p:RefreshRequest,db:DatabaseSession):
    try: uid=UUID(str(decode_token(p.refresh_token,"refresh")["sub"]))
    except Exception:raise HTTPException(401,"Invalid or expired refresh token")
    stored=db.scalar(select(RefreshToken).where(RefreshToken.token_hash==token_hash(p.refresh_token),RefreshToken.revoked_at.is_(None)));user=db.get(User,uid)
    if not stored or stored.user_id!=uid or not user or not user.is_active:raise HTTPException(401,"Invalid or expired refresh token")
    stored.revoked_at=datetime.now(timezone.utc);pair=issue_pair(user,db);db.commit();return {"data":pair}
@router.get("/me",response_model=APIResponse[UserResponse])
def me(user:CurrentUser):return {"data":user}
@router.patch("/me",response_model=APIResponse[UserResponse])
def update(p:ProfileUpdateRequest,db:DatabaseSession,user:CurrentUser):
    user.full_name=p.full_name;user.phone=p.phone;user.permanent_address=p.permanent_address;user.profile_photo_url=p.profile_photo_url;db.commit();db.refresh(user);return {"data":user}
