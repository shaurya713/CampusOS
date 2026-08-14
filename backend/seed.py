"""Seed a local CampusOS database with safe development credentials."""
from app.core.security import hash_password
from app.db.database import SessionLocal
from app.models.domain import Category, Department, StaffProfile
from app.models.user import Role, StudentProfile, User

PASSWORD="CampusOS123"
DEPARTMENTS=["Hostel","Electrical","Plumbing","IT Support","Transport","Security","Cleaning"]
CATEGORIES={"Electrical":["Fan","Light","Power"],"Plumbing":["Water Leakage","Drainage"],"IT Support":["WiFi","Projector"],"Hostel":["Room Maintenance"]}

def create_user(db,name,email,role):
    user=db.query(User).filter_by(email=email).first()
    if not user:
        user=User(full_name=name,email=email,role=role,password_hash=hash_password(PASSWORD),is_verified=True);db.add(user);db.flush()
    return user

def main():
    with SessionLocal() as db:
        departments={}
        for name in DEPARTMENTS:
            x=db.query(Department).filter_by(name=name).first() or Department(name=name);db.add(x);db.flush();departments[name]=x
        for dep,names in CATEGORIES.items():
            for name in names:
                if not db.query(Category).filter_by(name=name).first():db.add(Category(name=name,subcategories=[],department_id=departments[dep].id))
        admin=create_user(db,"Campus Administrator","admin@campus.edu",Role.ADMIN)
        for index,(name,dept) in enumerate((("Asha Electrician","Electrical"),("Ravi Plumber","Plumbing")),1):
            staff=create_user(db,name,f"staff{index}@campus.edu",Role.STAFF)
            if not db.query(StaffProfile).filter_by(user_id=staff.id).first():db.add(StaffProfile(user_id=staff.id,employee_id=f"EMP-{index:03}",department_id=departments[dept].id,designation="Service Technician",specialization=[dept]))
        for index in range(1,6):
            student=create_user(db,f"Student {index}",f"student{index}@campus.edu",Role.STUDENT)
            if not db.query(StudentProfile).filter_by(user_id=student.id).first():db.add(StudentProfile(user_id=student.id,student_id=f"STU-{index:03}",department_name="Hostel",year=2,section="A"))
        db.commit();print(f"Seed complete. Admin: admin@campus.edu / {PASSWORD}")

if __name__=="__main__": main()
