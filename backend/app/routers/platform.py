import secrets
from datetime import datetime,timezone
from uuid import UUID
from fastapi import APIRouter,Depends,HTTPException,Query,UploadFile
from sqlalchemy import func,or_,select
from sqlalchemy.orm import Session
from app.core.dependencies import CurrentUser,DatabaseSession,require_roles
from app.core.security import hash_password
from app.models.domain import Announcement,Category,Complaint,ComplaintAIAnalysis,ComplaintComment,ComplaintHistory,ComplaintStatus,Department,LostFoundItem,Notification,NotificationType,Priority,StaffProfile
from app.models.user import Role,User
from app.schemas.common import APIResponse
from app.schemas.domain import *
from app.services.ai import classify
from app.services.storage import save_upload
router=APIRouter()
def admin():return Depends(require_roles(Role.ADMIN))
def access(x:Complaint,u:User):
    if u.role==Role.ADMIN or x.student_id==u.id or x.assigned_staff_id==u.id:return
    raise HTTPException(403,"You cannot access this complaint")
def item(db:Session,id:UUID):
    x=db.get(Complaint,id)
    if not x:raise HTTPException(404,"Complaint not found")
    return x
@router.get("/departments",response_model=APIResponse[list[DepartmentOut]])
def departments(db:DatabaseSession):return {"data":list(db.scalars(select(Department).where(Department.is_active)).all())}
@router.post("/departments",response_model=APIResponse[DepartmentOut],status_code=201)
def add_department(p:DepartmentIn,db:DatabaseSession,_:User=admin()):
    x=Department(**p.model_dump());db.add(x);db.commit();db.refresh(x);return {"data":x}
@router.get("/categories",response_model=APIResponse[list[CategoryOut]])
def categories(db:DatabaseSession):return {"data":list(db.scalars(select(Category).where(Category.is_active)).all())}
@router.post("/staff",status_code=201)
def add_staff(p:StaffIn,db:DatabaseSession,_:User=admin()):
    if db.scalar(select(User).where(or_(User.email==p.email.lower(),User.government_id==p.government_id))) or db.scalar(select(StaffProfile).where(StaffProfile.employee_id==p.employee_id)):raise HTTPException(409,"Email, government ID or employee ID already exists")
    u=User(full_name=p.full_name,email=p.email.lower(),phone=p.phone,government_id=p.government_id,permanent_address=p.permanent_address,profile_photo_url=p.profile_photo_url,password_hash=hash_password(p.password),role=Role.STAFF,is_verified=True);db.add(u);db.flush();d=p.model_dump(exclude={"full_name","email","phone","password","government_id","permanent_address","profile_photo_url"});db.add(StaffProfile(user_id=u.id,**d));db.commit();return {"data":{"id":str(u.id)}}
@router.get("/staff")
def staff(db:DatabaseSession,_:User=admin()):
    rows=db.execute(select(User,StaffProfile,Department).join(StaffProfile,StaffProfile.user_id==User.id).outerjoin(Department,Department.id==StaffProfile.department_id)).all();return {"data":[{"id":str(u.id),"full_name":u.full_name,"email":u.email,"phone":u.phone,"department":d.name if d else "Campus Services","employee_id":p.employee_id,"designation":p.designation,"specialization":p.specialization,"experience_years":p.experience_years,"working_hours":p.working_hours,"availability_status":p.availability_status,"is_active":u.is_active}for u,p,d in rows]}
@router.get("/experts")
def experts(db:DatabaseSession,_:CurrentUser):
    rows=db.execute(select(User,StaffProfile,Department).join(StaffProfile,StaffProfile.user_id==User.id).outerjoin(Department,Department.id==StaffProfile.department_id).where(User.is_active,StaffProfile.availability_status)).all();return {"data":[{"id":str(u.id),"name":u.full_name,"phone":u.phone,"photo":u.profile_photo_url,"department":d.name if d else "Campus Services","designation":p.designation,"specialization":p.specialization,"experience_years":p.experience_years,"working_hours":p.working_hours}for u,p,d in rows]}
@router.get("/complaints",response_model=APIResponse[list[ComplaintOut]])
def complaints(db:DatabaseSession,user:CurrentUser,page:int=Query(1,ge=1),limit:int=Query(20,ge=1,le=100),search:str|None=None):
    q=select(Complaint)
    if user.role==Role.STUDENT:q=q.where(Complaint.student_id==user.id)
    elif user.role==Role.STAFF:q=q.where(Complaint.assigned_staff_id==user.id)
    if search:q=q.where(or_(Complaint.title.ilike(f"%{search}%"),Complaint.reference_no.ilike(f"%{search}%")))
    return {"data":list(db.scalars(q.order_by(Complaint.created_at.desc()).offset((page-1)*limit).limit(limit)).all())}
@router.post("/complaints",response_model=APIResponse[ComplaintOut],status_code=201)
def create_complaint(p:ComplaintIn,db:DatabaseSession,user:CurrentUser):
    if user.role!=Role.STUDENT:raise HTTPException(403,"Only students can raise complaints")
    ai=classify(f"{p.title} {p.description}");dept=db.scalar(select(Department).where(Department.name.ilike(ai.department)));cat=db.scalar(select(Category).where(Category.name.ilike(ai.category)))
    x=Complaint(reference_no=f"CMP-{datetime.now():%Y%m%d}-{secrets.token_hex(3).upper()}",student_id=user.id,department_id=dept.id if dept else None,category_id=p.category_id or (cat.id if cat else None),title=p.title,description=p.description,location=p.location,building=p.building,floor=p.floor,room_number=p.room_number,preferred_contact=p.preferred_contact,image_url=p.image_url,video_url=p.video_url,priority=Priority(ai.priority.lower()),status=ComplaintStatus.SUBMITTED,ai_status=ai.ai_status);db.add(x);db.flush();db.add(ComplaintAIAnalysis(complaint_id=x.id,category=ai.category,subcategory=ai.subcategory,department=ai.department,suggested_staff_type=ai.suggested_staff_type,reason=ai.reason,urgency_score=ai.urgency_score,confidence=ai.confidence,provider_used=ai.provider_used,model_name=ai.model_name,ai_status=ai.ai_status));db.add(ComplaintHistory(complaint_id=x.id,new_status=x.status.value,changed_by=user.id,reason="Submitted"));db.commit();db.refresh(x);return {"data":x}
@router.patch("/complaints/{id}/assign")
def assign(id:UUID,p:AssignIn,db:DatabaseSession,user:User=admin()):
    x=item(db,id);expert=db.get(User,p.staff_user_id)
    if not expert or expert.role!=Role.STAFF or not expert.is_active:raise HTTPException(422,"Choose an active staff expert")
    x.assigned_staff_id=expert.id;x.status=ComplaintStatus.ASSIGNED;db.add(ComplaintHistory(complaint_id=x.id,new_status=x.status.value,changed_by=user.id,reason=p.reason));db.commit();return {"data":{"status":x.status}}
@router.patch("/complaints/{id}/status")
def update_status(id:UUID,p:ComplaintStatusIn,db:DatabaseSession,user:CurrentUser):
    x=item(db,id);access(x,user)
    if user.role==Role.STUDENT and p.status!=ComplaintStatus.CANCELLED:raise HTTPException(403,"Students can only cancel a submitted complaint")
    x.status=p.status;x.resolution_note=p.resolution_note or x.resolution_note;db.add(ComplaintHistory(complaint_id=x.id,new_status=x.status.value,changed_by=user.id,reason=p.reason));db.commit();return {"data":{"status":x.status}}
@router.patch("/complaints/{id}/priority")
def update_priority(id:UUID,p:ComplaintPriorityIn,db:DatabaseSession,user:User=admin()):
    x=item(db,id);x.priority=p.priority;db.commit();return {"data":{"priority":x.priority}}
@router.get("/complaints/{id}",response_model=APIResponse[ComplaintOut])
def detail(id:UUID,db:DatabaseSession,user:CurrentUser):x=item(db,id);access(x,user);return {"data":x}
@router.get("/lost-found")
def lost_found(db:DatabaseSession,search:str|None=None,type:str|None=None):
    q=select(LostFoundItem).where(LostFoundItem.is_active)
    if search:q=q.where(or_(LostFoundItem.title.ilike(f"%{search}%"),LostFoundItem.description.ilike(f"%{search}%"),LostFoundItem.category.ilike(f"%{search}%")))
    if type:q=q.where(LostFoundItem.type==type)
    return {"data":list(db.scalars(q.order_by(LostFoundItem.created_at.desc())).all())}
@router.post("/lost-found",status_code=201)
def add_lost_found(p:LostFoundIn,db:DatabaseSession,user:CurrentUser):x=LostFoundItem(reporter_id=user.id,**p.model_dump());db.add(x);db.commit();return {"data":{"id":str(x.id)}}
@router.get("/reports/monthly")
def report(db:DatabaseSession,user:CurrentUser):
    q=select(Complaint).where(Complaint.created_at>=datetime.now(timezone.utc).replace(day=1,hour=0,minute=0,second=0,microsecond=0))
    if user.role==Role.STAFF:q=q.where(Complaint.assigned_staff_id==user.id)
    rows=list(db.scalars(q).all());done=sum(x.status in(ComplaintStatus.RESOLVED,ComplaintStatus.CLOSED)for x in rows);return {"data":{"month":datetime.now().strftime("%B %Y"),"total":len(rows),"resolved":done,"active":len(rows)-done,"critical":sum(x.priority==Priority.CRITICAL for x in rows),"resolution_rate":round(done*100/len(rows),1)if rows else 0}}
@router.get("/admin/users")
def users(db:DatabaseSession,_:User=admin()):return {"data":[{"id":str(u.id),"full_name":u.full_name,"email":u.email,"role":u.role,"is_active":u.is_active,"is_verified":u.is_verified,"created_at":u.created_at}for u in db.scalars(select(User).order_by(User.created_at.desc())).all()]}
@router.patch("/admin/users/{id}")
def user_control(id:UUID,p:UserControlIn,db:DatabaseSession,a:User=admin()):
    u=db.get(User,id)
    if not u:raise HTTPException(404,"User not found")
    if u.id==a.id and p.is_active is False:raise HTTPException(409,"You cannot suspend your own administrator account")
    if p.is_active is not None:u.is_active=p.is_active
    if p.is_verified is not None:u.is_verified=p.is_verified
    db.commit();return {"data":{"id":str(u.id),"is_active":u.is_active,"is_verified":u.is_verified}}
@router.get("/analytics")
def analytics(db:DatabaseSession,_:User=admin()):return {"data":{"total_complaints":db.scalar(select(func.count()).select_from(Complaint))or 0,"unassigned":db.scalar(select(func.count()).select_from(Complaint).where(Complaint.assigned_staff_id.is_(None)))or 0}}
@router.post("/uploads/image",status_code=201)
async def upload_image(file:UploadFile,_:CurrentUser):return {"data":{"url":await save_upload(file,"image")}}
@router.post("/uploads/video",status_code=201)
async def upload_video(file:UploadFile,_:CurrentUser):return {"data":{"url":await save_upload(file,"video")}}
