# backend/services/diagnosis_service.py

import json
from datetime import datetime
from typing import Dict, Any

import boto3
from botocore.exceptions import ClientError

from backend.config import settings
from backend.core.database import (
    cases_table,
    patients_table,
    generate_uuid,
)
from backend.models.case import DiagnosisAIOutput


# --------------------------------------------
# Initialize Bedrock Client
# --------------------------------------------

bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name=settings.AWS_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)


# --------------------------------------------
# Emergency Keyword Failsafe
# --------------------------------------------

EMERGENCY_KEYWORDS = [
    "pre-eclampsia", "eclampsia", "convulsion", "seizure",
    "heavy bleeding", "hemorrhage", "unconscious", "not breathing",
    "behoshi", "zyada khoon", "dauraa",
    "chest pain", "no pulse", "heart attack", "stroke"
]


def emergency_override(text: str) -> bool:
    text = text.lower()
    return any(keyword in text for keyword in EMERGENCY_KEYWORDS)


# --------------------------------------------
# Bedrock Diagnosis Call
# --------------------------------------------

def clean_model_output(text: str) -> str:
    """
    Extract first complete JSON object using brace counting.
    """

    text = text.replace("```json", "").replace("```", "")

    start = text.find("{")
    if start == -1:
        raise Exception("No JSON object found")

    brace_count = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            brace_count += 1
        elif text[i] == "}":
            brace_count -= 1
            if brace_count == 0:
                return text[start:i+1]

    raise Exception("Incomplete JSON object")


def call_bedrock(prompt: str):

    body = {
        "prompt": prompt,
        "max_gen_len": 800,
        "temperature": 0.0,
        "top_p": 0.9
    }

    response = bedrock.invoke_model(
        modelId=settings.BEDROCK_MODEL_ID,
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json",
    )

    response_body = json.loads(response["body"].read())

    output_text = response_body.get("generation", "")

    if not output_text:
        raise Exception("Empty response from model")

    cleaned_json = clean_model_output(output_text)

    return json.loads(cleaned_json)

# --------------------------------------------
# Main Diagnosis Function
# --------------------------------------------

def diagnose_case(payload):

    # Fetch Patient
    patient_response = patients_table.get_item(
        Key={"PatientID": payload.PatientID}
    )
    patient = patient_response.get("Item")

    if not patient:
        raise Exception("Patient not found")

    # Build Prompt
    system_prompt = """
    You are MediConnect AI, an expert rural diagnosis assistant.

    Return ONLY valid JSON.
    Do NOT use markdown.
    Do NOT use code blocks.
    Do NOT include explanations.
    Do NOT include references.
    Do NOT include disclaimers.
    Output must begin with { and end with }.
    No text before or after the JSON.
    """

    user_prompt = f"""
Patient: {patient['Name']}, {patient['Age']}yr, {patient['Gender']}
Known conditions: {patient.get('KnownConditions', [])}
Known allergies: {patient.get('KnownAllergies', [])}
Current symptoms: "{payload.SymptomsRaw}"
Language: {payload.Language}

Return STRICT JSON in this exact structure:

{{
  "symptoms_english": "translated symptoms",
  "primary_diagnosis": "string",
  "differential_diagnoses": ["string"],
  "confidence_percent": 0,
  "risk_level": "EMERGENCY | URGENT | ROUTINE",
  "risk_reason": "string",
  "immediate_actions": ["string"],
  "icmr_protocol": "string",
  "icd10_code": "string",
  "icd10_description": "string",
  "auto_tag_conditions": ["string"]
}}
"""

    full_prompt = system_prompt + "\n" + user_prompt

    # Call Bedrock
    ai_output_raw = call_bedrock(full_prompt)

    # Validate against schema
    ai_output = DiagnosisAIOutput(**ai_output_raw)

    # Emergency Override
    if emergency_override(payload.SymptomsRaw):
        ai_output.risk_level = "EMERGENCY"
        ai_output.risk_reason = "Detected high-risk emergency keywords in symptoms"

    # Create Case ID
    case_id = generate_uuid("CASE")

    case_item = {
        "CaseID": case_id,
        "PatientID": payload.PatientID,
        "ASHAWorkerID": payload.ASHAWorkerID,
        "DoctorID": None,

        "SymptomsRaw": payload.SymptomsRaw,
        "SymptomsEnglish": ai_output.symptoms_english,
        "Language": payload.Language,

        "PrimaryDiagnosis": ai_output.primary_diagnosis,
        "DifferentialDiagnoses": ai_output.differential_diagnoses,
        "ConfidencePercent": ai_output.confidence_percent,
        "RiskLevel": ai_output.risk_level,
        "RiskReason": ai_output.risk_reason,
        "ImmediateActions": ai_output.immediate_actions,
        "ICMRProtocol": ai_output.icmr_protocol,
        "ICD10Code": ai_output.icd10_code,
        "ICD10Description": ai_output.icd10_description,

        "Status": "PENDING",
        "CreatedAt": datetime.utcnow().isoformat(),
        "UpdatedAt": datetime.utcnow().isoformat(),
    }

    # Store Case
    cases_table.put_item(Item=case_item)

    # Auto-tag patient conditions
    if ai_output.auto_tag_conditions:
        updated_conditions = list(set(
            patient.get("KnownConditions", []) +
            ai_output.auto_tag_conditions
        ))

        patients_table.update_item(
            Key={"PatientID": payload.PatientID},
            UpdateExpression="SET KnownConditions = :kc",
            ExpressionAttributeValues={":kc": updated_conditions}
        )

    return case_item