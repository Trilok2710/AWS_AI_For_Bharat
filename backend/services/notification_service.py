# backend/services/notification_service.py

from typing import Dict


def format_whatsapp_case_message(
    case: Dict,
    patient: Dict,
    doctor: Dict
) -> str:

    message = f"""
🏥 *MediConnect AI — Case Report*
Case ID: {case['CaseID']}

👤 *Patient:* {patient['Name']}, {patient['Age']}yr ({patient['Gender']})
📋 *Symptoms:* {case['SymptomsRaw']}

🔬 *AI Diagnosis:* {case['PrimaryDiagnosis']}
📊 *Confidence:* {case['ConfidencePercent']}%
🏷️ *ICD-10:* {case['ICD10Code']} — {case['ICD10Description']}

🚨 *Risk Level:* {case['RiskLevel']}
💡 _{case['RiskReason']}_

📌 *Immediate Actions:*
"""

    for i, action in enumerate(case["ImmediateActions"], 1):
        message += f"  {i}. {action}\n"

    message += f"""
📖 *Protocol:* {case['ICMRProtocol']}

👨‍⚕️ *Assigned Doctor:* {doctor['Name']}
🏥 Specialization: {doctor['Specialization']}
📍 Distance: {round(doctor.get('DistanceKm', 0), 2)} km

_Powered by MediConnect AI | AWS Bedrock_
"""

    return message.strip()