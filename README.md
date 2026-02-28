#  SentinelX: AI-Powered Continuous Behavioral Authentication

"Security that never sleeps."

-- Zero Trust Security Mode --

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
