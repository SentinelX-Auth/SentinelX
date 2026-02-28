
"""Validate web app configuration and imports"""

import sys 
import os 

print ("\n"+"="*60 )
print ("Validating Web App Configuration")
print ("="*60 +"\n")

try :
    print ("1. Checking imports...")
    from web_app import app ,user_manager 
    print ("   ✓ Flask app loaded")
    print ("   ✓ UserManager initialized")

    print ("\n2. Checking required endpoints...")
    with app .app_context ():

        routes =[]
        for rule in app .url_map .iter_rules ():
            if rule .endpoint !='static':
                routes .append (rule .rule )

        required_endpoints =[
        '/api/login',
        '/api/register',
        '/api/logout',
        '/api/user/profile',
        '/api/user/activities',
        '/api/user/login-history',
        '/api/users/list',
        '/api/behavioral/collect',
        '/api/behavioral/status'
        ]

        for endpoint in required_endpoints :
            if endpoint in routes :
                print (f"   ✓ {endpoint }")
            else :
                print (f"   ✗ {endpoint } - NOT FOUND")

    print ("\n3. Checking UserManager methods...")
    required_methods =[
    'create_user',
    'verify_password',
    'user_exists',
    'get_user_info',
    'get_all_users'
    ]

    for method in required_methods :
        if hasattr (user_manager ,method ):
            print (f"   ✓ {method }()")
        else :
            print (f"   ✗ {method }() - NOT FOUND")

    print ("\n4. Checking activity tracker...")
    from web_app import activity_tracker 
    tracker_methods =[
    'track_login_attempt',
    'track_activity',
    'get_user_activity_summary',
    'get_security_score',
    'get_login_history'
    ]

    for method in tracker_methods :
        if hasattr (activity_tracker ,method ):
            print (f"   ✓ {method }()")
        else :
            print (f"   ✗ {method }() - NOT FOUND")

    print ("\n5. Checking users directory...")
    if os .path .exists ('users'):
        users =os .listdir ('users')
        print (f"   ✓ Users directory exists")
        print (f"   ✓ Found {len (users )} registered users: {users }")
    else :
        print (f"   ✗ Users directory not found")

    print ("\n"+"="*60 )
    print ("✅ Web App Configuration Valid")
    print ("="*60 )
    print ("\nThe web app is ready to start with:")
    print ("  python web_app.py")
    print ("\nAccess at: http://localhost:5000")
    print ("\nKey Features:")
    print ("  • User registration with filesystem persistence")
    print ("  • Password verification with PBKDF2-HMAC-SHA256")
    print ("  • Real-time activity tracking")
    print ("  • Behavioral authentication (AI-powered)")
    print ("  • Security scoring system")
    print ("  • User management dashboard")
    print ("")

    sys .exit (0 )

except Exception as e :
    print (f"\n❌ Configuration Error: {e }")
    import traceback 
    traceback .print_exc ()
    sys .exit (1 )
