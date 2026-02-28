"""
API Documentation - Complete reference for the Behavioral Authentication System
"""

"""
=============================================================================
BEHAVIORAL AUTHENTICATION SYSTEM - API REFERENCE
=============================================================================

For complete documentation and examples, see README.md

═══════════════════════════════════════════════════════════════════════════
1. BehavioralDataCollector
═══════════════════════════════════════════════════════════════════════════

Class: BehavioralDataCollector
Purpose: Collects real-time keyboard and mouse behavioral data

Methods:
--------

__init__(duration: int = 60) -> None
    Initialize the data collector
    Args:
        duration: Collection duration in seconds (default: 60)
    
    Example:
        collector = BehavioralDataCollector(duration=30)

collect() -> Dict
    Collect behavioral data for the specified duration
    Returns: Dictionary with keys:
        - 'keystroke_data': List of keystroke events
        - 'mouse_data': List of mouse movement events
        - 'duration': Collection duration in seconds
    
    Example:
        data = collector.collect()

save_data(filename: str, data: Dict) -> None
    Save collected data to a JSON file
    Args:
        filename: Path to save file
        data: Data dictionary from collect()
    
    Example:
        collector.save_data('behavior.json', data)

load_data(filename: str) -> Dict
    Load previously saved behavioral data
    Args:
        filename: Path to data file
    Returns: Data dictionary
    
    Example:
        data = BehavioralDataCollector.load_data('behavior.json')

Keystroke Data Format:
{
    'timestamp': float,          # Unix timestamp
    'char': str,                 # Character pressed
    'iki': float or None,        # Inter-keystroke interval (ms)
    'key_code': str              # Key identifier
}

Mouse Data Format:
{
    'timestamp': float,          # Unix timestamp
    'x': int,                    # X coordinate
    'y': int,                    # Y coordinate
    'distance': float or None,   # Distance from last position (pixels)
    'velocity': float or None    # Movement velocity (pixels/sec)
}


═══════════════════════════════════════════════════════════════════════════
2. FeatureExtractor
═══════════════════════════════════════════════════════════════════════════

Class: FeatureExtractor
Purpose: Extract behavioral biometric features from raw data

Static Methods:
---------------

extract_keystroke_features(keystroke_data: List[Dict]) -> Dict
    Extract keystroke-based features
    Returns: Dictionary with 10 keystroke features
    
    Features:
        - iki_mean, iki_std, iki_min, iki_max, iki_median
        - iki_q25, iki_q75
        - total_keystrokes, keystroke_rate, unique_keys
    
    Example:
        features = FeatureExtractor.extract_keystroke_features(data['keystroke_data'])

extract_mouse_features(mouse_data: List[Dict]) -> Dict
    Extract mouse movement features
    Returns: Dictionary with 13 mouse features
    
    Features:
        - distance_mean, distance_std, distance_min, distance_max
        - distance_median, distance_total
        - velocity_mean, velocity_std, velocity_min, velocity_max
        - velocity_median, total_movements, movement_rate
    
    Example:
        features = FeatureExtractor.extract_mouse_features(data['mouse_data'])

extract_all_features(data: Dict) -> np.ndarray
    Extract all 23 features as a vector
    Args:
        data: Raw behavioral data dictionary
    Returns: 1D numpy array of 23 features
    
    Example:
        feature_vector = FeatureExtractor.extract_all_features(data)

get_feature_names() -> List[str]
    Get names of all 23 features in order
    Returns: List of feature names
    
    Example:
        names = FeatureExtractor.get_feature_names()
        for name, value in zip(names, feature_vector):
            print(f"{name}: {value}")


═══════════════════════════════════════════════════════════════════════════
3. BehavioralAuthenticationModel
═══════════════════════════════════════════════════════════════════════════

Class: BehavioralAuthenticationModel
Purpose: Train and use ML model for authentication

Methods:
--------

__init__(contamination: float = 0.1) -> None
    Initialize the model
    Args:
        contamination: Expected outlier proportion (0.0-0.5)
    
    Example:
        model = BehavioralAuthenticationModel(contamination=0.1)

enroll_user(behavioral_data_list: List[Dict], num_samples: int = 5) -> bool
    Enroll a user with behavioral samples
    Args:
        behavioral_data_list: List of data dictionaries from collection
        num_samples: Minimum samples required (default: 5)
    Returns: True if successful, False otherwise
    
    Example:
        samples = [data1, data2, data3]
        success = model.enroll_user(samples, num_samples=3)

authenticate(behavioral_data: Dict, threshold: float = -0.5) -> Tuple[bool, float, str]
    Authenticate a user
    Args:
        behavioral_data: Data from authentication attempt
        threshold: Anomaly score threshold (lower = stricter)
    Returns: Tuple of:
        - is_authentic: bool - True if user authenticated
        - confidence: float - Confidence 0-100%
        - message: str - Descriptive message
    
    Example:
        is_authentic, confidence, msg = model.authenticate(test_data)
        if is_authentic:
            print(f"Welcome! Confidence: {confidence:.1f}%")

save_model(filename: str) -> None
    Save trained model to file
    Args:
        filename: Path to save model
    
    Example:
        model.save_model('my_model.pkl')

load_model(filename: str) -> None
    Load previously trained model
    Args:
        filename: Path to model file
    
    Example:
        model = BehavioralAuthenticationModel()
        model.load_model('my_model.pkl')

get_model_info() -> Dict
    Get information about the model
    Returns: Dictionary with model details
    
    Example:
        info = model.get_model_info()
        print(f"Trained: {info['is_trained']}")
        print(f"Samples: {info['enrollment_samples']}")


═══════════════════════════════════════════════════════════════════════════
4. UserManager
═══════════════════════════════════════════════════════════════════════════

Class: UserManager
Purpose: Manage user profiles and enrollment

Methods:
--------

__init__(users_dir: str = "users") -> None
    Initialize user manager
    Args:
        users_dir: Directory for user profiles
    
    Example:
        manager = UserManager(users_dir="users")

user_exists(username: str) -> bool
    Check if user exists
    
    Example:
        if manager.user_exists("john"):
            print("User exists")

create_user(username: str) -> bool
    Create new user profile
    Returns: True if successful
    
    Example:
        manager.create_user("john")

enroll_user(username: str, num_sessions: int = 5, session_duration: int = 30) -> bool
    Enroll user with behavioral data
    Args:
        username: Username to enroll
        num_sessions: Number of enrollment sessions
        session_duration: Duration per session (seconds)
    
    Example:
        manager.enroll_user("john", num_sessions=5, session_duration=30)

authenticate_user(username: str, session_duration: int = 30) -> Tuple[bool, str]
    Authenticate a user
    Returns: Tuple of (is_authentic, message)
    
    Example:
        is_authentic, msg = manager.authenticate_user("john")

list_users() -> List[str]
    Get list of all users
    
    Example:
        users = manager.list_users()

delete_user(username: str) -> bool
    Delete user profile
    
    Example:
        manager.delete_user("john")

get_user_info(username: str) -> Optional[Dict]
    Get user profile information
    
    Example:
        info = manager.get_user_info("john")
        print(info['sessions'])  # Number of enrollment sessions


═══════════════════════════════════════════════════════════════════════════
USAGE EXAMPLES
═══════════════════════════════════════════════════════════════════════════

Example 1: Basic Workflow
------------------------
from behavioral_data_collector import BehavioralDataCollector
from behavioral_model import BehavioralAuthenticationModel

# Enroll
collector = BehavioralDataCollector(duration=20)
sample1 = collector.collect()
sample2 = collector.collect()

model = BehavioralAuthenticationModel()
model.enroll_user([sample1, sample2], num_samples=2)

# Authenticate
test = collector.collect()
is_authentic, confidence, msg = model.authenticate(test)
print(msg)

# Save
model.save_model('user_john.pkl')


Example 2: Using UserManager
-----------------------------
from user_manager import UserManager

manager = UserManager()

# Create and enroll
manager.create_user("alice")
manager.enroll_user("alice", num_sessions=5, session_duration=30)

# Authenticate
is_authentic, msg = manager.authenticate_user("alice")

# Manage
users = manager.list_users()
info = manager.get_user_info("alice")


Example 3: Feature Analysis
---------------------------
from behavioral_data_collector import BehavioralDataCollector
from feature_extractor import FeatureExtractor

collector = BehavioralDataCollector(duration=30)
data = collector.collect()

keystroke_feats = FeatureExtractor.extract_keystroke_features(data['keystroke_data'])
mouse_feats = FeatureExtractor.extract_mouse_features(data['mouse_data'])

print("Keystroke IKI Mean:", keystroke_feats['iki_mean'])
print("Mouse Velocity Mean:", mouse_feats['velocity_mean'])


═══════════════════════════════════════════════════════════════════════════
CONFIGURATION
═══════════════════════════════════════════════════════════════════════════

Modify config.py to customize:

- DATA_COLLECTION: Session duration settings
- MODEL_TRAINING: Enrollment requirements, contamination rate
- AUTHENTICATION: Thresholds for different security levels
- USER_MANAGEMENT: Storage locations
- FEATURES: Feature count information


═══════════════════════════════════════════════════════════════════════════
ERROR HANDLING
═══════════════════════════════════════════════════════════════════════════

Common Errors & Solutions:

1. "Model not trained"
   → Call enroll_user() before authenticate()

2. "Need at least X samples"
   → Provide minimum required samples for enrollment

3. "User not found"
   → Check username spelling or create user first

4. "pynput error" (Windows)
   → May need admin privileges for mouse/keyboard listening
   → Run with: python -m admin (or run CMD as administrator)


═══════════════════════════════════════════════════════════════════════════
SYSTEM LIMITATIONS & BEST PRACTICES
═══════════════════════════════════════════════════════════════════════════

Best Practices:
✓ Use minimum 5 enrollment samples
✓ Keep sessions 20-60 seconds for best features
✓ Encourage natural typing/mouse movement
✓ Save models for reuse
✓ Combine with traditional auth (passwords)

Limitations:
✗ Requires keyboard/mouse activity
✗ Behavior varies over time (requires retraining)
✗ May have false positives/negatives
✗ Platform-specific behavior patterns
✗ Session context affects results


═══════════════════════════════════════════════════════════════════════════
"""

# Quick reference table
FEATURE_REFERENCE = {
    'Keystroke Features': [
        'iki_mean', 'iki_std', 'iki_min', 'iki_max', 'iki_median',
        'iki_q25', 'iki_q75', 'total_keystrokes', 'keystroke_rate', 'unique_keys'
    ],
    'Mouse Features': [
        'distance_mean', 'distance_std', 'distance_min', 'distance_max',
        'distance_median', 'distance_total', 'velocity_mean', 'velocity_std',
        'velocity_min', 'velocity_max', 'velocity_median', 'total_movements', 'movement_rate'
    ]
}

if __name__ == "__main__":
    print(__doc__)
    print("\n📚 Feature Reference Table:\n")
    for category, features in FEATURE_REFERENCE.items():
        print(f"{category} ({len(features)}):")
        for i, feat in enumerate(features, 1):
            print(f"  {i:2}. {feat}")
        print()
