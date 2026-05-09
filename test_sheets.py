"""
Quick test script to verify Google Sheets connection.
Run with: py test_sheets.py
"""
import os
from dotenv import load_dotenv

load_dotenv()

CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "CustomerSupportEscalations")

print(f"[INFO] Credentials file : {CREDENTIALS_FILE}")
print(f"[INFO] Sheet name       : {SHEET_NAME}")
print()

# Step 1: Check credentials file exists
if not os.path.exists(CREDENTIALS_FILE):
    print(f"[FAIL] '{CREDENTIALS_FILE}' not found in project root.")
    print("       Make sure you placed the downloaded JSON key here and rename it to credentials.json")
    exit(1)
print(f"[OK] Credentials file found: {CREDENTIALS_FILE}")

# Step 2: Authenticate
try:
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)
    print("[OK] Authentication successful!")
except Exception as e:
    print(f"[FAIL] Authentication error: {e}")
    exit(1)

# Step 3: Open the sheet
try:
    sheet = client.open(SHEET_NAME).sheet1
    print(f"[OK] Opened sheet: '{SHEET_NAME}'")
except Exception as e:
    print(f"[FAIL] Could not open sheet '{SHEET_NAME}': {e}")
    print()
    print("  Common fixes:")
    print("  - Share the sheet with: sheets-bot@wired-sign-495709-v1.iam.gserviceaccount.com")
    print(f"  - Make sure the sheet is named exactly: {SHEET_NAME}")
    exit(1)

# Step 4: Write a test row
try:
    test_row = ["TEST-001", "Test Subject", "This is a test escalation", "HIGH", "billing"]
    sheet.append_row(test_row)
    print("[OK] Test row written successfully!")
    print()
    print("SUCCESS: Google Sheets integration is working!")
    print("Open your sheet to see the test row: https://docs.google.com/spreadsheets")
except Exception as e:
    print(f"[FAIL] Could not write to sheet: {e}")
