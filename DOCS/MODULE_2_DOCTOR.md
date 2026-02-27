# MediConnect AI — MODULE 2: Doctor Dashboard
## Build Spec for AWS AI for Bharat Hackathon | Team AamRas

---

## YOUR ROLE
You are an expert full-stack developer helping build the Doctor module of MediConnect AI — a healthcare platform connecting rural ASHA workers to doctors across India. Build exactly what is specified here. Ask before deviating.

---

## CONTEXT — HOW THIS MODULE FITS IN

The ASHA module (Module 1) handles patient registration and AI diagnosis. When an ASHA worker clicks "Connect to Doctor," a case is pushed to this Doctor Dashboard in real-time. The doctor reviews the AI-generated case summary, conducts a simulated video consultation, and AWS Bedrock auto-generates SOAP notes + prescription. Doctor sends e-prescription to ASHA via WhatsApp.

This module runs on **desktop/tablet** — doctors use laptops, not phones.

---

## WHO IS THE DOCTOR?

- MBBS General Physician or specialist at a PHC/CHC in rural Bihar
- Sees 40-80 patients per day, 40% of time lost to paperwork
- Already overwhelmed — this tool gives him time back
- Comfortable with English for clinical documentation
- Pain points: manual SOAP notes (15 min each), no pre-consultation context, disconnected from ASHA workers

---

## TECH STACK

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + Vite + Tailwind CSS (desktop-optimised) |
| Real-time | AWS API Gateway WebSockets (receive cases from ASHA) |
| AI — SOAP Notes | AWS Bedrock — Amazon Nova Pro |
| AI — ICD-10 Coding | AWS Bedrock — Amazon Nova Pro |
| Transcription | AWS Transcribe (standard, async) |
| Database | AWS DynamoDB (shared with ASHA module) |
| Video | Simulated (pre-recorded clip embedded in UI) |
| Backend | FastAPI (Python) — shared with ASHA module |
| Notifications | Twilio WhatsApp (mocked — show message on screen) |

---

## DYNAMODB TABLES (shared with ASHA module)

### Table: Patients (read-only from Doctor module)
```
PatientID (PK) | ASHAWorkerID | Name | Age | Gender | Village
KnownConditions | KnownAllergies | LastVisitDate
```

### Table: Cases
```
CaseID (PK) | PatientID | ASHAWorkerID | DoctorID
SymptomsRaw | SymptomsEnglish | PrimaryDiagnosis | RiskLevel
ImmediateActions | ICD10Code | Status | CreatedAt

Status values:
  PENDING          → case created, no doctor yet
  DOCTOR_ASSIGNED  → doctor matched, not yet in consultation
  IN_CONSULTATION  → video call active
  SOAP_GENERATED   → SOAP notes ready, pending approval
  COMPLETED        → prescription sent, case closed
```

### Table: Doctors
```
Partition Key: DoctorID (String)

Attributes:
  DoctorID          String  (PK)
  Name              String
  Specialization    String  (General Physician / Gynaecologist / Paediatrician)
  ClinicName        String
  Lat               Number
  Lng               Number
  IsAvailable       Boolean  (updated in real-time when doctor logs in/out)
  Phone             String
  Rating            Number   (4.8)
  CasesToday        Number   (incremented on each case)
  TotalCases        Number
```

### Pre-seed Demo Doctors:
```python
[
  {"DoctorID": "DR-001", "Name": "Dr. Priya Patel",
   "Specialization": "Gynaecologist", "ClinicName": "Bikram PHC",
   "Lat": 25.5941, "Lng": 85.1376, "IsAvailable": True,
   "Rating": 4.9, "CasesToday": 12},

  {"DoctorID": "DR-002", "Name": "Dr. Ramesh Sharma",
   "Specialization": "General Physician", "ClinicName": "Gopal Nagar CHC",
   "Lat": 25.6121, "Lng": 85.1534, "IsAvailable": True,
   "Rating": 4.7, "CasesToday": 8},

  {"DoctorID": "DR-003", "Name": "Dr. Anita Singh",
   "Specialization": "Paediatrician", "ClinicName": "Rural Central PHC",
   "Lat": 25.5712, "Lng": 85.1892, "IsAvailable": True,
   "Rating": 4.8, "CasesToday": 6},
]
```

---

## BACKEND API ENDPOINTS

### Base URL: `http://localhost:8000`

```
GET    /doctor/{doctor_id}/cases              All cases for this doctor
GET    /doctor/{doctor_id}/cases/pending       Pending cases (not yet seen)
GET    /doctor/{doctor_id}/stats              Today's stats (cases, time saved, income)
PUT    /doctor/{doctor_id}/availability       Toggle IsAvailable true/false

GET    /cases/{case_id}                       Full case details
PUT    /cases/{case_id}/status               Update case status
GET    /cases/{case_id}/patient              Patient profile for this case

POST   /consultation/start/{case_id}         Mark consultation started
POST   /consultation/end/{case_id}           End call, trigger Bedrock SOAP generation
         Body: { transcript: "..." }

GET    /soap/{case_id}                       Get generated SOAP notes
PUT    /soap/{case_id}                       Doctor edits SOAP notes
POST   /soap/{case_id}/approve              Approve and trigger prescription send

POST   /prescription/send/{case_id}         Send e-prescription via WhatsApp
         Body: { asha_phone: "...", patient_phone: "..." }

WebSocket: /ws/doctor/{doctor_id}           Receive real-time case notifications
```

---

## BEDROCK INTEGRATION — SOAP NOTES + ICD-10

### Model: `amazon.nova-pro-v1:0`

### SOAP Generation Prompt:
```python
system_prompt = """You are a clinical documentation AI for Indian doctors.
Generate professional SOAP notes following ABDM-compliant standards.
Use generic medicine names only (not brand names).
Respond ONLY with valid JSON."""

user_prompt = f"""
Generate SOAP notes for this consultation.

Patient: {name}, {age}yr, {gender}
Known Conditions: {known_conditions}
Known Allergies: {allergies}

ASHA's Field Report: "{symptoms_raw}"
AI Preliminary Diagnosis: {primary_diagnosis} (Confidence: {confidence}%)
Risk Level: {risk_level}

Doctor Consultation Transcript:
"{consultation_transcript}"

Respond with this exact JSON:
{{
  "subjective": "patient complaints in clinical language",
  "objective": "vital signs and observations from transcript",
  "assessment": "clinical assessment with confirmed diagnosis",
  "plan": "detailed treatment plan",
  "icd10_codes": ["{icd10_code}", "secondary if applicable"],
  "prescription": [
    {{"drug": "generic name", "dose": "500mg", "frequency": "TDS",
      "duration": "5 days", "notes": "after meals"}},
    {{"drug": "generic name 2", "dose": "...", "frequency": "...",
      "duration": "...", "notes": "..."}}
  ],
  "follow_up_days": 7,
  "referral_needed": false,
  "referral_reason": ""
}}
"""
```

### AWS Transcribe — Pre-processing Strategy for Demo:
Since AWS Transcribe standard takes 30-60 seconds, use this approach for demo:
1. Pre-record a 3-minute consultation audio clip
2. Upload to S3, run Transcribe job BEFORE the demo
3. Store the transcript result in DynamoDB against a demo case
4. When doctor clicks "End Consultation" → transcript loads from DynamoDB instantly
5. Then Bedrock generates SOAP in ~5 seconds — this is what judges see

For production: start chunked Transcribe jobs throughout the call so most is done by end.

```python
# Transcribe job setup
transcribe_client.start_transcription_job(
    TranscriptionJobName=f"mediconnect-{case_id}",
    Media={"MediaFileUri": f"s3://mediconnect-audio/{case_id}.webm"},
    MediaFormat="webm",
    LanguageCode="en-IN",
    OutputBucketName="mediconnect-transcripts",
    Settings={
        "ShowSpeakerLabels": True,
        "MaxSpeakerLabels": 2  # Doctor + Patient
    }
)
```

---

## REAL-TIME WEBSOCKET — RECEIVING CASES

When ASHA module sends "Connect to Doctor," this dashboard receives:

```javascript
// WebSocket message received
{
  "event": "NEW_CASE",
  "case_id": "CASE-ABC123",
  "patient_name": "Priya Devi",
  "patient_age": 28,
  "patient_gender": "F",
  "risk_level": "EMERGENCY",
  "primary_diagnosis": "Pre-eclampsia (Severe)",
  "confidence_percent": 89,
  "asha_name": "Amita Devi",
  "village": "Bikram",
  "distance_km": 4.2,
  "symptoms_english": "Severe headache, swollen hands and feet, 8 months pregnant",
  "immediate_actions": ["Call 108 ambulance", "Left lateral position"]
}
```

On receiving this:
1. Show notification banner/sound at top of dashboard
2. Add new case card to "Waiting Cases" list with pulsing animation
3. EMERGENCY cases go to TOP of list, highlighted in red

```javascript
// WebSocket connection setup
const ws = new WebSocket(`${WEBSOCKET_URL}?doctorId=${doctorId}`);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.event === 'NEW_CASE') {
    playNotificationSound();
    showNotificationBanner(data);
    addCaseToQueue(data);
  }
};
```

---

## SCREENS — 5 TOTAL

### Screen 1: Doctor Dashboard (Main)
```
┌──────────────────────────────────────────────────────────────────┐
│  🏥 MediConnect AI — Dr. Priya Patel          [🔴 Available ▼]  │
├──────────┬──────────┬──────────┬──────────────────────────────────┤
│ 12       │ 24 min   │ ₹6,200   │ 4.8/5                           │
│ Cases    │ Doc Time │ Income   │ Rating                          │
│ Today    │ (saved 8h)│ Today   │                                 │
├──────────┴──────────┴──────────┴──────────────────────────────────┤
│  🔴 WAITING CASES (2)          ← Live, WebSocket-driven          │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │ 🚨 EMERGENCY  Priya Devi, 28F              [JOIN CALL]   │    │
│  │    Pre-eclampsia • ASHA: Amita • Bikram • 4.2km • 0:45  │    │
│  │    AI Confidence: 89%                      [DEFER]       │    │
│  └──────────────────────────────────────────────────────────┘    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │ ⚠️ URGENT    Rajesh Kumar, 32M             [JOIN CALL]   │    │
│  │    Dengue • ASHA: Fatima • Gopal Nagar • 6.8km • 3:12   │    │
│  │    AI Confidence: 82%                      [DEFER]       │    │
│  └──────────────────────────────────────────────────────────┘    │
├──────────────────────────────────────────────────────────────────┤
│  ✅ COMPLETED TODAY (10)                                         │
│  [10:30] Asha Baby, 5F — Gastroenteritis — 3 min ✅             │
│  [10:45] Lokesh, 46M — Diabetes — 2 min ✅                      │
│  [11:00] Geeta, 34F — Asthma — 4 min ✅                         │
│                                              [View All...]       │
├──────────────────────────────────────────────────────────────────┤
│  [📊 Analytics]  [💰 Billing]  [⚙️ Settings]                    │
└──────────────────────────────────────────────────────────────────┘
```

**Stats calculation:**
- Cases Today: count of COMPLETED cases for this doctor today
- Doc Time: total minutes spent on consultations today
- "Saved 8h": (cases × 15min manual SOAP) - actual_doc_time = time saved
- Income Today: cases × average fee (configurable per doctor)

### Screen 2: Case Detail (Pre-Consultation Review)
```
┌──────────────────────────────────────────────────────────────────┐
│  ← Back        CASE SUMMARY — Priya Devi             🚨 EMERG   │
├──────────────────────────────────────────────────────────────────┤
│  👤 Patient                      📍 Location                    │
│  Priya Devi, 28yr, Female        Bikram Village, Patna           │
│  ASHA: Amita Devi                PHC: Bikram | 4.2km away       │
├──────────────────────────────────────────────────────────────────┤
│  ⚕️ Known Conditions                                             │
│  🏷 Pregnant — 8 months   🏷 Gestational Hypertension           │
├──────────────────────────────────────────────────────────────────┤
│  📋 ASHA's Report (verbatim)                                     │
│  "sir dard bahut tej hai, haath pair sujan hai, pregnant         │
│  hoon 8 mahine" — Translated: Severe headache, swollen          │
│  hands and feet, 8 months pregnant                               │
├──────────────────────────────────────────────────────────────────┤
│  🤖 AI Assessment (Bedrock)                                      │
│  Primary: Pre-eclampsia (Severe) — 89% confidence               │
│  Differential: Gestational HTN, HELLP Syndrome                  │
│  ICD-10: O14.1                                                   │
├──────────────────────────────────────────────────────────────────┤
│  📖 Previous Cases (2)                                           │
│  🟢 2 Jan — Anemia screening — Routine                          │
│  🟢 15 Dec — General checkup — Routine                          │
├──────────────────────────────────────────────────────────────────┤
│  💡 Suggested Questions (AI-generated)                           │
│  • When did the headache start? Severity 1-10?                  │
│  • Any visual disturbances (blurring, flashing)?                 │
│  • BP reading in last 24 hours?                                  │
│  • Any epigastric pain?                                          │
├──────────────────────────────────────────────────────────────────┤
│  [▶️ START CONSULTATION                                        ]  │
└──────────────────────────────────────────────────────────────────┘
```

**Suggested questions** are generated by a separate Bedrock call:
```python
f"Given diagnosis {primary_diagnosis} and patient history, 
suggest 4 specific questions the doctor should ask in the consultation. 
Return as JSON array of strings."
```

### Screen 3: Video Consultation
```
┌──────────────────────────────────────────────────────────────────┐
│  🔴 LIVE CONSULTATION    ⏱ 03:45          [⏹ STOP CALL]        │
├──────────────────────────┬───────────────────────────────────────┤
│                          │  📋 CASE SUMMARY                     │
│   [VIDEO FEED - LEFT]    │  Patient: Priya Devi, 28F            │
│                          │  Chief Complaint: Fever 3 days        │
│   Dr. Priya Patel        │  AI Diagnosis: Pre-eclampsia          │
│   (simulated video       │  Risk Level: 🚨 EMERGENCY            │
│    clip playing)         │  Actions Taken: Called 108            │
│                          │─────────────────────────────────────  │
│   [ASHA VIDEO - BOTTOM]  │  📝 Transcription (Live):            │
│   (static placeholder)   │                                       │
│                          │  "Doctor, patient reports high        │
│                          │   blood pressure and swelling         │
│   [Patient Photo]        │   in hands and feet. She is          │
│                          │   8 months pregnant..."               │
│                          │                                       │
│                          │  (text appends as Transcribe          │
│                          │   returns chunks)                     │
├──────────────────────────┴───────────────────────────────────────┤
│  [👁 Show ASHA]  [🖥 Share Screen]  [🔊 Volume ──────]  [⏹ End] │
└──────────────────────────────────────────────────────────────────┘
```

**Simulated video approach:**
- Left panel: `<video>` element playing a looping .mp4 clip of someone at a desk
- Add `LIVE ●` badge with CSS pulsing animation
- Timer counts up from 00:00
- Right panel: transcript builds up — either from pre-processed Transcribe result or simulated typing effect

**Transcript display for demo:**
```javascript
// For demo: show pre-written transcript with typewriter effect
const DEMO_TRANSCRIPT = `Doctor, patient reports high blood pressure and swelling in hands and feet. She is 8 months pregnant and has been experiencing severe headaches for the past 3 days. Blood pressure reading this morning was 160/110. This is her first pregnancy. She has no history of hypertension before pregnancy.`;

// Typewriter effect — adds one character every 50ms
const typewriterEffect = (text, setter) => {
  let i = 0;
  const interval = setInterval(() => {
    setter(text.slice(0, i));
    i++;
    if (i > text.length) clearInterval(interval);
  }, 50);
};
```

### Screen 4: SOAP Notes Review
```
┌──────────────────────────────────────────────────────────────────┐
│  ✅ CONSULTATION COMPLETED — AI-Generated SOAP Notes             │
│  ⏱ Generated in 28 seconds by Amazon Bedrock Nova Pro           │
├──────────────────────────────────────────────────────────────────┤
│  📋 SUBJECTIVE:                                                  │
│  Patient reports persistent high fever (101.5°F) for 3 days,    │
│  severe headache, and swelling in extremities. Pregnant (8       │
│  months), first-time mother. BP 160/110 this morning.            │
│                                                    [✏️ Edit]     │
├──────────────────────────────────────────────────────────────────┤
│  🔬 OBJECTIVE:                                                   │
│  Blood Pressure: 160/110    Temp: 38.2°C    Resp Rate: 18       │
│  Swelling noted: hands, face, ankles                             │
│  Proteinuria: Present (per ASHA assessment)                      │
│                                                    [✏️ Edit]     │
├──────────────────────────────────────────────────────────────────┤
│  🧠 ASSESSMENT:                                                  │
│  Pre-eclampsia with severe features. Immediate referral          │
│  required. High risk for eclampsia progression.                  │
│                                                    [✏️ Edit]     │
├──────────────────────────────────────────────────────────────────┤
│  📋 PLAN:                                                        │
│  1. Refer to Sadar Hospital for delivery planning                │
│  2. Rest in left lateral position                                │
│  3. Monitor BP twice daily                                       │
│  4. Do NOT give dipryone or aspirin                              │
│  5. Admit if symptoms worsen                                     │
│                                                    [✏️ Edit]     │
├──────────────────────────────────────────────────────────────────┤
│  🏷️ ICD-10 CODES:                                               │
│  [O14.9 — Gestational HTN] [O14.1 — Pre-eclampsia severe]       │
├──────────────────────────────────────────────────────────────────┤
│  💊 PRESCRIPTION:                                                │
│  Rx 1: Methyldopa Tab 250mg TDS × 10 days                        │
│  Rx 2: Calcium supplement 1g daily (fortified milk)              │
│  Rx 3: MgSO4 inj (ready at hospital)                            │
├──────────────────────────────────────────────────────────────────┤
│  [📄 GENERATE PDF]  [📱 SEND VIA WHATSAPP]  [✅ CONFIRM]        │
└──────────────────────────────────────────────────────────────────┘
```

**Key detail:** Each section has an inline edit button. Doctor can modify any part before approving. Changes save to DynamoDB.

### Screen 5: E-Prescription Sent
```
┌──────────────────────────────────────────────────────────────────┐
│  ✅ Prescription Sent Successfully                               │
├──────────────────────────────────────────────────────────────────┤
│  📱 WhatsApp sent to:                                            │
│  ASHA Amita Devi: +91 9876543210 ✅                             │
│  Patient Priya Devi: +91 9998887776 ✅                          │
├──────────────────────────────────────────────────────────────────┤
│  Message Preview:                                                 │
│  ┌────────────────────────────────────┐                         │
│  │ ✅ E-Prescription — MediConnect AI  │                         │
│  │ Patient: Priya Devi, 28yr           │                         │
│  │ Diagnosis: Pre-eclampsia            │                         │
│  │ 💊 Methyldopa 250mg TDS × 10 days  │                         │
│  │ 💊 Calcium 1g daily                │                         │
│  │ 📅 Follow-up: 7 days               │                         │
│  └────────────────────────────────────┘                         │
├──────────────────────────────────────────────────────────────────┤
│  📊 Session Summary:                                             │
│  Duration: 3min 45sec                                            │
│  Documentation time: 28 seconds (saved 14.5 minutes)            │
│  Case marked: COMPLETED                                          │
├──────────────────────────────────────────────────────────────────┤
│  [📅 Schedule Follow-up]  [← Back to Dashboard]                 │
└──────────────────────────────────────────────────────────────────┘
```

---

## STATS CALCULATION LOGIC

```python
def get_doctor_stats(doctor_id: str, date: str) -> dict:
    cases = get_cases_by_doctor_and_date(doctor_id, date)
    completed = [c for c in cases if c.status == "COMPLETED"]
    
    total_cases = len(completed)
    
    # Avg consultation: 3-5 min per case
    total_consultation_minutes = sum(c.consultation_duration_minutes for c in completed)
    
    # Without AI: each case = 15min SOAP + 5min consultation = 20min
    # With AI: each case = 3-5min consultation + 0.5min SOAP review
    time_saved_minutes = (total_cases * 15) - total_consultation_minutes
    
    # Income: doctor sets their per-consultation fee
    income = total_cases * doctor.consultation_fee  # e.g. ₹500/case
    
    return {
        "cases_today": total_cases,
        "documentation_minutes": total_consultation_minutes,
        "time_saved_hours": round(time_saved_minutes / 60, 1),
        "income_today": income,
        "rating": doctor.rating
    }
```

---

## ENVIRONMENT VARIABLES

```bash
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
AWS_REGION=us-east-1
DYNAMODB_CASES_TABLE=mediconnect-cases
DYNAMODB_PATIENTS_TABLE=mediconnect-patients
DYNAMODB_DOCTORS_TABLE=mediconnect-doctors
WEBSOCKET_URL=wss://xxx.execute-api.us-east-1.amazonaws.com/prod
S3_AUDIO_BUCKET=mediconnect-audio
MOCK_WHATSAPP=true
MOCK_TRANSCRIBE=true   ← use pre-processed transcript for demo
```

---

## WHAT TO MOCK

- Video feed: `<video>` element with looping mp4 clip, LIVE badge overlay
- Transcription: typewriter effect with pre-written consultation text
- WhatsApp sending: show formatted message on screen, log to console
- PDF generation: show "PDF Generated ✅" toast, no actual PDF needed
- Follow-up scheduling: show success toast only

## WHAT MUST BE REAL

- WebSocket receiving cases from ASHA module
- DynamoDB reading case + patient data
- Bedrock SOAP note generation (real API call)
- ICD-10 codes (from Bedrock response)
- Case status updates in DynamoDB
- Stats calculation from real case data

---

## SUCCESS CRITERIA

Demo flow works end-to-end:
1. Doctor dashboard open → sees Priya's EMERGENCY case in queue
2. New case arrives via WebSocket → notification appears with sound
3. Doctor clicks "JOIN CALL" → Case Detail screen loads with full AI summary
4. Doctor clicks "Start Consultation" → video screen with simulated feed
5. Transcript builds up in real-time (typewriter effect)
6. Doctor clicks "End Consultation" → "Generating SOAP notes..." (3-5 sec)
7. SOAP notes appear — full clinical documentation, editable
8. Doctor clicks "Confirm" → prescription sent confirmation screen
9. WhatsApp message preview shown on screen
