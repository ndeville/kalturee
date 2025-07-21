from datetime import datetime
import os
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
import sqlite3
import yt_dlp

# GLOBALS
verbose = 1

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

def format_file_size(size_bytes):
    """
    Format file size in bytes to a human-readable string
    
    Args:
        size_bytes (int): Size in bytes
        
    Returns:
        str: Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

def get_channel_stats(channel_url):
    """
    Get statistics for all videos in a YouTube channel
    
    Args:
        channel_url (str): YouTube channel URL
    
    Returns:
        dict: Statistics including total videos, duration, and size
    """
    try:
        # Configure yt-dlp options for retrieving all videos
        ydl_opts = {
            'extract_flat': 'in_playlist',
            'quiet': not verbose,
            'ignoreerrors': True,
            'simulate': True,
            'no_warnings': True
        }
        
        # If getting all videos, need to fetch the channel's playlist URL
        if "/@" in channel_url and not channel_url.endswith('/videos'):
            channel_url = channel_url + '/videos'
        
        total_duration = 0
        total_size = 0
        video_count = 0
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            channel_info = ydl.extract_info(channel_url, download=False)
            
            # Process all videos in the channel
            for entry in channel_info.get('entries', []):
                if entry and entry.get('_type') != 'playlist':
                    duration = entry.get('duration', 0)
                    if duration:
                        total_duration += duration
                        video_count += 1
                    
                    # Estimate file size based on duration and typical bitrates
                    # Assuming average bitrate of 2 Mbps for video + 128 Kbps for audio
                    estimated_size = duration * (2 * 1024 * 1024 + 128 * 1024) / 8  # Convert to bytes
                    total_size += estimated_size
        
        return {
            'total_videos': video_count,
            'total_duration': total_duration,
            'average_duration': total_duration / video_count if video_count > 0 else 0,
            'total_size': total_size
        }
            
    except Exception as e:
        print(f"Error fetching channel stats: {e}")
        import traceback
        traceback.print_exc()
        return {
            'total_videos': 0,
            'total_duration': 0,
            'average_duration': 0,
            'total_size': 0
        }







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
if __name__ == '__main__':
    
    # youtube_channel_url = input("\nEnter the YouTube channel URL: ")
    youtube_channel_url = "https://www.youtube.com/@henkel"  # Replace with your desired YouTube channel
    
    # Run first both long processes, for a clean output/print at the end
    stats = get_channel_stats(youtube_channel_url)
    videos = get_youtube_channel_videos(youtube_channel_url)
    
    # Define table headers and data
    headers = ["Metric", "Value"]
    data = [
        ["Total Videos", f"{stats['total_videos']:,}"],
        ["Total Duration", format_duration(stats['total_duration'])],
        ["Average Duration per Video", format_duration(stats['average_duration'])],
        ["Estimated Total Size", format_file_size(stats['total_size'])]
    ]
    
    # Calculate column widths
    col1_width = max(len(str(row[0])) for row in data)
    col2_width = max(len(str(row[1])) for row in data)
    
    # Print table
    print(f"\n\n\n\n\nChannel Statistics for {youtube_channel_url}")
    print("=" * (col1_width + col2_width + 3))
    print(f"{headers[0]:<{col1_width}} | {headers[1]:<{col2_width}}")
    print("-" * (col1_width + col2_width + 3))
    for row in data:
        print(f"{row[0]:<{col1_width}}   {row[1]:<{col2_width}}")
    print("=" * (col1_width + col2_width + 3))


    # Get videos from the channel

    videos_longer_than = 1 # minutes

    if videos:
        # Sort videos by duration (longest first)
        videos_sorted = sorted(videos, key=lambda x: x.get('duration', 0) or 0, reverse=True)
        
        # Filter videos longer than 10 minutes (600 seconds)
        long_videos = [video for video in videos_sorted if video.get('duration', 0) and video['duration'] > videos_longer_than * 60]
        
        print(f"\nFound {len(long_videos)} videos longer than {videos_longer_than} minutes in the channel, out of a total of {stats['total_videos']:,} videos (sorted below by length):\n")
        for i, video in enumerate(long_videos, 1):
            # Format date if available
            formatted_date = "Unknown"
            if video['upload_date']:
                date = video['upload_date']
                formatted_date = f"{date[:4]}-{date[4:6]}-{date[6:8]}" if len(date) >= 8 else "Unknown"
            
            # Format view count
            view_count = f"{video['view_count']:,}" if video['view_count'] else "Unknown"
            
            # Print all information on a single line, starting with duration
            print(f"{video['duration_string']} | #{i}: {video['title']} | URL: {video['url']}")

