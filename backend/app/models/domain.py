import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Enum, Float, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Priority(str, enum.Enum): LOW="low"; MEDIUM="medium"; HIGH="high"; CRITICAL="critical"
class ComplaintStatus(str, enum.Enum): SUBMITTED="submitted"; AI_ANALYZING="ai_analyzing"; ASSIGNED="assigned"; ACCEPTED="accepted"; IN_PROGRESS="in_progress"; ON_HOLD="on_hold"; RESOLVED="resolved"; CLOSED="closed"; REJECTED="rejected"; CANCELLED="cancelled"
class NotificationType(str, enum.Enum): COMPLAINT_ASSIGNED="complaint_assigned"; COMPLAINT_ACCEPTED="complaint_accepted"; COMPLAINT_STATUS_CHANGED="complaint_status_changed"; COMPLAINT_RESOLVED="complaint_resolved"; COMPLAINT_REASSIGNED="complaint_reassigned"; NEW_COMMENT="new_comment"; NEW_ANNOUNCEMENT="new_announcement"; SYSTEM_ALERT="system_alert"
class LostFoundType(str, enum.Enum): LOST="lost"; FOUND="found"

class Department(Base):
    __tablename__="departments"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    name: Mapped[str]=mapped_column(String(100),unique=True,nullable=False)
    description: Mapped[str|None]=mapped_column(Text)
    is_active: Mapped[bool]=mapped_column(Boolean,default=True,nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now(),nullable=False)

class Category(Base):
    __tablename__="categories"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    name: Mapped[str]=mapped_column(String(100),unique=True,nullable=False)
    subcategories: Mapped[list]=mapped_column(JSON,default=list,nullable=False)
    department_id: Mapped[uuid.UUID|None]=mapped_column(UUID(as_uuid=True),ForeignKey("departments.id",ondelete="SET NULL"))
    is_active: Mapped[bool]=mapped_column(Boolean,default=True,nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now(),nullable=False)

class StaffProfile(Base):
    __tablename__="staff_profiles"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    user_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("users.id",ondelete="CASCADE"),unique=True,nullable=False)
    employee_id: Mapped[str]=mapped_column(String(64),unique=True,nullable=False)
    department_id: Mapped[uuid.UUID|None]=mapped_column(UUID(as_uuid=True),ForeignKey("departments.id",ondelete="SET NULL"))
    designation: Mapped[str|None]=mapped_column(String(100))
    specialization: Mapped[list]=mapped_column(JSON,default=list,nullable=False)
    service_area: Mapped[str|None]=mapped_column(String(160))
    max_active_complaints: Mapped[int]=mapped_column(Integer,default=10,nullable=False)
    availability_status: Mapped[bool]=mapped_column(Boolean,default=True,nullable=False)
    experience_years: Mapped[int]=mapped_column(Integer,default=0,nullable=False)
    working_hours: Mapped[str|None]=mapped_column(String(120))
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now(),nullable=False)

class Complaint(Base):
    __tablename__="complaints"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    reference_no: Mapped[str]=mapped_column(String(24),unique=True,index=True,nullable=False)
    student_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("users.id",ondelete="CASCADE"),nullable=False,index=True)
    assigned_staff_id: Mapped[uuid.UUID|None]=mapped_column(UUID(as_uuid=True),ForeignKey("users.id",ondelete="SET NULL"),index=True)
    department_id: Mapped[uuid.UUID|None]=mapped_column(UUID(as_uuid=True),ForeignKey("departments.id",ondelete="SET NULL"))
    category_id: Mapped[uuid.UUID|None]=mapped_column(UUID(as_uuid=True),ForeignKey("categories.id",ondelete="SET NULL"))
    title: Mapped[str]=mapped_column(String(200),nullable=False)
    description: Mapped[str]=mapped_column(Text,nullable=False)
    location: Mapped[str]=mapped_column(String(200),nullable=False)
    building: Mapped[str|None]=mapped_column(String(100)); floor: Mapped[str|None]=mapped_column(String(40)); room_number: Mapped[str|None]=mapped_column(String(40)); preferred_contact: Mapped[str|None]=mapped_column(String(100))
    priority: Mapped[Priority]=mapped_column(Enum(Priority,name="complaint_priority"),default=Priority.MEDIUM,nullable=False)
    status: Mapped[ComplaintStatus]=mapped_column(Enum(ComplaintStatus,name="complaint_status"),default=ComplaintStatus.SUBMITTED,nullable=False,index=True)
    ai_status: Mapped[str]=mapped_column(String(32),default="pending",nullable=False)
    resolution_note: Mapped[str|None]=mapped_column(Text)
    image_url: Mapped[str|None]=mapped_column(String(500))
    video_url: Mapped[str|None]=mapped_column(String(500))
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now(),nullable=False)

class ComplaintAIAnalysis(Base):
    __tablename__="complaint_ai_analysis"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    complaint_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("complaints.id",ondelete="CASCADE"),unique=True,nullable=False)
    category: Mapped[str|None]=mapped_column(String(100)); subcategory: Mapped[str|None]=mapped_column(String(100)); department: Mapped[str|None]=mapped_column(String(100)); suggested_staff_type: Mapped[str|None]=mapped_column(String(100)); reason: Mapped[str|None]=mapped_column(Text)
    urgency_score: Mapped[int]=mapped_column(Integer,default=5,nullable=False); confidence: Mapped[float]=mapped_column(Float,default=0.0,nullable=False)
    provider_used: Mapped[str]=mapped_column(String(50),nullable=False); model_name: Mapped[str|None]=mapped_column(String(100)); processing_time: Mapped[float|None]=mapped_column(Float); ai_status: Mapped[str]=mapped_column(String(32),nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now(),nullable=False)

class ComplaintHistory(Base):
    __tablename__="complaint_status_history"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    complaint_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("complaints.id",ondelete="CASCADE"),nullable=False,index=True)
    old_status: Mapped[str|None]=mapped_column(String(32)); new_status: Mapped[str]=mapped_column(String(32),nullable=False); changed_by: Mapped[uuid.UUID|None]=mapped_column(UUID(as_uuid=True),ForeignKey("users.id",ondelete="SET NULL")); reason: Mapped[str|None]=mapped_column(Text)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now(),nullable=False)

class ComplaintComment(Base):
    __tablename__="complaint_comments"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    complaint_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("complaints.id",ondelete="CASCADE"),nullable=False,index=True); author_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("users.id",ondelete="CASCADE"),nullable=False); text: Mapped[str]=mapped_column(Text,nullable=False); attachment_url: Mapped[str|None]=mapped_column(String(500))
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False); updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now(),nullable=False)

class Notification(Base):
    __tablename__="notifications"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4); user_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("users.id",ondelete="CASCADE"),nullable=False,index=True); type: Mapped[NotificationType]=mapped_column(Enum(NotificationType,name="notification_type"),nullable=False); title: Mapped[str]=mapped_column(String(160),nullable=False); body: Mapped[str]=mapped_column(Text,nullable=False); data: Mapped[dict]=mapped_column(JSON,default=dict,nullable=False); read_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True)); created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False); updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now(),nullable=False)

class LostFoundItem(Base):
    __tablename__="lost_found_items"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4); reporter_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("users.id",ondelete="CASCADE"),nullable=False); type: Mapped[LostFoundType]=mapped_column(Enum(LostFoundType,name="lost_found_type"),nullable=False); title: Mapped[str]=mapped_column(String(200),nullable=False); description: Mapped[str]=mapped_column(Text,nullable=False); category: Mapped[str]=mapped_column(String(80),nullable=False); location: Mapped[str]=mapped_column(String(200),nullable=False); date: Mapped[date]=mapped_column(Date,nullable=False); image_url: Mapped[str|None]=mapped_column(String(500)); contact_preference: Mapped[str|None]=mapped_column(String(120)); is_active: Mapped[bool]=mapped_column(Boolean,default=True,nullable=False); created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False); updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now(),nullable=False)

class Announcement(Base):
    __tablename__="announcements"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4); author_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("users.id",ondelete="CASCADE"),nullable=False); title: Mapped[str]=mapped_column(String(200),nullable=False); content: Mapped[str]=mapped_column(Text,nullable=False); priority: Mapped[Priority]=mapped_column(Enum(Priority,name="announcement_priority"),default=Priority.MEDIUM,nullable=False); target_department: Mapped[str|None]=mapped_column(String(100)); target_year: Mapped[int|None]=mapped_column(Integer); expiry_date: Mapped[date|None]=mapped_column(Date); created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False); updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now(),nullable=False)
