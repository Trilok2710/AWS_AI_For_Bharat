# backend/models/case.py

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


# -------------------------------------------------
# Request: Diagnosis Input
# -------------------------------------------------

class CaseDiagnoseRequest(BaseModel):
    PatientID: str
    ASHAWorkerID: str
    SymptomsRaw: str = Field(..., example="sir dard bahut tej hai, haath pair sujan")
    Language: str = Field(..., example="hi-IN")  # hi-IN / en-IN


# -------------------------------------------------
# Bedrock Diagnosis Output Structure
# -------------------------------------------------

class DiagnosisAIOutput(BaseModel):
    symptoms_english: str
    primary_diagnosis: str
    differential_diagnoses: List[str]
    confidence_percent: int
    risk_level: str  # EMERGENCY / URGENT / ROUTINE
    risk_reason: str
    immediate_actions: List[str]
    icmr_protocol: str
    icd10_code: str
    icd10_description: str
    auto_tag_conditions: List[str]


# -------------------------------------------------
# Stored Case Model (DB Representation)
# -------------------------------------------------

class CaseDB(BaseModel):
    CaseID: str
    PatientID: str
    ASHAWorkerID: str
    DoctorID: Optional[str] = None

    SymptomsRaw: str
    SymptomsEnglish: str
    Language: str

    PrimaryDiagnosis: str
    DifferentialDiagnoses: List[str]
    ConfidencePercent: int
    RiskLevel: str
    RiskReason: str
    ImmediateActions: List[str]
    ICMRProtocol: str
    ICD10Code: str
    ICD10Description: str

    Status: str  # PENDING / DOCTOR_ASSIGNED / COMPLETED / CLOSED
    CreatedAt: str
    UpdatedAt: str


# -------------------------------------------------
# API Response Model
# -------------------------------------------------

class CaseResponse(BaseModel):
    CaseID: str
    PrimaryDiagnosis: str
    ConfidencePercent: int
    RiskLevel: str
    RiskReason: str
    ImmediateActions: List[str]
    ICD10Code: str
    ICD10Description: str
    Status: str

    class Config:
        from_attributes = True