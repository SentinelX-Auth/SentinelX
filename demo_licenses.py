
"""
Demo script showing license key system usage
Run this to see the license system in action
"""

import sys 
import os 

print ("""
╔════════════════════════════════════════════════════════════════════════════╗
║                      LICENSE KEY SYSTEM DEMO                              ║
║                 Give License Keys to Anyone for App Access                ║
╚════════════════════════════════════════════════════════════════════════════╝

🔑 NEW FEATURES:

  ✅ Generate License Keys           - Create license keys for app access
  ✅ Share Keys with Anyone          - Give license keys to users
  ✅ License-Based Login             - Login with username + license key
  ✅ Set User Limits                 - Control max users per license
  ✅ Expiration Control              - Set license expiration dates
  ✅ Multiple Tiers                  - Basic, Pro, Enterprise options
  ✅ Usage Tracking                  - Monitor logins per license
  ✅ Revoke Licenses                 - Disable keys when needed
  ✅ Dashboard Management            - Manage licenses visually

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP-BY-STEP DEMO:

1. START THE APP
   • The web app is running at: http://localhost:5000
   • Open in your browser

2. REGISTER AS OWNER
   • Click "Register"
   • Username: admin
   • Password: admin123
   • Register account

3. LOGIN AS OWNER
   • Click "Login"
   • Username: admin
   • Password: admin123
   • Sign in to dashboard

4. GENERATE LICENSE KEY
   • Scroll to "🔑 License Key Management"
   • Click "Generate License Key"
   • Set options:
     - Max Users: 2
     - Expires in Days: (leave blank)
     - Tier: Basic
   • Click "Create License"
   • Copy the generated key (e.g., LIC-ABC123...)

5. CREATE TEST USER
   • Logout
   • Click "Register"
   • Username: guest1
   • Password: guest123
   • Register

6. LOGIN WITH LICENSE KEY
   • Click "Login" tab
   • Username: guest1
   • Check "🔑 Use License Key"
   • Paste: LIC-ABC123...
   • Click "Sign In"
   • You should login successfully!

7. VIEW LICENSE STATS (as owner)
   • Logout from guest1
   • Login as admin (admin / admin123)
   • Go to dashboard
   • Click "Show My Licenses"
   • See license with 1 login tracked

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

USE CASES:

📋 TEAM ACCESS
  • Generate Pro license (5 users, 90 days)
  • Share key with team members
  • They login: username + license key
  • After 90 days, regenerate for renewal

👤 GUEST ACCESS
  • Generate Basic license (1 user, 7 days)
  • Give to guest/visitor
  • Guest uses: username + license key
  • Auto-expires after 7 days

🏢 PARTNER INTEGRATION
  • Generate Enterprise license (unlimited users)
  • Share with partner company
  • Partner distributes to their team
  • Monitor usage via dashboard

🔌 API INTEGRATION
  • Generate license for applications
  • Applications authenticate with key
  • Track usage per application
  • Revoke if security issue

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

API EXAMPLES:

curl -X POST http://localhost:5000/api/licenses/generate \\
  -H "Content-Type: application/json" \\
  -d '{
    "owner": "Company",
    "max_users": 5,
    "expires_in_days": 30,
    "tier": "pro"
  }'

curl -X POST http://localhost:5000/api/login \\
  -H "Content-Type: application/json" \\
  -d '{
    "username": "john",
    "license_key": "LIC-ABC123...",
    "use_license": true
  }'

curl http://localhost:5000/api/licenses/info/LIC-ABC123...

curl http://localhost:5000/api/licenses/list

curl -X POST http://localhost:5000/api/licenses/authorize-user \\
  -H "Content-Type: application/json" \\
  -d '{
    "license_key": "LIC-ABC123...",
    "username": "john"
  }'

curl -X POST http://localhost:5000/api/licenses/revoke/LIC-ABC123...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DOCUMENTATION:

📖 Quick Start:     LICENSE_QUICKSTART.md
📖 Full Guide:      LICENSE_KEYS_GUIDE.md
📖 Implementation:  LICENSE_IMPLEMENTATION_SUMMARY.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SECURITY FEATURES:

🔒 License Key Format:    LIC-{24 random hex chars}
🔒 User Limits:           Enforced per license
🔒 Expiration:            Optional, auto-enforced
🔒 Revocation:            Immediate & permanent
🔒 Behavioral Analysis:   Still active for license logins
🔒 Activity Tracking:     All logins logged
🔒 Session Management:    Secure session handling

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LICENSE TIERS:

🎯 BASIC
   • Max Users: 1-2
   • Use Case: Individual, testing
   • Tier Name: Basic

🎯 PRO
   • Max Users: 5-10
   • Use Case: Small teams
   • Tier Name: Pro

🎯 ENTERPRISE
   • Max Users: 100+ or unlimited
   • Use Case: Large organizations
   • Tier Name: Enterprise

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TROUBLESHOOTING:

❌ "License key not found"
   → Check key spelling & format (LIC-XXXXX)
   → Verify license hasn't been revoked
   → Make sure you copied entire key

❌ "License has expired"
   → License expiration date passed
   → Generate new license with fresh expiration

❌ "License has reached maximum users"
   → License already has max users authorized
   → Generate new license or increase limit

❌ "User not authorized for this license"
   → Your username not in license's user list
   → Contact license owner to authorize you
   → Or generate new license

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 READY TO START?

1. Open: http://localhost:5000
2. Register as: admin / admin123
3. Generate first license key
4. Share with a friend or colleague
5. They login with their username + your license key
6. Check usage stats in dashboard

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ License Key System is LIVE and READY!

Questions? Check the documentation files!
Support? Review your dashboard for stats & info!

Happy licensing! 🎉

""")

print ("\nRunning quick system check...")
try :
    from license_manager import LicenseManager 
    mgr =LicenseManager ()
    print ("✅ License system loaded successfully")
    print (f"✅ Found {len (mgr .get_all_licenses ())} existing licenses")
except Exception as e :
    print (f"❌ Error: {e }")

print ("\n"+"="*80 )
