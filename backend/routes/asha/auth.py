# backend/routes/asha/auth.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


router = APIRouter(prefix="/asha", tags=["ASHA - Auth"])


# -------------------------------------------------
# Demo ASHA Profile (Hardcoded for Hackathon)
# -------------------------------------------------

DEMO_ASHA = {
    "ASHAWorkerID": "ASHA-001",
    "Name": "Amita Devi",
    "Block": "Bikram",
    "District": "Patna",
    "Phone": "+919876543210",
    "Lat": 25.5921,
    "Lng": 85.1376,
    "PIN": "1234"   # Demo PIN
}


# -------------------------------------------------
# Request Model
# -------------------------------------------------

class LoginRequest(BaseModel):
    phone: str
    pin: str


# -------------------------------------------------
# Login Endpoint
# -------------------------------------------------

@router.post("/login")
def login(payload: LoginRequest):

    if payload.phone != DEMO_ASHA["Phone"]:
        raise HTTPException(status_code=401, detail="Invalid phone number")

    if payload.pin != DEMO_ASHA["PIN"]:
        raise HTTPException(status_code=401, detail="Invalid PIN")

    return {
        "message": "Login successful",
        "asha": {
            "ASHAWorkerID": DEMO_ASHA["ASHAWorkerID"],
            "Name": DEMO_ASHA["Name"],
            "Block": DEMO_ASHA["Block"],
            "District": DEMO_ASHA["District"],
            "Phone": DEMO_ASHA["Phone"],
        }
    }


# -------------------------------------------------
# Get ASHA Profile
# -------------------------------------------------

@router.get("/{asha_id}/profile")
def get_profile(asha_id: str):

    if asha_id != DEMO_ASHA["ASHAWorkerID"]:
        raise HTTPException(status_code=404, detail="ASHA not found")

    return {
        "ASHAWorkerID": DEMO_ASHA["ASHAWorkerID"],
        "Name": DEMO_ASHA["Name"],
        "Block": DEMO_ASHA["Block"],
        "District": DEMO_ASHA["District"],
        "Phone": DEMO_ASHA["Phone"],
        "Lat": DEMO_ASHA["Lat"],
        "Lng": DEMO_ASHA["Lng"],
    }