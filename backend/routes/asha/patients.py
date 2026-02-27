# backend/routes/asha/patients.py

from fastapi import APIRouter, HTTPException, Query
from typing import List
from datetime import datetime

from backend.models.patient import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
)
from backend.core.database import (
    patients_table,
    generate_uuid,
)

from boto3.dynamodb.conditions import Key, Attr


router = APIRouter(prefix="/patients", tags=["ASHA - Patients"])


# -------------------------------------------------
# Register New Patient
# -------------------------------------------------

@router.post("/register", response_model=PatientResponse)
def register_patient(payload: PatientCreate):
    patient_id = generate_uuid("PAT")

    item = {
        "PatientID": patient_id,
        "ASHAWorkerID": payload.ASHAWorkerID,
        "Name": payload.Name,
        "Age": payload.Age,
        "Gender": payload.Gender,
        "Village": payload.Village,
        "Block": payload.Block,
        "District": payload.District,
        "Phone": payload.Phone,
        "ABHA_ID": payload.ABHA_ID,
        "BloodGroup": payload.BloodGroup,
        "KnownConditions": payload.KnownConditions or [],
        "KnownAllergies": payload.KnownAllergies or [],
        "CurrentMedications": payload.CurrentMedications or [],
        "RegisteredDate": datetime.utcnow().isoformat(),
        "LastVisitDate": None,
    }

    patients_table.put_item(Item=item)

    return item


# -------------------------------------------------
# Get All Patients for ASHA
# -------------------------------------------------

@router.get("/{asha_id}", response_model=List[PatientResponse])
def get_patients_for_asha(asha_id: str):
    response = patients_table.query(
        IndexName="ASHAWorkerID-index",
        KeyConditionExpression=Key("ASHAWorkerID").eq(asha_id)
    )

    return response.get("Items", [])


# -------------------------------------------------
# Get Single Patient Profile
# -------------------------------------------------

@router.get("/profile/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: str):
    response = patients_table.get_item(Key={"PatientID": patient_id})
    item = response.get("Item")

    if not item:
        raise HTTPException(status_code=404, detail="Patient not found")

    return item


# -------------------------------------------------
# Search Patients (Name or Village)
# -------------------------------------------------

@router.get("/search")
def search_patients(
    asha_id: str = Query(...),
    q: str = Query(...)
):
    response = patients_table.query(
        IndexName="ASHAWorkerID-index",
        KeyConditionExpression=Key("ASHAWorkerID").eq(asha_id),
        FilterExpression=Attr("Name").contains(q) | Attr("Village").contains(q)
    )

    return response.get("Items", [])


# -------------------------------------------------
# Update Patient
# -------------------------------------------------

@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(patient_id: str, payload: PatientUpdate):

    update_fields = {k: v for k, v in payload.dict().items() if v is not None}

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    update_expression = "SET " + ", ".join(
        f"{key} = :{key}" for key in update_fields.keys()
    )

    expression_values = {
        f":{key}": value for key, value in update_fields.items()
    }

    response = patients_table.update_item(
        Key={"PatientID": patient_id},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_values,
        ReturnValues="ALL_NEW",
    )

    return response.get("Attributes")