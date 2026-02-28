import os
import json
import glob

users_dir = "users"
banned_hwids_file = os.path.join(users_dir, "banned_hwids.json")

if os.path.exists(banned_hwids_file):
    with open(banned_hwids_file, "w") as f:
        json.dump({}, f)
    print("Cleared banned_hwids.json")

config_files = glob.glob(os.path.join(users_dir, "*", "config.json"))
count = 0
for cfile in config_files:
    try:
        with open(cfile, "r") as f:
            data = json.load(f)
        
        if "suspended_until" in data:
            del data["suspended_until"]
            with open(cfile, "w") as f:
                json.dump(data, f, indent=2)
            print(f"Removed ban from {cfile}")
            count += 1
    except Exception as e:
        print(f"Error processing {cfile}: {e}")

print(f"Unban process complete. Unbanned {count} user(s).")
