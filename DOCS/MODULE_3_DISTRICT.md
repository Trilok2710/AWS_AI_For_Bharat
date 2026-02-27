# MediConnect AI — MODULE 3: District Health Officer Dashboard
## Build Spec for AWS AI for Bharat Hackathon | Team AamRas

---

## YOUR ROLE
You are an expert full-stack developer helping build the District Health Officer module of MediConnect AI. Build exactly what is specified here. Ask before deviating.

---

## CONTEXT — HOW THIS MODULE FITS IN

Modules 1 (ASHA) and 2 (Doctor) handle individual patient care. Every diagnosis made anywhere in the district automatically flows into this dashboard as a data point. The District Health Officer sees disease patterns forming in real-time — days before paper reports would arrive. AWS Bedrock analyzes trends and predicts outbreaks 7 days in advance.

This module is **desktop-only**, data-heavy, visually impressive.

---

## WHO IS THE DISTRICT HEALTH OFFICER?

- Senior government official managing public health for Patna District, Bihar
- Responsible for 200+ villages, 50-100 ASHA workers, 20-30 PHCs
- Current reality: gets paper reports 2-3 weeks late — outbreak already spread
- Needs: **real-time disease intelligence, outbreak early warning, resource allocation**
- Uses: laptop in district office, good internet, English-comfortable

---

## TECH STACK

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + Vite + Tailwind CSS |
| Maps | Leaflet.js + OpenStreetMap + leaflet.heat plugin |
| Charts | Recharts (React charting library) |
| AI — Prediction | AWS Bedrock — Amazon Nova Pro |
| Database | AWS DynamoDB (shared Cases table from Modules 1+2) |
| Backend | FastAPI (Python) — shared with other modules |
| Data | 90 days seeded case data + live cases from ASHA module |

---

## THE DEMO STORY — DENGUE OUTBREAK IN BIKRAM

This is the narrative that drives the entire dashboard. Everything is designed to tell this story convincingly:

**Background (90 days seeded data):**
- Normal disease distribution across 5 blocks of Patna district
- Dengue baseline: ~2 cases/week across entire district (monsoon season)
- Malaria, Typhoid, Diarrhea, TB — normal seasonal patterns

**The outbreak forming (last 14 days):**
- Dengue cases in Bikram block: jumped from 2/week to 8/week
- Last 7 days: 12 dengue cases, concentrated in 3 adjacent villages
- Yesterday: 4 new dengue cases in Bikram + Punpun blocks

**What the dashboard shows:**
- Heatmap: red hotspot glowing over Bikram block
- Alert panel: "🔴 Bikram Block: Dengue 4x above baseline — OUTBREAK RISK"
- Bedrock AI: "High probability dengue outbreak in Bikram by Day 5. Deploy fogging team to villages X, Y, Z immediately."
- 7-day prediction chart: cases trending sharply upward

**Why this story works for judges:**
It's specific, actionable, and demonstrates the core value — the officer can act TODAY instead of finding out in 3 weeks.

---

## DYNAMODB — DATA STRUCTURE

### Uses existing Cases table from Modules 1+2
No new tables needed. Add these fields to Case records:

```
Block     String  (e.g. "Bikram", "Punpun", "Danapur")
Village   String  (e.g. "Rampur", "Shivpur")
District  String  (default: "Patna")
Lat       Number  (village coordinates)
Lng       Number  (village coordinates)
```

### Access Patterns for District Module:
```
Query by District + date range → get all cases in last 30/90 days
Filter by Block → block-level drill down
Filter by Disease → disease-specific view
Aggregate by [Block, Disease, Week] → chart data
```

---

## DATA SEEDING — CRITICAL

Seed ~500 synthetic case records in DynamoDB before demo. This is what powers the charts and map.

### Patna District Blocks + Villages:
```python
DISTRICT_DATA = {
    "Bikram": {
        "lat": 25.4234, "lng": 84.9876,
        "villages": [
            {"name": "Rampur", "lat": 25.4156, "lng": 84.9765},
            {"name": "Shivpur", "lat": 25.4312, "lng": 84.9934},
            {"name": "Krishnapur", "lat": 25.4089, "lng": 84.9698},
        ]
    },
    "Punpun": {
        "lat": 25.4987, "lng": 85.1234,
        "villages": [
            {"name": "Punpun Central", "lat": 25.4923, "lng": 85.1189},
            {"name": "Nayagaon", "lat": 25.5034, "lng": 85.1312},
        ]
    },
    "Danapur": {
        "lat": 25.6123, "lng": 85.0456,
        "villages": [
            {"name": "Danapur Main", "lat": 25.6089, "lng": 85.0412},
            {"name": "Saguna", "lat": 25.6198, "lng": 85.0534},
        ]
    },
    "Phulwari": {
        "lat": 25.5678, "lng": 85.0987,
        "villages": [
            {"name": "Phulwari Sharif", "lat": 25.5634, "lng": 85.0945},
        ]
    },
    "Patna Sadar": {
        "lat": 25.5941, "lng": 85.1376,
        "villages": [
            {"name": "Khagaul", "lat": 25.5876, "lng": 85.1289},
            {"name": "Sampatchak", "lat": 25.6012, "lng": 85.1423},
        ]
    }
}

DISEASES = ["Dengue", "Malaria", "Typhoid", "Diarrhea", 
            "TB", "Pneumonia", "Anemia", "Common Cold"]

RISK_WEIGHTS = {
    "Dengue": "URGENT", "Malaria": "URGENT", "Typhoid": "URGENT",
    "TB": "URGENT", "Pneumonia": "ROUTINE", "Diarrhea": "ROUTINE",
    "Anemia": "ROUTINE", "Common Cold": "ROUTINE"
}
```

### Seeding Logic:
```python
import random
from datetime import datetime, timedelta

def seed_90_days():
    cases = []
    base_date = datetime.now() - timedelta(days=90)
    
    for day in range(90):
        current_date = base_date + timedelta(days=day)
        
        for block_name, block_data in DISTRICT_DATA.items():
            for village in block_data["villages"]:
                # Normal baseline cases
                for disease in DISEASES:
                    # Base rate: 0-2 cases per village per week
                    if random.random() < 0.15:  # 15% chance per day
                        cases.append(make_case(village, disease, current_date, "ROUTINE"))
                
                # THE OUTBREAK: Dengue in Bikram block, last 14 days
                if block_name == "Bikram" and day >= 76:
                    # Days 76-90: dengue cases spike 4x
                    for _ in range(random.randint(0, 3)):  # 0-3 dengue cases per day
                        if village["name"] in ["Rampur", "Shivpur"]:  # 2 epicentre villages
                            cases.append(make_case(village, "Dengue", current_date, "URGENT"))
    
    # Batch write to DynamoDB
    return cases
```

---

## BACKEND API ENDPOINTS

```
GET  /district/overview                    Top-level district stats
     Response: { total_cases_today, active_ashas, alerts[], 
                 top_diseases[], cases_by_block{} }

GET  /district/heatmap?disease=&days=      Heatmap data points
     Response: [ {lat, lng, intensity}, ... ]
     intensity = case count in that location in last N days

GET  /district/trends?days=30              Time series data for charts
     Response: { by_disease: { Dengue: [day1_count, day2_count, ...] } }

GET  /district/blocks                      All block summaries
     Response: [ {block, total_cases, top_disease, alert_level, ...} ]

GET  /district/blocks/{block_name}         Single block drill-down
     Response: { block_stats, village_breakdown[], recent_cases[] }

GET  /district/alerts                      Active anomaly alerts
     Response: [ {block, disease, current_rate, baseline_rate, 
                  multiplier, severity} ]

POST /district/predict                     Trigger Bedrock prediction
     Body: { block: "Bikram", disease: "Dengue", days_history: 30 }
     Response: { predictions[], interventions[], priority_actions[] }

GET  /district/asha-activity               ASHA worker performance
     Response: [ {asha_id, name, cases_this_week, last_active} ]
```

---

## BEDROCK INTEGRATION — OUTBREAK PREDICTION

### Model: `amazon.nova-pro-v1:0`

### Prediction Prompt:
```python
system_prompt = """You are an epidemiological analysis AI for district 
health officers in rural India. You analyze disease surveillance data and 
provide outbreak risk assessments and intervention recommendations based 
on ICMR and WHO surveillance guidelines for Bihar.

Respond ONLY with valid JSON. Be specific about villages, not vague."""

user_prompt = f"""
Analyze this 30-day disease surveillance data for {block_name} Block, 
Patna District, Bihar. Provide outbreak prediction and interventions.

Disease Trend Data (last 30 days, weekly counts):
{json.dumps(trend_data, indent=2)}

Current Season: {season}  (Post-monsoon = dengue/malaria risk)
Block Population: ~{population}
Active ASHA Workers: {asha_count}

Respond with this exact JSON:
{{
  "risk_level": "HIGH|MEDIUM|LOW",
  "risk_summary": "2-sentence summary for the health officer",
  "outbreak_probability_7days": 85,
  "predicted_cases_7days": [
    {{"disease": "Dengue", "day1": 5, "day2": 6, "day3": 8, 
      "day4": 9, "day5": 11, "day6": 12, "day7": 14}}
  ],
  "risk_alerts": [
    {{"disease": "Dengue", "alert": "4x above baseline", 
      "affected_villages": ["Rampur", "Shivpur"],
      "severity": "CRITICAL"}}
  ],
  "interventions": [
    "Deploy fogging team to Rampur and Shivpur villages immediately",
    "Set up dengue screening camp at Bikram PHC this week",
    "Distribute mosquito nets to 200 households in Rampur"
  ],
  "priority_actions_today": [
    "Call Bikram PHC in-charge — escalate dengue alert",
    "Request additional rapid test kits from state supply",
    "Alert vector control department for emergency fogging"
  ]
}}
"""
```

### When to call Bedrock:
- On dashboard load (first time)
- When officer clicks "Refresh AI Prediction" button
- Auto-refresh every 60 minutes
- Cache result in DynamoDB to avoid repeated calls

---

## ANOMALY DETECTION ALGORITHM

Run server-side to generate alerts, triggered on each dashboard load:

```python
def detect_anomalies(cases_last_30_days: list) -> list:
    alerts = []
    
    # Calculate baseline: average cases per disease per block per week
    # Using days 1-60 as baseline, days 61-90 as "current"
    
    for block in BLOCKS:
        for disease in DISEASES:
            baseline_weekly = get_weekly_average(cases, block, disease, days=1-60)
            current_weekly = get_weekly_count(cases, block, disease, last_days=7)
            
            if baseline_weekly == 0:
                continue
                
            multiplier = current_weekly / baseline_weekly
            
            if multiplier >= 4.0:
                alerts.append({
                    "block": block, "disease": disease,
                    "current": current_weekly, "baseline": baseline_weekly,
                    "multiplier": round(multiplier, 1),
                    "severity": "CRITICAL",    # 4x+
                    "message": f"{block}: {disease} {multiplier}x above baseline"
                })
            elif multiplier >= 2.0:
                alerts.append({
                    "severity": "WARNING",     # 2-4x
                    "message": f"{block}: {disease} {multiplier}x above baseline"
                })
    
    return sorted(alerts, key=lambda x: x["multiplier"], reverse=True)
```

---

## SCREENS — 3 TOTAL

### Screen 1: Main Dashboard
```
┌──────────────────────────────────────────────────────────────────────┐
│  🏥 MediConnect AI — District Epidemiology Dashboard    [Refresh AI] │
│  Patna District, Bihar | Last updated: 2 min ago                     │
├────────────┬────────────┬────────────┬────────────────────────────────┤
│ 847        │ 47         │ 3          │ 89                             │
│ Total Cases│ Active     │ 🚨 Active  │ Active ASHAs                   │
│ (30 days)  │ Today      │ Alerts     │ Today                          │
├────────────┴────────────┴────────────┴────────────────────────────────┤
│                          │                                            │
│   HEATMAP (60%)          │  ALERT PANEL (40%)                        │
│                          │                                            │
│   [Leaflet.js map of     │  🔴 Bikram Block                          │
│    Patna district]       │  Dengue: 4.1x above baseline              │
│                          │  12 cases in 3 villages this week         │
│   Heat overlay shows     │  [→ VIEW DETAILS]                         │
│   disease concentration  │                                            │
│   Red = Bikram hotspot   │  🟡 Punpun Block                          │
│                          │  Malaria: 2.3x above baseline             │
│   Disease filter:        │  6 cases this week                        │
│   [All] [Dengue]         │  [→ VIEW DETAILS]                         │
│   [Malaria] [Typhoid]    │                                            │
│                          │  🟢 Danapur Block: Normal                 │
│   Each dot = 1 case      │  🟢 Phulwari Block: Normal                │
│   Heatmap radius=0.5km   │  🟢 Patna Sadar: Normal                  │
│                          │─────────────────────────────────────────  │
│                          │  🤖 AI INSIGHT (Bedrock)                  │
│                          │  "Dengue outbreak likely in Bikram        │
│                          │   block within 5 days. Rainfall           │
│                          │   post-monsoon is driving vector           │
│                          │   breeding. Recommend immediate            │
│                          │   fogging in Rampur and Shivpur."         │
│                          │  [↻ Refresh Prediction]                   │
└──────────────────────────┴────────────────────────────────────────────┘
```

**Leaflet.js Heatmap Setup:**
```javascript
import L from 'leaflet';
import 'leaflet.heat';

const map = L.map('map').setView([25.5941, 85.1376], 11); // Patna center

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap'
}).addTo(map);

// heatData = [[lat, lng, intensity], ...]
// intensity = normalized case count (0-1)
const heat = L.heatLayer(heatData, {
  radius: 25,
  blur: 15,
  maxZoom: 17,
  gradient: { 0.4: 'blue', 0.6: 'lime', 0.8: 'yellow', 1.0: 'red' }
}).addTo(map);

// Disease filter — re-render heatmap with filtered data
const filterByDisease = (disease) => {
  const filtered = disease === 'All' ? allCases 
    : allCases.filter(c => c.disease === disease);
  const newData = filtered.map(c => [c.lat, c.lng, c.intensity]);
  heat.setLatLngs(newData);
};
```

### Screen 2: Disease Trends
```
┌──────────────────────────────────────────────────────────────────────┐
│  ← Back     Disease Trends — Patna District    [30 days ▼]          │
├──────────────────────────────────────────────────────────────────────┤
│  📈 Weekly Case Trends (All Diseases)                                │
│                                                                      │
│  [Recharts LineChart — 30 days on X axis]                           │
│  - Dengue line: shows sharp uptick last 2 weeks (red)               │
│  - Malaria line: slight increase (orange)                            │
│  - Typhoid, Diarrhea: stable (green, blue)                          │
│  - Dotted lines after today: 7-day Bedrock predictions              │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│  📊 Top Diseases This Week (Bar Chart)                               │
│                                                                      │
│  Dengue     ████████████████████████████  47 cases  +23% ↑         │
│  Malaria    ████████████████████          34 cases  -5% ↓          │
│  Typhoid    █████████████                 19 cases  +15% ↑         │
│  Common Cold████████████████████████████████████ 156 cases stable  │
│  Diarrhea   █████████████████████         89 cases  -2% ↓          │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│  🔮 7-Day Predictions (Bedrock AI)                                   │
│  ⚠️ Dengue outbreak likely in Bikram Block                           │
│  📈 Forecast: +25 cases (rainfall increases vector)                  │
│  ✅ Recommended: Deploy screening team TODAY                          │
└──────────────────────────────────────────────────────────────────────┘
```

**Recharts setup:**
```javascript
import { LineChart, Line, XAxis, YAxis, CartesianGrid, 
         Tooltip, Legend, ReferenceLine } from 'recharts';

// data = [{date: "Jan 1", Dengue: 3, Malaria: 5, Typhoid: 2, ...}, ...]
// Add isPrediction: true for the last 7 data points

<LineChart data={trendData} width={800} height={400}>
  <CartesianGrid strokeDasharray="3 3" />
  <XAxis dataKey="date" />
  <YAxis />
  <Tooltip />
  <Legend />
  <ReferenceLine x={today} stroke="gray" label="Today" strokeDasharray="5 5"/>
  <Line type="monotone" dataKey="Dengue" stroke="#ef4444" strokeWidth={2}
        strokeDasharray={isPrediction ? "5 5" : "0"} />
  <Line type="monotone" dataKey="Malaria" stroke="#f97316" strokeWidth={2} />
  <Line type="monotone" dataKey="Typhoid" stroke="#eab308" strokeWidth={2} />
</LineChart>
```

### Screen 3: Block Detail (Drill-down)
```
┌──────────────────────────────────────────────────────────────────────┐
│  ← Back    Bikram Block — Detailed View                             │
├──────────────────────────────────────────────────────────────────────┤
│  Block Stats:                                                        │
│  Population: ~45,000 | PHCs: 2 | Active ASHAs: 8 | Cases(7d): 18   │
├──────────────────────────────────────────────────────────────────────┤
│  🔴 OUTBREAK ALERT — Dengue                                          │
│  12 cases in last 7 days | Baseline: 3/week | 4.1x above normal     │
│                                                                      │
│  Village Breakdown:                                                  │
│  Village        Dengue  Malaria  Typhoid  Total   Alert             │
│  Rampur          8        1        2       11     🔴 HIGH            │
│  Shivpur         4        0        1        5     🟡 MEDIUM          │
│  Krishnapur      0        2        0        2     🟢 NORMAL          │
├──────────────────────────────────────────────────────────────────────┤
│  🤖 AI Recommendations for Bikram Block:                             │
│  1. Deploy fogging team to Rampur and Shivpur today                 │
│  2. Set up dengue rapid test camp at Bikram PHC                     │
│  3. Distribute mosquito nets to 200 high-risk households            │
│  4. Alert vector control department — emergency protocol             │
├──────────────────────────────────────────────────────────────────────┤
│  ASHA Activity in Bikram:                                            │
│  Amita Devi     — 12 cases this week — Last active: 2h ago          │
│  Priya Kumari   — 8 cases this week  — Last active: 5h ago          │
│  Sunita Devi    — 3 cases this week  — Last active: 1d ago          │
├──────────────────────────────────────────────────────────────────────┤
│  [📤 Export Report]  [🔔 Set Alert Threshold]  [📞 Call PHC]         │
└──────────────────────────────────────────────────────────────────────┘
```

**Export Report** — mock only. Show toast: "Report exported ✅" with no actual file generated.

---

## FRONTEND STATE

```javascript
const [districtData, setDistrictData] = useState({
  overview: null,
  heatmapPoints: [],      // [[lat, lng, intensity], ...]
  trends: {},             // { Dengue: [3,4,2,...], Malaria: [...] }
  alerts: [],
  blocks: [],
  aiPrediction: null,
  selectedDisease: 'All',
  selectedBlock: null,
  isLoading: false,
  lastUpdated: null
});
```

---

## DATA AGGREGATION LOGIC

```python
def get_heatmap_data(district: str, disease: str = None, days: int = 30) -> list:
    """Returns list of [lat, lng, intensity] for Leaflet heatmap"""
    cutoff = datetime.now() - timedelta(days=days)
    
    # Query DynamoDB
    cases = query_cases(district=district, since=cutoff, disease=disease)
    
    # Group by village coordinates
    village_counts = defaultdict(int)
    village_coords = {}
    for case in cases:
        key = (case.lat, case.lng)
        village_counts[key] += 1
        village_coords[key] = (case.lat, case.lng)
    
    # Normalize intensity to 0-1
    max_count = max(village_counts.values()) if village_counts else 1
    
    return [
        [lat, lng, count / max_count]
        for (lat, lng), count in village_counts.items()
    ]


def get_trend_data(district: str, days: int = 30) -> dict:
    """Returns weekly case counts by disease for Recharts"""
    cutoff = datetime.now() - timedelta(days=days)
    cases = query_cases(district=district, since=cutoff)
    
    # Group by week + disease
    trends = defaultdict(lambda: defaultdict(int))
    for case in cases:
        week_label = case.created_at.strftime("%b %d")
        trends[week_label][case.primary_diagnosis] += 1
    
    # Format for Recharts: [{date, Dengue: 5, Malaria: 3, ...}, ...]
    return [
        {"date": date, **diseases}
        for date, diseases in sorted(trends.items())
    ]
```

---

## ENVIRONMENT VARIABLES

```bash
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx  
AWS_REGION=us-east-1
DYNAMODB_CASES_TABLE=mediconnect-cases
BEDROCK_MODEL_ID=amazon.nova-pro-v1:0
DISTRICT_NAME=Patna
```

---

## WHAT TO MOCK

- Export to PDF/Excel — show "Report Exported ✅" toast only
- Vaccination coverage — hardcode percentages on block cards
- "Call PHC" button — show phone number in a modal
- Alert threshold setting — show a form modal, don't actually save

## WHAT MUST BE REAL

- Leaflet.js heatmap rendering with seeded DynamoDB data
- Disease trend charts with Recharts (real aggregated data)
- Anomaly detection alerts (real algorithm on seeded data)
- Bedrock AI prediction (real API call)
- Block drill-down with real case counts

---

## SUCCESS CRITERIA

Demo flow works end-to-end:
1. Officer opens dashboard → sees map with red hotspot over Bikram
2. Alert panel shows: "🔴 Bikram: Dengue 4.1x above baseline"
3. AI Insight panel shows Bedrock-generated prediction
4. Officer taps disease filter "Dengue" → heatmap updates to show only dengue
5. Officer taps "Bikram Block" alert → Block Detail screen loads
6. Block detail shows village breakdown (Rampur worst affected)
7. AI recommendations shown: fogging, screening camp, mosquito nets
8. Officer taps "Export Report" → toast shows "Report Exported ✅"
