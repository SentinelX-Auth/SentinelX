"""
Activity Tracker - Tracks user activities and behavioral data for analytics
"""

import json 
from datetime import datetime ,timedelta 
from typing import Dict ,List 

class ActivityTracker :
    """Tracks user activities, login attempts, and behavioral patterns"""

    def __init__ (self ):
        """Initialize activity tracker"""
        self .activities ={}
        self .login_attempts ={}
        self .behavioral_profiles ={}

    def track_activity (self ,username :str ,activity_type :str ,details :Dict =None )->None :
        """
        Track a user activity
        
        Args:
            username: Username
            activity_type: Type of activity (login, logout, enrollment, auth_attempt, etc)
            details: Additional details about the activity
        """
        if username not in self .activities :
            self .activities [username ]=[]

        activity ={
        'timestamp':datetime .now ().isoformat (),
        'type':activity_type ,
        'details':details or {}
        }

        self .activities [username ].append (activity )

    def track_login_attempt (self ,username :str ,success :bool ,behavioral_score :float =None )->None :
        """
        Track login attempt
        
        Args:
            username: Username
            success: Whether login was successful
            behavioral_score: Behavioral anomaly score (0-1), lower is better
        """
        if username not in self .login_attempts :
            self .login_attempts [username ]=[]

        attempt ={
        'timestamp':datetime .now ().isoformat (),
        'success':success ,
        'behavioral_score':behavioral_score ,
        'status':'authenticated'if success else 'denied'
        }

        self .login_attempts [username ].append (attempt )

        self .track_activity (username ,'login_attempt',{
        'success':success ,
        'score':behavioral_score 
        })

    def store_behavioral_profile (self ,username :str ,profile_data :Dict )->None :
        """
        Store behavioral profile for a user
        
        Args:
            username: Username
            profile_data: User's behavioral profile data
        """
        self .behavioral_profiles [username ]={
        'timestamp':datetime .now ().isoformat (),
        'data':profile_data 
        }

        self .track_activity (username ,'profile_updated',{
        'profile_size':len (profile_data )
        })

    def get_user_activity_summary (self ,username :str ,days :int =7 )->Dict :
        """
        Get activity summary for a user in the last N days
        
        Args:
            username: Username
            days: Number of days to look back
            
        Returns:
            Dictionary with activity summary
        """
        cutoff_time =datetime .now ()-timedelta (days =days )

        activities =self .activities .get (username ,[])
        login_attempts =self .login_attempts .get (username ,[])

        recent_activities =[
        a for a in activities 
        if datetime .fromisoformat (a ['timestamp'])>cutoff_time 
        ]

        recent_logins =[
        l for l in login_attempts 
        if datetime .fromisoformat (l ['timestamp'])>cutoff_time 
        ]

        fraud_blocked_count = sum(1 for a in recent_activities if a.get('type') == 'fraud_blocked')

        successful_logins =sum (1 for l in recent_logins if l ['success'])
        failed_logins =sum (1 for l in recent_logins if not l ['success'])

        avg_score =None 
        if recent_logins :
            scores =[l ['behavioral_score']for l in recent_logins if l ['behavioral_score']is not None ]
            if scores :
                avg_score =sum (scores )/len (scores )

        return {
        'total_activities':len (recent_activities ),
        'total_login_attempts':len (recent_logins ),
        'successful_logins':successful_logins ,
        'failed_logins':failed_logins ,
        'fraud_blocks':fraud_blocked_count ,
        'success_rate':(successful_logins /max (1 ,len (recent_logins )))*100 ,
        'average_behavioral_score':avg_score ,
        'last_activity':recent_activities [-1 ]if recent_activities else None ,
        'last_login':recent_logins [-1 ]if recent_logins else None 
        }

    def get_all_user_activities (self ,username :str ,limit :int =50 )->List [Dict ]:
        """
        Get all activities for a user
        
        Args:
            username: Username
            limit: Maximum number of activities to return
            
        Returns:
            List of activities (most recent first)
        """
        activities =self .activities .get (username ,[])
        return sorted (activities ,key =lambda x :x ['timestamp'],reverse =True )[:limit ]

    def get_login_history (self ,username :str ,limit :int =20 )->List [Dict ]:
        """
        Get login history for a user
        
        Args:
            username: Username
            limit: Maximum number of login attempts to return
            
        Returns:
            List of login attempts (most recent first)
        """
        attempts =self .login_attempts .get (username ,[])
        return sorted (attempts ,key =lambda x :x ['timestamp'],reverse =True )[:limit ]

    def get_behavioral_profile (self ,username :str )->Dict :
        """
        Get behavioral profile for a user
        
        Args:
            username: Username
            
        Returns:
            User's behavioral profile or None
        """
        return self .behavioral_profiles .get (username )

    def get_security_score (self ,username :str )->float :
        """
        Calculate security score for a user (0-100)
        
        Args:
            username: Username
            
        Returns:
            Security score (higher is better)
        """
        summary =self .get_user_activity_summary (username ,days =30 )

        score =50.0 

        score +=summary ['success_rate']*0.3 

        score -=summary ['failed_logins']*5 

        if summary ['average_behavioral_score']is not None :

            score +=(1 -summary ['average_behavioral_score'])*30 

        return max (0 ,min (100 ,score ))

activity_tracker =ActivityTracker ()
