# backend/models/patient.py

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# -------------------------------------------------
# Base Schema (Shared Fields)
# -------------------------------------------------

class PatientBase(BaseModel):
    Name: str = Field(..., example="Priya Devi")
    Age: int = Field(..., ge=0, le=120, example=28)
    Gender: str = Field(..., example="F")  # M / F / Other
    Village: str = Field(..., example="Bikram")
    Block: Optional[str] = Field(default="Bikram")
    District: Optional[str] = Field(default="Patna")
    Phone: Optional[str] = Field(None, example="+919876543210")
    ABHA_ID: Optional[str] = None
    BloodGroup: Optional[str] = None
    KnownConditions: Optional[List[str]] = []
    KnownAllergies: Optional[List[str]] = []
    CurrentMedications: Optional[List[str]] = []


# -------------------------------------------------
# Request: Register Patient
# -------------------------------------------------

class PatientCreate(PatientBase):
    ASHAWorkerID: str = Field(..., example="ASHA-001")


# -------------------------------------------------
# Request: Update Patient
# -------------------------------------------------

class PatientUpdate(BaseModel):
    KnownConditions: Optional[List[str]] = None
    KnownAllergies: Optional[List[str]] = None
    CurrentMedications: Optional[List[str]] = None
    Phone: Optional[str] = None
    BloodGroup: Optional[str] = None


# -------------------------------------------------
# Response Model
# -------------------------------------------------

class PatientResponse(PatientBase):
    PatientID: str
    ASHAWorkerID: str
    RegisteredDate: str
    LastVisitDate: Optional[str] = None

    class Config:
        from_attributes = True


# -------------------------------------------------
# Internal DB Model
# -------------------------------------------------

class PatientDB(PatientBase):
    PatientID: str
    ASHAWorkerID: str
    RegisteredDate: str
    LastVisitDate: Optional[str] = None