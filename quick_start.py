"""
Quick Start Guide - Simple implementation example
"""

from behavioral_data_collector import BehavioralDataCollector 
from feature_extractor import FeatureExtractor 
from behavioral_model import BehavioralAuthenticationModel 

def quick_demo ():
    """
    Minimal example showing the core workflow
    """

    print ("\n"+"="*70 )
    print ("QUICK START: Behavioral Authentication System")
    print ("="*70 )

    print ("\n📝 STEP 1: Enrolling User (Collecting Behavioral Samples)")
    print ("-"*70 )

    enrollment_samples =[]
    num_samples =2 

    for i in range (num_samples ):
        print (f"\n[Sample {i +1 }/{num_samples }] Collecting for 10 seconds...")
        print ("Tip: Type naturally and move your mouse around")

        collector =BehavioralDataCollector (duration =10 )
        data =collector .collect ()
        enrollment_samples .append (data )

    print ("\n\n🤖 STEP 2: Training Authentication Model")
    print ("-"*70 )

    model =BehavioralAuthenticationModel (contamination =0.05 )
    success =model .enroll_user (enrollment_samples ,num_samples =num_samples )

    if not success :
        print ("❌ Enrollment failed!")
        return 

    print ("✅ Model trained successfully!")

    print ("\n\n📊 STEP 3: Feature Analysis")
    print ("-"*70 )

    features =FeatureExtractor .extract_all_features (enrollment_samples [0 ])
    names =FeatureExtractor .get_feature_names ()

    print ("\nTop 10 Behavioral Features:")
    print ("  # | Feature Name           | Value")
    print ("  "+"-"*45 )
    for i ,(name ,value )in enumerate (zip (names [:10 ],features [:10 ]),1 ):
        print (f"  {i :2} | {name :22} | {value :8.4f}")

    print ("\n\n🔐 STEP 4: Testing Authentication")
    print ("-"*70 )

    print ("\n[Test] Collecting test behavior for 10 seconds...")
    collector =BehavioralDataCollector (duration =10 )
    test_data =collector .collect ()

    is_authentic ,confidence ,message =model .authenticate (test_data )

    print (f"\n{message }")

    if is_authentic :
        print (f"✅ User VERIFIED with {confidence :.1f}% confidence")
    else :
        print (f"❌ User REJECTED - possible impersonation")

    print ("\n"+"="*70 )
    print ("Demo Complete!")
    print ("="*70 )

def minimal_example ():
    """
    Absolute minimal code example (3 steps)
    """
    print ("""
    
=== MINIMAL CODE EXAMPLE ===

from behavioral_data_collector import BehavioralDataCollector
from behavioral_model import BehavioralAuthenticationModel

collector = BehavioralDataCollector(duration=30)
sample1 = collector.collect()
sample2 = collector.collect()

model = BehavioralAuthenticationModel()
model.enroll_user([sample1, sample2])

test = collector.collect()
is_authentic, confidence, msg = model.authenticate(test)
print(msg)
    """)

if __name__ =="__main__":
    import sys 

    print ("""
╔══════════════════════════════════════════════════════════════════╗
║   AI-Based Behavioral Authentication System - Quick Start        ║
╚══════════════════════════════════════════════════════════════════╝

This script demonstrates the Core functionality of the system:
  • Data collection from keyboard & mouse
  • Feature extraction (23 behavioral metrics)
  • Model training using Isolation Forest
  • Real-time user authentication

Duration: ~1 minute (10s enrollment + 10s test)
    """)

    choice =input ("\nChoose:\n[1] Run Quick Demo (Full Workflow)\n[2] Show Minimal Code Example\n[3] Exit\n\nSelect (1-3): ").strip ()

    if choice =="1":
        try :
            quick_demo ()
        except KeyboardInterrupt :
            print ("\n\n⚠️ Demo interrupted by user")
        except Exception as e :
            print (f"\n❌ Error: {e }")
    elif choice =="2":
        minimal_example ()
    else :
        print ("Goodbye!")
        sys .exit (0 )
