from datetime import datetime
import os
ts_db = f"{datetime.now().strftime('%Y-%m-%d %H:%M')}"
ts_time = f"{datetime.now().strftime('%H:%M:%S')}"
ts_folder = f"{datetime.now().strftime('%y%m%d%H%M')}"
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
            
        os.makedirs(output_path, exist_ok=True)
            
        # Add YouTube Premium authentication
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'writethumbnail': True,
            'writeinfojson': True,
            'quiet': not verbose,
            'progress': verbose,
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'extract_flat': False,
            'playlist': True,
            'yes_playlist': True,
            # Add YouTube authentication
            'username': os.getenv('YOUTUBE_EMAIL'),      # Your YouTube/Google email
            'password': os.getenv('YOUTUBE_PASSWORD'),   # Your YouTube/Google password
        }
        
        # Create a yt-dlp instance and download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading from: {url}")
            # First extract info to check if it's a playlist
            meta_info = ydl.extract_info(url, download=False)
            
            if '_type' in meta_info and meta_info['_type'] == 'playlist':
                print(f"Playlist detected with {len(meta_info['entries'])} videos")
                # Download each video in the playlist
                for entry in meta_info['entries']:
                    if entry:
                        video_url = entry['webpage_url']
                        print(f"\nProcessing video: {entry.get('title', 'Unknown')}")
                        ydl.download([video_url])
            else:
                # Single video
                ydl.download([url])
            
            # Convert webp thumbnail to jpg
            webp_files = glob.glob(os.path.join(output_path, f"*{ydl_opts['outtmpl'][-10:]}*"))
            
            # If no files found with the exact title match, try a more flexible approach
            if not webp_files:
                # Look for any webp files that might have been created recently
                webp_files = glob.glob(os.path.join(output_path, "*.webp"))
                
                # Alternative: use the info dict to get the exact filename
                if 'thumbnails' in meta_info and meta_info['thumbnails']:
                    for thumb in meta_info['thumbnails']:
                        if 'filename' in thumb:
                            potential_file = os.path.join(output_path, thumb['filename'])
                            if os.path.exists(potential_file) and potential_file.endswith('.webp'):
                                webp_files.append(potential_file)
            
            if webp_files:
                if verbose:
                    print(f"Found {len(webp_files)} webp thumbnails to convert")
            else:
                print("No webp thumbnails found to convert")
                
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

def process_youtube_url_to_download(youtube_url=None):
    """
    Main function to download YouTube videos
    
    Args:
        youtube_url (str, optional): YouTube URL to download, defaults to a specific playlist
        
    Returns:
        str: Path to the folder where videos were downloaded
    """
    # Create a timestamped folder for this run
    download_path = os.path.join("/Users/nic/Movies/Youtube", ts_folder)
    os.makedirs(download_path, exist_ok=True)
    
    print(f"\nℹ️  Files will be saved to: {download_path}")
    
    # vpn_connection = my_utils.connect_vpn() # <class 'subprocess.Popen'> but reverts to True/False it seems

    # if vpn_connection:
    # print(f"✅ Connected to VPN")
    
    # Use the timestamped folder
    download_folder = download_path
    
    # Download the video
    success = download_youtube_video(youtube_url, download_folder)
    
    if success:
        print(f"\n✅ Download completed successfully! Files saved to {download_folder}")
    else:
        print("\n❌ Download failed.")
        
    # else:
    #     print(f"❌ Failed to connect to VPN")
    
    # my_utils.disconnect_vpn()
    
    return download_path

# MAIN

if __name__ == '__main__':

    # youtube_url = "https://www.youtube.com/watch?v=pYsv9hxGo_0"
    # youtube_url = "https://www.youtube.com/@GlencoreVideos"
    # youtube_url = "https://www.youtube.com/playlist?list=PL-Q2v2azALUPW9j2mfKc3posK7tIcwqHe" # ABB ?
    youtube_url = "https://www.youtube.com/watch?v=7zT17jK5qLU&list=PLSWR1ylG_6JYl612AZJ_hA0N0y5EgOp_y"

    process_youtube_url_to_download(youtube_url)


    run_time = round((time.time() - start_time), 3)
    if run_time < 1:
        print(f'\n{os.path.basename(__file__)} finished in {round(run_time*1000)}ms at {datetime.now().strftime("%H:%M:%S")}.\n')
    elif run_time < 60:
        print(f'\n{os.path.basename(__file__)} finished in {round(run_time)}s at {datetime.now().strftime("%H:%M:%S")}.\n')
    elif run_time < 3600:
        print(f'\n{os.path.basename(__file__)} finished in {round(run_time/60)}mns at {datetime.now().strftime("%H:%M:%S")}.\n')
    else:
        print(f'\n{os.path.basename(__file__)} finished in {round(run_time/3600, 2)}hrs at {datetime.now().strftime("%H:%M:%S")}.\n')