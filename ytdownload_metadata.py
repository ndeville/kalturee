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
# SCRIPT_TITLE

# IMPORTS

# import my_utils
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
    Download a YouTube video using yt-dlp
    
    Args:
        url (str): YouTube URL to download
        output_path (str, optional): Directory to save the video. Defaults to current directory.
        format (str, optional): Video format. Defaults to 'mp4'.
    
    Returns:
        bool: True if download was successful, False otherwise
    """
    try:
        import yt_dlp
        
        if not output_path:
            output_path = os.getcwd()
            
        # Make sure output directory exists
        os.makedirs(output_path, exist_ok=True)
            
        # Configure yt-dlp options
        ydl_opts = {
            'format': f'bestvideo[ext={format}]+bestaudio[ext=m4a]/best[ext={format}]',
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'quiet': not verbose,
            'progress': verbose
        }
        
        # Create a yt-dlp instance and download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading video from: {url}")
            info = ydl.extract_info(url, download=True)
            if verbose:
                print(f"Downloaded: {info.get('title', 'Unknown title')}")
            
            global count
            count += 1
            return True
            
    except Exception as e:
        print(f"Error downloading video: {e}")
        return False

def get_youtube_channel_videos(channel_url, limit=None):
    """
    Get a list of videos and their metadata from a YouTube channel
    
    Args:
        channel_url (str): YouTube channel URL
        limit (int, optional): Maximum number of videos to retrieve. None means all videos.
    
    Returns:
        list: List of dictionaries containing video metadata
    """
    try:
        import yt_dlp
        
        # Configure yt-dlp options for retrieving all videos
        ydl_opts = {
            'extract_flat': 'in_playlist',
            'quiet': not verbose,
            'ignoreerrors': True,
            'simulate': True,
            'no_warnings': True,
            'playlistend': limit if limit else None  # Limit if specified
        }
        
        # If getting all videos, need to fetch the channel's playlist URL
        if "/@" in channel_url:
            # Add /videos to the URL to ensure we get the videos tab
            if not channel_url.endswith('/videos'):
                channel_url = channel_url + '/videos'
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Fetching videos from channel: {channel_url}")
            channel_info = ydl.extract_info(channel_url, download=False)
            
            # Get all videos from the channel
            all_videos = []
            
            # Handle the nested playlist structure
            if channel_info.get('_type') == 'playlist':
                for item in channel_info.get('entries', []):
                    if item.get('_type') == 'playlist':
                        # This is a tab (like 'Videos' or 'Shorts')
                        print(f"Processing playlist: {item.get('title')}")
                        
                        # Extract all videos from this tab
                        for video in item.get('entries', []):
                            if video and video.get('_type') != 'playlist':
                                all_videos.append(video)
                    elif item:
                        # Direct video item
                        all_videos.append(item)
            
            # Extract relevant metadata
            videos = []
            for entry in all_videos:
                if not entry:
                    continue
                
                video_data = {
                    'title': entry.get('title', 'Unknown title'),
                    'id': entry.get('id'),
                    'url': entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}",
                    'upload_date': entry.get('upload_date'),
                    'duration': entry.get('duration'),
                    'duration_string': format_duration(entry.get('duration')),
                    'view_count': entry.get('view_count'),
                    'description': entry.get('description')
                }
                videos.append(video_data)
            
            # Apply overall limit if specified
            if limit and len(videos) > limit:
                videos = videos[:limit]
                
            global count
            count = len(videos)
            
            if verbose:
                print(f"Found {count} videos total")
                
            return videos
            
    except Exception as e:
        print(f"Error fetching channel videos: {e}")
        import traceback
        traceback.print_exc()
        return []

def format_duration(seconds):
    """
    Format duration in seconds to a readable time string (HH:MM:SS)
    
    Args:
        seconds (int or float): Duration in seconds
        
    Returns:
        str: Formatted duration string
    """
    if not seconds:
        return "Unknown"
    
    # Convert to integer to handle float values
    try:
        seconds_int = int(seconds)
        hours = seconds_int // 3600
        minutes = (seconds_int % 3600) // 60
        seconds = seconds_int % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
    except (TypeError, ValueError):
        return "Unknown"

# MAIN

# Example usage
youtube_channel_url = "https://www.youtube.com/@GroupeCreditAgricole"  # Replace with your desired YouTube channel
video_limit = None  # Set to None to get all videos, or a number to limit results

# Get videos from the channel
videos = get_youtube_channel_videos(youtube_channel_url, video_limit)

if videos:
    # Sort videos by duration (longest first)
    videos_sorted = sorted(videos, key=lambda x: x.get('duration', 0) or 0, reverse=True)
    
    print(f"\nFound {len(videos_sorted)} videos in the channel (sorted by length):")
    for i, video in enumerate(videos_sorted, 1):
        print(f"\n{i}. {video['title']}")
        print(f"   URL: {video['url']}")
        print(f"   Duration: {video['duration_string']}")
        
        if video['upload_date']:
            # Format: YYYYMMDD to YYYY-MM-DD
            date = video['upload_date']
            formatted_date = f"{date[:4]}-{date[4:6]}-{date[6:8]}" if len(date) >= 8 else "Unknown"
            print(f"   Uploaded: {formatted_date}")
        if video['view_count']:
            print(f"   Views: {video['view_count']:,}")
else:
    print("No videos found or error occurred.")

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