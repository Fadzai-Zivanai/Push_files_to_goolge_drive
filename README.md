# Push_files_to_goolge_drive

'''
This uploads files from flah drive to Google Drive and deletes files older than one week in the flash drive
'''

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
import time
from datetime import datetime, timedelta

# --- Setup Authentication ---
gauth = GoogleAuth()
gauth.LoadCredentialsFile("mycreds.txt")

if gauth.credentials is None:
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    gauth.Refresh()
else:
    gauth.Authorize()

gauth.SaveCredentialsFile("mycreds.txt")
drive = GoogleDrive(gauth)

# --- Path to flash drive 
FLASH_DRIVE_PATH = "/media/logger/SEEPAGE_TAN"

# --- File to track uploaded files ---
UPLOADED_TRACK_FILE = "/home/pi/uploaded_files.txt"

# --- Load uploaded files list ---
if os.path.exists(UPLOADED_TRACK_FILE):
    with open(UPLOADED_TRACK_FILE, "r") as f:
        uploaded_files = set(line.strip() for line in f.readlines())
else:
    uploaded_files = set()

# --- Defining cutoff time for deleting files older than 7 days ---
ONE_WEEK_AGO = time.time() - (7 * 24 * 60 * 60)

# --- Upload new files & delete old ones in the flash drive ---
if os.path.exists(FLASH_DRIVE_PATH):
    for filename in os.listdir(FLASH_DRIVE_PATH):
        file_path = os.path.join(FLASH_DRIVE_PATH, filename)

        # Skip if not a file
        if not os.path.isfile(file_path):
            continue

        # Delete files older than 7 days
        if os.path.getmtime(file_path) < ONE_WEEK_AGO:
            print(f"Deleting old file: {filename}")
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error deleting {filename}: {e}")
            continue

        # Skip files already uploaded
        if filename in uploaded_files:
            continue

        # Upload file to Google Drive
        print(f"⬆️ Uploading: {filename}")
        try:
            gfile = drive.CreateFile({'title': filename})
            gfile.SetContentFile(file_path)
            gfile.Upload()
            print(f"✅ Uploaded: {filename}")
            # Mark file as uploaded
            with open(UPLOADED_TRACK_FILE, "a") as f:
                f.write(filename + "\n")
        except Exception as e:
            print(f"Failed to upload {filename}: {e}")
else:
    print(f"⚠️ Flash drive not found at: {FLASH_DRIVE_PATH}")
