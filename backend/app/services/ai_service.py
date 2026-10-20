"""Transparent rule-based fallback. This is not a trained AI model."""
RULES = {
    "Flooding": ["flood", "flooding", "heavy rain", "water covering", "overflowing river"],
    "Water Leakage": ["leak", "leaking", "pipe burst", "pipe damage", "water wastage"],
    "Waterlogging": ["waterlogging", "standing water", "water accumulated", "puddle", "road covered with water"],
    "Blocked Drainage": ["blocked drain", "drain blocked", "drainage", "sewage", "clogged"],
    "Potholes": ["pothole", "hole in road", "road crater"],
    "Road Damage": ["road damage", "broken road", "cracked road", "road collapsed", "road surface"],
    "Streetlight Failure": ["streetlight", "street light", "lamp not working", "dark street", "light pole"],
    "Landslide Risk": ["landslide", "slope failure", "rockfall", "soil sliding", "hill collapse"],
}
DEPARTMENTS = {
    "Flooding": "Disaster Management", "Waterlogging": "Drainage and Sanitation", "Water Leakage": "Water Supply",
    "Blocked Drainage": "Drainage and Sanitation", "Potholes": "Roads and Transport", "Road Damage": "Roads and Transport",
    "Streetlight Failure": "Street Lighting", "Landslide Risk": "Disaster Management",
}

def analyze(title: str, description: str, selected_category: str):
    text = f"{title} {description}".lower()
    suggestion = selected_category
    for category, terms in RULES.items():
        if any(term in text for term in terms):
            suggestion = category
            break
    high_terms = ["trapped", "building", "collapsed", "landslide", "injured", "major road obstruction", "severe flooding", "school evacuation"]
    medium_terms = ["overflow", "main road", "traffic", "large", "burst", "spreading across the road"]
    if any(term in text for term in high_terms):
        severity, explanation = "High", "Urgent-sounding hazard keywords were found; human review is required."
    elif any(term in text for term in medium_terms):
        severity, explanation = "Medium", "The description mentions a potentially disruptive issue; verify impact on site."
    else:
        severity, explanation = "Low", "No configured high-urgency terms were detected; this is not a safety determination."
    summary = (description.strip().split("\n")[0][:220]).strip()
    if len(description) > 220: summary = summary.rstrip(" .,;:") + "…"
    return {"suggested_category": suggestion, "severity": severity, "explanation": explanation,
            "summary": summary, "department": DEPARTMENTS.get(suggestion, "General Municipal Services"),
            "method": "rule-based fallback (not a trained AI model)"}
