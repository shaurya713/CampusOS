"""Idempotent local-development seed data for CampusOS."""
from app.core.security import hash_password
from app.db.database import SessionLocal
from app.models.domain import Category, Complaint, ComplaintAIAnalysis, ComplaintHistory, ComplaintStatus, Department, Priority, StaffProfile
from app.models.user import Role, StudentProfile, User

PASSWORD = "CampusOS123"
DEPARTMENTS = ["Hostel", "Electrical", "Plumbing", "IT Support", "Transport", "Security", "Cleaning", "Library", "Infrastructure"]
CATEGORIES = {"Electrical": ["Fan", "Light", "Power", "Electrical Hazard"], "Plumbing": ["Water Leakage", "Drainage", "Water Supply Issue"], "IT Support": ["WiFi", "Projector", "Network Connectivity"], "Hostel": ["Room Maintenance"], "Security": ["Security Breach", "Access Management"], "Cleaning": ["Waste Clearance", "Sanitation Cleaning"]}
STAFF = [("Asha Mehta", "asha.mehta@campus.edu", "EMP-101", "Electrical", "Electrical Technician", ["Electrical", "Power", "Lighting"]), ("Ravi Kumar", "ravi.kumar@campus.edu", "EMP-102", "Plumbing", "Plumbing Technician", ["Plumbing", "Water Leakage", "Drainage"]), ("Neha Singh", "neha.singh@campus.edu", "EMP-103", "IT Support", "IT Support Specialist", ["WiFi", "Network", "Projector"]), ("Farhan Ali", "farhan.ali@campus.edu", "EMP-104", "Security", "Security Supervisor", ["Security", "Access Management"])]
STUDENTS = [("Aarav Sharma", "aarav.sharma@campus.edu", "STU-2024-031", "Computer Science", 2, "A"), ("Meera Iyer", "meera.iyer@campus.edu", "STU-2024-044", "Electrical Engineering", 2, "B"), ("Kabir Khan", "kabir.khan@campus.edu", "STU-2023-118", "Mechanical Engineering", 3, "A"), ("Sana Kapoor", "sana.kapoor@campus.edu", "STU-2024-087", "Information Technology", 2, "C")]
COMPLAINTS = [
    ("CMP-2026-0001", 0, "Water leaking from hostel washroom tap", "The washroom tap in Block A room 214 has been leaking continuously since morning.", "Hostel Block A, Room 214", "Plumbing", "Water Leakage", "HIGH", "IN_PROGRESS", 1, "Ravi Kumar is scheduled to inspect the fitting today."),
    ("CMP-2026-0002", 1, "Exposed wire near electrical panel", "A cable insulation is damaged near the corridor electrical panel outside Lab E-12.", "Engineering Block, Lab E-12", "Electrical", "Electrical Hazard", "CRITICAL", "ASSIGNED", 0, "Area secured and technician assigned for immediate inspection."),
    ("CMP-2026-0003", 3, "Library Wi-Fi keeps disconnecting", "Wi-Fi disconnects every few minutes on the second floor reading area.", "Central Library, Second Floor", "IT Support", "Network Connectivity", "HIGH", "ACCEPTED", 2, "Network diagnostics have been started."),
    ("CMP-2026-0004", 2, "Ceiling fan making loud noise", "The fan in the south hostel study room is vibrating and making a loud noise.", "South Hostel, Study Room 3", "Electrical", "Fan", "MEDIUM", "RESOLVED", 0, "Fan mounting and regulator were repaired."),
    ("CMP-2026-0005", 0, "Overflowing waste bin outside cafeteria", "The bin near the cafeteria entrance has overflowed and needs clearance.", "Main Cafeteria Entrance", "Cleaning", "Waste Clearance", "MEDIUM", "SUBMITTED", None, "Awaiting housekeeping assignment."),
    ("CMP-2026-0006", 1, "Projector not detecting HDMI input", "The projector in seminar room B is powered on but does not detect any HDMI source.", "Academic Block, Seminar Room B", "IT Support", "Projector", "MEDIUM", "ASSIGNED", 2, "AV technician assigned for the next available slot."),
    ("CMP-2026-0007", 3, "Main gate access card reader is offline", "The entry card reader at the main gate does not respond to valid student cards.", "Main Gate", "Security", "Access Management", "HIGH", "IN_PROGRESS", 3, "Security team has moved to manual verification while the reader is checked."),
]


def get_user(db, full_name: str, email: str, role: Role) -> User:
    user = db.query(User).filter_by(email=email).first()
    if not user:
        user = User(full_name=full_name, email=email, role=role, password_hash=hash_password(PASSWORD), is_verified=True)
        db.add(user)
        db.flush()
    return user


def main() -> None:
    with SessionLocal() as db:
        departments: dict[str, Department] = {}
        for name in DEPARTMENTS:
            department = db.query(Department).filter_by(name=name).first() or Department(name=name)
            db.add(department); db.flush(); departments[name] = department
        categories: dict[tuple[str, str], Category] = {}
        for department_name, names in CATEGORIES.items():
            for name in names:
                category = db.query(Category).filter_by(name=name).first() or Category(name=name, subcategories=[], department_id=departments[department_name].id)
                db.add(category); db.flush(); categories[(department_name, name)] = category
        get_user(db, "Campus Operations Admin", "admin@campus.edu", Role.ADMIN)
        staff_users: list[User] = []
        for name, email, employee_id, department_name, designation, specialization in STAFF:
            user = get_user(db, name, email, Role.STAFF); staff_users.append(user)
            if not db.query(StaffProfile).filter_by(user_id=user.id).first(): db.add(StaffProfile(user_id=user.id, employee_id=employee_id, department_id=departments[department_name].id, designation=designation, specialization=specialization))
        student_users: list[User] = []
        for name, email, student_id, department_name, year, section in STUDENTS:
            user = get_user(db, name, email, Role.STUDENT); student_users.append(user)
            if not db.query(StudentProfile).filter_by(user_id=user.id).first(): db.add(StudentProfile(user_id=user.id, student_id=student_id, department_name=department_name, year=year, section=section))
        for reference, student_index, title, description, location, department_name, category_name, priority, complaint_status, staff_index, note in COMPLAINTS:
            if db.query(Complaint).filter_by(reference_no=reference).first(): continue
            complaint = Complaint(reference_no=reference, student_id=student_users[student_index].id, assigned_staff_id=staff_users[staff_index].id if staff_index is not None else None, department_id=departments[department_name].id, category_id=categories[(department_name, category_name)].id, title=title, description=description, location=location, priority=Priority[priority], status=ComplaintStatus[complaint_status], ai_status="seeded")
            db.add(complaint); db.flush()
            db.add(ComplaintAIAnalysis(complaint_id=complaint.id, category=category_name, subcategory=category_name, department=department_name, suggested_staff_type="Campus Service Team", reason="Created as a realistic development record.", urgency_score=8 if priority in ("HIGH", "CRITICAL") else 5, confidence=.92, provider_used="seed", model_name="development", ai_status="seeded"))
            db.add(ComplaintHistory(complaint_id=complaint.id, new_status=complaint_status.lower(), changed_by=student_users[student_index].id, reason=note))
        db.commit()
    print("Seed complete: 1 admin, 4 staff, 4 students, 7 realistic complaints.")
    print(f"Development password for all seeded users: {PASSWORD}")


if __name__ == "__main__": main()
