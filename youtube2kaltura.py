"""AUTOMATED YOUTUBE VIDEO DOWNLOAD & UPLOAD TO KALTURA KMS"""

""""
TODO:
- extract title, description, thumbnail, and more from JSON
- run LLM to generate description, where missing
- run Whisper to get captions, in different languages
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

import ytdownload_videos
import kaltura_video_upload


download_youtube_videos = False # False to test post-processing steps from saved files

if download_youtube_videos:
    youtube_url = "https://www.youtube.com/playlist?list=PL-Q2v2azALUPW9j2mfKc3posK7tIcwqHe"
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
    # "DE",
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
        
        caption_files = []
        
        for lang in target_languages:
            print(f"  Generating {lang} captions...")
            try:
                # For the first language, we'll use it as source and target
                if lang == target_languages[0]:
                    srt_path = generate_srt(mp4_file, source_lang=lang, output_lang=lang)
                    # Rename the output file to include language code
                    base_path = mp4_file.rsplit(".", 1)[0]
                    new_srt_path = f"{base_path}_{lang.lower()}.srt"
                    if srt_path != new_srt_path:
                        os.rename(srt_path, new_srt_path)
                        srt_path = new_srt_path
                else:
                    # For other languages, use the first language as source
                    source_lang = target_languages[0]
                    base_path = mp4_file.rsplit(".", 1)[0]
                    srt_path = f"{base_path}_{lang.lower()}.srt"
                    generate_srt(mp4_file, source_lang=source_lang, output_lang=lang)
                
                caption_files.append(srt_path)
                print(f"  ✅ {lang} captions saved to: {os.path.basename(srt_path)}")
            except Exception as e:
                print(f"  ❌ Error generating {lang} captions: {e}")
        
        results[mp4_file] = caption_files
    
    return results



captions = generate_captions(youtube_download_path_with_files)



# End Chrono
run_time = round((time.time() - start_time), 3)
print(f'\n{os.path.basename(__file__)} finished in {round(run_time)}s at {datetime.now().strftime("%H:%M:%S")}.\n')