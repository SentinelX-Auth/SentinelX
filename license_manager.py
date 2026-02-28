"""
License Key Management System
Manages license key generation, validation, and authorization
"""

import os 
import json 
import hashlib 
import secrets 
from datetime import datetime ,timedelta 
from typing import Dict ,Optional ,List ,Tuple 

class LicenseManager :
    """Manages license keys for app authorization"""

    def __init__ (self ,licenses_dir :str ="licenses"):
        """Initialize license manager"""
        self .licenses_dir =licenses_dir 
        if not os .path .exists (licenses_dir ):
            os .makedirs (licenses_dir )

        self .licenses_file =os .path .join (licenses_dir ,"licenses.json")
        self .load_licenses ()

    def load_licenses (self )->None :
        """Load licenses from file"""
        if os .path .exists (self .licenses_file ):
            try :
                with open (self .licenses_file ,'r')as f :
                    self .licenses =json .load (f )
            except :
                self .licenses ={}
        else :
            self .licenses ={}

    def save_licenses (self )->None :
        """Save licenses to file"""
        os .makedirs (self .licenses_dir ,exist_ok =True )
        with open (self .licenses_file ,'w')as f :
            json .dump (self .licenses ,f ,indent =2 )

    def generate_license_key (self ,
    owner :str ,
    max_users :int =1 ,
    expires_in_days :Optional [int ]=None ,
    tier :str ="basic")->str :
        """
        Generate a new license key
        
        Args:
            owner: License owner name (will be stored as-is, matched case-insensitively)
            max_users: Maximum number of users allowed
            expires_in_days: Days until license expires (None = never)
            tier: License tier (basic, pro, enterprise)
        
        Returns:
            Generated license key
        """

        random_part =secrets .token_hex (12 )
        key =f"LIC-{random_part .upper ()}"

        owner =str (owner ).strip ()

        expires_at =None 
        if expires_in_days :
            expires_at =(datetime .now ()+timedelta (days =expires_in_days )).isoformat ()

        self .licenses [key ]={
        'owner':owner ,
        'created_at':datetime .now ().isoformat (),
        'expires_at':expires_at ,
        'max_users':max_users ,
        'tier':tier ,
        'active_users':[],
        'total_logins':0 ,
        'active':True 
        }

        self .save_licenses ()
        return key 

    def validate_license (self ,license_key :str )->Tuple [bool ,str ]:
        """
        Validate a license key
        
        Args:
            license_key: License key to validate
        
        Returns:
            Tuple of (is_valid, message)
        """
        if license_key not in self .licenses :
            return False ,"License key not found"

        license_data =self .licenses [license_key ]

        if not license_data .get ('active',False ):
            return False ,"License key is inactive"

        if license_data .get ('expires_at'):
            expires =datetime .fromisoformat (license_data ['expires_at'])
            if datetime .now ()>expires :
                return False ,"License key has expired"

        return True ,"License key is valid"

    def add_user_to_license (self ,license_key :str ,username :str )->Tuple [bool ,str ]:
        """
        Add a user to a license
        
        Args:
            license_key: License key
            username: Username to add
        
        Returns:
            Tuple of (success, message)
        """
        if license_key not in self .licenses :
            return False ,"License key not found"

        license_data =self .licenses [license_key ]

        if username in license_data .get ('active_users',[]):
            return True ,"User already authorized"

        active_users =license_data .get ('active_users',[])
        max_users =license_data .get ('max_users',1 )

        if len (active_users )>=max_users :
            return False ,f"License has reached maximum users ({max_users })"

        license_data ['active_users'].append (username )
        self .save_licenses ()

        return True ,f"User {username } added to license"

    def is_user_authorized (self ,username :str ,license_key :str )->bool :
        """Check if user is authorized with license"""
        if license_key not in self .licenses :
            return False 

        license_data =self .licenses [license_key ]

        if not license_data .get ('active',False ):
            return False 

        if license_data .get ('expires_at'):
            expires =datetime .fromisoformat (license_data ['expires_at'])
            if datetime .now ()>expires :
                return False 

        if username in license_data .get ('active_users',[]):
            return True 

        active_users =license_data .get ('active_users',[])
        max_users =license_data .get ('max_users',1 )

        if len (active_users )<max_users :

            license_data ['active_users'].append (username )
            self .save_licenses ()
            return True 

        return False 

    def revoke_license (self ,license_key :str )->Tuple [bool ,str ]:
        """Revoke a license key"""
        if license_key not in self .licenses :
            return False ,"License key not found"

        self .licenses [license_key ]['active']=False 
        self .save_licenses ()
        return True ,"License revoked"

    def delete_license (self ,license_key :str )->Tuple [bool ,str ]:
        """Delete a license key permanently"""
        if license_key not in self .licenses :
            return False ,"License key not found"

        del self .licenses [license_key ]
        self .save_licenses ()
        return True ,"License deleted"

    def get_license_info (self ,license_key :str )->Optional [Dict ]:
        """Get license information"""
        if license_key not in self .licenses :
            return None 

        license_data =self .licenses [license_key ].copy ()

        is_valid ,msg =self .validate_license (license_key )
        license_data ['valid']=is_valid 
        license_data ['users_count']=len (license_data .get ('active_users',[]))
        license_data ['remaining_users']=license_data .get ('max_users',1 )-license_data ['users_count']

        return license_data 

    def get_all_licenses (self ,owner :Optional [str ]=None )->List [Dict ]:
        """Get all licenses, optionally filtered by owner"""
        result =[]
        for key ,data in self .licenses .items ():
            if owner :

                license_owner =str (data .get ('owner','')).strip ()
                filter_owner =str (owner ).strip ()
                if license_owner .lower ()!=filter_owner .lower ():
                    continue 

            info =data .copy ()
            info ['key']=key 
            result .append (info )

        return result 

    def track_login (self ,license_key :str )->None :
        """Track login attempt with license"""
        if license_key in self .licenses :
            self .licenses [license_key ]['total_logins']=self .licenses [license_key ].get ('total_logins',0 )+1 
            self .save_licenses ()
