"""
AUTOMATED YOUTUBE VIDEO DOWNLOAD & UPLOAD TO KALTURA KMS
1) download a Youtube URL (video/playlist/channel) to a folder (incl. videos & metadata JSON)
2) download captions OR generate captions for each video, in different languages
3) download official Youtube thumbnail for each video OR generate a .jpg for each video
4) generate title, description, tags, etc. using AI
4) upload videos to Kaltura with thumbnail, captions, title, description, tags.

TODO:
- use the CLI captions approach (1/3 time needed)
- extract title, description, thumbnail, and more from JSON
- TRANSLATIONS: run additional languages after the basic tasks (EN captiosn for all) + check what languages captions are missing
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
import cv2

# Clean up warnings printouts
import logging
logging.getLogger("speechbrain.utils.quirks").setLevel(logging.WARNING)
import warnings
warnings.filterwarnings("ignore", message="Model was trained with")
warnings.filterwarnings("ignore", message="Lightning automatically upgraded")


# import my_utils

import ytdownload_videos
import kaltura_video_upload
from pathlib import Path
import os
import glob
from generate_captions import generate_en_srt
from generate_metadata import generate_title, generate_description, generate_tags
from generate_thumbnail import extract_best_thumbnail
from generate_translation import generate_translated_srt
from kaltura_video_upload import upload_video_to_kaltura
from assign_kaltura_channel import assign_kaltura_channel_id


""" CONFIGURATION """

test = False
project_name = "pharma-demo"
start_with = "longest_first" # "shortest_first" or "longest_first"
new_thumbnail = True # Generate new thumbnail randomly if True, otherwise extract from _json if available (else generate a new one anyway)
target_languages = [
    "EN",
    "FR",
    "DE",
    # "ES",
    # "CN",
    # "IT",
    # "PT",
    # "AR",
]


# GLOBAL VARIABLES

count = 0

# DOWNLOAD YOUTUBE VIDEOS

download_youtube_videos = False # False to only do post-processing steps from saved files
youtube_url = "https://www.youtube.com/playlist?list=PL-Q2v2azALUPW9j2mfKc3posK7tIcwqHe"


if download_youtube_videos:
    youtube_download_path_with_files = ytdownload_videos.process_youtube_url_to_download(youtube_url)
    print(f"\n\n{youtube_download_path_with_files=}")
else:
    youtube_download_path_with_files = f"/Users/nic/dl/yt/{project_name}"

if test:
    youtube_download_path_with_files = f"/Users/nic/dl/yt/test"

print(f"\n\n⚙️  Processing files in {youtube_download_path_with_files}")

# JSON



# EN CAPTIONS

def get_video_duration(video_path):
    """Get the duration of a video file in seconds."""
    try:
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            return 0
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count/fps
        cap.release()
        return duration
    except Exception as e:
        print(f"Error getting duration for {video_path}: {e}")
        return 0

# def generate_captions(download_folder, source_lang="EN", target_languages=None, model_name="large-v2"):
#     """Generate captions for all MP4 files in the download folder in multiple languages."""
#     if target_languages is None:
#         target_languages = ["EN"]
    
#     results = {}
    
#     print("\nScanning for MP4 files...")
#     # Get all video files recursively from all subfolders
#     video_files = []
#     video_dir = Path(download_folder)
#     for file in video_dir.rglob("*.mp4"):
#         # Check if an equivalent .srt file already exists
#         srt_file = file.with_suffix('.srt')
#         if not srt_file.exists():
#             video_files.append(file)
#             # print(f"Found: {file.relative_to(video_dir)}")

#     count_total = len(video_files)

#     print(f"\nℹ️  Total MP4 files found: {count_total}")

#     # Sort video files by duration
#     if start_with == "shortest_first":
#         video_files.sort(key=lambda x: get_video_duration(x))
#     elif start_with == "longest_first":
#         video_files.sort(key=lambda x: get_video_duration(x), reverse=True)
    
#     if not video_files:
#         print(f"No MP4 files found in {download_folder}")
#         return results
    
#     print(f"ℹ️  generate_captions > found {count_total} MP4 files to process")
    
#     for mp4_file in video_files:
#         video_name = os.path.basename(mp4_file)
#         base_path = str(mp4_file).rsplit(".", 1)[0]

#         duration = get_video_duration(mp4_file)
#         minutes = int(duration // 60)
#         seconds = int(duration % 60)
        
#         video_results = []
#         print(f"\n\n{datetime.now().strftime('%H:%M:%S')} =============== ℹ️  processing captions for {video_name} ({minutes}m {seconds}s) with model '{model_name}'\n")
        
#         for output_lang in target_languages:
#             # Check if SRT already exists
#             srt_path = f"{base_path}.srt" if output_lang.upper() == "EN" else f"{base_path}_{output_lang.lower()}.srt"
            
#             if os.path.exists(srt_path):
#                 print(f"  ⏩ Skipping {output_lang} captions - SRT file already exists: {os.path.basename(srt_path)}")
#                 video_results.append(srt_path)
#                 continue
            
#             print(f"  🔄 Generating {output_lang} captions for: {video_name}\n")
#             caption_start_time = time.time()
#             try:
#                 srt_path = generate_srt(str(mp4_file), source_lang=source_lang, output_lang=output_lang, model_name=model_name)
#                 video_results.append(srt_path)
#             except Exception as e:
#                 print(f"  ❌ Error generating {output_lang} captions for {video_name}: {str(e)}")

#             print(f"\n⏱️  Total processing time for {output_lang} caption: {round((time.time() - caption_start_time)/60, 1)}min\n")
        
#         results[str(mp4_file)] = video_results
    
#     return results


# generate_captions(youtube_download_path_with_files, source_lang="EN", target_languages=target_languages, model_name="large-v3")


def generate_en_captions(download_folder, source_lang="EN"):
    """Generate EN captions for all MP4 files in the download folder."""
    global count

    print(f"\nℹ️  generate_en_captions > hardcoded as source-language EN. Update logic to accomodate other source languages.")
    
    results = {}
    
    print("\nScanning for MP4 files...")
    # Get all video files recursively from all subfolders
    video_files = []
    video_dir = Path(download_folder)
    for file in video_dir.rglob("*.mp4"):
        # Check if an equivalent .srt file already exists
        srt_file = file.with_suffix('.srt')
        if not srt_file.exists():
            video_files.append(file)
            # print(f"Found: {file.relative_to(video_dir)}")

    count_total = len(video_files)

    print(f"\nℹ️  Total MP4 files found: {count_total}")

    # Sort video files by duration
    if start_with == "shortest_first":
        video_files.sort(key=lambda x: get_video_duration(x))
    elif start_with == "longest_first":
        video_files.sort(key=lambda x: get_video_duration(x), reverse=True)
    
    if not video_files:
        print(f"No MP4 files found in {download_folder}")
        return results
    
    print(f"ℹ️  generate_captions > found {count_total} MP4 files to process")
    
    for mp4_file in video_files:
        count += 1
        video_name = os.path.basename(mp4_file)
        base_path = str(mp4_file).rsplit(".", 1)[0]

        duration = get_video_duration(mp4_file)
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        
        video_results = []
        print(f"\n\n{datetime.now().strftime('%H:%M:%S')} =============== ℹ️  {count}/{count_total} > processing captions for {mp4_file} ({minutes}m {seconds}s)'\n")
        
        # Check if SRT already exists
        srt_path = f"{base_path}.srt"
        
        if os.path.exists(srt_path):
            print(f"  ⏩ Skipping EN captions - SRT file already exists: {os.path.basename(srt_path)}")
            video_results.append(srt_path)
        else:
            # print(f"  🔄 Generating EN captions for: {video_name}\n")
            caption_start_time = time.time()
            try:
                srt_path = generate_en_srt(str(mp4_file))
                video_results.append(srt_path)
            except Exception as e:
                print(f"  ❌ Error generating EN captions for {video_name}: {str(e)}")

            caption_time = time.time() - caption_start_time
            caption_time_minutes = round(caption_time/60, 1)
            conversion_ratio = round(duration / caption_time, 2)
            print(f"\n⏱️  Processed EN caption of {minutes}m {seconds}s video in {caption_time_minutes}min ({conversion_ratio}x)\n")
        
        results[str(mp4_file)] = video_results
    
    return results


generate_en_captions(youtube_download_path_with_files)



# CAPTION TRANSLATIONS

def generate_translated_captions(folder_path, target_languages=["EN"]):
    """
    Process all .srt files in the folder and translate them to the target languages
    using the generate_translated_srt function.
    """
    import os
    import glob
    from generate_translation import generate_translated_srt
    from datetime import datetime
    import time
    
    # Find all SRT files in the folder
    srt_files = glob.glob(os.path.join(folder_path, "*.srt"))
    count_total = len(srt_files)
    count = 0
    results = {}
    
    if not srt_files:
        print(f"No SRT files found in {folder_path}")
        return results
    
    print(f"ℹ️  generate_translated_captions > found {count_total} SRT files to process")
    
    # Skip English if it's in the target languages since we already have English captions
    translation_languages = [lang for lang in target_languages if lang.upper() != "EN"]
    
    if not translation_languages:
        print("No languages to translate to (English captions already exist)")
        return results
    
    for srt_file in srt_files:
        count += 1
        srt_name = os.path.basename(srt_file)
        base_path = str(srt_file).rsplit(".", 1)[0]
        
        video_results = []
        print(f"\n\n{datetime.now().strftime('%H:%M:%S')} =============== ℹ️  {count}/{count_total} > processing translations for {srt_name}\n")
        
        for target_lang in translation_languages:
            # Check if translated SRT already exists
            translated_srt_path = f"{base_path}_{target_lang.lower()}.srt"
            
            if os.path.exists(translated_srt_path):
                print(f"  ⏩ Skipping {target_lang} translation - File already exists: {os.path.basename(translated_srt_path)}")
                video_results.append(translated_srt_path)
            else:
                print(f"  🔄 Generating {target_lang} translation for: {srt_name}")
                translation_start_time = time.time()
                try:
                    translated_path = generate_translated_srt(str(srt_file), target_lang)
                    if translated_path:
                        video_results.append(translated_path)
                        translation_time = time.time() - translation_start_time
                        translation_time_minutes = round(translation_time/60, 1)
                        print(f"  ✅ {target_lang} translation completed in {translation_time_minutes} minutes")
                except Exception as e:
                    print(f"  ❌ Error generating {target_lang} translation for {srt_name}: {str(e)}")
        
        results[str(srt_file)] = video_results
    
    return results

# Generate translations for all SRT files in the download folder
if target_languages and len(target_languages) > 1:  # Only run if we have languages other than EN
    generate_translated_captions(youtube_download_path_with_files, target_languages)
else:
    print("\nℹ️  Skipping translations - No additional languages specified")


# TITLE
"""each .mp4 file needs to have a _title.txt file with the title of the video inside"""

# IMPLEMENT LOGIC FOR MAX title LENGTH WITH A LOOP THAT REDOES IT

def generate_titles(folder_path):

    import os
    import generate_metadata
    
    mp4_files = glob.glob(os.path.join(folder_path, "*.mp4"))
    
    if not mp4_files:
        print(f"No MP4 files found in {folder_path}")
        return {}
    
    print(f"\nℹ️  Generating titles for MP4 files in {folder_path}")
    
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

# TEST ALL THE LOGIC BELOW


if new_thumbnail:
    def generate_thumbnails(folder_path):

        import os
        from generate_thumbnail import extract_best_thumbnail
        
        mp4_files = glob.glob(os.path.join(folder_path, "*.mp4"))
        
        if not mp4_files:
            print(f"No MP4 files found in {folder_path}")
            return {}
        
        print(f"\nGenerating thumbnails for MP4 files in {folder_path}")
        
        results = {}
        
        for mp4_file in mp4_files:
            video_name = os.path.basename(mp4_file)
            thumbnail_file_path = mp4_file.rsplit(".", 1)[0] + ".jpg"
            
            # Skip if thumbnail file already exists
            if os.path.exists(thumbnail_file_path):
                print(f"  ⏩ Skipping thumbnail generation - Thumbnail file already exists: {os.path.basename(thumbnail_file_path)}")
                results[mp4_file] = thumbnail_file_path
                continue
            
            print(f"  🔄 Generating thumbnail for: {video_name}")
            try:
                extract_best_thumbnail(mp4_file)
                print(f"  ✅ Thumbnail generated successfully")
                results[mp4_file] = thumbnail_file_path
            except Exception as e:
                print(f"  ❌ Error generating thumbnail for {video_name}: {str(e)}")
        
        return results

    # Generate thumbnails for all MP4 files in the download folder
    generate_thumbnails(youtube_download_path_with_files)

else:
    def extract_thumbnails_from_json(folder_path):

        import os
        import json
        import requests
        from generate_thumbnail import extract_best_thumbnail
        
        mp4_files = glob.glob(os.path.join(folder_path, "*.mp4"))
        
        if not mp4_files:
            print(f"No MP4 files found in {folder_path}")
            return {}
        
        print(f"\nExtracting thumbnails from JSON metadata for MP4 files in {folder_path}")
        
        results = {}
        
        for mp4_file in mp4_files:
            video_name = os.path.basename(mp4_file)
            thumbnail_file_path = mp4_file.rsplit(".", 1)[0] + ".jpg"
            json_file_path = mp4_file + ".info.json"
            
            # Skip if thumbnail file already exists
            if os.path.exists(thumbnail_file_path):
                print(f"  ⏩ Skipping thumbnail extraction - Thumbnail file already exists: {os.path.basename(thumbnail_file_path)}")
                results[mp4_file] = thumbnail_file_path
                continue
            
            # Try to extract thumbnail URL from JSON file
            thumbnail_extracted = False
            if os.path.exists(json_file_path):
                try:
                    with open(json_file_path, 'r', encoding='utf-8') as f:
                        json_data = json.load(f)
                    
                    if "thumbnail" in json_data and json_data["thumbnail"]:
                        thumbnail_url = json_data["thumbnail"]
                        print(f"  🔄 Downloading thumbnail from URL: {thumbnail_url}")
                        
                        response = requests.get(thumbnail_url, stream=True)
                        if response.status_code == 200:
                            with open(thumbnail_file_path, 'wb') as f:
                                for chunk in response.iter_content(1024):
                                    f.write(chunk)
                            print(f"  ✅ Thumbnail downloaded successfully")
                            thumbnail_extracted = True
                            results[mp4_file] = thumbnail_file_path
                        else:
                            print(f"  ⚠️ Failed to download thumbnail: HTTP status {response.status_code}")
                    else:
                        print(f"  ⚠️ No thumbnail URL found in JSON metadata for {video_name}")
                except Exception as e:
                    print(f"  ⚠️ Error extracting thumbnail from JSON for {video_name}: {str(e)}")
            else:
                print(f"  ⚠️ No JSON metadata file found for {video_name}")
            
            # If thumbnail extraction failed, generate one
            if not thumbnail_extracted:
                print(f"  🔄 Falling back to generating thumbnail for: {video_name}")
                try:
                    extract_best_thumbnail(mp4_file)
                    print(f"  ✅ Thumbnail generated successfully")
                    results[mp4_file] = thumbnail_file_path
                except Exception as e:
                    print(f"  ❌ Error generating thumbnail for {video_name}: {str(e)}")
        
        return results

    # Extract thumbnails from JSON metadata for all MP4 files in the download folder
    extract_thumbnails_from_json(youtube_download_path_with_files)


# CHANNEL ID

# TODO write logic to 
# create a new category/channel in kaltura if missing 
# fetch the channel ids from kaltura
# assign each video to the correct category/channel based on content.


# assign_kaltura_channel_id(video_id, channel_id)


# UPLOAD VIDEOS TO KALTURA

# TODO TO TEST
# def upload_videos_to_kaltura(folder_path, channel_id=374334092):
#     """
#     Upload all videos in the folder to Kaltura with their metadata
    
#     Args:
#         folder_path (str): Path to the folder containing MP4 files and metadata
#         channel_id (int): Kaltura category ID (channel)
#     """
#     import os
#     import glob
    
#     mp4_files = glob.glob(os.path.join(folder_path, "*.mp4"))
    
#     if not mp4_files:
#         print(f"No MP4 files found in {folder_path}")
#         return
    
#     print(f"\nUploading videos to Kaltura from {folder_path}")
    
#     # Sort videos by duration if needed
#     if start_with == "shortest_first":
#         # Sort by file size as a proxy for duration (smaller files first)
#         mp4_files.sort(key=lambda x: os.path.getsize(x))
#     elif start_with == "longest_first":
#         # Sort by file size as a proxy for duration (larger files first)
#         mp4_files.sort(key=lambda x: os.path.getsize(x), reverse=True)
    
#     for mp4_file in mp4_files:
#         video_name = os.path.basename(mp4_file)
#         base_name = mp4_file.rsplit(".", 1)[0]
        
#         print(f"\n📤 Processing {video_name} for upload")
        
#         # Check for title
#         title = None
#         title_file_path = f"{base_name}_title.txt"
#         if os.path.exists(title_file_path):
#             with open(title_file_path, 'r', encoding='utf-8') as f:
#                 title = f.read().strip()
#             print(f"  ✅ Found title: {title}")
#         else:
#             print(f"  ⚠️ No title file found, will use default")
        
#         # Check for description
#         description = None
#         description_file_path = f"{base_name}_description.txt"
#         if os.path.exists(description_file_path):
#             with open(description_file_path, 'r', encoding='utf-8') as f:
#                 description = f.read().strip()
#             print(f"  ✅ Found description")
#         else:
#             print(f"  ⚠️ No description file found, will use default")
        
#         # Check for thumbnail
#         thumbnail_file_path = f"{base_name}.jpg"
#         if os.path.exists(thumbnail_file_path):
#             print(f"  ✅ Found thumbnail")
#         else:
#             thumbnail_file_path = None
#             print(f"  ⚠️ No thumbnail file found")
        
#         # Check for caption files
#         caption_files = {}
#         for lang in target_languages:
#             caption_file_path = f"{base_name}_{lang}.vtt"
#             if os.path.exists(caption_file_path):
#                 caption_files[lang] = caption_file_path
        
#         if caption_files:
#             print(f"  ✅ Found {len(caption_files)} caption files: {', '.join(caption_files.keys())}")
#         else:
#             print(f"  ⚠️ No caption files found")
        
#         # Upload the video with all available metadata
#         try:
#             print(f"  🔄 Uploading video to Kaltura...")
#             upload_video_to_kaltura(
#                 file_path=mp4_file,
#                 title=title,
#                 description=description,
#                 caption_files=caption_files,
#                 thumbnail_file_path=thumbnail_file_path,
#                 channel_id=channel_id
#             )
#             print(f"  ✅ Video uploaded successfully")
#         except Exception as e:
#             print(f"  ❌ Error uploading video: {str(e)}")

# # Upload all videos with metadata to Kaltura
# upload_videos_to_kaltura(youtube_download_path_with_files)



# End Chrono
run_time = round((time.time() - start_time), 3)
print(f'\n{os.path.basename(__file__)} finished in {round(run_time)}s at {datetime.now().strftime("%H:%M:%S")}.\n')