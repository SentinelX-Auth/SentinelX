"""
Configuration - System settings and constants
"""

DATA_COLLECTION ={
'default_duration':30 ,
'min_duration':10 ,
'max_duration':300 ,
}

MODEL_TRAINING ={
'min_enrollment_samples':3 ,
'default_enrollment_samples':5 ,
'contamination':0.1 ,
'random_state':42 ,
'n_estimators':100 ,
}

AUTHENTICATION ={
'default_threshold':-0.5 ,
'strict_threshold':-0.3 ,
'lenient_threshold':-0.7 ,
'confidence_threshold':50 ,
}

USER_MANAGEMENT ={
'users_directory':'users',
'model_filename':'model.pkl',
'metadata_filename':'metadata.json',
'session_filename_pattern':'session_{}.json',
}

LOGGING ={
'log_file':'auth_system.log',
'log_level':'INFO',
'verbose':True ,
}

FEATURES ={
'keystroke_features':10 ,
'mouse_features':13 ,
'total_features':23 ,
}

PERFORMANCE ={
'batch_size':5 ,
'max_cache_size':100 ,
'enable_optimization':True ,
}

SECURITY ={
'enable_encryption':False ,
'hash_passwords':False ,
'audit_logging':True ,
}
