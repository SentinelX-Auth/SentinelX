import time
import requests
import json
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

TARGET_URL = "http://127.0.0.1:5000/"
API_URL = "http://127.0.0.1:5000/api/login"
USERNAME = "test"
LICENSE_KEY = "LIC-9C89DA844AFA54247FCF0BBA"

print("--- Method 1: Direct API Request (0 Behavioral Data) ---")

try:
    response = requests.post(API_URL, json={
        "username": USERNAME,
        "license_key": LICENSE_KEY,
        "use_license": True,
        "behavioral_data": {
            "keystroke_data": [],
            "mouse_data": [],
            "duration": 0
        }
    })
    
    print(f"API Response Code: {response.status_code}")
    print(f"API Response Body: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"API bot failed: {e}")

print("\n[!] Clearing backend bans triggered by API test before starting Selenium...")
import subprocess
try:
    subprocess.run(["python", "unban_all.py"], check=True)
except Exception as e:
    pass

print("\n--- Method 2: Selenium Browser Automation (Instant Typed + Teleporting Mouse) ---")
try:
    print("Launching headless Chrome...")
    options = webdriver.ChromeOptions()

    driver = webdriver.Chrome(options=options)
    
    print(f"Navigating to {TARGET_URL}...")
    driver.get(TARGET_URL)
    
    wait = WebDriverWait(driver, 5)
    

    print("Switching to License Tab...")
    license_tab = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-tab='license']")))
    license_tab.click()
    

    username_field = wait.until(EC.visibility_of_element_located((By.ID, "licUsername")))
    license_field = driver.find_element(By.ID, "licenseKeyInput")
    submit_button = driver.find_element(By.CSS_SELECTOR, "#licenseForm button[type='submit']")
    
    print("Bot injecting credentials instantly (no human typing rhythm)...")
    username_field.send_keys(USERNAME)
    license_field.send_keys(LICENSE_KEY)
    
    print("Bot teleporting mouse and instantly clicking Sign In...")
    submit_button.click()
    

    time.sleep(3)
    

    try:
        msg_element = wait.until(EC.presence_of_element_located((By.ID, "msg")))
        time.sleep(1)
        print(f"Frontend Result Message: {msg_element.text}")
    except Exception as inner_e:
        print(f"Could not read frontend message block: {inner_e}")
    
    driver.quit()
    print("Browser closed.")
    
except Exception as e:
    print(f"Selenium bot failed. Ensure you have Chrome installed. Error: {e}")

print(f"\nBot tests completed. Check your dashboard Security Results tab for user '{USERNAME}'!")
