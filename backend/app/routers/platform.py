import secrets
from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session
from app.core.dependencies import CurrentUser, DatabaseSession, require_roles
from app.core.security import hash_password
from app.models.domain import Announcement, Category, Complaint, ComplaintAIAnalysis, ComplaintComment, ComplaintHistory, ComplaintStatus, Department, LostFoundItem, Notification, NotificationType, Priority, StaffProfile
from app.models.user import Role, User
from app.schemas.common import APIResponse
<<<<<<< HEAD
from app.schemas.domain import AnnouncementIn, AssignIn, CategoryIn, CategoryOut, CommentIn, ComplaintIn, ComplaintOut, ComplaintPriorityIn, ComplaintStatusIn, DepartmentIn, DepartmentOut, LostFoundIn, StaffIn, UserControlIn
=======
from app.schemas.domain import AnnouncementIn, AssignIn, CategoryIn, CategoryOut, CommentIn, ComplaintIn, ComplaintOut, ComplaintStatusIn, DepartmentIn, DepartmentOut, LostFoundIn, StaffIn
>>>>>>> 1b8878ef404f483e7609ab1c87da6c2e8c648546
from app.services.ai import classify
from app.services.storage import save_upload

router=APIRouter()
def admin(): return Depends(require_roles(Role.ADMIN))
def notify(db:Session,user_id:UUID,kind:NotificationType,title:str,body:str,data:dict): db.add(Notification(user_id=user_id,type=kind,title=title,body=body,data=data))
def get_complaint(db:Session,complaint_id:UUID)->Complaint:
    item=db.get(Complaint,complaint_id)
    if not item: raise HTTPException(404,"Complaint not found")
    return item
def access(item:Complaint,user:User):
    if user.role==Role.ADMIN or item.student_id==user.id or item.assigned_staff_id==user.id:return
    raise HTTPException(403,"You cannot access this complaint")

@router.get("/departments",response_model=APIResponse[list[DepartmentOut]])
def departments(db:DatabaseSession): return {"data":list(db.scalars(select(Department).where(Department.is_active)).all())}
@router.post("/departments",response_model=APIResponse[DepartmentOut],status_code=201)
def create_department(payload:DepartmentIn,db:DatabaseSession,_:User=admin()):
    if db.scalar(select(Department).where(Department.name==payload.name)): raise HTTPException(409,"Department already exists")
    x=Department(**payload.model_dump());db.add(x);db.commit();db.refresh(x);return {"data":x}
@router.get("/categories",response_model=APIResponse[list[CategoryOut]])
def categories(db:DatabaseSession):return {"data":list(db.scalars(select(Category).where(Category.is_active)).all())}
@router.post("/categories",response_model=APIResponse[CategoryOut],status_code=201)
def create_category(payload:CategoryIn,db:DatabaseSession,_:User=admin()):
    x=Category(**payload.model_dump());db.add(x);db.commit();db.refresh(x);return {"data":x}

@router.post("/staff",status_code=201)
def create_staff(payload:StaffIn,db:DatabaseSession,_:User=admin()):
<<<<<<< HEAD
    if db.scalar(select(User).where(or_(User.email==payload.email.lower(), User.government_id==payload.government_id))) or db.scalar(select(StaffProfile).where(StaffProfile.employee_id==payload.employee_id)):raise HTTPException(409,"Email, government ID or employee ID already exists")
    u=User(full_name=payload.full_name,email=payload.email.lower(),phone=payload.phone,government_id=payload.government_id,permanent_address=payload.permanent_address,profile_photo_url=payload.profile_photo_url,password_hash=hash_password(payload.password),role=Role.STAFF,is_verified=True);db.add(u);db.flush()
    d=payload.model_dump(exclude={"full_name","email","phone","password","government_id","permanent_address","profile_photo_url"}); db.add(StaffProfile(user_id=u.id,**d));db.commit();return {"data":{"id":str(u.id),"email":u.email}}

@router.get("/staff")
def list_staff(db: DatabaseSession, _: User = admin()):
    rows = db.execute(select(User, StaffProfile).join(StaffProfile, StaffProfile.user_id == User.id).order_by(User.full_name)).all()
    return {"data": [{"id": str(user.id), "full_name": user.full_name, "email": user.email, "phone": user.phone, "employee_id": profile.employee_id, "designation": profile.designation, "availability_status": profile.availability_status, "specialization": profile.specialization, "experience_years": profile.experience_years, "working_hours": profile.working_hours, "is_active": user.is_active} for user, profile in rows]}

@router.get("/experts")
def experts(db: DatabaseSession, _: CurrentUser):
    rows = db.execute(select(User, StaffProfile, Department).join(StaffProfile, StaffProfile.user_id == User.id).outerjoin(Department, Department.id == StaffProfile.department_id).where(User.is_active, StaffProfile.availability_status).order_by(User.full_name)).all()
    return {"data": [{"id": str(user.id), "name": user.full_name, "phone": user.phone, "photo": user.profile_photo_url, "department": department.name if department else "Campus Services", "designation": profile.designation or "Campus Expert", "specialization": profile.specialization, "experience_years": profile.experience_years, "working_hours": profile.working_hours or "09:00 – 17:00"} for user, profile, department in rows]}
=======
    if db.scalar(select(User).where(User.email==payload.email.lower())) or db.scalar(select(StaffProfile).where(StaffProfile.employee_id==payload.employee_id)):raise HTTPException(409,"Email or employee ID already exists")
    u=User(full_name=payload.full_name,email=payload.email.lower(),phone=payload.phone,password_hash=hash_password(payload.password),role=Role.STAFF,is_verified=True);db.add(u);db.flush()
    d=payload.model_dump(exclude={"full_name","email","phone","password"}); db.add(StaffProfile(user_id=u.id,**d));db.commit();return {"data":{"id":str(u.id),"email":u.email}}
>>>>>>> 1b8878ef404f483e7609ab1c87da6c2e8c648546

@router.get("/complaints",response_model=APIResponse[list[ComplaintOut]])
def complaints(db:DatabaseSession,user:CurrentUser,page:int=Query(1,ge=1),limit:int=Query(20,ge=1,le=100),search:str|None=None,status_filter:ComplaintStatus|None=None):
    q=select(Complaint)
    if user.role==Role.STUDENT:q=q.where(Complaint.student_id==user.id)
    elif user.role==Role.STAFF:q=q.where(Complaint.assigned_staff_id==user.id)
    if status_filter:q=q.where(Complaint.status==status_filter)
    if search:q=q.where(or_(Complaint.reference_no.ilike(f"%{search}%"),Complaint.title.ilike(f"%{search}%"),Complaint.description.ilike(f"%{search}%")))
    return {"data":list(db.scalars(q.order_by(Complaint.created_at.desc()).offset((page-1)*limit).limit(limit)).all())}

@router.post("/complaints",response_model=APIResponse[ComplaintOut],status_code=201)
def create_complaint(payload:ComplaintIn,db:DatabaseSession,user:CurrentUser):
    if user.role!=Role.STUDENT: raise HTTPException(403,"Only students can raise complaints")
    result=classify(f"{payload.title} {payload.description}")
    category=db.scalar(select(Category).where(Category.name.ilike(result.category)))
    dept=db.scalar(select(Department).where(Department.name.ilike(result.department)))
<<<<<<< HEAD
    item=Complaint(reference_no=f"CMP-{datetime.now():%Y%m%d}-{secrets.token_hex(3).upper()}",student_id=user.id,category_id=payload.category_id or (category.id if category else None),department_id=dept.id if dept else None,title=payload.title,description=payload.description,location=payload.location,building=payload.building,floor=payload.floor,room_number=payload.room_number,preferred_contact=payload.preferred_contact,image_url=payload.image_url,video_url=payload.video_url,priority=Priority(result.priority.lower()),status=ComplaintStatus.SUBMITTED,ai_status=result.ai_status)
=======
    item=Complaint(reference_no=f"CMP-{datetime.now():%Y%m%d}-{secrets.token_hex(3).upper()}",student_id=user.id,category_id=payload.category_id or (category.id if category else None),department_id=dept.id if dept else None,title=payload.title,description=payload.description,location=payload.location,building=payload.building,floor=payload.floor,room_number=payload.room_number,preferred_contact=payload.preferred_contact,priority=Priority(result.priority.lower()),status=ComplaintStatus.SUBMITTED,ai_status=result.ai_status)
>>>>>>> 1b8878ef404f483e7609ab1c87da6c2e8c648546
    db.add(item);db.flush();db.add(ComplaintAIAnalysis(complaint_id=item.id,category=result.category,subcategory=result.subcategory,department=result.department,suggested_staff_type=result.suggested_staff_type,reason=result.reason,urgency_score=result.urgency_score,confidence=result.confidence,provider_used=result.provider_used,model_name=result.model_name,ai_status=result.ai_status));db.add(ComplaintHistory(complaint_id=item.id,new_status=item.status.value,changed_by=user.id,reason="Complaint submitted"));db.commit();db.refresh(item);return {"data":item}

@router.get("/complaints/{complaint_id}",response_model=APIResponse[ComplaintOut])
def complaint_detail(complaint_id:UUID,db:DatabaseSession,user:CurrentUser):
    item=get_complaint(db,complaint_id);access(item,user);return {"data":item}
@router.patch("/complaints/{complaint_id}/assign")
def assign(complaint_id:UUID,payload:AssignIn,db:DatabaseSession,user:User=admin()):
    item=get_complaint(db,complaint_id); staff=db.get(User,payload.staff_user_id) if payload.staff_user_id else None
    if not staff or staff.role!=Role.STAFF:raise HTTPException(422,"A valid staff user is required")
    old=item.status;item.assigned_staff_id=staff.id;item.status=ComplaintStatus.ASSIGNED;db.add(ComplaintHistory(complaint_id=item.id,old_status=old.value,new_status=item.status.value,changed_by=user.id,reason=payload.reason));notify(db,staff.id,NotificationType.COMPLAINT_ASSIGNED,"New complaint assigned",item.title,{"complaint_id":str(item.id)});db.commit();return {"data":{"id":str(item.id),"status":item.status}}
@router.patch("/complaints/{complaint_id}/status")
def change_status(complaint_id:UUID,payload:ComplaintStatusIn,db:DatabaseSession,user:CurrentUser):
    item=get_complaint(db,complaint_id);access(item,user)
    if user.role==Role.STUDENT and payload.status!=ComplaintStatus.CANCELLED:raise HTTPException(403,"Students can only cancel a complaint")
    if user.role==Role.STUDENT and item.status not in (ComplaintStatus.SUBMITTED,ComplaintStatus.AI_ANALYZING):raise HTTPException(409,"Assigned complaints cannot be cancelled")
    old=item.status;item.status=payload.status;item.resolution_note=payload.resolution_note or item.resolution_note;db.add(ComplaintHistory(complaint_id=item.id,old_status=old.value,new_status=item.status.value,changed_by=user.id,reason=payload.reason));notify(db,item.student_id,NotificationType.COMPLAINT_STATUS_CHANGED,"Complaint status updated",f"{item.reference_no} is now {item.status.value.replace('_',' ')}",{"complaint_id":str(item.id)});db.commit();return {"data":{"status":item.status}}
<<<<<<< HEAD

@router.patch("/complaints/{complaint_id}/priority")
def change_priority(complaint_id:UUID,payload:ComplaintPriorityIn,db:DatabaseSession,user:User=admin()):
    item=get_complaint(db,complaint_id); item.priority=payload.priority
    db.add(ComplaintHistory(complaint_id=item.id,old_status=item.status.value,new_status=item.status.value,changed_by=user.id,reason=payload.reason or f"Priority set to {payload.priority.value}")); db.commit()
    return {"data":{"priority":item.priority}}
=======
>>>>>>> 1b8878ef404f483e7609ab1c87da6c2e8c648546
@router.get("/complaints/{complaint_id}/comments")
def comments(complaint_id:UUID,db:DatabaseSession,user:CurrentUser):
    item=get_complaint(db,complaint_id);access(item,user);return {"data":list(db.scalars(select(ComplaintComment).where(ComplaintComment.complaint_id==item.id).order_by(ComplaintComment.created_at)).all())}
@router.post("/complaints/{complaint_id}/comments",status_code=201)
def comment(complaint_id:UUID,payload:CommentIn,db:DatabaseSession,user:CurrentUser):
    item=get_complaint(db,complaint_id);access(item,user);x=ComplaintComment(complaint_id=item.id,author_id=user.id,**payload.model_dump());db.add(x); recipient=item.assigned_staff_id if user.id==item.student_id else item.student_id
    if recipient:notify(db,recipient,NotificationType.NEW_COMMENT,"New complaint comment",payload.text[:120],{"complaint_id":str(item.id)})
    db.commit();return {"data":{"id":str(x.id)}}

@router.get("/notifications")
def notifications(db:DatabaseSession,user:CurrentUser):return {"data":list(db.scalars(select(Notification).where(Notification.user_id==user.id).order_by(Notification.created_at.desc()).limit(100)).all())}
@router.patch("/notifications/{notification_id}/read")
def read(notification_id:UUID,db:DatabaseSession,user:CurrentUser):
    x=db.get(Notification,notification_id)
    if not x or x.user_id!=user.id:raise HTTPException(404,"Notification not found")
    x.read_at=datetime.now(timezone.utc);db.commit();return {"data":True}
@router.patch("/notifications/read-all")
def read_all(db:DatabaseSession,user:CurrentUser):
    for x in db.scalars(select(Notification).where(Notification.user_id==user.id,Notification.read_at.is_(None))):x.read_at=datetime.now(timezone.utc)
    db.commit();return {"data":True}

@router.get("/lost-found")
def lost_found(db:DatabaseSession,search:str|None=None):
    q=select(LostFoundItem).where(LostFoundItem.is_active)
    if search:q=q.where(or_(LostFoundItem.title.ilike(f"%{search}%"),LostFoundItem.description.ilike(f"%{search}%")))
    return {"data":list(db.scalars(q.order_by(LostFoundItem.created_at.desc())).all())}
@router.post("/lost-found",status_code=201)
def create_lost_found(payload:LostFoundIn,db:DatabaseSession,user:CurrentUser):
    x=LostFoundItem(reporter_id=user.id,**payload.model_dump());db.add(x);db.commit();return {"data":{"id":str(x.id)}}
@router.get("/announcements")
def announcements(db:DatabaseSession):return {"data":list(db.scalars(select(Announcement).where(or_(Announcement.expiry_date.is_(None),Announcement.expiry_date>=datetime.now().date())).order_by(Announcement.created_at.desc())).all())}
@router.post("/announcements",status_code=201)
def create_announcement(payload:AnnouncementIn,db:DatabaseSession,user:User=admin()):
    x=Announcement(author_id=user.id,**payload.model_dump());db.add(x);db.commit();return {"data":{"id":str(x.id)}}
@router.get("/analytics")
def analytics(db:DatabaseSession,_:User=admin()):
    total=db.scalar(select(func.count()).select_from(Complaint)) or 0
    by_status={s.value:db.scalar(select(func.count()).select_from(Complaint).where(Complaint.status==s)) or 0 for s in ComplaintStatus}
    by_priority={p.value:db.scalar(select(func.count()).select_from(Complaint).where(Complaint.priority==p)) or 0 for p in Priority}
    return {"data":{"total_complaints":total,"by_status":by_status,"by_priority":by_priority,"unassigned":db.scalar(select(func.count()).select_from(Complaint).where(Complaint.assigned_staff_id.is_(None))) or 0}}

<<<<<<< HEAD
@router.get("/reports/monthly")
def monthly_report(db:DatabaseSession,user:CurrentUser):
    q=select(Complaint)
    if user.role==Role.STAFF:
        profile=db.scalar(select(StaffProfile).where(StaffProfile.user_id==user.id))
        if not profile: raise HTTPException(403,"Staff profile is required")
        q=q.where(Complaint.department_id==profile.department_id)
    rows=list(db.scalars(q.where(Complaint.created_at>=datetime.now(timezone.utc).replace(day=1,hour=0,minute=0,second=0,microsecond=0))).all())
    resolved=sum(1 for row in rows if row.status in (ComplaintStatus.RESOLVED,ComplaintStatus.CLOSED)); active=len(rows)-resolved
    return {"data":{"month":datetime.now().strftime("%B %Y"),"total":len(rows),"resolved":resolved,"active":active,"resolution_rate":round((resolved/len(rows))*100,1) if rows else 0,"critical":sum(1 for row in rows if row.priority==Priority.CRITICAL)}}

@router.get("/admin/users")
def admin_users(db:DatabaseSession,_:User=admin()):
    rows=list(db.scalars(select(User).order_by(User.created_at.desc())).all())
    return {"data":[{"id":str(row.id),"full_name":row.full_name,"email":row.email,"role":row.role,"is_active":row.is_active,"is_verified":row.is_verified,"created_at":row.created_at} for row in rows]}

@router.patch("/admin/users/{user_id}")
def control_user(user_id:UUID,payload:UserControlIn,db:DatabaseSession,admin_user:User=admin()):
    target=db.get(User,user_id)
    if not target: raise HTTPException(404,"User not found")
    if target.id==admin_user.id and payload.is_active is False: raise HTTPException(409,"Administrators cannot suspend themselves")
    if payload.is_active is not None: target.is_active=payload.is_active
    if payload.is_verified is not None: target.is_verified=payload.is_verified
    db.commit(); return {"data":{"id":str(target.id),"is_active":target.is_active,"is_verified":target.is_verified}}

=======
>>>>>>> 1b8878ef404f483e7609ab1c87da6c2e8c648546
@router.post("/uploads/image",status_code=201)
async def upload_image(file:UploadFile,user:CurrentUser): return {"data":{"url":await save_upload(file,"image")}}
@router.post("/uploads/video",status_code=201)
async def upload_video(file:UploadFile,user:CurrentUser): return {"data":{"url":await save_upload(file,"video")}}
