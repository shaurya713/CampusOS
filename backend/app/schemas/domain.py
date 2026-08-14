from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.models.domain import ComplaintStatus, LostFoundType, Priority

class ORM(BaseModel): model_config=ConfigDict(from_attributes=True)
class DepartmentIn(BaseModel): name:str=Field(min_length=2,max_length=100); description:str|None=None
class CategoryIn(BaseModel): name:str=Field(min_length=2,max_length=100); subcategories:list[str]=[]; department_id:UUID|None=None
class StaffIn(BaseModel): full_name:str; email:str; phone:str|None=None; password:str=Field(min_length=8); employee_id:str; department_id:UUID|None=None; designation:str|None=None; specialization:list[str]=[]; service_area:str|None=None; max_active_complaints:int=10
class ComplaintIn(BaseModel): title:str=Field(min_length=4,max_length=200); description:str=Field(min_length=10); location:str=Field(min_length=2,max_length=200); building:str|None=None; floor:str|None=None; room_number:str|None=None; preferred_contact:str|None=None; category_id:UUID|None=None
class ComplaintStatusIn(BaseModel): status:ComplaintStatus; reason:str|None=None; resolution_note:str|None=None
class AssignIn(BaseModel): staff_user_id:UUID|None=None; reason:str|None=None
class CommentIn(BaseModel): text:str=Field(min_length=1,max_length=5000); attachment_url:str|None=None
class LostFoundIn(BaseModel): type:LostFoundType; title:str; description:str; category:str; location:str; date:date; image_url:str|None=None; contact_preference:str|None=None
class AnnouncementIn(BaseModel): title:str; content:str; priority:Priority=Priority.MEDIUM; target_department:str|None=None; target_year:int|None=None; expiry_date:date|None=None
class FeedbackIn(BaseModel): rating:int=Field(ge=1,le=5); comment:str|None=None

class DepartmentOut(ORM): id:UUID; name:str; description:str|None; is_active:bool; created_at:datetime
class CategoryOut(ORM): id:UUID; name:str; subcategories:list[str]; department_id:UUID|None; is_active:bool
class ComplaintOut(ORM): id:UUID; reference_no:str; student_id:UUID; assigned_staff_id:UUID|None; department_id:UUID|None; category_id:UUID|None; title:str; description:str; location:str; priority:Priority; status:ComplaintStatus; ai_status:str; resolution_note:str|None; created_at:datetime; updated_at:datetime
