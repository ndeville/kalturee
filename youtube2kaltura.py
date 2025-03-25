"""
AUTOMATED YOUTUBE VIDEO DOWNLOAD & UPLOAD TO KALTURA KMS
1) download a Youtube URL (video/playlist/channel) to a folder (incl. videos & metadata JSON)
2) download captions OR generate captions for each video, in different languages
3) download official Youtube thumbnail for each video OR generate a .jpg for each video
4) generate title, description, tags, etc. using AI
4) upload videos to Kaltura with thumbnail, captions, title, description, tags.

TODO:
- extract title, description, thumbnail, and more from JSON
- run LLM to generate description, where missing
- upload videos to Kaltura
"""

from datetime import datetime
import os
ts_time = f"{datetime.now().strftime('%H:%M:%S')}"
ts_file = f"{datetime.now().strftime('%y%m%d-%H%M')}"
print(f"\n---------- {ts_time} starting {os.path.basename(__file__)}")

# Start Chrono
import time
start_time = time.time()

import my_utils

import ytdownload_videos
import kaltura_video_upload


download_youtube_videos = True # False to test post-processing steps from saved files
youtube_url = "https://www.youtube.com/playlist?list=PL-Q2v2azALUPW9j2mfKc3posK7tIcwqHe"

if download_youtube_videos:
    youtube_download_path_with_files = ytdownload_videos.process_youtube_url_to_download(youtube_url)
    print(f"\n\n{youtube_download_path_with_files=}")
else:
    youtube_download_path_with_files = "/Users/nic/Movies/Youtube/2503221756"

print(f"\n\nProcessing files in {youtube_download_path_with_files}")

# JSON



# CAPTIONS

target_languages = [
    "EN",
    "FR",
    "DE",
    # "ES",
    # "IT",
    # "PT",
    # "AR",
]

import os
import glob
from generate_captions import generate_srt

def generate_captions(download_folder):
    """
    Generate captions for all MP4 files in the download folder for each target language.
    
    Args:
        download_folder (str): Path to the folder containing downloaded videos
        
    Returns:
        dict: Dictionary mapping video paths to lists of generated caption files
    """
    results = {}
    
    # Find all MP4 files in the download folder
    mp4_files = glob.glob(os.path.join(download_folder, "*.mp4"))
    
    if not mp4_files:
        print(f"No MP4 files found in {download_folder}")
        return results
    
    print(f"Found {len(mp4_files)} MP4 files to process")
    
    for mp4_file in mp4_files:
        video_name = os.path.basename(mp4_file)
        print(f"\nProcessing captions for: {video_name}")
        
        # caption_files = []
        
        for lang in target_languages:
            print(f"  Generating {lang} captions...")
            srt_path = generate_srt(mp4_file, source_lang="EN", output_lang=lang)


captions = generate_captions(youtube_download_path_with_files)


# THUMBNAIL
"""
Download official Youtube thumbnail for each .mp4 file, using the JSON file.
OR
Generate a .jpg for each .mp4 file (logic TBC).
"""

# End Chrono
run_time = round((time.time() - start_time), 3)
print(f'\n{os.path.basename(__file__)} finished in {round(run_time)}s at {datetime.now().strftime("%H:%M:%S")}.\n')