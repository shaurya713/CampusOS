from dataclasses import dataclass
import re
@dataclass
class Classification:
    category:str;subcategory:str;department:str;priority:str;urgency_score:int;confidence:float;reason:str;suggested_staff_type:str;provider_used:str="rule_based";model_name:str|None=None;ai_status:str="fallback";processing_time:float|None=None
RULES=[(r"wire|shock|sparks?|fire|exposed","Electrical","Electrical Hazard","CRITICAL",10,"Electrician"),(r"gas leak|chemical spill|toxic","Safety","Safety Hazard","CRITICAL",10,"Safety Specialist"),(r"water|leak|tap|drain|toilet|sewage","Plumbing","Water & Drainage","HIGH",8,"Plumber"),(r"fan|light|power|socket|switch","Electrical","Power & Lighting","HIGH",7,"Electrician"),(r"wifi|internet|network|computer|laptop","IT Support","Network & Devices","HIGH",7,"IT Support Specialist"),(r"projector|hdmi|speaker|microphone","IT Support","AV Equipment","MEDIUM",6,"AV Technician"),(r"security|gate|theft|access card","Security","Security & Access","HIGH",8,"Security Supervisor"),(r"clean|garbage|waste|washroom","Cleaning","Housekeeping","MEDIUM",5,"Cleaning Team"),(r"ac|air conditioner|cooling","HVAC","Cooling & Ventilation","MEDIUM",6,"HVAC Technician")]
def classify(text:str)->Classification:
    for pattern,cat,sub,priority,score,staff in RULES:
        if re.search(pattern,text.lower()):return Classification(cat,sub,cat,priority,score,.82,f"Matched {sub.lower()} indicators.",staff)
    return Classification("General Administration","General","General Administration","MEDIUM",4,.45,"Manual review recommended.","Campus Services")
