# MediConnect AI — MODULE 1: ASHA Worker App
## Build Spec for AWS AI for Bharat Hackathon | Team AamRas

---

## YOUR ROLE
You are an expert full-stack developer helping build the ASHA Worker module of MediConnect AI — a healthcare platform connecting rural ASHA workers to doctors across India. Build exactly what is specified here. Ask before deviating from the spec.

---

## WHAT IS THIS MODULE?

The ASHA (Accredited Social Health Activist) module is a **mobile-first React PWA** used by ASHA workers in rural Indian villages. An ASHA manages 150 households (~600 people) in her area. She is not a doctor — she observes symptoms, follows protocols, and connects patients to doctors when needed.

Her biggest needs:
- Register patients once, load them instantly on return visits
- Speak symptoms in Hindi or English, get AI diagnosis in seconds
- Know immediately if a case is EMERGENCY / URGENT / ROUTINE
- Connect the patient to a doctor with one tap in emergencies

---

## TECH STACK

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | React 18 + Vite + Tailwind CSS | Fast to build, mobile-first |
| Voice Input | Web Speech API (browser native) | Real-time Hindi/English, zero latency |
| AI Diagnosis | AWS Bedrock — Amazon Nova Pro | Core AWS service, judges reward this |
| Database | AWS DynamoDB | AWS points, two tables |
| Real-time | AWS API Gateway WebSockets | Push case to doctor dashboard live |
| Notifications | Twilio WhatsApp (mocked in demo) | Show formatted message on screen |
| Backend | FastAPI (Python) | Team's strength |
| Hosting | Vercel (frontend) + AWS Lambda (backend) | Free tier |

---

## BACKEND API ENDPOINTS TO BUILD

### Base URL: `http://localhost:8000`

### Patient Endpoints
```
POST   /patients/register          Register new patient
GET    /patients/{asha_id}         Get all patients for this ASHA worker
GET    /patients/search?q=&asha_id= Search patients by name or village
GET    /patients/{patient_id}/profile  Full profile + case history
PUT    /patients/{patient_id}      Update patient profile (allergies, conditions)
```

### Case / Diagnosis Endpoints
```
POST   /cases/diagnose             Submit symptoms → get AI diagnosis
GET    /cases/{case_id}            Get single case details
GET    /patients/{patient_id}/cases  All cases for a patient
POST   /cases/{case_id}/connect-doctor  Trigger doctor connection flow
```

### ASHA Auth (simple for hackathon)
```
POST   /asha/login                 Login with phone + PIN
GET    /asha/{asha_id}/profile     Get ASHA worker profile
```

---

## DATABASE — AWS DYNAMODB

### Table 1: Patients
```
Partition Key: PatientID (String) — UUID generated at registration
GSI 1: ASHAWorkerID-index (for listing all patients of one ASHA)
GSI 2: Village-index (for browsing by village)

Attributes:
  PatientID         String  (PK)
  ASHAWorkerID      String  (GSI)
  Name              String
  Age               Number
  Gender            String  (M/F/Other)
  Village           String
  Block             String
  District          String  (default: "Patna")
  Phone             String
  ABHA_ID           String  (optional)
  BloodGroup        String  (optional)
  KnownConditions   List    (auto-populated by AI over time)
  KnownAllergies    List    (manual entry)
  CurrentMedications List   (manual entry)
  RegisteredDate    String  (ISO timestamp)
  LastVisitDate     String  (ISO timestamp — updated on each case)
```

### Table 2: Cases
```
Partition Key: CaseID (String) — UUID generated at diagnosis
GSI 1: PatientID-index (all cases for a patient)
GSI 2: ASHAWorkerID-CreatedAt-index (all cases by ASHA, sorted by date)
GSI 3: Status-index (PENDING cases for doctor queue)

Attributes:
  CaseID              String  (PK)
  PatientID           String  (GSI)
  ASHAWorkerID        String  (GSI)
  DoctorID            String  (set when doctor is matched)
  
  SymptomsRaw         String  (original voice/text input)
  SymptomsEnglish     String  (translated by Bedrock if Hindi)
  Language            String  (hi-IN / en-IN)
  
  PrimaryDiagnosis    String
  DifferentialDiagnoses List
  ConfidencePercent   Number
  RiskLevel           String  (EMERGENCY / URGENT / ROUTINE)
  RiskReason          String
  ImmediateActions    List
  ICMRProtocol        String
  ICD10Code           String
  ICD10Description    String
  
  Status              String  (PENDING / DOCTOR_ASSIGNED / COMPLETED / CLOSED)
  CreatedAt           String  (ISO timestamp)
  UpdatedAt           String  (ISO timestamp)
```

---

## BEDROCK INTEGRATION — CORE AI ENGINE

### Model: `amazon.nova-pro-v1:0`
### Region: `us-east-1`

### Diagnosis Prompt Structure:
```python
system_prompt = """You are MediConnect AI, an expert medical diagnosis assistant 
trained on ICMR clinical guidelines for rural India. You assist ASHA workers.

Prioritize for rural India: Dengue, Malaria, Typhoid, TB, Pre-eclampsia, 
Dehydration, Pneumonia, Anemia, Diarrhea, Diabetes complications.

CRITICAL RULE: Pregnant woman + severe headache + swelling → ALWAYS EMERGENCY.

Respond ONLY with valid JSON. No markdown. No text outside JSON."""

user_prompt = f"""
Patient: {name}, {age}yr, {gender}
Known conditions: {known_conditions}  ← include for return patients
Known allergies: {allergies}
Previous diagnoses: {last_3_cases}  ← include for return patients
Current symptoms: "{symptoms_text}"
Language: {language}

Return this exact JSON:
{{
  "symptoms_english": "...",
  "primary_diagnosis": "...",
  "differential_diagnoses": ["...", "..."],
  "confidence_percent": 85,
  "risk_level": "EMERGENCY|URGENT|ROUTINE",
  "risk_reason": "one sentence",
  "immediate_actions": ["action 1", "action 2", "action 3"],
  "icmr_protocol": "ICMR Dengue Protocol 2021",
  "icd10_code": "A90",
  "icd10_description": "Dengue fever [classical dengue]",
  "auto_tag_conditions": ["condition to add to patient profile"]
}}
"""
```

### Emergency Keyword Failsafe (run BEFORE Bedrock, override AFTER):
```python
EMERGENCY_KEYWORDS = [
    "pre-eclampsia", "eclampsia", "convulsion", "seizure",
    "heavy bleeding", "hemorrhage", "unconscious", "not breathing",
    "behoshi", "zyada khoon", "dauraa",  # Hindi
    "chest pain", "no pulse", "heart attack", "stroke"
]
# If keyword found → force RiskLevel = EMERGENCY regardless of Bedrock output
```

### Auto-tag patient conditions:
After each diagnosis, take `auto_tag_conditions` from Bedrock response and append to patient's `KnownConditions` in DynamoDB. This makes future diagnoses richer automatically.

---

## REAL-TIME DOCTOR CONNECTION

When ASHA taps "Connect to Doctor":

1. Backend calls doctor matching algorithm (see below)
2. Backend saves matched DoctorID to Case record in DynamoDB
3. Backend sends WebSocket message to doctor's dashboard:
```json
{
  "event": "NEW_CASE",
  "case_id": "CASE-ABC123",
  "patient_name": "Priya Devi",
  "patient_age": 28,
  "risk_level": "EMERGENCY",
  "primary_diagnosis": "Pre-eclampsia",
  "asha_name": "Amita Devi",
  "village": "Bikram",
  "distance_km": 4.2,
  "wait_time_seconds": 0
}
```
4. Backend formats WhatsApp message and logs it (mock send for demo)
5. ASHA screen shows: "Dr. Patel notified — connecting in 30 seconds..."

### Doctor Matching Algorithm:
```python
SPECIALIZATION_MAP = {
    "pre-eclampsia": "Gynaecologist",
    "eclampsia": "Gynaecologist", 
    "pregnancy": "Gynaecologist",
    "child": "Paediatrician",      # if patient age < 12
    "paediatric": "Paediatrician",
    # everything else → "General Physician"
}

def match_doctor(diagnosis, patient_age, asha_lat, asha_lng):
    required_spec = get_required_specialization(diagnosis, patient_age)
    available_doctors = get_available_doctors_from_dynamodb()
    
    # Filter by specialization first, fallback to General Physician
    specialists = [d for d in available_doctors if d.specialization == required_spec]
    pool = specialists if specialists else available_doctors
    
    # Sort by distance from ASHA location
    pool.sort(key=lambda d: haversine(asha_lat, asha_lng, d.lat, d.lng))
    
    return pool[0] if pool else None
```

### Pre-seeded Demo Doctors in DynamoDB:
```python
DEMO_DOCTORS = [
    {"DoctorID": "DR-001", "Name": "Dr. Priya Patel", 
     "Specialization": "Gynaecologist", "Lat": 25.5941, "Lng": 85.1376,
     "IsAvailable": True, "ClinicName": "Bikram PHC", "DistanceKm": 4.2},
    {"DoctorID": "DR-002", "Name": "Dr. Ramesh Sharma",
     "Specialization": "General Physician", "Lat": 25.6121, "Lng": 85.1534,
     "IsAvailable": True, "ClinicName": "Gopal Nagar CHC", "DistanceKm": 6.8},
    {"DoctorID": "DR-003", "Name": "Dr. Anita Singh",
     "Specialization": "Paediatrician", "Lat": 25.5712, "Lng": 85.1892,
     "IsAvailable": True, "ClinicName": "Rural Central PHC", "DistanceKm": 12.3},
]
```

---

## FRONTEND — REACT PWA

### Global State:
```javascript
{
  asha: { id, name, block, district, language: 'hi'|'en' },
  patients: [],           // loaded on app start
  currentPatient: null,
  currentCase: null,
  isRecording: false,
  transcript: ''
}
```

### Language Toggle:
```javascript
// All UI strings in both languages
const STRINGS = {
  hi: {
    recordSymptoms: "लक्षण बताएं",
    analyzing: "विश्लेषण हो रहा है...",
    emergency: "अति आपातकाल",
    urgent: "जल्द देखभाल",
    routine: "सामान्य",
    connectDoctor: "डॉक्टर से जोड़ें",
    call108: "108 कॉल करें",
    newPatient: "नया मरीज़",
    searchPatient: "मरीज़ खोजें...",
    recentPatients: "हाल के मरीज़",
  },
  en: {
    recordSymptoms: "Record Symptoms",
    analyzing: "Analyzing...",
    emergency: "EMERGENCY",
    urgent: "URGENT",
    routine: "ROUTINE",
    connectDoctor: "Connect to Doctor",
    call108: "Call 108",
    newPatient: "New Patient",
    searchPatient: "Search patients...",
    recentPatients: "Recent Patients",
  }
}
```

### Voice Input — Web Speech API:
```javascript
const startRecording = () => {
  const recognition = new window.webkitSpeechRecognition();
  recognition.lang = language === 'hi' ? 'hi-IN' : 'en-IN';
  recognition.continuous = true;
  recognition.interimResults = true;

  recognition.onresult = (event) => {
    const transcript = Array.from(event.results)
      .map(r => r[0].transcript).join('');
    setTranscript(transcript);  // Shows text in real-time as user speaks
  };

  recognition.start();
  setIsRecording(true);
};
```

---

## SCREENS — 7 TOTAL

### Screen 1: Home / Patient List
```
┌─────────────────────────────────┐
│  🏥 MediConnect AI    [हि|EN]   │  ← Language toggle top right
│  Amita Devi | Bikram Block      │  ← ASHA name + location
├─────────────────────────────────┤
│  🔍 [मरीज़ खोजें...           ] │  ← Search bar (filters as typed)
├─────────────────────────────────┤
│  हाल के मरीज़ (Recent)          │
│  ┌───────────────────────────┐  │
│  │ 🔴 Priya Devi, 28F        │  │  ← Red = had EMERGENCY recently
│  │    Pre-eclampsia | कल     │  │
│  └───────────────────────────┘  │
│  ┌───────────────────────────┐  │
│  │ 🟡 Rajesh Kumar, 32M      │  │  ← Yellow = URGENT
│  │    Dengue | 2 दिन पहले   │  │
│  └───────────────────────────┘  │
│  ┌───────────────────────────┐  │
│  │ 🟢 Asha Baby, 5F          │  │  ← Green = ROUTINE
│  │    Gastroenteritis | आज   │  │
│  └───────────────────────────┘  │
├─────────────────────────────────┤
│  [+ नया मरीज़ जोड़ें          ] │  ← Big green button
└─────────────────────────────────┘
```

### Screen 2: New Patient Registration
```
Simple form — mobile optimised, large touch targets:
  • Name (text)
  • Age (number)  
  • Gender (M/F/Other — tap to select)
  • Village (text)
  • Phone (number, optional)
  
Submit → creates Patient in DynamoDB → navigates to Screen 3 (their profile)
Takes <60 seconds to complete
```

### Screen 3: Patient Profile
```
┌─────────────────────────────────┐
│  ← Priya Devi                   │
│  28 साल | महिला | बिक्रम गाँव  │
│  📞 9876543210                  │
├─────────────────────────────────┤
│  ⚕️ Known Conditions            │
│  🏷 Gestational Hypertension    │  ← Auto-tagged from past diagnosis
│  🏷 Pregnant (8 months)         │
├─────────────────────────────────┤
│  📋 Case History                │
│  ┌───────────────────────────┐  │
│  │ 🔴 15 Jan — Pre-eclampsia │  │
│  │    EMERGENCY | Dr. Patel  │  │
│  └───────────────────────────┘  │
│  ┌───────────────────────────┐  │
│  │ 🟢 2 Jan — Anemia checkup │  │
│  │    ROUTINE | Dr. Sharma   │  │
│  └───────────────────────────┘  │
├─────────────────────────────────┤
│  [🎤 नई जाँच शुरू करें       ] │  ← Goes to Screen 4
└─────────────────────────────────┘
```

### Screen 4: New Assessment (Voice + Text)
```
┌─────────────────────────────────┐
│  ← Priya Devi की जाँच          │
├─────────────────────────────────┤
│                                 │
│         🎤                      │  ← Mic icon, large
│   [टैप करके बोलें]             │
│                                 │
│  ─────── या टाइप करें ─────── │
│  [लक्षण यहाँ लिखें...        ] │  ← Text area fallback
│                                 │
│  Transcript appears here as     │
│  user speaks — real time        │
│                                 │
│  "sir dard bahut tej hai,       │
│   haath pair sujan..."          │
│                                 │
├─────────────────────────────────┤
│  [🔬 AI से जाँच करें          ] │  ← Calls Bedrock
└─────────────────────────────────┘
```

### Screen 5: Analyzing (Loading)
```
┌─────────────────────────────────┐
│  MediConnect AI                 │
├─────────────────────────────────┤
│                                 │
│  🔄 विश्लेषण हो रहा है...      │
│                                 │
│  [████████████░░░░░░] 70%       │  ← Animated progress bar
│                                 │
│  ✅ Symptoms translated         │
│  ✅ Medical history loaded      │
│  ⏳ Bedrock AI analyzing...     │
│                                 │
│  (Usually takes 3-5 seconds)    │
│                                 │
└─────────────────────────────────┘
```

### Screen 6: Diagnosis Result
```
┌─────────────────────────────────┐
│  ← जाँच परिणाम                 │
├─────────────────────────────────┤
│  🚨 अति आपातकाल                │  ← RED banner (or yellow/green)
│  EMERGENCY                      │
├─────────────────────────────────┤
│  🔬 Pre-eclampsia (Severe)      │
│  विश्वास: 89%                   │
│  ICD-10: O14.1                  │
├─────────────────────────────────┤
│  ⚠️ Pregnant patient with       │
│  severe headache and swelling   │
├─────────────────────────────────┤
│  📋 तुरंत करें:                │
│  1. 108 एम्बुलेंस बुलाएं       │
│  2. बायीं करवट लिटाएं          │
│  3. कोई दवाई न दें             │
├─────────────────────────────────┤
│  📖 ICMR Maternal Protocol 2023│
├─────────────────────────────────┤
│  [📞 108 कॉल करें  ] [👨‍⚕️ डॉक्टर]│
└─────────────────────────────────┘
```

### Screen 7: Emergency Actions
```
┌─────────────────────────────────┐
│  🚨 EMERGENCY ALERT             │  ← Full red screen
├─────────────────────────────────┤
│  Pre-eclampsia Suspected        │
│  Confidence: 89%                │
├─────────────────────────────────┤
│  IMMEDIATE ACTIONS:             │
│  ✅ Call 108 Ambulance          │
│  ✅ Position on left side       │
│  ✅ Monitor BP                  │
│  ✅ Do NOT give medicine        │
├─────────────────────────────────┤
│  [📞 CALL 108 ]                 │  ← tel:108 link
│                                 │
│  [👨‍⚕️ CONNECT TO DOCTOR NOW   ] │  ← Triggers doctor match + WebSocket
├─────────────────────────────────┤
│  📍 Nearest Hospital:           │
│  Sadar Hospital (4.2 km)        │
└─────────────────────────────────┘
```

---

## WHATSAPP MESSAGE FORMAT (shown on screen, not actually sent in demo)

```
🏥 *MediConnect AI — Case Report*
Case ID: CASE-ABC123

👤 *Patient:* Priya Devi, 28yr (F)
📋 *Symptoms:* Severe headache, swollen hands and feet, 8 months pregnant

🔬 *AI Diagnosis:* Pre-eclampsia (Severe)
📊 *Confidence:* 89%
🏷️ *ICD-10:* O14.1 — Severe pre-eclampsia

🚨 *Risk Level: EMERGENCY*
💡 _Pregnant patient with severe headache and peripheral edema_

📌 *Immediate Actions:*
  1. Call 108 ambulance immediately
  2. Position patient on left lateral side
  3. Do NOT give any medicine

📖 *Protocol:* ICMR Maternal Health Protocol 2023

_Powered by MediConnect AI | AWS Bedrock_
```

---

## DEMO DATA — PRE-SEED ON STARTUP

Pre-seed these patients and cases in DynamoDB when the app first loads:

### ASHA Worker:
```python
{
  "ASHAWorkerID": "ASHA-001",
  "Name": "Amita Devi",
  "Block": "Bikram",
  "District": "Patna",
  "Phone": "+919876543210",
  "Lat": 25.5921,
  "Lng": 85.1376
}
```

### 3 Demo Patients with 1 case each:
```python
# Patient 1 — Emergency story
{"PatientID": "PAT-001", "Name": "Priya Devi", "Age": 28, "Gender": "F",
 "Village": "Bikram", "KnownConditions": ["Pregnant - 8 months", "Gestational Hypertension"]}

# Patient 2 — Urgent story  
{"PatientID": "PAT-002", "Name": "Rajesh Kumar", "Age": 32, "Gender": "M",
 "Village": "Bikram", "KnownConditions": []}

# Patient 3 — Routine story
{"PatientID": "PAT-003", "Name": "Asha Baby", "Age": 5, "Gender": "F",
 "Village": "Punpun", "KnownConditions": []}
```

---

## ENVIRONMENT VARIABLES

```bash
# .env
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
AWS_REGION=us-east-1
DYNAMODB_PATIENTS_TABLE=mediconnect-patients
DYNAMODB_CASES_TABLE=mediconnect-cases
WEBSOCKET_URL=wss://xxx.execute-api.us-east-1.amazonaws.com/prod
MOCK_WHATSAPP=true
```

---

## BUILD ORDER (suggested)

1. DynamoDB tables + seed data script
2. FastAPI backend — patient CRUD endpoints
3. FastAPI backend — diagnosis endpoint (Bedrock)
4. FastAPI backend — doctor connect + WebSocket
5. React — Screen 1 (Home + patient list)
6. React — Screen 2 (New patient form)
7. React — Screen 3 (Patient profile)
8. React — Screen 4 (Voice assessment)
9. React — Screen 5+6 (Loading + Results)
10. React — Screen 7 (Emergency)
11. Language toggle (hi/en) across all screens
12. Polish + mobile responsiveness

---

## WHAT TO MOCK (don't build for real)

- WhatsApp actual sending — just show formatted message on screen
- Offline TinyBERT — mention in architecture only
- 108 ambulance call — just a `<a href="tel:108">` link
- Hospital distance — hardcode "Sadar Hospital 4.2km" for demo

---

## SUCCESS CRITERIA

The module is complete when this demo flow works end-to-end:
1. ASHA opens app → sees patient list with Priya, Rajesh, Asha Baby
2. Taps Priya → sees her profile with known conditions + past case
3. Taps "New Assessment" → speaks Hindi symptoms via mic → text appears
4. Taps "Analyze" → loading screen → EMERGENCY result appears
5. Taps "Connect to Doctor" → doctor dashboard receives live notification
6. WhatsApp message preview shown on screen
