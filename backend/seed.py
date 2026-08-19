from app.core.security import hash_password
from app.db.database import SessionLocal
from app.models.domain import Category,Department,StaffProfile
from app.models.user import Role,StudentProfile,User
PASSWORD="CampusOS123"
DEPTS=["Electrical","Plumbing","IT Support","Security","Cleaning","Hostel"]
EXPERTS=[("Asha Mehta","asha.mehta@campus.edu","EMP-101","Electrical","Senior Electrical Technician",8,"08:00 – 16:00",["Lighting","Power","Safety"]),("Ravi Kumar","ravi.kumar@campus.edu","EMP-102","Plumbing","Plumbing Specialist",10,"09:00 – 17:00",["Leakage","Drainage","Water Supply"]),("Neha Singh","neha.singh@campus.edu","EMP-103","IT Support","IT & AV Specialist",6,"10:00 – 18:00",["Wi-Fi","Projector","Network"]),("Farhan Ali","farhan.ali@campus.edu","EMP-104","Security","Security Supervisor",9,"07:00 – 15:00",["Access","CCTV","Incident Response"]),("Priya Nair","priya.nair@campus.edu","EMP-105","Cleaning","Facilities Coordinator",7,"08:00 – 16:00",["Sanitation","Waste","Pest Coordination"])]
def user(db,name,email,role,n):
    x=db.query(User).filter_by(email=email).first()
    if not x:x=User(full_name=name,email=email,phone=f"9000000{n:03}",government_id=f"SEED-ID-{n:03}",permanent_address="Campus Staff Residence, Main Campus",password_hash=hash_password(PASSWORD),role=role,is_verified=True);db.add(x);db.flush()
    return x
def main():
  with SessionLocal() as db:
    depts={}
    for name in DEPTS:
      d=db.query(Department).filter_by(name=name).first() or Department(name=name);db.add(d);db.flush();depts[name]=d
    for dep,cat in [("Electrical","Electrical Hazard"),("Plumbing","Water Leakage"),("IT Support","Network & Devices"),("Security","Security & Access"),("Cleaning","Housekeeping")]:
      if not db.query(Category).filter_by(name=cat).first():db.add(Category(name=cat,department_id=depts[dep].id,subcategories=[]))
    user(db,"Campus Operations Admin","admin@campus.edu",Role.ADMIN,1)
    for i,(name,email,eid,dep,title,years,hours,skills) in enumerate(EXPERTS,10):
      u=user(db,name,email,Role.STAFF,i)
      if not db.query(StaffProfile).filter_by(user_id=u.id).first():db.add(StaffProfile(user_id=u.id,employee_id=eid,department_id=depts[dep].id,designation=title,specialization=skills,experience_years=years,working_hours=hours))
    for i,(name,email,sid,dep) in enumerate([("Aarav Sharma","aarav.sharma@campus.edu","STU-031","Computer Science"),("Meera Iyer","meera.iyer@campus.edu","STU-044","Electrical Engineering")],30):
      u=user(db,name,email,Role.STUDENT,i)
      if not db.query(StudentProfile).filter_by(user_id=u.id).first():db.add(StudentProfile(user_id=u.id,student_id=sid,department_name=dep,year=2,section="A"))
    db.commit()
  print("Seed complete: admin, 5 multidisciplinary experts and 2 students.")
if __name__=="__main__":main()
