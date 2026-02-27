# backend/services/doctor_match_service.py

from math import radians, cos, sin, asin, sqrt
from typing import Optional, Dict, Any, List

from backend.core.database import doctors_table


# -------------------------------------------------
# Specialization Mapping
# -------------------------------------------------

SPECIALIZATION_MAP = {
    "pre-eclampsia": "Gynaecologist",
    "eclampsia": "Gynaecologist",
    "pregnancy": "Gynaecologist",
    "anemia": "General Physician",
    "dengue": "General Physician",
    "malaria": "General Physician",
    "child": "Paediatrician",
}


# -------------------------------------------------
# Haversine Distance Formula
# -------------------------------------------------

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two lat/lng points in KM.
    """
    # convert to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6371 * c
    return km


# -------------------------------------------------
# Determine Required Specialization
# -------------------------------------------------

def get_required_specialization(
    primary_diagnosis: str,
    patient_age: int
) -> str:

    diagnosis = primary_diagnosis.lower()

    # Age-based rule
    if patient_age < 12:
        return "Paediatrician"

    for keyword, specialization in SPECIALIZATION_MAP.items():
        if keyword in diagnosis:
            return specialization

    return "General Physician"


# -------------------------------------------------
# Fetch Available Doctors
# -------------------------------------------------

def get_available_doctors() -> List[Dict[str, Any]]:

    response = doctors_table.scan()

    doctors = response.get("Items", [])

    # Filter only available doctors
    return [doc for doc in doctors if doc.get("IsAvailable") is True]


# -------------------------------------------------
# Main Matching Function
# -------------------------------------------------

def match_doctor(
    primary_diagnosis: str,
    patient_age: int,
    asha_lat: float,
    asha_lng: float
) -> Optional[Dict[str, Any]]:

    required_spec = get_required_specialization(
        primary_diagnosis,
        patient_age
    )

    available_doctors = get_available_doctors()

    if not available_doctors:
        return None

    # Filter by specialization first
    specialists = [
        doc for doc in available_doctors
        if doc.get("Specialization") == required_spec
    ]

    pool = specialists if specialists else available_doctors

    # Sort by distance
    for doc in pool:
        doc["DistanceKm"] = haversine(
            asha_lat,
            asha_lng,
            doc["Lat"],
            doc["Lng"]
        )

    pool.sort(key=lambda x: x["DistanceKm"])

    return pool[0] if pool else None