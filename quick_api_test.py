import requests 
import json 

base ='http://127.0.0.1:5000'

print ('create user testfast')
try :
    r =requests .post (base +'/api/user/create',json ={'username':'testfast'})
    print (r .status_code ,r .json ())
except Exception as e :
    print ('create error',e )

print ('\nstart enroll')
try :
    r =requests .post (base +'/api/user/testfast/enroll',json ={'num_sessions':1 ,'session_duration':1 })
    print (r .status_code ,r .json ())
except Exception as e :
    print ('enroll error',e )

print ('\nstart auth')
try :
    r =requests .post (base +'/api/user/testfast/authenticate',json ={'session_duration':1 })
    print (r .status_code ,r .json ())
except Exception as e :
    print ('auth error',e )
