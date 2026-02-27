# MediConnect AI — Master Overview
## AWS AI for Bharat Hackathon | Team AamRas

Paste this at the start of EVERY module chat so Claude understands the full system.

---

## WHAT WE'RE BUILDING

MediConnect AI connects 1M+ ASHA (rural health workers) to 1.3M+ doctors across India using voice-first AI diagnosis, real-time telemedicine, and automated clinical documentation.

**Hackathon:** AWS AI for Bharat | **Team:** Team AamRas | **Deadline:** 4th March

---

## THREE MODULES

| Module | Users | Interface | Status |
|--------|-------|-----------|--------|
| MODULE 1 — ASHA App | ASHA workers in villages | React PWA, mobile | See MODULE_1_ASHA.md |
| MODULE 2 — Doctor Dashboard | PHC/CHC doctors | React web, desktop | See MODULE_2_DOCTOR.md |
| MODULE 3 — District Dashboard | District Health Officer | React web, desktop | See MODULE_3_DISTRICT.md |

---

## SHARED INFRASTRUCTURE

### Backend: Single FastAPI app
- `main.py` — app entry, CORS, startup seeding
- `routes/asha.py` — patient + diagnosis endpoints
- `routes/doctor.py` — case review + SOAP + prescription
- `routes/district.py` — aggregation + prediction endpoints
- `services/diagnosis.py` — AWS Bedrock Nova Pro
- `services/store.py` — DynamoDB operations
- `services/notification.py` — WhatsApp formatting

### AWS Services Used:
| Service | Purpose |
|---------|---------|
| Amazon Bedrock (Nova Pro) | Diagnosis + SOAP notes + ICD-10 + Outbreak prediction |
| AWS Transcribe Medical | Voice-to-text (consultation) |
| AWS DynamoDB | All data storage |
| AWS API Gateway WebSockets | Real-time ASHA→Doctor push |
| AWS Lambda | Serverless backend deployment |
| AWS S3 | Audio file storage |

### DynamoDB Tables:
```
mediconnect-patients   — Patient profiles (ASHA module creates)
mediconnect-cases      — All diagnoses (shared across all modules)
mediconnect-doctors    — Doctor profiles (Doctor module reads)
```

### Environment Variables (all modules share):
```bash
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
AWS_REGION=us-east-1
DYNAMODB_PATIENTS_TABLE=mediconnect-patients
DYNAMODB_CASES_TABLE=mediconnect-cases
DYNAMODB_DOCTORS_TABLE=mediconnect-doctors
WEBSOCKET_URL=wss://xxx.execute-api.us-east-1.amazonaws.com/prod
BEDROCK_MODEL_ID=amazon.nova-pro-v1:0
MOCK_WHATSAPP=true
MOCK_TRANSCRIBE=true
```

---

## DEMO SCENARIO (memorise this)

The demo tells ONE connected story across all three modules:

1. **ASHA module:** Amita (ASHA worker) opens app in Bikram village. Selects patient Priya Devi (28F, known pregnancy + hypertension). Records Hindi symptoms via mic. Bedrock diagnoses **Pre-eclampsia — EMERGENCY**. Amita taps "Connect to Doctor."

2. **Doctor module:** Dr. Patel's dashboard shows new EMERGENCY case arrive in real-time (WebSocket). She reviews AI case summary, joins simulated video call. Consultation transcript builds up. After call, Bedrock generates SOAP notes + ICD-10 + prescription in 28 seconds. She approves. E-prescription sent to Amita's WhatsApp.

3. **District module:** Health Officer opens dashboard. Sees red heatmap hotspot over Bikram block. Alert: "Dengue 4x above baseline." Bedrock predicts outbreak in 5 days. Officer sees recommended interventions.

**This whole story should be demonstrable in a 3-minute video.**

---

## WHAT'S MOCKED (do not build for real)

- WhatsApp message sending — show formatted message on screen only
- Video call — simulated clip playing in a video element
- Offline TinyBERT — mention in architecture diagram only
- PDF export — show success toast only
- 108 ambulance — just `<a href="tel:108">`
- Actual Twilio delivery — mock in code, show message preview

## WHAT MUST BE REAL

- AWS Bedrock Nova Pro API calls (diagnosis, SOAP, prediction)
- DynamoDB reads and writes
- WebSocket real-time push (ASHA → Doctor)
- Voice input via Web Speech API
- Leaflet.js heatmap with real seeded data
- Recharts trend charts with aggregated data

---

## BUILD ORDER ACROSS MODULES

**Day 1-2:** Module 1 backend (FastAPI + DynamoDB + Bedrock diagnosis)
**Day 2-3:** Module 1 frontend (React PWA — 7 screens)
**Day 3-4:** Module 2 backend (SOAP generation + WebSocket)
**Day 4:** Module 2 frontend (Doctor dashboard — 5 screens)
**Day 5:** Module 3 (backend aggregation + Bedrock prediction + frontend)
**Day 6:** Data seeding + integration testing + demo rehearsal
**Day 7:** Record video + submit
