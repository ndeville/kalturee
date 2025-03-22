import my_utils

my_utils.connect_vpn()

import json
import requests
import os
import random
import time

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
    url = entry['url']
    print(f"\nDownloading {url}")
    response = requests.get(url)
    if response.status_code == 200:
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"✅ Downloaded: {filename}")
    else:
        print(f"❌ Failed to download {entry['language']} subtitle: {response.status_code}")
    
    # Add random delay between downloads (2-5 seconds)
    if entry != vtt_urls[-1]:  # Skip delay after the last download
        delay = random.uniform(2, 5)
        print(f"Waiting {delay:.2f} seconds before next download...")
        time.sleep(delay)

print(f"Downloaded VTT files saved to: {download_dir}")

my_utils.disconnect_vpn()