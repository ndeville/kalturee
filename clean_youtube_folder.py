#!/usr/bin/env python3
"""
Script to clean YouTube download folder by moving MP4 files and their JSON metadata
to a queue folder if they don't have any associated files with other extensions.
"""

import os
import shutil
import glob
from pathlib import Path
from datetime import datetime

# Start Chrono
import time
start_time = time.time()

test = True
count = 0

# Configuration
source_folder = "/Users/nic/dl/yt/pharma-demo"
destination_folder = "/Users/nic/dl/yt/pharma-demo-queue"


# # MOVE TO QUEUE
# print(f"\n---------- {datetime.now().strftime('%H:%M:%S')} starting {os.path.basename(__file__)}")
# print(f"Cleaning folder: {source_folder}")
# print(f"Moving eligible files to: {destination_folder}")

# # Get all MP4 files in the source folder
# mp4_files = glob.glob(os.path.join(source_folder, "*.mp4"))
# print(f"Found {len(mp4_files)} MP4 files in source folder")

# files_moved = 0

# for mp4_file in mp4_files:
#     base_name = os.path.splitext(mp4_file)[0]
#     mp4_filename = os.path.basename(mp4_file)
    
#     # Check for the associated JSON file
#     json_file = f"{base_name}.info.json"
#     json_exists = os.path.exists(json_file)
    
#     # Check specifically for .srt file
#     srt_file = f"{base_name}.srt"
#     srt_exists = os.path.exists(srt_file)
    
#     # If there's no .srt file, move the MP4 and JSON
#     if not srt_exists:
#         print(f"Moving {mp4_filename} (no .srt file found)")
#         count += 1
        
#         # Move MP4 file
#         if not test:
#             shutil.move(mp4_file, os.path.join(destination_folder, os.path.basename(mp4_file)))
        
#         # Move JSON file if it exists
#         if json_exists:
#             if not test:
#                 shutil.move(json_file, os.path.join(destination_folder, os.path.basename(json_file)))
#             print(f"  ✅ Moved MP4 and JSON files")
#         else:
#             print(f"  ✅ Moved MP4 file (no JSON found)")
            
#         files_moved += 1
#     # else:
#     #     print(f"Skipping {mp4_filename} - Has associated .srt file")

# print(f"\nCount: {count}\n")

# print(f"\nSummary: Moved {files_moved} out of {len(mp4_files)} MP4 files to queue folder")

# # End Chrono
# run_time = round((time.time() - start_time), 3)
# print(f'\n{os.path.basename(__file__)} finished in {run_time}s at {datetime.now().strftime("%H:%M:%S")}.\n')




## RESET TXT FILES
# # Delete all existing .txt files in the source folder
# txt_files = glob.glob(os.path.join(source_folder, "*.txt"))
# print(f"\nFound {len(txt_files)} existing .txt files in source folder")

# for txt_file in txt_files:
#     try:
#         if not test:
#             os.remove(txt_file)
#             print(f"🗑️ Deleted: {os.path.basename(txt_file)}")
#         else:
#             print(f"  🗑️ Would have deleted: {os.path.basename(txt_file)}")
#     except Exception as e:
#         print(f"❌ Error deleting {os.path.basename(txt_file)}: {str(e)}")


# # GENERATE NEW TXT FILES FROM SRT FILES
# # Find all English .srt files (those without language codes)
# srt_files = glob.glob(os.path.join(source_folder, "*.srt"))
# english_srt_files = [f for f in srt_files if not any(f.endswith(f"_{lang.lower()}.srt") for lang in ["de", "fr", "es", "cn", "it", "pt", "ar"])]

# print(f"\nFound {len(english_srt_files)} English .srt files to process")

# txt_files_created = 0

# # Create new .txt files from English .srt files
# for srt_path in english_srt_files:
#     base_name = os.path.splitext(srt_path)[0]
#     txt_path = f"{base_name}.txt"
    
#     try:
#         with open(srt_path, "r") as srt_file, open(txt_path, "w") as txt_file:
#             current_segment_text = []
#             for line in srt_file:
#                 line = line.strip()
#                 # Skip empty lines, timestamp lines, and segment number lines
#                 if not line:
#                     # Empty line indicates end of a segment
#                     if current_segment_text:
#                         # Join all text lines from the segment into a single line
#                         txt_file.write(" ".join(current_segment_text) + "\n")
#                         current_segment_text = []
#                 elif '-->' in line or line[0].isdigit() and line.isdigit():
#                     # Skip timestamp lines and segment numbers
#                     continue
#                 else:
#                     # Add text line to current segment
#                     current_segment_text.append(line)
            
#             # Handle the last segment if file doesn't end with empty line
#             if current_segment_text:
#                 txt_file.write(" ".join(current_segment_text) + "\n")
        
#         # Remove trailing newline if the last line is empty
#         with open(txt_path, "r") as f:
#             content = f.read()
#         if content.endswith("\n"):
#             with open(txt_path, "w") as f:
#                 f.write(content.rstrip("\n"))
        
#         print(f"✅ Generated clean TXT file: {os.path.basename(txt_path)}")
#         txt_files_created += 1
#     except Exception as e:
#         print(f"❌ Error creating TXT file for {os.path.basename(srt_path)}: {str(e)}")

# print(f"\nSummary: Created {txt_files_created} new .txt files from English .srt files")



# # Delete all _title.txt files in the source folder
# title_files = glob.glob(os.path.join(source_folder, "*_title.txt"))
# title_files_count = len(title_files)

# if title_files_count > 0:
#     print(f"\nFound {title_files_count} _title.txt files to delete")
#     deleted_count = 0
    
#     for title_file in title_files:
#         try:
#             os.remove(title_file)
#             print(f"✅ Deleted: {title_file}")
#             deleted_count += 1
#         except Exception as e:
#             print(f"❌ Error deleting {os.path.basename(title_file)}: {str(e)}")
    
#     print(f"\nSummary: Deleted {deleted_count} out of {title_files_count} _title.txt files")
# else:
#     print("\nNo _title.txt files found to delete")






# Delete all _title.txt files in the source folder, especially those with quotes in content
title_files = glob.glob(os.path.join(source_folder, "*_title.txt"))
title_files_count = len(title_files)

if title_files_count > 0:
    print(f"\nFound {title_files_count} _title.txt files to check")
    deleted_count = 0
    
    for title_file in title_files:
        try:
            # Check if file content contains quotes
            with open(title_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if '"' in content or "'" in content:
                os.remove(title_file)
                print(f"✅ Deleted (contains quotes): {title_file}")
                deleted_count += 1
        except Exception as e:
            print(f"❌ Error processing {os.path.basename(title_file)}: {str(e)}")
    
    print(f"\nSummary: Deleted {deleted_count} out of {title_files_count} _title.txt files containing quotes")
else:
    print("\nNo _title.txt files found to check")




# Delete all _description.txt files in the source folder if content doesn't end with a period
description_files = glob.glob(os.path.join(source_folder, "*_description.txt"))
description_files_count = len(description_files)

if description_files_count > 0:
    print(f"\nFound {description_files_count} _description.txt files to check")
    deleted_count = 0
    
    for description_file in description_files:
        try:
            # Check if file content ends with a period
            with open(description_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            if not content.endswith('.'):
                os.remove(description_file)
                print(f"✅ Deleted (doesn't end with period): {description_file}")
                deleted_count += 1
        except Exception as e:
            print(f"❌ Error processing {os.path.basename(description_file)}: {str(e)}")
    
    print(f"\nSummary: Deleted {deleted_count} out of {description_files_count} _description.txt files without ending period")
else:
    print("\nNo _description.txt files found to check")







# Delete all _tags.txt files in the source folder if content is longer than 1 line
tags_files = glob.glob(os.path.join(source_folder, "*_tags.txt"))
tags_files_count = len(tags_files)

if tags_files_count > 0:
    print(f"\nFound {tags_files_count} _tags.txt files to check")
    deleted_count = 0
    
    for tags_file in tags_files:
        try:
            # Check if file content is longer than 1 line
            with open(tags_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                line_count = len(content.splitlines())
            
            if line_count > 1:
                os.remove(tags_file)
                print(f"✅ Deleted (more than 1 line): {tags_file}")
                deleted_count += 1
        except Exception as e:
            print(f"❌ Error processing {os.path.basename(tags_file)}: {str(e)}")
    
    print(f"\nSummary: Deleted {deleted_count} out of {tags_files_count} _tags.txt files with more than 1 line")
else:
    print("\nNo _tags.txt files found to check")