#!/usr/bin/env python3
import sys
import json
import os
import argparse
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
from datetime import datetime

def download_video_with_metadata(url, list_formats=False, format_id=None):
    global output_dir

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get timestamp for filename
    from datetime import datetime
    timestamp = datetime.now().strftime('%y%m%d%H%M')
    
    # Configure yt-dlp options
    ydl_opts = {
        'format': format_id if format_id else 'bestvideo+bestaudio/best',  # Select specific format or use merged streams
        'merge_output_format': 'mp4',  # Force merged output to be mp4
        # 'outtmpl': os.path.join(output_dir, f'{timestamp}_%(title)s.%(ext)s'),
        'outtmpl': os.path.join(output_dir, f'%(title)s.%(ext)s'),
        'writeinfojson': True,
        'writesubtitles': True,
        'subtitleslangs': ['en', 'de', 'fr', 'es', 'it', 'ja', 'ko', 'pt', 'ru', 'zh'],
        'skip_download': list_formats,  # Skip download if just listing formats
        'quiet': False,
        'no_warnings': False,
        'ignoreerrors': False,
        'noplaylist': True,  # Ignore playlist, just download the video
        'listformats': list_formats,  # List formats if requested
        'username': os.getenv("YOUTUBE_EMAIL"), # Add YouTube Premium authentication
        'password': os.getenv("YOUTUBE_PASSWORD"), # Add YouTube Premium authentication
    }
    
    try:
        # Download video and metadata
        with YoutubeDL(ydl_opts) as ydl:
            if list_formats:
                ydl.extract_info(url, download=False)
                return True, None, "Formats listed above"
            
            info = ydl.extract_info(url, download=True)
            
            # Get video and metadata file paths
            video_title = info.get('title', 'video')
            video_ext = info.get('ext', 'mp4')
            video_path = os.path.join(output_dir, f"{video_title}.{video_ext}")
            metadata_path = os.path.join(output_dir, f"{video_title}.json")
            
            print(f"\n✅ Video downloaded successfully: {video_path}")
            
            return video_path
            
    except DownloadError as e:
        print(f"❌ Error downloading video: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ An unexpected error occurred: {str(e)}")
        return False


def download_playlist(playlist_url, format_id=None):
    global output_dir

    # First, extract playlist info to get video URLs
    ydl_opts = {
        'quiet': False,
        'no_warnings': False,
        'ignoreerrors': True,  # Important: ignore errors to continue with playlist
        'extract_flat': True,  # Don't download videos yet, just get info
    }
    
    successful_downloads = []
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            playlist_info = ydl.extract_info(playlist_url, download=False)
            
            if 'entries' not in playlist_info:
                print(f"❌ Error: Could not find videos in the playlist: {playlist_url}")
                return successful_downloads
            
            total_videos = len(playlist_info['entries'])
            print(f"\nFound {total_videos} videos in playlist '{playlist_info.get('title', 'Unknown')}'")
            
            # Process each video
            for index, entry in enumerate(playlist_info['entries']):
                if not entry:
                    print(f"⚠️ Skipping unavailable video at position {index+1}")
                    continue
                
                video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                print(f"\n[{index+1}/{total_videos}] Attempting to download: {entry.get('title', 'Unknown video')}")
                
                try:
                    video_path = download_video_with_metadata(
                        video_url, 
                        format_id=format_id
                    )
                    
                    if video_path:
                        successful_downloads.append(video_path)
                        print(f"✅ Successfully downloaded video {index+1}/{total_videos}")
                    else:
                        print(f"⚠️ Failed to download video {index+1}/{total_videos}")
                        
                except Exception as e:
                    print(f"❌ Error downloading video {index+1}/{total_videos}: {str(e)}")
                    print(f"Continuing with next video...")
    
    except Exception as e:
        print(f"❌ Error processing playlist: {str(e)}")
    
    print(f"\n✅ Successfully downloaded {len(successful_downloads)}/{total_videos} videos")
    return successful_downloads

if __name__ == "__main__":

    output_dir=f"/Users/nic/dl/yt/{datetime.now().strftime('%y%m%d%H%M')}"

    # # First list available formats
    # print("\n\nListing available formats:")
    # download_video_with_metadata("https://www.youtube.com/watch?v=QpHZHtBkoKw", list_formats=True)
    
    # # Then download with explicit format specification
    print("\nNow attempting to download playlist:")
    # Try best video + best audio combination
    successfully_downloaded = download_playlist("https://www.youtube.com/playlist?list=PL17765924A33BEADB")

    print(f"\n\nTotal videos successfully downloaded: {len(successfully_downloaded)}")

    # If the above fails, you could try with specific format IDs from the list:
    # For example, to get 1080p video + audio:
    # download_video_with_metadata("https://www.youtube.com/watch?v=QpHZHtBkoKw", format_id="270+234")