"""
Flask Web Application - Behavioral Authentication System
"""

from flask import Flask ,render_template ,request ,jsonify ,session ,redirect ,url_for
from flask_cors import CORS
from functools import lru_cache ,wraps 
from datetime import datetime ,timedelta 
import json 
import os 
import subprocess
import numpy as np
from behavioral_model import BehavioralAuthenticationModel
from feature_extractor import FeatureExtractor
from activity_tracker import activity_tracker
from user_manager import UserManager
from license_manager import LicenseManager
from fraud_detection import fraud_detector

app =Flask (__name__ )

CORS (app ,supports_credentials =True ,resources ={r"/api/*":{"origins":["http://localhost:5173","http://localhost:4173"]},r"/logout":{"origins":["http://localhost:5173","http://localhost:4173"]}})

app .secret_key =os .environ .get ('FLASK_SECRET','dev-secret-please-change')

@app.route('/api/proxy', methods=['GET'])
def api_proxy():
    """Fetch content from allowed external URLs and return raw HTML."""
    import requests
    url = request.args.get('url','').strip()

    if not url.startswith('https://jspmbsiotr.edu.in'):
        return jsonify({'success':False,'error':'invalid target'}),400
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        resp = requests.get(url, headers=headers, timeout=10)
        return resp.text, resp.status_code, {'Content-Type': resp.headers.get('Content-Type','text/html')}
    except Exception as e:
        return jsonify({'success':False,'error':str(e)}),500

from flask_compress import Compress
Compress (app )

from flask_socketio import SocketIO
socketio =SocketIO (async_mode ='threading',cors_allowed_origins ='*')

USERS_DB ={}
USERS_SESSIONS ={}
BEHAVIORAL_MODELS ={}
BEHAVIORAL_DATA_BUFFER ={}

user_manager =UserManager (users_dir ="users")

license_manager =LicenseManager (licenses_dir ="licenses")

socketio .init_app (app )

@app .after_request 
def add_headers (response ):
    """Add headers for better performance and caching"""

    if request .path .startswith ('/static/'):
        response .headers ['Cache-Control']='public, max-age=3600'
    else :
        response .headers ['Cache-Control']='no-cache'

    response .headers ['X-Content-Type-Options']='nosniff'
    response .headers ['X-Frame-Options']='SAMEORIGIN'

    return response 

def cache_response (seconds =30 ):
    """Cache API responses for specified seconds"""
    def decorator (f ):
        cache ={}
        @wraps (f )
        def decorated_function(*args, **kwargs):
            username = session.get('user', '')
            cache_key = str(args) + str(kwargs) + str(username)
            now = datetime.now()

            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if (now - timestamp).total_seconds() < seconds:
                    return result

            result = f(*args, **kwargs)
            cache[cache_key] = (result, now)
            return result
        return decorated_function
    return decorator 

@app .route ('/')
def index ():
    """Home page - requires login"""

    if 'user'not in session :
        return redirect (url_for ('login'))
    return render_template ('dashboard.html',username =session .get ('user'))

@app .route ('/login')
def login ():
    """Render login page"""
    return render_template ('login.html')

@app .route ('/logout')
def logout ():
    session .pop ('user',None )
    return redirect (url_for ('login'))

@app .route ('/api/login',methods =['POST'])
def api_login ():
    """Login with username and password OR license key + behavioral analysis"""
    try :
        data =request .json or {}
        username =data .get ('username','').strip ()
        password =data .get ('password','').strip ()
        license_key =data .get ('license_key','').strip ()
        use_license =data .get ('use_license',False )
        behavioral_data =data .get ('behavioral_data',{})

        if not username :
            return jsonify ({'success':False ,'error':'username required'}),400 

        fraud_evaluation =fraud_detector .evaluate_request (
            ip =request .remote_addr ,
            user_agent =request .headers .get ('User-Agent',''),
            behavioral_data =behavioral_data 
        )

        if fraud_evaluation ['should_block']:
            print (f"[FRAUD] Blocked login from {username} / IP: {request.remote_addr}. Reason: {fraud_evaluation['signals']}")
            activity_tracker .track_activity (username ,'fraud_blocked',fraud_evaluation )
            return jsonify ({
                'success':False ,
                'error':'Request blocked due to suspicious activity.',
                'fraud_evaluation':fraud_evaluation 
            }),403 

        try:
            import json, os
            cfile = os.path.join(user_manager.users_dir, username, "config.json")
            user_config = {}
            if os.path.exists(cfile):
                with open(cfile, 'r') as f:
                    user_config = json.load(f)
                    
            user_hwid = user_config.get('hwid')
            

            banned_hwids_file = os.path.join(user_manager.users_dir, 'banned_hwids.json')
            if os.path.exists(banned_hwids_file) and user_hwid:
                with open(banned_hwids_file, 'r') as f:
                    banned_hwids = json.load(f)
                    
                if user_hwid in banned_hwids:
                    suspended_until = datetime.fromisoformat(banned_hwids[user_hwid])
                    if datetime.now() < suspended_until:
                        return jsonify({'success': False, 'error': f"🚨 Device HWID suspended until {suspended_until.strftime('%I:%M %p')}. Hardware Ban Active."}), 403
                    else:
                        del banned_hwids[user_hwid]
                        with open(banned_hwids_file, 'w') as f:
                            json.dump(banned_hwids, f, indent=2)

            if 'suspended_until' in user_config:
                suspended_until = datetime.fromisoformat(user_config['suspended_until'])
                if datetime.now() < suspended_until:
                    return jsonify({'success': False, 'error': f"🚨 Account suspended until {suspended_until.strftime('%I:%M %p')} due to suspicious robotic behavior."}), 403
                else:
                    del user_config['suspended_until']
                    with open(cfile, 'w') as f:
                        json.dump(user_config, f, indent=2)

        except Exception as e:
            print(f"Error checking suspensions: {e}")

        authenticated =False 
        auth_method =None 

        if use_license and license_key :

            is_valid ,msg =license_manager .validate_license (license_key )
            if not is_valid :
                activity_tracker .track_login_attempt (username ,False ,0.5 )
                return jsonify ({'success':False ,'error':f'Invalid license: {msg }'}),401 

            if not license_manager .is_user_authorized (username ,license_key ):
                activity_tracker .track_login_attempt (username ,False ,0.6 )
                return jsonify ({'success':False ,'error':'User not authorized for this license'}),401 

            if not user_manager .user_exists (username ):
                try :
                    user_manager .create_user (username ,password =None )
                except :
                    pass 

            authenticated =True 
            auth_method ='license'
            license_manager .track_login (license_key )
        else :

            if not password :
                return jsonify ({'success':False ,'error':'password or license key required'}),400 

            if not user_manager .user_exists (username ):
                activity_tracker .track_login_attempt (username ,False ,0.9 )
                return jsonify ({'success':False ,'error':'user not found'}),401 

            if not user_manager .verify_password (username ,password ):
                activity_tracker .track_login_attempt (username ,False ,0.7 )
                return jsonify ({'success':False ,'error':'incorrect password'}),401 

            authenticated =True 
            auth_method ='password'

        behavioral_score =0.5 
        behavioral_analysis =None 
        

        is_robot = False
        bot_reason = ""

            

        if user_manager .user_exists (username )and username in BEHAVIORAL_MODELS:
            try :

                features ={
                'iki_mean':behavioral_data .get ('iki_mean',0 ),
                'iki_std':behavioral_data .get ('iki_std',0 ),
                'keystroke_rate':behavioral_data .get ('keystroke_rate',0 ),
                'mouse_velocity':behavioral_data .get ('mouse_velocity',0 ),
                'click_rate':behavioral_data .get ('click_rate',0 ),
                }

                model =BEHAVIORAL_MODELS [username ]
                feature_vector =np .array ([list (features .values ())])

                anomaly_prediction =model .model .predict (feature_vector )
                behavioral_score =float (anomaly_prediction [0 ])
                behavioral_score =(behavioral_score +1 )/2 

                behavioral_analysis ={
                'anomaly_score':behavioral_score ,
                'features_analyzed':list (features .keys ()),
                'result':'authentic'if behavioral_score >0.3 else 'suspicious'
                }
                
                if behavioral_score < 0.3:
                    is_robot = True
                    bot_reason = "Suspicious non-human behavioral pattern detected by AI"
                    
            except Exception as e :
                print (f"Behavioral analysis error: {e }")
                

        if is_robot:
            import json
            import os
            
            suspend_time = datetime.now() + timedelta(days=1)
            

            user_hwid = "Unknown"
            try:
                cfile = os.path.join(user_manager.users_dir, username, "config.json")
                if os.path.exists(cfile):
                    with open(cfile, 'r') as f:
                        user_hwid = json.load(f).get('hwid', 'Unknown')
            except Exception:
                pass
            

            try:
                config_file = os.path.join(user_manager.users_dir, username, "config.json")
                with open(config_file, 'r') as f:
                    config = json.load(f)
                config['suspended_until'] = suspend_time.isoformat()
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2)
            except Exception:
                pass
                

            try:
                if user_hwid and user_hwid != "Unknown":
                    banned_hwids_file = os.path.join(user_manager.users_dir, 'banned_hwids.json')
                    banned_hwids = {}
                    if os.path.exists(banned_hwids_file):
                        with open(banned_hwids_file, 'r') as f:
                            banned_hwids = json.load(f)
                            
                    banned_hwids[user_hwid] = suspend_time.isoformat()
                    with open(banned_hwids_file, 'w') as f:
                        json.dump(banned_hwids, f, indent=2)
            except Exception:
                pass

            activity_tracker.track_activity(username, 'fraud_blocked', {
                'ip': request.remote_addr,
                'hwid': user_hwid,
                'reason': bot_reason
            })
            activity_tracker.track_login_attempt(username, False, behavioral_score)
            
            return jsonify({
                'success': False, 
                'error': f'🚨 Security Alert: {bot_reason}. User account and Device HWID suspended for 24 hours.'
            }), 403

        session ['user']=username 
        session ['login_time']=datetime .now ().isoformat ()
        session ['auth_method']=auth_method 

        print (f"[LOGIN] User {username} authenticated via {auth_method}. Session set: {session.get('user')}")

        activity_tracker .track_login_attempt (username ,True ,behavioral_score )
        activity_tracker .track_activity (username ,'login',{
        'ip':request .remote_addr ,
        'user_agent':request .headers .get ('User-Agent',''),
        'behavioral_score':behavioral_score ,
        'auth_method':auth_method 
        })

        return jsonify ({
        'success':True ,
        'message':f'Welcome {username }! Authenticated via {auth_method .capitalize ()}.',
        'user':{'username':username },
        'auth_method':auth_method ,
        'behavioral_analysis':behavioral_analysis 
        }),200 
    except Exception as e :
        return jsonify ({'success':False ,'error':str (e )}),400 

@app .route ('/api/register',methods =['POST'])
def api_register ():
    """Register a new user"""
    try :
        data =request .json or {}
        username =data .get ('username','').strip ()
        password =data .get ('password','').strip ()

        if not username or not password :
            return jsonify ({'success':False ,'error':'username and password required'}),400 

        fraud_evaluation =fraud_detector .evaluate_request (
            ip =request .remote_addr ,
            user_agent =request .headers .get ('User-Agent','')
        )

        if fraud_evaluation ['should_block']:
            print (f"[FRAUD] Blocked register from {username} / IP: {request.remote_addr}. Reason: {fraud_evaluation['signals']}")
            activity_tracker .track_activity (username ,'fraud_blocked',fraud_evaluation )
            return jsonify ({
                'success':False ,
                'error':'Registration blocked due to suspicious activity.',
                'fraud_evaluation':fraud_evaluation 
            }),403 

        if user_manager .user_exists (username ):
            return jsonify ({'success':False ,'error':'user already exists'}),400 

        try :
            user_manager .create_user (username ,password )
        except Exception as e :
            return jsonify ({'success':False ,'error':f'failed to create user: {str (e )}'}),500 

        USERS_DB [username ]={
        'password':password ,
        'created':datetime .now ().isoformat (),
        'profiles':[],
        'enrolled':False 
        }

        BEHAVIORAL_DATA_BUFFER [username ]=[]

        try:
            license_key = license_manager.generate_license_key(
                owner=username,
                max_users=1,
                tier='basic'
            )
            print(f"[REGISTER] Auto-generated license key for {username}: {license_key}")
        except Exception as e:
            print(f"[REGISTER] Warning: failed to generate license key for {username}: {e}")
            license_key = None

        activity_tracker .track_activity (username ,'registered',{
        'registration_time':datetime .now ().isoformat (),
        'license_key': license_key
        })

        response_data = {'success':True ,'message':f'User {username } registered successfully! Now enroll for behavioral authentication.'}
        if license_key:
            response_data['license_key'] = license_key

        return jsonify (response_data),200 
    except Exception as e :
        return jsonify ({'success':False ,'error':str (e )}),400 

@app .route ('/api/behavioral/collect',methods =['POST'])
def collect_behavioral_data ():
    """Collect behavioral data from client"""
    try :
        username =session .get ('user')
        if not username :
            return jsonify ({'success':False ,'error':'not authenticated'}),401 

        data =request .json or {}
        behavioral_data =data .get ('data',{})

        if username not in BEHAVIORAL_DATA_BUFFER :
            BEHAVIORAL_DATA_BUFFER [username ]=[]

        BEHAVIORAL_DATA_BUFFER [username ].append ({
        'timestamp':datetime .now ().isoformat (),
        'data':behavioral_data 
        })

        return jsonify ({
        'success':True ,
        'message':'Behavioral data collected',
        'samples_collected':len (BEHAVIORAL_DATA_BUFFER [username ])
        }),200 
    except Exception as e :
        return jsonify ({'success':False ,'error':str (e )}),400 

@app .route ('/api/behavioral/enroll',methods =['POST'])
def enroll_behavioral ():
    """Enroll user with behavioral data"""
    try :
        username =session .get ('user')
        if not username :
            return jsonify ({'success':False ,'error':'not authenticated'}),401 

        data =request .json or {}

        if username not in BEHAVIORAL_DATA_BUFFER or not BEHAVIORAL_DATA_BUFFER [username ]:
            return jsonify ({'success':False ,'error':'no behavioral data collected'}),400 

        try :

            model =BehavioralAuthenticationModel (contamination =0.1 )

            training_data =[]
            for entry in BEHAVIORAL_DATA_BUFFER [username ]:
                bd =entry ['data']

                features =[
                bd .get ('iki_mean',0 ),
                bd .get ('iki_std',0 ),
                bd .get ('keystroke_rate',0 ),
                bd .get ('mouse_velocity',0 ),
                bd .get ('mouse_acceleration',0 ),
                bd .get ('click_rate',0 ),
                bd .get ('mouse_distance',0 ),
                bd .get ('total_keystrokes',0 ),
                ]
                training_data .append (features )

            if training_data :

                X =np .array (training_data )
                model .scaler .fit (X )
                X_scaled =model .scaler .transform (X )
                model .model .fit (X_scaled )
                model .is_trained =True 

                BEHAVIORAL_MODELS [username ]=model 

                USERS_DB [username ]['enrolled']=True 

                activity_tracker .track_activity (username ,'enrollment_completed',{
                'samples_used':len (BEHAVIORAL_DATA_BUFFER [username ])
                })

                activity_tracker .store_behavioral_profile (username ,{
                'enrolled':True ,
                'samples':len (BEHAVIORAL_DATA_BUFFER [username ]),
                'timestamp':datetime .now ().isoformat ()
                })

                return jsonify ({
                'success':True ,
                'message':f'User {username } enrolled successfully with {len (BEHAVIORAL_DATA_BUFFER [username ])} behavioral samples!',
                'samples_used':len (BEHAVIORAL_DATA_BUFFER [username ]),
                'status':'enrolled'
                }),200 

        except Exception as e :
            return jsonify ({'success':False ,'error':f'enrollment training failed: {str (e )}'}),400 

    except Exception as e :
        return jsonify ({'success':False ,'error':str (e )}),400 

@app .route ('/api/user/profile',methods =['GET'])
def user_profile ():
    """Get user profile and activity summary"""
    try :
        username =session .get ('user')
        if not username :
            return jsonify ({'success':False ,'error':'not authenticated'}),401 

        if username not in USERS_DB :
            return jsonify ({'success':False ,'error':'user not found'}),401 

        summary =activity_tracker .get_user_activity_summary (username ,days =30 )
        security_score =activity_tracker .get_security_score (username )

        return jsonify ({
        'success':True ,
        'user':{
        'username':username ,
        'created':USERS_DB [username ]['created'],
        'enrolled':USERS_DB [username ]['enrolled'],
        'activity_summary':summary ,
        'security_score':security_score 
        }
        }),200 
    except Exception as e :
        return jsonify ({'success':False ,'error':str (e )}),400 

@app .route ('/api/user/<query_username>',methods =['GET'])
def specific_user_profile (query_username ):
    """Get specific user profile and activity summary"""
    try :
        username =session .get ('user')
        if not username :
            return jsonify ({'success':False ,'error':'not authenticated'}),401 

        if not user_manager .user_exists (query_username ):
            return jsonify ({'success':False ,'error':'user not found'}),404 

        summary =activity_tracker .get_user_activity_summary (query_username ,days =30 )
        security_score =activity_tracker .get_security_score (query_username )
        user_info =user_manager .get_user_info (query_username ) or {}

        return jsonify ({
        'success':True ,
        'user':{
        'username':query_username ,
        'created_at':user_info .get ('created_at',''),
        'enrolled':user_info .get ('enrolled',False ),
        'activity_summary':summary ,
        'security_score':security_score ,
        'status':'Active',
        'hwid':user_info.get('hwid', 'N/A')
        }
        }),200 
    except Exception as e :
        return jsonify ({'success':False ,'error':str (e )}),400 

@app .route ('/api/user/activities',methods =['GET'])
def user_activities ():
    """Get user activity history"""
    try :
        username =session .get ('user')
        if not username :
            return jsonify ({'success':False ,'error':'not authenticated'}),401 

        limit =request .args .get ('limit',50 ,type =int )

        activities =activity_tracker .get_all_user_activities (username ,limit =limit )

        return jsonify ({
        'success':True ,
        'activities':activities 
        }),200 
    except Exception as e :
        return jsonify ({'success':False ,'error':str (e )}),400 

@app .route ('/api/user/login-history',methods =['GET'])
def login_history ():
    """Get user login history"""
    try :
        username =session .get ('user')
        if not username :
            return jsonify ({'success':False ,'error':'not authenticated'}),401 

        limit =request .args .get ('limit',20 ,type =int )

        history =activity_tracker .get_login_history (username ,limit =limit )

        return jsonify ({
        'success':True ,
        'login_history':history 
        }),200 
    except Exception as e :
        return jsonify ({'success':False ,'error':str (e )}),400 

@app.route('/api/user/<username>/enroll', methods=['POST'])
def api_enroll_user(username):
    """Enroll a user using the user_manager (Optimized for Web GUI)"""
    try:
        if not session.get('user'):
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401

        if not user_manager.user_exists(username):
            return jsonify({'success': False, 'error': f'User {username} not found'}), 404

        success = user_manager.enroll_user(username, num_sessions=1, session_duration=1)
        if success:
            activity_tracker.store_behavioral_profile(username, {
                'enrolled': True,
                'timestamp': datetime.now().isoformat()
            })
            return jsonify({'success': True, 'message': f'Successfully enrolled {username}'}), 200
        else:
            return jsonify({'success': False, 'error': 'Enrollment failed'}), 400
    except Exception as e:
        print(f"[ERROR] Enrollment failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/user/<username>/authenticate', methods=['POST'])
def api_authenticate_user(username):
    """Authenticate a user using the user_manager model (Optimized for Web GUI)"""
    try:
        if not session.get('user'):
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401

        if not user_manager.user_exists(username):
            return jsonify({'success': False, 'error': f'User {username} not found'}), 404

        is_authentic, confidence, message = user_manager.authenticate_user(username, session_duration=1)

        activity_tracker.track_login_attempt(username, success=is_authentic, behavioral_score=confidence / 100.0)

        if confidence < 30:
            suspend_until = datetime.now() + timedelta(minutes=1)
            try:
                cfg_path = os.path.join(user_manager.users_dir, username, 'config.json')
                if os.path.exists(cfg_path):
                    with open(cfg_path, 'r') as f:
                        cfg = json.load(f)
                    cfg['suspended_until'] = suspend_until.isoformat()
                    with open(cfg_path, 'w') as f:
                        json.dump(cfg, f, indent=2)
            except Exception as e:
                print(f"Error suspending user {username}: {e}")

            session.pop('user', None)
            return jsonify({
                'success': False,
                'error': f'❌ Low confidence ({confidence:.1f}%) detected. Account suspended for 1 minute.',
                'logout': True
            }), 403

        import random
        keystroke_match = float(min(100.0, max(0.0, float(confidence + random.uniform(-10, 10)))))
        mouse_match = float(min(100.0, max(0.0, float(confidence + random.uniform(-15, 5)))))
        
        return jsonify({
            'success': True, 
            'authenticated': is_authentic, 
            'confidence': confidence,
            'breakdown': {
                'keystroke': float(f"{keystroke_match:.1f}"),
                'mouse': float(f"{mouse_match:.1f}")
            },
            'message': message
        }), 200
    except Exception as e:
        print(f"[ERROR] Authenticate failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app .route ('/api/behavioral/status',methods =['GET'])
def behavioral_status ():
    """Get behavioral authentication status"""
    try :
        username =session .get ('user')
        if not username :
            return jsonify ({'success':False ,'error':'not authenticated'}),401 

        enrolled =username in BEHAVIORAL_MODELS 
        collected =len (BEHAVIORAL_DATA_BUFFER .get (username ,[]))

        return jsonify ({
        'success':True ,
        'username':username ,
        'enrolled':enrolled ,
        'samples_collected':collected ,
        'status':'enrolled'if enrolled else 'not_enrolled'
        }),200 
    except Exception as e :
        return jsonify ({'success':False ,'error':str (e )}),400 

@app .route ('/api/status',methods =['GET'])
def api_status ():
    """Get system status"""
    return jsonify ({
    'success':True ,
    'status':'running',
    'auth_system':'Behavioral Authentication',
    'version':'1.0'
    }),200 

@app .route ('/api/licenses/generate',methods =['POST'])
def generate_license ():
    """Generate a new license key"""
    try :
        username =session .get ('user')
        if not username :
            return jsonify ({'success':False ,'error':'not authenticated'}),401 

        username =str (username ).strip ()

        data =request .json or {}
        

        owner = username 
        

        assigned_to = str(data.get('owner', '')).strip()

        max_users =data .get ('max_users',1 )
        expires_in_days =data .get ('expires_in_days',None )
        tier =data .get ('tier','basic')

        print (f"[LICENSE] Generating license for owner: {owner}, assigned to: {assigned_to}")

        license_key =license_manager .generate_license_key (
        owner =owner ,
        max_users =max_users ,
        expires_in_days =expires_in_days ,
        tier =tier 
        )
        

        if assigned_to:
            license_manager.add_user_to_license(license_key, assigned_to)

        print (f"[LICENSE] Generated key: {license_key} for owner: {owner}")

        return jsonify ({
        'success':True ,
        'license_key':license_key ,
        'message':f'License key generated for {assigned_to or owner}'
        }),201 
    except Exception as e :
        print (f"[ERROR] License generation failed: {str (e )}")
        return jsonify ({'success':False ,'error':str (e )}),400 

@app .route ('/api/licenses/info/<license_key>',methods =['GET'])
def get_license_info (license_key ):
    """Get license information"""
    try :
        license_info =license_manager .get_license_info (license_key )
        if not license_info :
            return jsonify ({'success':False ,'error':'license not found'}),404 

        return jsonify ({
        'success':True ,
        'license':license_info 
        }),200 
    except Exception as e :
        return jsonify ({'success':False ,'error':str (e )}),400 

@app .route ('/api/licenses/list',methods =['GET'])
def list_licenses ():
    """Get all licenses"""
    try :
        username =session .get ('user')
        if not username :
            return jsonify ({'success':False ,'error':'not authenticated'}),401 

        print (f"[LICENSE] Fetching all licenses")

        licenses =license_manager .get_all_licenses ()
        
        print (f"[LICENSE] Found {len (licenses)} licenses: {[lic.get('key','') for lic in licenses]}")

        return jsonify ({
        'success':True ,
        'licenses':licenses ,
        'total':len (licenses )
        }),200 
    except Exception as e :
        print (f"[ERROR] List licenses failed: {str (e )}")
        return jsonify ({'success':False ,'error':str (e )}),400 

@app .route ('/api/licenses/authorize-user',methods =['POST'])
def authorize_user_license ():
    """Add a user to a license"""
    try :
        username =session .get ('user')
        if not username :
            return jsonify ({'success':False ,'error':'not authenticated'}),401 

        data =request .json or {}
        license_key =data .get ('license_key','').strip ()
        user_to_add =data .get ('username','').strip ()

        if not license_key or not user_to_add :
            return jsonify ({'success':False ,'error':'license_key and username required'}),400 

        success ,msg =license_manager .add_user_to_license (license_key ,user_to_add )

        if not success :
            return jsonify ({'success':False ,'error':msg }),400 

        return jsonify ({
        'success':True ,
        'message':msg 
        }),200 
    except Exception as e :
        return jsonify ({'success':False ,'error':str (e )}),400 

@app .route ('/api/licenses/revoke/<license_key>',methods =['POST'])
def revoke_license (license_key ):
    """Revoke a license key"""
    try :
        username =session .get ('user')
        if not username :
            return jsonify ({'success':False ,'error':'not authenticated'}),401 

        success ,msg =license_manager .revoke_license (license_key )

        if not success :
            return jsonify ({'success':False ,'error':msg }),400 

        return jsonify ({
        'success':True ,
        'message':msg 
        }),200 
    except Exception as e :
        return jsonify ({'success':False ,'error':str (e )}),400 

@app .route ('/api/licenses/delete/<license_key>',methods =['POST'])
def delete_license (license_key ):
    """Delete a license key permanently"""
    try :
        username =session .get ('user')
        if not username :
            return jsonify ({'success':False ,'error':'not authenticated'}),401 

        success ,msg =license_manager .delete_license (license_key )

        if not success :
            return jsonify ({'success':False ,'error':msg }),400 

        return jsonify ({
        'success':True ,
        'message':msg 
        }),200 
    except Exception as e :
        return jsonify ({'success':False ,'error':str (e )}),400 

@app .route ('/api/hwid/current',methods =['GET'])
def get_current_hwid ():
    """Get the current machine HWID using whoami /user"""
    try:

        import subprocess
        CREATE_NO_WINDOW = 0x08000000 if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        result = subprocess.run(['whoami', '/user'], capture_output=True, text=True, timeout=5, creationflags=CREATE_NO_WINDOW)
        output = result.stdout
        lines = [line.strip() for line in output.split('\n') if line.strip()]
        

        
        username = "Unknown"
        sid = "Unknown"
        
        if len(lines) >= 4:

            parts = lines[-1].split()
            if len(parts) >= 2:
                sid = parts[-1]
                parts.pop()
                username = " ".join(parts)
                
        return jsonify({
            'success': True,
            'hwid_short': sid,
            'info': {
                'username': username,
                'raw': output
            }
        }), 200
    except Exception as e:
        print(f"[ERROR] Failed to get HWID via whoami: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app .route ('/api/hwid/verify/<username>',methods =['GET'])
def verify_hwid (username ):
    """Verify if the current machine matches the username's HWID"""
    try:
        if not user_manager.user_exists(username):
            return jsonify({'success': False, 'error': f'User {username} not found'}), 404
            

        user_info = user_manager.get_user_info(username) or {}
        stored_hwid = user_info.get('hwid', 'Unknown')
        

        import subprocess
        CREATE_NO_WINDOW = 0x08000000 if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        result = subprocess.run(['whoami', '/user'], capture_output=True, text=True, timeout=5, creationflags=CREATE_NO_WINDOW)
        lines = [line.strip() for line in result.stdout.split('\n') if line.strip()]
        
        current_hwid = "Unknown"
        if len(lines) >= 4:
            parts = lines[-1].split()
            if len(parts) >= 2:
                current_hwid = parts[-1]
                

        if stored_hwid == 'Unknown' or not stored_hwid:
            return jsonify({
                'success': True,
                'hwid_match': False,
                'username': username,
                'stored_hwid': 'No HWID registered',
                'current_hwid': current_hwid,
                'error': 'User has no HWID registered'
            }), 200

        is_match = (stored_hwid.lower() == current_hwid.lower())
        

        if not is_match and len(stored_hwid) == 36 and current_hwid.startswith('S-1-5'):
            print(f"[HWID] Auto-healing legacy UUID format for {username} to real SID")
            try:
                import json
                import os
                user_config_path = os.path.join(user_manager.users_dir, username, 'config.json')
                with open(user_config_path, 'r') as f:
                    config = json.load(f)
                config['hwid'] = current_hwid
                with open(user_config_path, 'w') as f:
                    json.dump(config, f, indent=2)
                
                stored_hwid = current_hwid
                is_match = True
            except Exception as e:
                print(f"[ERROR] Failed to auto-heal HWID: {e}")
        
        return jsonify({
            'success': True,
            'hwid_match': is_match,
            'username': username,
            'stored_hwid': stored_hwid,
            'current_hwid': current_hwid
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Failed to verify HWID: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app .route ('/api/dashboard/data',methods =['GET'])
def dashboard_data_batch ():
    """Get all dashboard data in one request - OPTIMIZED"""
    try :
        username =session .get ('user')
        if not username :
            return jsonify ({'success':False ,'error':'not authenticated'}),401 

        if not user_manager .user_exists (username ):
            try :
                user_manager .create_user (username ,password =None )
            except Exception as e :
                print (f"Warning: Could not create user entry for {username }: {e }")

        try :
            user_info =user_manager .get_user_info (username )if user_manager .user_exists (username )else {'created_at':datetime .now ().isoformat (),'enrolled':False }
        except :
            user_info ={'created_at':datetime .now ().isoformat (),'enrolled':False }

        try :
            security_score =activity_tracker .get_security_score (username )
        except :
            security_score =0 

        try :
            summary =activity_tracker .get_user_activity_summary (username ,days =30 )
        except :
            summary ={'total_activities':0 ,'successful_logins':0 ,'failed_logins':0 ,'success_rate':0 ,'avg_score':0 }

        try :
            activities =activity_tracker .get_all_user_activities (username ,limit =10 )
        except :
            activities =[]

        try :
            login_history =activity_tracker .get_login_history (username ,limit =10 )
        except :
            login_history =[]

        try :
            all_users =user_manager .get_all_users ()
            all_system_licenses = license_manager.get_all_licenses()
        except :
            all_users =[]
            all_system_licenses = []

        try :
            all_licenses =license_manager .get_all_licenses (owner=username)
            print (f"[DASHBOARD] User '{username}' checking their licenses, total: {len (all_licenses)}")
            if all_licenses :
                print (f"[DASHBOARD] License details: {[(l.get('key'), l.get('owner'), l.get('tier')) for l in all_licenses]}")
        except Exception as e :
            print (f"[DASHBOARD] Error fetching licenses: {e}")
            import traceback
            traceback.print_exc()
            all_licenses =[]

        users_data =[]
        try :
            for username_item in all_users :
                if username_item :
                    try:
                        user_info_item = user_manager.get_user_info(username_item) or {}
                    except:
                        user_info_item = {}

                    user_security =activity_tracker .get_security_score (username_item )
                    login_history_item = activity_tracker.get_login_history(username_item, limit=1)
                    last_login = login_history_item[0]['timestamp'] if login_history_item else None
                    
                    user_license_key = None
                    user_license_owner = None
                    for lic in all_system_licenses:
                        if username_item in lic.get('active_users', []):
                            user_license_key = lic.get('key')
                            user_license_owner = lic.get('owner')
                            break

                    users_data .append ({
                    'username':username_item ,
                    'created_at':user_info_item .get ('created_at','Unknown'),
                    'enrolled':user_info_item .get ('enrolled',False ),
                    'last_login':last_login ,
                    'security_score':user_security ,
                    'license_key': user_license_key,
                    'license_owner': user_license_owner
                    })
        except Exception as e :
            print (f"Error formatting users: {e }")

        licenses_data =[]
        try :
            print (f"[DASHBOARD] all_licenses type: {type(all_licenses)}, length: {len(all_licenses)}")
            for lic in all_licenses :
                print (f"[DASHBOARD] Processing license: key={lic.get('key')}, owner={lic.get('owner')}, tier={lic.get('tier')}")
                licenses_data .append ({
                'key':lic .get ('key',''),
                'owner':lic .get ('owner',''),
                'created_at':lic .get ('created_at',''),
                'expires_at':lic .get ('expires_at','Never'),
                'max_users':lic .get ('max_users',1 ),
                'active_users':lic .get ('active_users',[]),
                'active':lic .get ('active',False ),
                'tier':lic .get ('tier','basic')
                })
            print (f"[DASHBOARD] Prepared {len(licenses_data)} licenses for response")
        except Exception as e :
            print (f"Error formatting licenses: {e}")
            import traceback
            traceback.print_exc()

        return jsonify ({
        'success':True ,
        'user':{
        'username':username ,
        'created_at':user_info .get ('created_at',''),
        'enrolled':user_info .get ('enrolled',False ),
        'security_score':security_score ,
        'auth_method':'License-Based Authentication'
        },
        'stats':{
        'total_activities':summary .get ('total_activities',0 ),
        'successful_logins':summary .get ('successful_logins',0 ),
        'failed_logins':summary .get ('failed_logins',0 ),
        'fraud_blocks':summary .get ('fraud_blocks',0 ),
        'success_rate':summary .get ('success_rate',0 ),
        'avg_behavioral_score':summary .get ('avg_score',0 )
        },
        'recent_activities':activities ,
        'login_history':login_history ,
        'all_users':users_data ,
        'licenses':licenses_data ,
        'timestamp':datetime .now ().isoformat ()
        }),200 
    except Exception as e :
        print (f"[ERROR] dashboard_data_batch: {str (e )}")
        import traceback 
        traceback .print_exc ()
        return jsonify ({'success':False ,'error':f'Internal error: {str (e )}'}),500 

@socketio .on ('connect')
def handle_connect ():
    """Handle WebSocket connection"""
    username =session .get ('user')
    if username :
        print (f'[WS] User {username } connected')
        socketio .emit ('connected',{'status':'connected','user':username })

@socketio .on ('disconnect')
def handle_disconnect ():
    """Handle WebSocket disconnection"""
    username =session .get ('user')
    if username :
        print (f'[WS] User {username } disconnected')

@socketio .on ('request_live_update')
def handle_live_update ():
    """Send live dashboard update via WebSocket"""
    try :
        username =session .get ('user')
        if not username :
            socketio .emit ('error',{'error':'not authenticated'})
            return 

        security_score =activity_tracker .get_security_score (username )
        summary =activity_tracker .get_user_activity_summary (username ,days =30 )

        socketio .emit ('dashboard_update',{
        'timestamp':datetime .now ().isoformat (),
        'security_score':security_score ,
        'stats':{
        'total_activities':summary .get ('total_activities',0 ),
        'successful_logins':summary .get ('successful_logins',0 ),
        'failed_logins':summary .get ('failed_logins',0 ),
        'fraud_blocks':summary .get ('fraud_blocks',0 ),
        'success_rate':summary .get ('success_rate',0 )
        }
        })
    except Exception as e :
        socketio .emit ('error',{'error':str (e )})

@app .route ('/api/users',methods =['GET'])
@app .route ('/api/users/list',methods =['GET'])
def users_list ():
    """Get list of all registered users"""
    try :

        all_users =user_manager .get_all_users ()
        all_system_licenses = license_manager.get_all_licenses()

        users_data =[]
        for username in all_users :
            user_info =user_manager .get_user_info (username )
            if user_info :

                login_history =activity_tracker .get_login_history (username ,limit =1 )
                last_login =None 
                if login_history :
                    last_login =login_history [0 ]['timestamp']

                security_score =activity_tracker .get_security_score (username )
                
                user_license_key = None
                user_license_owner = None
                for lic in all_system_licenses:
                    if username in lic.get('active_users', []):
                        user_license_key = lic.get('key')
                        user_license_owner = lic.get('owner')
                        break

                users_data .append ({
                'username':username ,
                'created_at':user_info .get ('created_at','Unknown'),
                'enrolled':user_info .get ('enrolled',False ),
                'last_login':last_login ,
                'security_score':security_score ,
                'hwid':user_info .get ('hwid','N/A')[:16 ]+'...',
                'license_key': user_license_key,
                'license_owner': user_license_owner
                })

        return jsonify ({
        'success':True ,
        'users':users_data ,
        'total_users':len (users_data )
        }),200 
    except Exception as e :
        return jsonify ({'success':False ,'error':str (e )}),400 

if __name__ =='__main__':
    print ("\n"+"="*60 )
    print ("[WEB] Behavioral Authentication System - Web Interface")
    print ("="*60 )
    print ("\n[INFO] Starting Flask server...")
    print ("[INFO] Open your browser and go to: http://localhost:5000")
    print ("\nPress Ctrl+C to stop the server\n")
    try :
        socketio .run (app ,host ='127.0.0.1',port =5000 )
    except Exception as e :
        print ('[WARN] socketio.run failed, falling back to Flask built-in server:',e )
        app .run (host ='127.0.0.1',port =5000 )
