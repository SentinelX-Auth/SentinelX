"""
Feature Extractor - Extracts behavioral biometric features from raw data
"""

import numpy as np 
from typing import Dict ,List ,Tuple 

class FeatureExtractor :
    """Extract behavioral biometric features from keystroke and mouse data"""

    @staticmethod 
    def extract_keystroke_features (keystroke_data :List [Dict ])->Dict :
        """
        Extract features from keystroke dynamics
        
        Args:
            keystroke_data: List of keystroke events
            
        Returns:
            Dictionary of keystroke features
        """
        if not keystroke_data :
            return {}

        ikis =[k ['iki']for k in keystroke_data if k ['iki']is not None ]

        if not ikis :
            ikis =[0 ]

        features ={

        'iki_mean':np .mean (ikis ),
        'iki_std':np .std (ikis ),
        'iki_min':np .min (ikis ),
        'iki_max':np .max (ikis ),
        'iki_median':np .median (ikis ),
        'iki_q25':np .percentile (ikis ,25 ),
        'iki_q75':np .percentile (ikis ,75 ),

        'total_keystrokes':len (keystroke_data ),
        'keystroke_rate':len (keystroke_data )/max (1 ,(keystroke_data [-1 ]['timestamp']-keystroke_data [0 ]['timestamp']))if len (keystroke_data )>1 else 0 ,

        'unique_keys':len (set (k ['key_code']for k in keystroke_data )),
        }

        return features 

    @staticmethod 
    def extract_mouse_features (mouse_data :List [Dict ])->Dict :
        """
        Extract features from mouse movement patterns
        
        Args:
            mouse_data: List of mouse movement events
            
        Returns:
            Dictionary of mouse features
        """
        if not mouse_data :
            return {}

        distances =[m ['distance']for m in mouse_data if m ['distance']is not None ]
        velocities =[m ['velocity']for m in mouse_data if m ['velocity']is not None ]

        if not distances :
            distances =[0 ]
        if not velocities :
            velocities =[0 ]

        features ={

        'distance_mean':np .mean (distances ),
        'distance_std':np .std (distances ),
        'distance_min':np .min (distances ),
        'distance_max':np .max (distances ),
        'distance_median':np .median (distances ),
        'distance_total':np .sum (distances ),

        'velocity_mean':np .mean (velocities ),
        'velocity_std':np .std (velocities ),
        'velocity_min':np .min (velocities ),
        'velocity_max':np .max (velocities ),
        'velocity_median':np .median (velocities ),

        'total_movements':len (mouse_data ),
        'movement_rate':len (mouse_data )/max (1 ,(mouse_data [-1 ]['timestamp']-mouse_data [0 ]['timestamp']))if len (mouse_data )>1 else 0 ,
        }

        return features 

    @staticmethod 
    def extract_all_features (data :Dict )->np .ndarray :
        """
        Extract all features and return as feature vector
        
        Args:
            data: Raw behavioral data from collector
            
        Returns:
            Feature vector as numpy array
        """
        keystroke_features =FeatureExtractor .extract_keystroke_features (data .get ('keystroke_data',[]))
        mouse_features =FeatureExtractor .extract_mouse_features (data .get ('mouse_data',[]))

        feature_vector =[]

        feature_order_keystroke =[
        'iki_mean','iki_std','iki_min','iki_max','iki_median','iki_q25','iki_q75',
        'total_keystrokes','keystroke_rate','unique_keys'
        ]

        feature_order_mouse =[
        'distance_mean','distance_std','distance_min','distance_max',
        'distance_median','distance_total','velocity_mean','velocity_std',
        'velocity_min','velocity_max','velocity_median','total_movements','movement_rate'
        ]

        for feature in feature_order_keystroke :
            feature_vector .append (keystroke_features .get (feature ,0 ))

        for feature in feature_order_mouse :
            feature_vector .append (mouse_features .get (feature ,0 ))

        return np .array (feature_vector )

    @staticmethod 
    def get_feature_names ()->List [str ]:
        """Get the list of all feature names in order"""
        keystroke_features =[
        'iki_mean','iki_std','iki_min','iki_max','iki_median','iki_q25','iki_q75',
        'total_keystrokes','keystroke_rate','unique_keys'
        ]

        mouse_features =[
        'distance_mean','distance_std','distance_min','distance_max',
        'distance_median','distance_total','velocity_mean','velocity_std',
        'velocity_min','velocity_max','velocity_median','total_movements','movement_rate'
        ]

        return keystroke_features +mouse_features 
