# Credentials management in .env file
from dotenv import load_dotenv
load_dotenv()


"""
Script to find the most recent .mp4 file in a specified folder
and upload it to Kaltura using the upload_video_to_kaltura function.
"""

import os
import glob
from datetime import datetime
import time
import subprocess
from kaltura_video_upload import upload_video_to_kaltura
from generate_metadata import generate_description
from generate_thumbnails import generate_video_thumbnail

# Start Chrono
start_time = time.time()
ts_time = f"{datetime.now().strftime('%H:%M:%S')}"
ts_file = f"{datetime.now().strftime('%y%m%d-%H%M')}"
print(f"\n---------- {ts_time} starting {os.path.basename(__file__)}")

# Define the folder path to search for videos
VIDEO_FOLDER = "/Users/nic/vid"

def get_latest_mp4_file(folder_path):
    """Find the most recent .mp4 file in the specified folder."""
    # Get all .mp4 files in the folder
    mp4_files = glob.glob(os.path.join(folder_path, "*.mp4"))
    
    if not mp4_files:
        return None
    
    # Sort files by modification time (most recent first)
    latest_file = max(mp4_files, key=os.path.getmtime)
    return latest_file




if __name__ == "__main__":

    USER_SECRET = os.getenv("user_secret")
    ADMIN_SECRET = os.getenv("admin_secret")
    PARTNER_ID = os.getenv("partner_id")

    # Find the latest .mp4 file
    latest_video = get_latest_mp4_file(VIDEO_FOLDER)
    
    if not latest_video:
        print(f"❌ No .mp4 files found in {VIDEO_FOLDER}")
        exit()
    
    # Prepare upload parameters
    base_filename = os.path.basename(latest_video)
    # Remove the .mp4 extension first
    filename_without_ext = os.path.splitext(base_filename)[0]
    
    # Remove date prefix (YYMMDD) and any appendix if they exist
    if len(filename_without_ext) > 6 and filename_without_ext[:6].isdigit():
        # Remove the date and optional appendix after the dash
        clean_title = filename_without_ext[7:].split('-', 1)[-1].strip()
    else:
        clean_title = filename_without_ext
        
    video_title = clean_title
    video_description = generate_description(latest_video)
    channel_id = 324250232  # My KMS "unlisted" channel ID = 324250232
    
    print(f"\nUploading latest video:\t\t{latest_video}")
    print(f"Title:\t\t\t\t{video_title}")
    print(f"Description:\t\t\t{video_description}")

    thumbnail_file_path = generate_video_thumbnail(latest_video)

    # Upload the video to Kaltura
    video_url = upload_video_to_kaltura(
        file_path=latest_video,
        title=video_title,
        description=video_description,
        thumbnail_file_path=thumbnail_file_path,
        channel_id=channel_id,
        USER_SECRET=USER_SECRET,
        ADMIN_SECRET=ADMIN_SECRET,
        PARTNER_ID=PARTNER_ID
    )

    # Copy the message to the clipboard using pbcopy
    process = subprocess.Popen('pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
    process.communicate(input=video_url.encode('utf-8'))
    
    print(f"\nVideo URL (copied to the clipboard 📋):\t\t\t{video_url}\n")

    # End Chrono
    run_time = time.time() - start_time
    minutes = int(run_time // 60)
    seconds = round(run_time % 60, 3)
    print(f'\n{"-" * 50}\n{os.path.basename(__file__)} finished in {minutes}m{seconds}s at {datetime.now().strftime("%H:%M:%S")}.\n')
