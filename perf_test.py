import time 
import requests 
import statistics 

BASE ='http://127.0.0.1:5000'
ENDPOINTS =['/api/system/status','/api/users']
SAMPLES =30 

results ={ep :[]for ep in ENDPOINTS }

print ('Starting quick performance test against',BASE )
for ep in ENDPOINTS :
    url =BASE +ep 
    print ('\nTesting',url )
    for i in range (SAMPLES ):
        t0 =time .time ()
        try :
            r =requests .get (url ,timeout =5 )
            code =r .status_code 
        except Exception as e :
            code ='ERR'
        t1 =time .time ()
        elapsed =(t1 -t0 )*1000.0 
        results [ep ].append (elapsed )
        print (f"{i +1 :02d}: {elapsed :.1f} ms (status={code })")

print ('\nSummary:')
for ep ,times in results .items ():
    clean =[t for t in times if t is not None ]
    print ('\nEndpoint:',ep )
    print ('  samples:',len (clean ))
    print ('  avg:  {:.1f} ms'.format (statistics .mean (clean )))
    print ('  med:  {:.1f} ms'.format (statistics .median (clean )))
    print ('  p95:  {:.1f} ms'.format (sorted (clean )[int (len (clean )*0.95 )-1 ]))
    print ('  max:  {:.1f} ms'.format (max (clean )))

print ('\nDone')
