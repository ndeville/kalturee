#!/usr/bin/env python3
import sys
import json
import os
import argparse
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
from datetime import datetime


def get_video_duration_info(video_url):
    try:
        # Configure minimal options to just extract info
        info_opts = {
            'quiet': True,
            'skip_download': True,
            'no_warnings': True,
            'ignoreerrors': False,
            'noplaylist': True,
        }
        
        with YoutubeDL(info_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # Get duration in seconds
            duration_seconds = info.get('duration', 0)
            
            # Convert to hours:minutes:seconds format
            hours, remainder = divmod(duration_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            if hours > 0:
                duration_formatted = f"{hours}:{minutes:02d}:{seconds:02d}"
            else:
                duration_formatted = f"{minutes}:{seconds:02d}"
            
            return duration_seconds, duration_formatted
            
    except Exception as e:
        print(f"⚠️  Could not retrieve video duration: {str(e)}")
        return 0, "unknown"



def download_video_with_metadata(url, output_dir, list_formats=False, format_id=None):

    # Print the URL being processed
    # Get and print the video duration
    duration_seconds, duration_formatted = get_video_duration_info(url)
    print(f"\n⚙️  Processing YouTube URL {duration_formatted}: {url}\n")

    # Get timestamp for filename
    # from datetime import datetime
    # timestamp = datetime.now().strftime('%y%m%d%H%M')
    
    # Configure yt-dlp options
    ydl_opts = {
        'format': format_id if format_id else 'bestvideo+bestaudio/best',  # Select specific format or use merged streams
        'merge_output_format': 'mp4',  # Force merged output to be mp4
        # 'outtmpl': os.path.join(output_dir, f'{timestamp}_%(title)s.%(ext)s'),
        'outtmpl': os.path.join(output_dir, f'%(title)s.%(ext)s'),
        'writeinfojson': True,
        'writesubtitles': True,
        # 'subtitleslangs': ['en', 'de', 'fr', 'es', 'it', 'ja', 'ko', 'pt', 'ru', 'zh'],
        'subtitleslangs': ['en', 'de', 'fr'],
        # 'skip_download': list_formats,  # Skip download if just listing formats
        'quiet': False,
        'skip-download': True,
        'write-thumbnail': True,
        'no_warnings': False,
        'ignoreerrors': False,
        'noplaylist': True,  # Ignore playlist, just download the video
        'listformats': list_formats,  # List formats if requested
        'cookies_from_browser': 'chrome',  # Extract cookies from browser, set to browser name if needed
        # 'username': os.getenv("YOUTUBE_EMAIL"), # Add YouTube Premium authentication
        # 'password': os.getenv("YOUTUBE_PASSWORD"), # Add YouTube Premium authentication
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
            
            print(f"\n✅ Video downloaded successfully: {video_path}\n\n\n")
            
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


def get_list_of_videos_in_channel_sorted_by_duration(channel_url, limit=None, verbose=False):
    try:
        ydl_opts = {
            'extract_flat': 'in_playlist',
            'quiet': not verbose,
            'ignoreerrors': True,
            'simulate': True,
            'no_warnings': True,
            'playlistend': limit if limit else None
        }
        
        if "/@" in channel_url and not channel_url.endswith('/videos'):
            channel_url = channel_url + '/videos'
        
        with YoutubeDL(ydl_opts) as ydl:
            channel_info = ydl.extract_info(channel_url, download=False)
            
            all_videos = []
            
            if channel_info.get('_type') == 'playlist':
                for item in channel_info.get('entries', []):
                    if item.get('_type') == 'playlist':
                        for video in item.get('entries', []):
                            if video and video.get('_type') != 'playlist':
                                all_videos.append(video)
                    elif item:
                        all_videos.append(item)
            
            video_data = []
            for entry in all_videos:
                if not entry:
                    continue
                
                video_info = {
                    'url': entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}",
                    'duration': entry.get('duration', 0)
                }
                video_data.append(video_info)
            
            video_data_sorted = sorted(video_data, key=lambda x: x['duration'], reverse=True)
            # return {video['url']: video['duration'] for video in video_data_sorted} # can't use a dict because unsorted and we need to keep the order
            return [video['url'] for video in video_data_sorted]
        
    except Exception as e:
        if verbose:
            print(f"Error fetching channel videos: {e}")
        return []




# write a function called process_youtube_channel(youtube_channel_url) that first fetches the sorted list of videos by duration using get_list_of_videos_in_channel_sorted_by_duration, then downloads each video with metadata using download_video_with_metadata

def process_youtube_channel(youtube_channel_url, max_videos_to_download=None):
    print(f"\n\n⚙️  Processing YouTube channel {youtube_channel_url} to get list of videos")
    videos = get_list_of_videos_in_channel_sorted_by_duration(youtube_channel_url)
    output_dir = f"/Users/nic/dl/yt/{youtube_channel_url.split('/')[-1].replace('@', '')}"
    
    if max_videos_to_download:
        print(f"\nLimiting download to {max_videos_to_download} videos")
        videos = videos[:max_videos_to_download]
    
    print(f"\n\n⚙️  Processing YouTube channel {youtube_channel_url} to download videos")
    for video in videos:
        download_video_with_metadata(video, output_dir)
    return output_dir






if __name__ == "__main__":

    output_dir=f"/Users/nic/dl/yt/abb"

    # # First list available formats
    # print("\n\nListing available formats:")
    # download_video_with_metadata("https://www.youtube.com/watch?v=QpHZHtBkoKw", list_formats=True)
    # get_list_of_videos_in_channel_sorted_by_duration("https://www.youtube.com/@abb")
    # get_list_of_videos_in_channel_sorted_by_duration("https://www.youtube.com/@lcl")

    process_youtube_channel("https://www.youtube.com/@GroupeCreditAgricole", max_videos_to_download=5)
    
    # print("\nNow attempting to download playlist:")
    # successfully_downloaded = download_playlist("https://www.youtube.com/playlist?list=PL17765924A33BEADB")
    # print(f"\n\nTotal videos successfully downloaded: {len(successfully_downloaded)}")

    # If the above fails, you could try with specific format IDs from the list:
    # For example, to get 1080p video + audio:
    # download_video_with_metadata("https://www.youtube.com/watch?v=QpHZHtBkoKw", format_id="270+234")