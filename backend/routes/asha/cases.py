# backend/routes/asha/cases.py

from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime

from boto3.dynamodb.conditions import Key

from backend.models.case import (
    CaseDiagnoseRequest,
    CaseResponse,
)
from backend.core.database import (
    cases_table,
    patients_table,
)
from backend.services.diagnosis_service import diagnose_case
from backend.services.doctor_match_service import match_doctor
from backend.services.notification_service import format_whatsapp_case_message


router = APIRouter(prefix="/cases", tags=["ASHA - Cases"])


# -------------------------------------------------
# Diagnose (Core AI Endpoint)
# -------------------------------------------------

@router.post("/diagnose", response_model=CaseResponse)
def diagnose(payload: CaseDiagnoseRequest):

    try:
        case_item = diagnose_case(payload)
        return case_item
    except Exception as e:
        print("DIAGNOSIS ERROR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "CaseID": case_item["CaseID"],
        "PrimaryDiagnosis": case_item["PrimaryDiagnosis"],
        "ConfidencePercent": case_item["ConfidencePercent"],
        "RiskLevel": case_item["RiskLevel"],
        "RiskReason": case_item["RiskReason"],
        "ImmediateActions": case_item["ImmediateActions"],
        "ICD10Code": case_item["ICD10Code"],
        "ICD10Description": case_item["ICD10Description"],
        "Status": case_item["Status"],
    }


# -------------------------------------------------
# Get Single Case
# -------------------------------------------------

@router.get("/{case_id}")
def get_case(case_id: str):

    response = cases_table.get_item(Key={"CaseID": case_id})
    item = response.get("Item")

    if not item:
        raise HTTPException(status_code=404, detail="Case not found")

    return item


# -------------------------------------------------
# Get All Cases for a Patient
# -------------------------------------------------

@router.get("/patient/{patient_id}", response_model=List[CaseResponse])
def get_cases_for_patient(patient_id: str):

    response = cases_table.query(
        IndexName="PatientID-index",
        KeyConditionExpression=Key("PatientID").eq(patient_id)
    )

    items = response.get("Items", [])

    return [
        {
            "CaseID": item["CaseID"],
            "PrimaryDiagnosis": item["PrimaryDiagnosis"],
            "ConfidencePercent": item["ConfidencePercent"],
            "RiskLevel": item["RiskLevel"],
            "RiskReason": item["RiskReason"],
            "ImmediateActions": item["ImmediateActions"],
            "ICD10Code": item["ICD10Code"],
            "ICD10Description": item["ICD10Description"],
            "Status": item["Status"],
        }
        for item in items
    ]


# -------------------------------------------------
# Connect Doctor
# -------------------------------------------------

@router.post("/{case_id}/connect-doctor")
def connect_doctor(case_id: str):

    # 1️⃣ Fetch Case
    case_response = cases_table.get_item(Key={"CaseID": case_id})
    case_item = case_response.get("Item")

    if not case_item:
        raise HTTPException(status_code=404, detail="Case not found")

    if case_item["Status"] != "PENDING":
        raise HTTPException(
            status_code=400,
            detail=f"Doctor already assigned. Current status: {case_item['Status']}"
        )

    # 2️⃣ Fetch Patient
    patient_response = patients_table.get_item(
        Key={"PatientID": case_item["PatientID"]}
    )
    patient = patient_response.get("Item")

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Demo ASHA coordinates (Bikram)
    asha_lat = 25.5921
    asha_lng = 85.1376

    # 3️⃣ Match Doctor
    matched_doctor = match_doctor(
        primary_diagnosis=case_item["PrimaryDiagnosis"],
        patient_age=patient["Age"],
        asha_lat=asha_lat,
        asha_lng=asha_lng
    )

    if not matched_doctor:
        raise HTTPException(status_code=404, detail="No available doctor found")

    # 4️⃣ Update Case with Doctor
    update_response = cases_table.update_item(
        Key={"CaseID": case_id},
        UpdateExpression="SET DoctorID = :d, #st = :s, UpdatedAt = :u",
        ExpressionAttributeValues={
            ":d": matched_doctor["DoctorID"],
            ":s": "DOCTOR_ASSIGNED",
            ":u": datetime.utcnow().isoformat(),
        },
        ExpressionAttributeNames={
            "#st": "Status"
        },
        ReturnValues="ALL_NEW",
    )

    updated_case = update_response.get("Attributes")

    # 5️⃣ Generate WhatsApp Preview (Mock)
    whatsapp_message = format_whatsapp_case_message(
        case=updated_case,
        patient=patient,
        doctor=matched_doctor
    )

    return {
        "message": "Doctor assigned successfully",
        "DoctorID": matched_doctor["DoctorID"],
        "DoctorName": matched_doctor["Name"],
        "Specialization": matched_doctor["Specialization"],
        "DistanceKm": round(matched_doctor["DistanceKm"], 2),
        "CaseStatus": updated_case["Status"],
        "whatsapp_preview": whatsapp_message,
    }