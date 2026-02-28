"""
Behavioral Authentication Model - Trains and authenticates users based on behavior
"""

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
from typing import Tuple, Dict, List
from feature_extractor import FeatureExtractor

class BehavioralAuthenticationModel :
    """AI-based behavioral authentication using Isolation Forest anomaly detection"""

    def __init__ (self ,contamination :float =0.1 ):
        """
        Initialize the model
        
        Args:
            contamination: Expected proportion of outliers in dataset (0.0-0.5)
        """
        self .model =IsolationForest (
        contamination =contamination ,
        random_state =42 ,
        n_estimators =100 
        )
        self .scaler =StandardScaler ()
        self .is_trained =False 
        self .feature_names =FeatureExtractor .get_feature_names ()
        self .enrollment_data =[]

    def enroll_user (self ,behavioral_data_list :List [Dict ],num_samples :int =5 )->bool :
        """
        Enroll a new user with multiple behavioral samples
        
        Args:
            behavioral_data_list: List of behavioral data dictionaries from collection sessions
            num_samples: Number of samples needed for enrollment (default 5)
            
        Returns:
            True if enrollment successful, False otherwise
        """
        if len (behavioral_data_list )<num_samples :
            print (f"❌ Need at least {num_samples } samples for enrollment. Got {len (behavioral_data_list )}")
            return False 

        print (f"\n📝 Enrolling user with {len (behavioral_data_list )} samples...")

        feature_vectors =[]
        for data in behavioral_data_list :
            features =FeatureExtractor .extract_all_features (data )
            feature_vectors .append (features )

        self .enrollment_data =np .array (feature_vectors )

        self .scaler .fit (self .enrollment_data )
        scaled_data =self .scaler .transform (self .enrollment_data )
        self .model .fit (scaled_data )
        self .is_trained =True 

        print (f"✅ User enrolled successfully with {len (feature_vectors )} behavior samples")
        return True 

    def authenticate (self ,behavioral_data :Dict ,threshold :float =-0.5 )->Tuple [bool ,float ,str ]:
        """
        Authenticate a user based on behavioral data
        
        Args:
            behavioral_data: Behavioral data from a login attempt
            threshold: Anomaly score threshold (lower = stricter). Default -0.5
            
        Returns:
            Tuple of (is_authentic: bool, confidence: float, message: str)
        """
        if not self .is_trained :
            return False ,0.0 ,"❌ Model not trained. Please enroll user first."

        test_features =FeatureExtractor .extract_all_features (behavioral_data )
        test_features =test_features .reshape (1 ,-1 )

        scaled_features =self .scaler .transform (test_features )
        anomaly_score =self .model .score_samples (scaled_features )[0 ]
        prediction =self .model .predict (scaled_features )[0 ]

        confidence = float(max(0, min(100, (anomaly_score - threshold) * 100)))

        is_authentic = bool(prediction == 1)

        if is_authentic :
            message =f"✅ Authentication SUCCESSFUL | Confidence: {confidence :.1f}%"
        else :
            message =f"❌ Authentication FAILED | Anomaly Score: {anomaly_score :.3f}"

        return is_authentic, confidence, message

    def save_model (self ,filename :str ):
        """Save trained model and scaler"""
        joblib .dump ((self .model ,self .scaler ,self .is_trained ),filename )
        print (f"✅ Model saved to {filename }")

    def load_model (self ,filename :str ):
        """Load trained model and scaler"""
        self .model ,self .scaler ,self .is_trained =joblib .load (filename )
        print (f"✅ Model loaded from {filename }")

    def get_model_info (self )->Dict :
        """Get information about the trained model"""
        return {
        'is_trained':self .is_trained ,
        'enrollment_samples':len (self .enrollment_data ),
        'feature_count':len (self .feature_names ),
        'feature_names':self .feature_names ,
        'model_type':'Isolation Forest'
        }
