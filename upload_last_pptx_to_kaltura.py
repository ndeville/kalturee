# Credentials management in .env file
from dotenv import load_dotenv
load_dotenv()


"""
Script to find the most recent .mp4 file in a specified folder
and upload it to Kaltura using the upload_pptx_to_kaltura function.
"""

import os
import glob
from datetime import datetime
import time
import subprocess
from kaltura_ppt_upload import upload_ppt_to_kaltura
# from generate_metadata import generate_description
# from generate_thumbnails import generate_pptx_thumbnail
import ollama

# Start Chrono
start_time = time.time()
ts_time = f"{datetime.now().strftime('%H:%M:%S')}"
ts_file = f"{datetime.now().strftime('%y%m%d-%H%M')}"
print(f"\n---------- {ts_time} starting {os.path.basename(__file__)}")

# Define the folder path to search for presentations
PPTX_FOLDER = os.getenv("PPTX_FOLDER")

def get_latest_pptx_file(folder_path):
    # """Find the most recent .pptx file recursively in the specified folder and its subfolders."""
    # Get all .pptx files in the folder and subfolders
    pptx_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.pptx'):
                pptx_files.append(os.path.join(root, file))
    
    if not pptx_files:
        return None
    
    # Sort files by modification time (most recent first)
    latest_file = max(pptx_files, key=os.path.getmtime)
    return latest_file




if __name__ == "__main__":

    USER_SECRET = os.getenv("user_secret")
    ADMIN_SECRET = os.getenv("admin_secret")
    PARTNER_ID = os.getenv("partner_id")

    # Find the latest .pptx file
    latest_pptx = get_latest_pptx_file(PPTX_FOLDER)
    
    if not latest_pptx:
        print(f"❌ No .pptx files found in {PPTX_FOLDER}")
        exit()
    
    # Prepare upload parameters
    base_filename = os.path.basename(latest_pptx)
    # Remove the .pptx extension first
    filename_without_ext = os.path.splitext(base_filename)[0]
    
    # Remove date prefix (YYMMDD) and any appendix if they exist
    if len(filename_without_ext) > 6 and filename_without_ext[:6].isdigit():
        # Remove the date and optional appendix after the dash
        clean_title = filename_without_ext[7:].split('-', 1)[-1].strip()
    else:
        clean_title = filename_without_ext
        
    # pptx_title = clean_title
    # pptx_description = generate_description_from_ppt(latest_pptx)
    # thumbnail_file_path = generate_pptx_thumbnail(latest_pptx)
    channel_id = 324250232  # My KMS "unlisted" channel ID = 324250232
    
    print(f"\n\nℹ️  Uploading latest presentation:\t{latest_pptx}\n")
    # print(f"Title:\t\t\t\t{pptx_title}")
    # print(f"Description:\t\t\t{pptx_description}")
    # print(f"Thumbnail:\t\t\t{thumbnail_file_path}")

    # Upload the PPTX to Kaltura
    pptx_url = upload_ppt_to_kaltura(
        file_path=latest_pptx,
        channel_id=channel_id,
        demo_mode=False,
        ppt_thumbnail_path=None,
        title_text=None,
        subtitle_text=None,
        MY_USER_SECRET=USER_SECRET, 
        MY_ADMIN_SECRET=ADMIN_SECRET, 
        MY_PARTNER_ID=PARTNER_ID
        )


    # Copy the message to the clipboard using pbcopy
    process = subprocess.Popen('pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
    process.communicate(input=pptx_url.encode('utf-8'))
    
    print(f"\nPPTX URL (copied to the clipboard 📋):\t\t\t{pptx_url}\n")

    # End Chrono
    run_time = time.time() - start_time
    minutes = int(run_time // 60)
    seconds = round(run_time % 60, 3)
    print(f'\n{"-" * 50}\n{os.path.basename(__file__)} finished in {minutes}m{seconds}s at {datetime.now().strftime("%H:%M:%S")}.\n')
