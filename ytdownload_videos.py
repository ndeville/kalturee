from datetime import datetime
import os
ts_db = f"{datetime.now().strftime('%Y-%m-%d %H:%M')}"
ts_time = f"{datetime.now().strftime('%H:%M:%S')}"
print(f"\n---------- {ts_time} starting {os.path.basename(__file__)}")
import time
start_time = time.time()

from dotenv import load_dotenv
load_dotenv()
DB_BTOB = os.getenv("DB_BTOB")
DB_MAILINGEE = os.getenv("DB_MAILINGEE")

import pprint
pp = pprint.PrettyPrinter(indent=4)

####################
# Download videos from YouTube with yt-dlp

# IMPORTS

import my_utils
# from DB.tools import select_all_records, update_record, create_record, delete_record
import sqlite3

# GLOBALS

test = 1
verbose = 1

count_row = 0
count_total = 0
count = 0


# FUNCTIONS

def download_youtube_video(url, output_path=None, format='mp4'):
    """
    Download a YouTube video using yt-dlp along with its thumbnail and metadata
    
    Args:
        url (str): YouTube URL to download
        output_path (str, optional): Directory to save the video. Defaults to current directory.
        format (str, optional): Video format. Defaults to 'mp4'.
    
    Returns:
        bool: True if download was successful, False otherwise
    """
    try:
        import yt_dlp
        import json
        from PIL import Image
        import glob
        
        if not output_path:
            output_path = os.getcwd()
            
        # Make sure output directory exists
        os.makedirs(output_path, exist_ok=True)
            
        # Configure yt-dlp options
        ydl_opts = {
            'format': f'bestvideo[ext={format}]+bestaudio[ext=m4a]/best[ext={format}]',
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'writethumbnail': True,  # Download thumbnail
            'writeinfojson': True,   # Save metadata as JSON
            'quiet': not verbose,
            'progress': verbose
        }
        
        # Create a yt-dlp instance and download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading video from: {url}")
            info = ydl.extract_info(url, download=True)
            video_title = info.get('title', 'Unknown title')
            
            if verbose:
                print(f"Downloaded: {video_title}")
            
            # Convert webp thumbnail to jpg
            webp_files = glob.glob(os.path.join(output_path, f"{video_title}*.webp"))
            for webp_file in webp_files:
                try:
                    jpg_file = webp_file.replace('.webp', '.jpg')
                    Image.open(webp_file).convert("RGB").save(jpg_file, "JPEG")
                    # Remove original webp file after conversion
                    os.remove(webp_file)
                    if verbose:
                        print(f"Converted thumbnail to JPG: {jpg_file}")
                except Exception as e:
                    print(f"Error converting thumbnail: {e}")
            
            if verbose:
                print(f"Thumbnail and metadata saved to: {output_path}")
            
            global count
            count += 1
            return True
            
    except Exception as e:
        print(f"Error downloading video: {e}")
        return False

# MAIN

vpn_connection =my_utils.connect_vpn()

print(f"vpn_connection:\t{vpn_connection}")
print(type(vpn_connection))

if vpn_connection:

    print(f"✅ Connected to VPN")

    youtube_url = "https://www.youtube.com/watch?v=pYsv9hxGo_0"  # Replace with your desired YouTube URL
    # youtube_url = "https://www.youtube.com/@GlencoreVideos"  # Replace with your desired YouTube URL
    download_folder = "/Users/nic/Downloads/temp"  # Folder to save downloaded videos

    # Download the video
    success = download_youtube_video(youtube_url, download_folder)

    if success:
        print("\n✅ Download completed successfully!")
    else:
        print("\n❌ Download failed.")

else:
    print(f"❌ Failed to connect to VPN")

my_utils.disconnect_vpn()

########################################################################################################

if __name__ == '__main__':
    print('\n\n-------------------------------')
    # print(f"\ncount_row:\t{count_row:,}")
    # print(f"count_total:\t{count_total:,}")
    # print(f"count:\t\t{count:,}")
    run_time = round((time.time() - start_time), 3)
    if run_time < 1:
        print(f'\n{os.path.basename(__file__)} finished in {round(run_time*1000)}ms at {datetime.now().strftime("%H:%M:%S")}.\n')
    elif run_time < 60:
        print(f'\n{os.path.basename(__file__)} finished in {round(run_time)}s at {datetime.now().strftime("%H:%M:%S")}.\n')
    elif run_time < 3600:
        print(f'\n{os.path.basename(__file__)} finished in {round(run_time/60)}mns at {datetime.now().strftime("%H:%M:%S")}.\n')
    else:
        print(f'\n{os.path.basename(__file__)} finished in {round(run_time/3600, 2)}hrs at {datetime.now().strftime("%H:%M:%S")}.\n')