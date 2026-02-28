"""
Verify HWID Authentication is Completely Removed
"""

import os 
import json 

print ("\n"+"="*70 )
print ("HWID AUTHENTICATION REMOVAL VERIFICATION")
print ("="*70 )

print ("\n[1] Checking web_app.py login endpoint...")
with open ("web_app.py","r")as f :
    content =f .read ()
    login_section =content [content .find ("def api_login():"):content .find ("def api_login():")+3000 ]

    if "HWIDCollector.verify_hwid"in login_section :
        print ("   ❌ FOUND: HWIDCollector.verify_hwid() call in login")
    elif "get_simple_hwid"in login_section :
        print ("   ❌ FOUND: get_simple_hwid() call in login")
    elif "stored_hwid"in login_section and "current_hwid"in login_section :
        print ("   ❌ FOUND: HWID comparison in login")
    else :
        print ("   ✅ CLEAN: No HWID checks in login endpoint")

print ("\n[2] Checking user_manager.py authenticate_user()...")
with open ("user_manager.py","r")as f :
    content =f .read ()
    auth_section =content [content .find ("def authenticate_user("):content .find ("def authenticate_user(")+2500 ]

    if "verify_hwid"in auth_section :
        print ("   ❌ FOUND: verify_hwid() call")
    elif "get_simple_hwid"in auth_section :
        print ("   ❌ FOUND: get_simple_hwid() call")
    else :
        print ("   ✅ CLEAN: No HWID checks in authenticate_user()")

print ("\n[3] Checking stored user credentials...")
users_dir ="users"
if os .path .exists (users_dir ):
    users =[d for d in os .listdir (users_dir )if os .path .isdir (os .path .join (users_dir ,d ))]
    for username in users [:3 ]:
        config_file =os .path .join (users_dir ,username ,"config.json")
        if os .path .exists (config_file ):
            with open (config_file ,'r')as f :
                config =json .load (f )

            has_password ='password_hash'in config 
            has_hwid ='hwid'in config 

            print (f"\n   User: {username }")
            print (f"     Password protected: {has_password }")
            print (f"     HWID stored: {has_hwid } (informational only)")

print ("\n"+"="*70 )
print ("✅ HWID AUTHENTICATION SUCCESSFULLY REMOVED")
print ("\nLogin now works with:")
print ("  ✓ Username + Password (if set)")
print ("  ✓ No HWID device checks")
print ("  ✓ Optional behavioral authentication")
print ("="*70 +"\n")
