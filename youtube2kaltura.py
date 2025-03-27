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

import os
import glob
from generate_captions import generate_srt
from generate_metadata import generate_title, generate_description, generate_tags


# DOWNLOAD YOUTUBE VIDEOS

download_youtube_videos = False # False to test post-processing steps from saved files
youtube_url = "https://www.youtube.com/playlist?list=PL-Q2v2azALUPW9j2mfKc3posK7tIcwqHe"

if download_youtube_videos:
    youtube_download_path_with_files = ytdownload_videos.process_youtube_url_to_download(youtube_url)
    print(f"\n\n{youtube_download_path_with_files=}")
else:
    youtube_download_path_with_files = "/Users/nic/dl/yt/test"

print(f"\n\nProcessing files in {youtube_download_path_with_files}")

# JSON



# CAPTIONS

# Generate captions in English



# def generate_captions(download_folder):

#     results = {}
    
#     # Find all MP4 files in the download folder
#     mp4_files = glob.glob(os.path.join(download_folder, "*.mp4"))
    
#     if not mp4_files:
#         print(f"No MP4 files found in {download_folder}")
#         return results
    
#     print(f"Found {len(mp4_files)} MP4 files to process")
    
#     for mp4_file in mp4_files:
#         video_name = os.path.basename(mp4_file)
#         print(f"\nProcessing captions for: {video_name}")
        
#         # caption_files = []
        
#         for lang in target_languages:
#             print(f"  Generating {lang} captions...")
#             srt_path = generate_srt(mp4_file, source_lang="EN", output_lang=lang)

# Generate captions
target_languages = [
    "EN",
    "FR",
    "DE",
    # "ES",
    # "IT",
    # "PT",
    # "AR",
]




def generate_captions(download_folder, source_lang="EN", target_languages=None, model_name="large-v3"):
    """Generate captions for all MP4 files in the download folder in multiple languages."""
    if target_languages is None:
        target_languages = ["EN"]
    
    results = {}
    
    # Find all MP4 files in the download folder
    mp4_files = glob.glob(os.path.join(download_folder, "*.mp4"))
    
    if not mp4_files:
        print(f"No MP4 files found in {download_folder}")
        return results
    
    print(f"Found {len(mp4_files)} MP4 files to process")
    
    for mp4_file in mp4_files:
        video_name = os.path.basename(mp4_file)
        base_path = mp4_file.rsplit(".", 1)[0]
        
        video_results = []
        print(f"\nProcessing captions for: {video_name}")
        
        for output_lang in target_languages:
            # Check if SRT already exists
            srt_path = f"{base_path}.srt" if output_lang.upper() == "EN" else f"{base_path}_{output_lang.lower()}.srt"
            
            if os.path.exists(srt_path):
                print(f"  ⏩ Skipping {output_lang} captions - SRT file already exists: {os.path.basename(srt_path)}")
                video_results.append(srt_path)
                continue
            
            print(f"  🔄 Generating {output_lang} captions for: {video_name}")
            try:
                srt_path = generate_srt(mp4_file, source_lang=source_lang, output_lang=output_lang, model_name=model_name)
                video_results.append(srt_path)
            except Exception as e:
                print(f"  ❌ Error generating {output_lang} captions for {video_name}: {str(e)}")
        
        results[mp4_file] = video_results
    
    return results



generate_captions(youtube_download_path_with_files, source_lang="EN", target_languages=target_languages, model_name="large-v3")









# TITLE
"""each .mp4 file needs to have a _title.txt file with the title of the video inside"""

def generate_titles(folder_path):
    """
    Generate titles for all MP4 files in the folder that don't already have a title file.
    
    Args:
        folder_path (str): Path to the folder containing MP4 files
        
    Returns:
        dict: Dictionary mapping MP4 files to their generated title files
    """
    import os
    import generate_metadata
    
    mp4_files = glob.glob(os.path.join(folder_path, "*.mp4"))
    
    if not mp4_files:
        print(f"No MP4 files found in {folder_path}")
        return {}
    
    print(f"\nGenerating titles for MP4 files in {folder_path}")
    
    results = {}
    
    for mp4_file in mp4_files:
        video_name = os.path.basename(mp4_file)
        title_file_path = mp4_file.rsplit(".", 1)[0] + "_title.txt"
        
        # Skip if title file already exists
        if os.path.exists(title_file_path):
            print(f"  ⏩ Skipping title generation - Title file already exists: {os.path.basename(title_file_path)}")
            results[mp4_file] = title_file_path
            continue
        
        print(f"  🔄 Generating title for: {video_name}")
        try:
            title = generate_metadata.generate_title(mp4_file)
            print(f"  ✅ Title generated: {title}")
            results[mp4_file] = title_file_path
        except Exception as e:
            print(f"  ❌ Error generating title for {video_name}: {str(e)}")
    
    return results

# Generate titles for all MP4 files in the download folder
generate_titles(youtube_download_path_with_files)



# DESCRIPTION
"""each .mp4 file needs to have a _description.txt file with the description of the video inside"""

def generate_descriptions(folder_path):
    """
    Generate descriptions for all MP4 files in the folder that don't already have a description file.
    
    Args:
        folder_path (str): Path to the folder containing MP4 files
        
    Returns:
        dict: Dictionary mapping MP4 files to their generated description files
    """
    import os
    import generate_metadata
    
    mp4_files = glob.glob(os.path.join(folder_path, "*.mp4"))
    
    if not mp4_files:
        print(f"No MP4 files found in {folder_path}")
        return {}
    
    print(f"\nGenerating descriptions for MP4 files in {folder_path}")
    
    results = {}
    
    for mp4_file in mp4_files:
        video_name = os.path.basename(mp4_file)
        description_file_path = mp4_file.rsplit(".", 1)[0] + "_description.txt"
        
        # Skip if description file already exists
        if os.path.exists(description_file_path):
            print(f"  ⏩ Skipping description generation - Description file already exists: {os.path.basename(description_file_path)}")
            results[mp4_file] = description_file_path
            continue
        
        print(f"  🔄 Generating description for: {video_name}")
        try:
            description = generate_metadata.generate_description(mp4_file)
            print(f"  ✅ Description generated successfully")
            results[mp4_file] = description_file_path
        except Exception as e:
            print(f"  ❌ Error generating description for {video_name}: {str(e)}")
    
    return results

# Generate descriptions for all MP4 files in the download folder
generate_descriptions(youtube_download_path_with_files)



# TAGS
"""each .mp4 file needs to have a _tags.txt file with the tags of the video inside"""

def generate_tags(folder_path):
    """
    Generate tags for all MP4 files in the folder that don't already have a tags file.
    
    Args:
        folder_path (str): Path to the folder containing MP4 files
        
    Returns:
        dict: Dictionary mapping MP4 files to their generated tags files
    """
    import os
    import generate_metadata

    mp4_files = glob.glob(os.path.join(folder_path, "*.mp4"))
    
    if not mp4_files:
        print(f"No MP4 files found in {folder_path}")
        return {}   
    
    print(f"\nGenerating tags for MP4 files in {folder_path}")
    
    results = {}
    
    for mp4_file in mp4_files:
        video_name = os.path.basename(mp4_file)
        tags_file_path = mp4_file.rsplit(".", 1)[0] + "_tags.txt"
        
        # Skip if tags file already exists
        if os.path.exists(tags_file_path):
            print(f"  ⏩ Skipping tags generation - Tags file already exists: {os.path.basename(tags_file_path)}")
            results[mp4_file] = tags_file_path  
            continue
        
        print(f"  🔄 Generating tags for: {video_name}")
        try:
            tags = generate_metadata.generate_tags(mp4_file)
            print(f"  ✅ Tags generated successfully")
            results[mp4_file] = tags_file_path  
        except Exception as e:
            print(f"  ❌ Error generating tags for {video_name}: {str(e)}")
    
    return results

# Generate tags for all MP4 files in the download folder
generate_tags(youtube_download_path_with_files)




# THUMBNAIL
"""
Download official Youtube thumbnail for each .mp4 file, using the JSON file.
OR
Generate a .jpg for each .mp4 file (logic TBC).
"""





# UPLOAD VIDEOS TO KALTURA




# End Chrono
run_time = round((time.time() - start_time), 3)
print(f'\n{os.path.basename(__file__)} finished in {round(run_time)}s at {datetime.now().strftime("%H:%M:%S")}.\n')