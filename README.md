# AI-Based Behavioral Authentication System

A comprehensive authentication system that uses artificial intelligence to authenticate users based on their behavioral biometrics, including keystroke dynamics and mouse movement patterns.

## Features

✨ **Core Capabilities:**
- 🎯 **Keystroke Dynamics Analysis** - Analyzes typing patterns (inter-keystroke intervals, key frequencies)
- 🖱️ **Mouse Movement Tracking** - Monitors movement velocity, distance, and patterns
- 🤖 **ML-Based Detection** - Uses Isolation Forest for anomaly detection
- 📊 **Feature Extraction** - Extracts 23 behavioral features for analysis
- 👥 **Multi-User Support** - Manage multiple users with separate profiles
- 💾 **Model Persistence** - Save and load trained models

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│         Behavioral Authentication System             │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Data Collector → Feature Extractor → ML Model     │
│      ↓                   ↓              ↓            │
│   Raw Behavior      23 Features    Anomaly Score   │
│   (Typing, Mouse)                  (Authentic?)    │
│                                                     │
│  User Manager: Handles enrollment & authentication  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Components

### 1. **behavioral_data_collector.py**
Collects real-time behavioral data:
- Keystroke events (timing, duration, patterns)
- Mouse movement (velocity, distance, acceleration)
- Real-time event listening

### 2. **feature_extractor.py**
Extracts 23 behavioral features:
- **Keystroke Features (10)**: IKI mean/std/min/max, keystroke rate, unique keys
- **Mouse Features (13)**: Distance/velocity statistics, movement patterns

### 3. **behavioral_model.py**
Machine learning model using Isolation Forest:
- Trains on enrollment behavioral samples
- Detects anomalies in login attempts
- Calculates confidence scores
- Model persistence (save/load)

### 4. **user_manager.py**
User profile management:
- Create/delete users
- Multi-session enrollment
- Model training and storage
- User metadata management

### 5. **main_app.py**
Interactive CLI application:
- User registration
- Enrollment workflow
- Authentication/login
- User management

### 6. **examples.py**
Demonstration and testing scripts

## Installation

### Prerequisites
- Python 3.7+
- Windows/Linux/Mac

### Setup

1. Clone or download the project
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Option 1: Main Application (Interactive)

```bash
python main_app.py
```


#  SentinelX: AI-Powered Continuous Behavioral Authentication

"Security that never sleeps."

---

#  Team Members
* Amit Sharma 
* Pratik Ambhore
* Ganesh Kumbhar 
* Hinesh Sakhare 

---

#  Problem Statement
Traditional static authentication (passwords, 2FA, Biometrics) only verifies identity at the "front gate." This creates a "Trust Gap": once an attacker bypasses the initial login, they have unrestricted access until the session expires. If a device is left unlocked or a session is hijacked, the system remains vulnerable.

#  Solution Approach
SentinelX implements a Continuous Zero Trust model. Instead of a one-time check, it uses an Isolation Forest (ML) model to constantly analyze behavioral biometrics—such as keystroke dynamics, mouse movement patterns, and interaction rhythms. 

The system verifies identity every second of a session without requiring extra hardware, ensuring that if behavioral patterns deviate from the owner's "fingerprint," the session is challenged or terminated instantly.

---

# Tech Stack
| Component    | Technology 
|   Backend    | Python (FastAPI), PostgreSQL 
|   AI / ML    | Scikit-learn, Pandas (Isolation Forest Anomaly Detection) 
|   Frontend   | React.js, Tailwind CSS 
|   Security   | JWT, NIST Zero Trust Framework 

---

# Installation Steps

# 1. Clone the Repository
```bash
git clone [https://github.com/SentinelX-Auth/SentinelX)
cd SentinelX


