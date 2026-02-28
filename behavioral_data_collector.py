"""
Behavioral Data Collector - Collects typing and mouse movement patterns for authentication
"""

import time 
import json 
from typing import Dict 
from pynput import keyboard ,mouse 

class BehavioralDataCollector :
    """Collects behavioral biometric data including typing dynamics and mouse patterns"""

    def __init__ (self ,duration :int =60 ):
        """
        Initialize the data collector
        
        Args:
            duration: Collection duration in seconds
        """
        self .duration =duration 
        self .keystroke_data =[]
        self .mouse_data =[]
        self .last_key_time =None 
        self .collection_active =False 
        self .last_mouse_position =None 

    def on_press (self ,key ):
        """Handle key press events"""
        if not self .collection_active :
            return 

        current_time =time .time ()

        iki =None 
        if self .last_key_time is not None :
            iki =(current_time -self .last_key_time )*1000 

        self .last_key_time =current_time 

        try :
            char =key .char 
        except AttributeError :
            char =str (key )

        self .keystroke_data .append ({
        'timestamp':current_time ,
        'char':char ,
        'iki':iki ,
        'key_code':str (key )
        })

    def on_move (self ,x ,y ):
        """Handle mouse movement events"""
        if not self .collection_active :
            return 

        current_time =time .time ()

        distance =None 
        velocity =None 

        if self .last_mouse_position is not None :
            prev_x ,prev_y ,prev_time =self .last_mouse_position 
            dx =x -prev_x 
            dy =y -prev_y 
            dt =current_time -prev_time 

            distance =(dx **2 +dy **2 )**0.5 
            if dt >0 :
                velocity =distance /dt 

        self .last_mouse_position =(x ,y ,current_time )

        self .mouse_data .append ({
        'timestamp':current_time ,
        'x':x ,
        'y':y ,
        'distance':distance ,
        'velocity':velocity 
        })

    def collect (self )->Dict :
        """
        Collect behavioral data for the specified duration
        
        Returns:
            Dictionary containing keystroke and mouse data
        """
        print (f"\n🔍 Behavioral Data Collection Starting... ({self .duration }s)")
        print ("="*50 )
        print ("Please perform natural interactions:")
        print ("- Type some text")
        print ("- Move your mouse around")
        print ("- Click occasionally")
        print ("="*50 )

        self .keystroke_data =[]
        self .mouse_data =[]
        self .last_key_time =None 
        self .last_mouse_position =None 
        self .collection_active =True 

        listener =keyboard .Listener (on_press =self .on_press )
        mouse_listener =mouse .Listener (on_move =self .on_move )

        listener .start ()
        mouse_listener .start ()

        start_time =time .time ()
        while time .time ()-start_time <self .duration :
            remaining =self .duration -(time .time ()-start_time )
            print (f"\rCollecting... {remaining :.1f}s remaining",end ='',flush =True )
            time .sleep (0.1 )

        self .collection_active =False 
        listener .stop ()
        mouse_listener .stop ()

        print ("\n✅ Data Collection Complete!")

        return {
        'keystroke_data':self .keystroke_data ,
        'mouse_data':self .mouse_data ,
        'duration':self .duration 
        }

    def save_data (self ,filename :str ,data :Dict ):
        """Save collected data to file"""
        with open (filename ,'w')as f :
            json .dump (data ,f ,indent =2 )
        print (f"✅ Data saved to {filename }")

    @staticmethod 
    def load_data (filename :str )->Dict :
        """Load previously collected data"""
        with open (filename ,'r')as f :
            return json .load (f )
