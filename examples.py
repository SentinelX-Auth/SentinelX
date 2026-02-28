"""
Example Usage - Demonstrates the Behavioral Authentication System
"""

from behavioral_data_collector import BehavioralDataCollector 
from feature_extractor import FeatureExtractor 
from behavioral_model import BehavioralAuthenticationModel 
import time 

def example_basic_workflow ():
    """Example: Basic workflow without file I/O"""
    print ("\n"+"="*70 )
    print ("EXAMPLE 1: Basic Behavioral Authentication Workflow")
    print ("="*70 )

    print ("\n1️⃣ USER ENROLLMENT PHASE")
    print ("-"*70 )

    collector =BehavioralDataCollector (duration =20 )

    print ("\n📝 Collecting behavioral sample 1...")
    enrollment_data_1 =collector .collect ()

    print ("\n📝 Collecting behavioral sample 2...")
    enrollment_data_2 =collector .collect ()

    print ("\n📝 Collecting behavioral sample 3...")
    enrollment_data_3 =collector .collect ()

    print ("\n\n2️⃣ MODEL TRAINING PHASE")
    print ("-"*70 )

    enrollment_data_list =[enrollment_data_1 ,enrollment_data_2 ,enrollment_data_3 ]

    model =BehavioralAuthenticationModel (contamination =0.1 )
    model .enroll_user (enrollment_data_list ,num_samples =3 )

    print ("\n📊 Model Information:")
    info =model .get_model_info ()
    for key ,value in info .items ():
        if key !='feature_names':
            print (f"  {key }: {value }")

    print ("\n\n3️⃣ AUTHENTICATION TESTING PHASE")
    print ("-"*70 )

    print ("\n✅ Authenticate with genuine behavior (similar to enrollment):")
    genuine_auth =collector .collect ()
    is_authentic ,confidence ,message =model .authenticate (genuine_auth )
    print (f"  {message }")

    print ("\n\n4️⃣ FEATURE ANALYSIS")
    print ("-"*70 )

    features =FeatureExtractor .extract_all_features (enrollment_data_1 )
    feature_names =FeatureExtractor .get_feature_names ()

    print ("\n📈 Extracted Features (Sample):")
    for i ,(name ,value )in enumerate (zip (feature_names [:5 ],features [:5 ])):
        print (f"  {name }: {value :.4f}")
    print (f"  ... and {len (feature_names )-5 } more features")

def example_feature_extraction ():
    """Example: Feature extraction and analysis"""
    print ("\n"+"="*70 )
    print ("EXAMPLE 2: Feature Extraction Analysis")
    print ("="*70 )

    collector =BehavioralDataCollector (duration =15 )
    print ("\n📝 Collecting behavioral data...")
    data =collector .collect ()

    print ("\n\n🔍 Keystroke Dynamics Features:")
    print ("-"*70 )
    keystroke_features =FeatureExtractor .extract_keystroke_features (data ['keystroke_data'])
    for key ,value in keystroke_features .items ():
        print (f"  {key }: {value :.4f}")

    print ("\n\n🔍 Mouse Movement Features:")
    print ("-"*70 )
    mouse_features =FeatureExtractor .extract_mouse_features (data ['mouse_data'])
    for key ,value in mouse_features .items ():
        print (f"  {key }: {value :.4f}")

def example_multiplesessions ():
    """Example: Multiple sessions and model robustness"""
    print ("\n"+"="*70 )
    print ("EXAMPLE 3: Training with Multiple Sessions")
    print ("="*70 )

    sessions =[]
    num_sessions =3 

    for i in range (num_sessions ):
        print (f"\n📊 Session {i +1 }/{num_sessions }")
        collector =BehavioralDataCollector (duration =15 )
        data =collector .collect ()
        sessions .append (data )

    print ("\n\n🤖 Training model with multiple sessions...")
    model =BehavioralAuthenticationModel ()
    model .enroll_user (sessions ,num_samples =num_sessions )

    print ("\n\n🔐 Testing authentication...")
    collector =BehavioralDataCollector (duration =15 )
    test_data =collector .collect ()

    is_authentic ,confidence ,message =model .authenticate (test_data )
    print (f"\n{message }")

def display_examples_menu ():
    """Display available examples"""
    print ("\n"+"="*70 )
    print ("🎓 Behavioral Authentication System - Examples")
    print ("="*70 )
    print ("\nAvailable Examples:")
    print ("1. Basic Workflow (Enrollment + Authentication)")
    print ("2. Feature Extraction Analysis")
    print ("3. Multiple Sessions Training")
    print ("4. Run All Examples")
    print ("5. Exit")
    print ("-"*70 )

def main ():
    """Run examples"""
    while True :
        display_examples_menu ()
        choice =input ("\nSelect example (1-5): ").strip ()

        try :
            if choice =="1":
                example_basic_workflow ()
            elif choice =="2":
                example_feature_extraction ()
            elif choice =="3":
                example_multiplesessions ()
            elif choice =="4":
                example_basic_workflow ()
                input ("\n\nPress Enter to continue...")
                example_feature_extraction ()
                input ("\n\nPress Enter to continue...")
                example_multiplesessions ()
            elif choice =="5":
                print ("\n👋 Thank you for using the Behavioral Authentication System!")
                break 
            else :
                print ("❌ Invalid option. Please try again.")
        except KeyboardInterrupt :
            print ("\n\n⚠️ Operation cancelled by user")
        except Exception as e :
            print (f"\n❌ Error: {e }")

        input ("\n\nPress Enter to continue...")

if __name__ =="__main__":
    print ("\n🚀 Welcome to the Behavioral Authentication System!")
    print ("This tool demonstrates AI-based authentication using behavioral biometrics")
    main ()
