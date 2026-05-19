"""Static precautions, treatments, and severity hints per disease label."""

DISEASE_INFO = {
    "mastitis": {
        "precautions": [
            "Isolate affected quarters; milk gently after hot compress",
            "Strict milking hygiene; discard abnormal milk",
            "Disinfect equipment between animals",
        ],
        "treatment": "Veterinary antibiotics and anti-inflammatory therapy as prescribed; culture-based plan.",
        "severity_default": "Medium",
        "vet_recommendation": "Schedule farm visit for milk culture and mastitis protocol.",
    },
    "foot_and_mouth": {
        "precautions": [
            "Isolate infected animal immediately",
            "Restrict farm movement; notify authorities if legally required",
            "Disinfect boots, vehicles, and tools",
        ],
        "treatment": "Supportive care; vaccination policy for herd; follow national FMD guidelines.",
        "severity_default": "High",
        "vet_recommendation": "Book veterinary appointment immediately; report suspected FMD.",
    },
    "black_quarter": {
        "precautions": ["Avoid grazing in known outbreak areas", "Vaccinate herd where advised"],
        "treatment": "Urgent veterinary care; antibiotics and surgical debridement if indicated.",
        "severity_default": "High",
        "vet_recommendation": "Emergency veterinary assessment.",
    },
    "milk_fever": {
        "precautions": ["Monitor peri-calving cows", "Ensure calcium supplementation per vet plan"],
        "treatment": "IV calcium under veterinary supervision; oral follow-up.",
        "severity_default": "Medium",
        "vet_recommendation": "Contact veterinarian for calcium therapy.",
    },
    "rabies": {
        "precautions": [
            "Do not handle saliva; use PPE",
            "Isolate animal; human exposure requires public health guidance",
        ],
        "treatment": "No cure once clinical; humane options per law; vaccination prevention for others.",
        "severity_default": "Critical",
        "vet_recommendation": "Immediate veterinary and public health notification.",
    },
    "distemper": {
        "precautions": ["Isolate from other dogs", "Disinfect environment"],
        "treatment": "Supportive care; antivirals limited; prevent secondary infection.",
        "severity_default": "High",
        "vet_recommendation": "Book clinic visit for diagnostics and supportive protocol.",
    },
    "skin_allergy": {
        "precautions": ["Avoid known allergens", "Use vet-approved shampoos"],
        "treatment": "Antihistamines, fatty acids, or prescribed immunotherapy.",
        "severity_default": "Low",
        "vet_recommendation": "Dermatology consult if chronic.",
    },
    "parvovirus": {
        "precautions": ["Strict isolation", "Disinfect with appropriate virucidal agents"],
        "treatment": "Aggressive fluid therapy and antiemetics in hospital setting.",
        "severity_default": "High",
        "vet_recommendation": "Emergency veterinary hospitalization.",
    },
    "bird_flu": {
        "precautions": ["Lock-down flock", "Report suspicion to authorities", "Biosecurity barrier"],
        "treatment": "Policy-driven depopulation or controlled treatment per jurisdiction.",
        "severity_default": "Critical",
        "vet_recommendation": "Immediate state vet / poultry specialist contact.",
    },
    "newcastle": {
        "precautions": ["Vaccination program", "Quarantine new birds"],
        "treatment": "Supportive care; vaccination of contacts; veterinary flock plan.",
        "severity_default": "High",
        "vet_recommendation": "Poultry veterinarian visit for flock assessment.",
    },
    "fowl_pox": {
        "precautions": ["Mosquito control", "Separate infected birds"],
        "treatment": "Supportive care; secondary infection control.",
        "severity_default": "Medium",
        "vet_recommendation": "Schedule vet visit for lesion assessment.",
    },
    "feline_flu": {
        "precautions": ["Isolate from other cats", "Humidify air; nutrition support"],
        "treatment": "Antibiotics for secondary bacterial; antivirals if indicated.",
        "severity_default": "Medium",
        "vet_recommendation": "Clinic visit if breathing difficulty or anorexia.",
    },
    "ringworm": {
        "precautions": ["Environmental cleaning", "Human hygiene—zoonotic risk"],
        "treatment": "Topical/systemic antifungals per vet.",
        "severity_default": "Low",
        "vet_recommendation": "Book appointment for fungal culture if persistent.",
    },
    "goat_pneumonia": {
        "precautions": ["Ventilation", "Reduce crowding and dust"],
        "treatment": "Antibiotics and NSAIDs as prescribed.",
        "severity_default": "Medium",
        "vet_recommendation": "Farm visit for auscultation and treatment plan.",
    },
    "foot_rot": {
        "precautions": ["Dry footing", "Hoof trimming hygiene"],
        "treatment": "Hoof soak/trim; antibiotics for deep infection.",
        "severity_default": "Medium",
        "vet_recommendation": "Schedule hoof care and veterinary antibiotics if lame.",
    },
    "healthy": {
        "precautions": ["Maintain vaccination and deworming schedule", "Balanced nutrition and clean water"],
        "treatment": "No specific treatment; continue wellness monitoring.",
        "severity_default": "None",
        "vet_recommendation": "Routine annual wellness check.",
    },
    "unknown": {
        "precautions": ["Monitor closely", "Isolate if contagious signs suspected"],
        "treatment": "Further diagnostics required (blood work, imaging, lab tests).",
        "severity_default": "Unknown",
        "vet_recommendation": "Book veterinary appointment for examination.",
    },
}


def normalize_key(name: str) -> str:
    return name.lower().replace(" ", "_").replace("-", "_")


def lookup_disease(disease_name: str) -> dict:
    key = normalize_key(disease_name)
    for k, v in DISEASE_INFO.items():
        if k == key or key in k or k in key:
            return v
    return DISEASE_INFO["unknown"]
