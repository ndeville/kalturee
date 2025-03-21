# # Process yt-dlp JSON metadata files

# import json
# import sys
# import os


# def extract_subtitle_urls(json_file):
#     """
#     Extract subtitle URLs from a yt-dlp JSON metadata file
#     Returns a dictionary mapping language codes to VTT subtitle URLs
#     """
#     # Load the JSON file
#     with open(json_file, 'r', encoding='utf-8') as f:
#         data = json.load(f)
    
#     # Initialize the subtitle dictionary
#     subtitle_dict = {}
    
#     # Check if the 'requested_subtitles' field exists
#     if 'requested_subtitles' in data:
#         for lang, subtitle_info in data['requested_subtitles'].items():
#             if 'url' in subtitle_info:
#                 subtitle_dict[lang] = subtitle_info['url']
    
#     # Alternative approach: check 'subtitles' field which might contain all available subtitles
#     elif 'subtitles' in data:
#         for lang, subtitle_formats in data['subtitles'].items():
#             # Find VTT format if available
#             for fmt in subtitle_formats:
#                 if fmt.get('ext') == 'vtt':
#                     subtitle_dict[lang] = fmt.get('url')
#                     break
    
#     return subtitle_dict


# json_file = "/Users/nic/Python/kalturee/yt_test.json"
    
    
# # Extract subtitle URLs
# subtitle_dict = extract_subtitle_urls(json_file)

# # Print the resulting dictionary
# print(json.dumps(subtitle_dict, indent=2, ensure_ascii=False))




import json
import requests
import os

# Load the JSON file
json_path = "/Users/nic/Python/kalturee/yt_test.json" 
with open(json_path, "r", encoding="utf-8") as file:
    data = json.load(file)

# Create download directory if it doesn't exist
download_dir = "/Users/nic/Downloads/temp"
os.makedirs(download_dir, exist_ok=True)

# Extract VTT URLs with associated language
vtt_urls = []
if "automatic_captions" in data:
    for lang, subtitle_list in data["automatic_captions"].items():
        for subtitle in subtitle_list:
            if subtitle.get("ext") == "vtt":
                vtt_urls.append({"language": lang, "url": subtitle["url"]})

# Download and save VTT files
for entry in vtt_urls:
    # Create a filename using the language code
    filename = f"{entry['language']}.vtt"
    filepath = os.path.join(download_dir, filename)
    
    # Download the VTT file
    response = requests.get(entry['url'])
    if response.status_code == 200:
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {filename}")
    else:
        print(f"Failed to download {entry['language']} subtitle: {response.status_code}")

print(f"Downloaded VTT files saved to: {download_dir}")