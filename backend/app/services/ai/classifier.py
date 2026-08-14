from dataclasses import dataclass
import re

@dataclass
class Classification:
    category: str; subcategory: str; department: str; priority: str; urgency_score: int; confidence: float; reason: str; suggested_staff_type: str; provider_used: str="rule_based"; model_name: str|None=None; ai_status: str="fallback"; processing_time: float|None=None

RULES=[
 (r"wire|shock|sparks?|fire|exposed", "Electrical", "Electrical Safety", "CRITICAL", 10, "Electrician"),
 (r"leak|tap|drain|water|plumb", "Plumbing", "Water Leakage", "HIGH", 8, "Plumber"),
 (r"electric|power|fan|light", "Electrical", "Power / Lighting", "HIGH", 7, "Electrician"),
 (r"wifi|internet|computer|projector", "IT Support", "IT Equipment", "MEDIUM", 5, "IT Technician"),
 (r"security|gate|theft", "Security", "Security Concern", "CRITICAL", 9, "Security Officer"),
 (r"clean|garbage|waste", "Cleaning", "Cleaning", "MEDIUM", 4, "Cleaning Staff"),
]
def classify(text: str) -> Classification:
    lowered=text.lower()
    for pattern,category,subcategory,priority,score,staff in RULES:
        if re.search(pattern,lowered):
            return Classification(category,subcategory,category,priority,score,.78,f"Detected {subcategory.lower()} keywords.",staff)
    return Classification("General Administration","General","General Administration","MEDIUM",4,.40,"No specific rule matched; review recommended.","General Staff")
