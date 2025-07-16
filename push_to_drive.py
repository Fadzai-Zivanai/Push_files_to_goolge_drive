#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 11 16:17:22 2025

@author: logger
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modified: Only upload .csv files that have corresponding .DONE file
"""

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
import time

# --- Constants ---
flash_drive_path = '/media/logger/SEEPAGE_TAN/data'  # Flash drive path
log_file = 'uploaded_files.txt'                      # Upload log (for .csv files only)
target_folder_name = 'Data_logs'                     # Google Drive folder

# --- Authenticate and save credentials ---
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

# --- Get or create the 'Data_logs' folder on Drive ---
folder_id = None
file_list = drive.ListFile({
    'q': f"title='{target_folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
}).GetList()

if file_list:
    folder_id = file_list[0]['id']
else:
    folder_metadata = {
        'title': target_folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = drive.CreateFile(folder_metadata)
    folder.Upload()
    folder_id = folder['id']
    print(f"Created folder '{target_folder_name}' in Drive.")

# --- Continuous upload loop (every 24 hours) ---
while True:
    print("\nChecking for .csv files with .DONE markers to upload...")

    # Reload uploaded files log
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            uploaded_files = set(line.strip() for line in f)
    else:
        uploaded_files = set()

    new_uploads = 0
    for filename in os.listdir(flash_drive_path):
        if filename.endswith(".csv"):
            csv_path = os.path.join(flash_drive_path, filename)
            done_path = csv_path.replace(".csv", "DONE")

            # Only upload if .DONE file exists and hasn't been uploaded before
            if os.path.isfile(csv_path) and os.path.isfile(done_path) and filename not in uploaded_files:
                try:
                    print(f"Uploading: {filename}")
                    gfile = drive.CreateFile({'title': filename, 'parents': [{'id': folder_id}]})
                    gfile.SetContentFile(csv_path)
                    gfile.Upload()
                    print(f"Uploaded: {filename}")
                    new_uploads += 1

                    # Log upload
                    with open(log_file, 'a') as f:
                        f.write(filename + '\n')

                except Exception as e:
                    print(f"Failed to upload {filename}: {e}")

    print(f"Upload check complete. {new_uploads} new files uploaded.")
    print("Sleeping for 24 hours...\n")
    time.sleep(86400)  # Sleep for 24 hours
