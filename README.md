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

**Menu Operations:**
1. **Create New User** - Register a new user account
2. **Enroll User** - Create behavioral profile (requires 5 sessions × 30 seconds)
3. **Authenticate User** - Login with behavioral verification
4. **List Users** - View all enrolled users
5. **Delete User** - Remove user profile
6. **View User Info** - Check enrollment details

### Option 2: Examples (Learning)

```bash
python examples.py
```

Demonstrates system capabilities with guided examples

## Workflow

### User Enrollment
1. User creates account
2. System collects 5 behavioral sessions (each ~30 seconds)
3. Features extracted from keystroke & mouse data
4. ML model trained on the 5 baseline samples
5. Model saved for future authentication

### User Authentication
1. User initiates login
2. System collects behavioral session (~30 seconds)
3. Features extracted from login attempt
4. Model checks for anomalies (Isolation Forest)
5. Confidence score calculated (0-100%)
6. User authenticated if score passes threshold

## Behavioral Features

### Keystroke Dynamics (10 features)
- **IKI (Inter-Keystroke Interval)**: Time between keypresses
  - Mean, Standard Deviation, Min, Max, Median
  - 25th and 75th percentiles
- **Keystroke Rate**: Keys per second
- **Unique Keys**: Variety of keys used

### Mouse Movement (13 features)
- **Distance**: Euclidean distance between positions
  - Mean, Std Dev, Min, Max, Median, Total
- **Velocity**: Speed of mouse movement
  - Mean, Std Dev, Min, Max, Median
- **Movement Rate**: Movements per second

## Machine Learning Model

**Algorithm:** Isolation Forest
- Type: Unsupervised anomaly detection
- Approach: Detects outliers by isolation
- Advantage: Works well with small training sets
- Outputs: Anomaly score (-1 to 1 range)

**Scoring:**
- Normal Behavior: Score ≈ 1
- Anomalous Behavior: Score ≈ -1
- Confidence: Normalized anomaly score (0-100%)

## Security Considerations

⚠️ **Important Notes:**
1. This is a **demonstration system** - production use requires additional security measures
2. Works best with 5+ enrollment sessions for accuracy
3. Requires persistent monitoring of user behavior patterns
4. Session duration affects feature accuracy (30s minimum recommended)
5. Should be combined with traditional authentication (passwords, 2FA) in production

## Configuration

### Key Parameters (in behavioral_model.py)
- `contamination`: Expected outlier proportion (default 0.1 = 10%)
- `random_state`: Random seed for reproducibility (42)
- `n_estimators`: Number of trees in Isolation Forest (100)

### Customization
- Adjust `session_duration` for enrollment/authentication
- Modify `num_sessions` for enrollment requirements
- Change `threshold` in authenticate() for strictness

## File Structure

```
AI HACK/
├── requirements.txt                    # Dependencies
├── behavioral_data_collector.py        # Data collection
├── feature_extractor.py                # Feature engineering
├── behavioral_model.py                 # ML model
├── user_manager.py                     # User management
├── main_app.py                         # Main application
├── examples.py                         # Examples
├── README.md                           # This file
└── users/                              # User profiles (created at runtime)
    ├── john/
    │   ├── model.pkl                   # Trained model
    │   ├── metadata.json               # User info
    │   ├── session_1.json              # Enrollment data
    │   └── session_2.json
    └── jane/
        └── ...
```

## Example Output

```
🚀 Behavioral Authentication System Started

============================================================
🔐 AI-Based Behavioral Authentication System
============================================================
1. Create New User
2. Enroll User (Create Behavioral Profile)
3. Authenticate User (Login)
...

Select option (1-7): 1
Enter username: john
✅ User 'john' created

Select option (1-7): 2
Enter username to enroll: john
Number of sessions (default 5): 3
Session duration in seconds (default 30): 20

📍 Session 1/3
🔍 Behavioral Data Collection Starting... (20s)
===... [User performs natural interaction] ...===
✅ Data Collection Complete!

[Model trains on collected data...]
✅ User enrolled successfully with 3 behavior samples


[Later: Authentication]
Select option (1-7): 3
Enter username: john

🔓 Authenticating user: john
🔍 Behavioral Data Collection Starting... (30s)
...
✅ Authentication SUCCESSFUL | Confidence: 92.3%
🎉 Welcome back, john!
```

## Technical Details

### Feature Engineering Pipeline
1. **Raw Events** → Keystroke/mouse events with timestamps
2. **Aggregation** → Group events into sessions
3. **Calculation** → Compute 23 statistical features
4. **Scaling** → Normalize features with StandardScaler
5. **Detection** → Isolation Forest identifies anomalies

### Anomaly Detection Logic
- Training: Learn "normal" user behavior from 5 sessions
- Testing: Score new behavior against learned pattern
- Decision: Flag as anomaly if score below threshold

## Limitations & Future Improvements

### Current Limitations
- Requires 30+ seconds of interaction per session
- Accuracy depends on sufficient keystroke variation
- May have false positives with natural behavior variations
- Single modality focus (keystroke + mouse)

### Potential Enhancements
- Multi-biometric fusion (gait, eye tracking, etc.)
- Deep learning models (LSTM, Autoencoders)
- Adaptive thresholding based on time/context
- Real-time continuous authentication
- Support for multiple devices/contexts
- Behavioral pattern evolution tracking

## References

### Related Technologies
- Keystroke Dynamics (Biometric Authentication)
- Behavioral Biometrics
- Anomaly Detection (Isolation Forest)
- User Behavior Analytics (UBA)

## License

This project is provided for educational and demonstration purposes.

## Contact & Support

For questions or improvements, please refer to the docstrings in individual files.

---

**Happy Authenticating! 🔐**
