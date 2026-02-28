# SYSTEM ARCHITECTURE & COMPONENTS

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│         USER INTERFACE LAYER                                    │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────┐ │
│  │  main_app.py │ │ quick_start.py│ │    examples.py           │ │
│  │  (Interactive│ │  (Quick Demo) │ │  (Learning Guides)      │ │
│  │   CLI Menu)  │ │               │ │                         │ │
│  └──────┬───────┘ └──────┬────────┘ └──────────┬──────────────┘ │
└─────────┼────────────────┼─────────────────────┼────────────────┘
          │                │                     │
          └────────────────┴─────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────────┐
│         APPLICATION LOGIC LAYER                                │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────┐│
│  │            user_manager.py                                  ││
│  │  Manages user profiles, enrollment, authentication          ││
│  │  ┌────────────────────────────────────────────────────────┐││
│  │  │ • create_user()      • list_users()                   │││
│  │  │ • enroll_user()      • delete_user()                  │││
│  │  │ • authenticate_user() • get_user_info()              │││
│  │  └────────────────────────────────────────────────────────┘││
│  └─────────────────────────────────────────────────────────────┘
└─────────────┬──────────────────────────────────┬────────────────┘
              │                                  │
┌─────────────▼──────┐            ┌──────────────▼─────────────┐
│  DATA COLLECTION   │            │  FEATURE ENGINEERING       │
│  LAYER             │            │  LAYER                     │
├────────────────────┤            ├────────────────────────────┤
│behavioral_data_    │            │feature_extractor.py        │
│collector.py        │            │                            │
│                    │            │ Extracts 23 Features:      │
│ • collect()        │            │ ┌──────────────────────┐   │
│ • on_press()       │            │ │ KEYSTROKE (10):      │   │
│ • on_move()        │            │ │ • IKI stats (mean,   │   │
│ • save_data()      │            │ │   std, min, max)     │   │
│ • load_data()      │            │ │ • Keystroke rate     │   │
│                    │            │ │ • Unique keys        │   │
│ Listens to:        │            │ └──────────────────────┘   │
│ • Keyboard events  │            │ ┌──────────────────────┐   │
│ • Mouse movement   │            │ │ MOUSE (13):          │   │
│                    │            │ │ • Distance stats     │   │
│ Data Collected:    │            │ │ • Velocity stats     │   │
│ • IKI (ms)         │            │ │ • Movement rate      │   │
│ • Key codes        │            │ │ • Total movements    │   │
│ • Positions (x,y)  │            │ │                      │   │
│ • Distance         │            │ └──────────────────────┘   │
│ • Velocity         │            │                            │
└────────────┬───────┘            └──────────────┬─────────────┘
             │                                   │
             └───────────────────┬───────────────┘
                                 │
                                 ▼
        ┌────────────────────────────────────────────┐
        │  ML MODEL LAYER                            │
        ├────────────────────────────────────────────┤
        │        behavioral_model.py                 │
        │                                            │
        │  Algorithm: Isolation Forest               │
        │                                            │
        │  Operations:                               │
        │  ┌──────────────────────────────────────┐ │
        │  │ ENROLLMENT:                          │ │
        │  │ • Collect 5 baseline sessions        │ │
        │  │ • Extract features                   │ │
        │  │ • Scale features (StandardScaler)    │ │
        │  │ • Train Isolation Forest             │ │
        │  │ • Save model (joblib)                │ │
        │  └──────────────────────────────────────┘ │
        │  ┌──────────────────────────────────────┐ │
        │  │ AUTHENTICATION:                      │ │
        │  │ • Extract test features              │ │
        │  │ • Scale with same scaler             │ │
        │  │ • Score with model                   │ │
        │  │ • Calculate confidence               │ │
        │  │ • Return: (authentic, confidence)    │ │
        │  └──────────────────────────────────────┘ │
        │                                            │
        └────────────────────┬───────────────────────┘
                             │
        ┌────────────────────▼───────────────────────┐
        │  STORAGE LAYER                             │
        ├────────────────────────────────────────────┤
        │                                            │
        │  users/                                    │
        │  ├── username1/                           │
        │  │   ├── model.pkl (binary model)         │
        │  │   ├── metadata.json (user info)        │
        │  │   ├── session_1.json (raw data)        │
        │  │   └── session_2.json                   │
        │  └── username2/                           │
        │      └── ...                              │
        │                                            │
        └────────────────────────────────────────────┘
```

## Component Interaction Diagram

```
ENROLLMENT FLOW:
================

User → main_app.py → user_manager.py → behavioral_data_collector.py
  (Input)  (Menu)       (Orchestration)   (Data Collection)
                           │                      │
                           │                      └──→ pynput listeners
                           │                           (keyboard, mouse)
                           │
                           ▼
                  feature_extractor.py
                    (Feature Extraction)
                           │
                           ▼
                  behavioral_model.py
                    (Model Training)
                           │
                           ▼
                    joblib save
                           │
                           ▼
                    users/username/model.pkl


AUTHENTICATION FLOW:
====================

User → main_app.py → user_manager.py → behavioral_data_collector.py
  (Input) (Menu)     (Orchestration)   (Data Collection)
                        │                      │
                        │                      └──→ pynput listeners
                        │
                        ▼
                  behavioral_model.py → joblib load
                    (Load Model)            │
                        │                   ▼
                        │          users/username/model.pkl
                        │
                        ▼
                  feature_extractor.py
                    (Feature Extraction)
                        │
                        ▼
                  Isolation Forest
                  (Score: -1 to 1)
                        │
                        ▼
                  Confidence Calculation
                  (0-100%)
                        │
                        ▼
                  User Authenticated ✅/❌
```

## Data Flow Example

```
STEP 1: ENROLLMENT DATA COLLECTION
=================================

Time    Keystroke Data              Mouse Data
────    ──────────────              ──────────
0.10s   {char: 'a', iki: None}      {x: 100, y: 200, distance: None}
0.25s   {char: 'b', iki: 150ms}     {x: 105, y: 205, distance: 7.07px}
0.35s   {char: 'c', iki: 100ms}     {x: 110, y: 210, distance: 7.07px}
0.52s   {char: 'd', iki: 170ms}     {x: 115, y: 215, distance: 7.07px}
... (more events)

(Collect 5 sessions like this)


STEP 2: FEATURE EXTRACTION
==========================

From Keystroke Data:
  • iki_mean: 125ms
  • iki_std: 35ms
  • keystroke_rate: 8.5 keys/sec
  • ... (10 features total)

From Mouse Data:
  • distance_mean: 6.8px
  • velocity_mean: 48.2 px/sec
  • movement_rate: 12.3 moves/sec
  • ... (13 features total)

↓

Feature Vector (23D):
[125.0, 35.0, ..., 6.8, 48.2, ..., 12.3]


STEP 3: MODEL TRAINING
======================

5 Feature Vectors (from 5 enrollment sessions)
→ Isolation Forest (n_estimators=100)
→ Learn "normal" user behavior pattern
→ Save model (model.pkl)


STEP 4: AUTHENTICATION
======================

Test Feature Vector (from login attempt)
→ Run through trained model
→ Anomaly Score: 0.85 (close to normal = 1.0) ✅
→ Confidence: 85%
→ AUTHENTIC (Grant Access)
```

## Module Dependencies

```
main_app.py
    ├── user_manager.py
    │   ├── behavioral_data_collector.py
    │   │   └── pynput
    │   ├── feature_extractor.py
    │   │   ├── numpy
    │   │   └── (feature_names)
    │   └── behavioral_model.py
    │       ├── feature_extractor.py
    │       ├── sklearn.ensemble (IsolationForest)
    │       ├── sklearn.preprocessing (StandardScaler)
    │       ├── joblib
    │       └── numpy

quick_start.py
    ├── behavioral_data_collector.py
    ├── feature_extractor.py
    │   └── numpy
    ├── behavioral_model.py
    │   ├── sklearn.ensemble
    │   ├── sklearn.preprocessing
    │   ├── joblib
    │   └── numpy

examples.py
    ├── behavioral_data_collector.py
    ├── feature_extractor.py
    └── behavioral_model.py

test_suite.py
    ├── feature_extractor.py
    ├── behavioral_model.py
    └── numpy

config.py
    (No external dependencies)

API_REFERENCE.md, README.md, QUICKSTART.txt
    (Documentation only)
```

## System Specifications

```
┌─────────────────────────────────────────────────────┐
│ COMPUTATIONAL REQUIREMENTS                          │
├─────────────────────────────────────────────────────┤
│ Min Python Version: 3.7+                            │
│ Memory per User: ~5-10 MB                           │
│ Model Size per User: ~100 KB                        │
│ Disk Space (100 users): ~50 MB                      │
│                                                     │
│ Processing Time:                                   │
│ • Data Collection: 30s (real-time)                 │
│ • Feature Extraction: <100ms                       │
│ • Model Training: <500ms                           │
│ • Authentication: <100ms                           │
│                                                     │
│ Dependencies: 5 packages (pip)                      │
└─────────────────────────────────────────────────────┘
```

## Security Architecture

```
         User Input
             │
             ▼
        (No encryption)
             │
             ▼
    Feature Extraction
         (Statistical)
             │
             ▼
    ML Model Anomaly Detection
         (Binary: Auth/Reject)
             │
             ├─→ ✅ Authentic
             │   └─→ Grant Access
             │
             └─→ ❌ Anomaly Detected
                 └─→ Deny Access
                     (Optional: Log + Alert)
```

## State Machine

```
    ┌──────────────┐
    │  NO USER     │
    └──────┬───────┘
           │ Create User
           ▼
    ┌──────────────────┐
    │  USER CREATED    │ (Model not trained)
    └──────┬───────────┘
           │ Enroll (collect 5 sessions)
           │
           ▼
    ┌──────────────────┐
    │  USER ENROLLED   │ (Model ready)
    └──────┬───────────┘
           │ Collect behavior data
           │
           ▼
    ┌──────────────────┐
    │  AUTHENTICATING  │
    └────┬──────────┬──┘
         │          │
    ✅ PASS    ❌ FAIL
         │          │
         ▼          ▼
      [Access]   [Deny]
         │          │
         └─────┬────┘
              │ Logout/Retry
              │
              ▼
         [Ready for next session]
```

## Performance Profile

```
Task                Duration      Notes
────────────────    ──────────    ───────────────────────
Data Collection     30s           Real-time keyboard+mouse
Feature Extract     <100ms        23 statistical features
Model Training      <500ms        Isolation Forest
Model Saving        <50ms         joblib serialization
Model Loading       <50ms         joblib deserialization
Authentication      <100ms        Anomaly scoring
User Creation       <10ms         Filesystem operation
Metadata Save       <25ms         JSON serialization

Total Enrollment:   2.5 min       5 sessions × 30s + overhead
Total Auth:         30.5 sec      Data collection + processing
```

## Error Handling Flow

```
User Action
    │
    ▼
Validation
    │
    ├─→ Invalid Input → Show Error → Retry
    │
    ▼
Processing
    │
    ├─→ Model Not Trained → Enroll First
    ├─→ Insufficient Data → Collect More
    ├─→ File Not Found → Handle gracefully
    │
    ▼
Result
    │
    ├─→ Success → Proceed
    └─→ Failure → Log & Retry
```

---

**For detailed method signatures, see [API_REFERENCE.md](API_REFERENCE.md)**
