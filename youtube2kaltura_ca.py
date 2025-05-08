"""
AUTOMATED YOUTUBE VIDEO DOWNLOAD & UPLOAD TO KALTURA KMS
1) download a Youtube URL (video/playlist/channel) to a folder (incl. videos & metadata JSON)
2) download captions OR generate captions for each video, in different languages
3) download official Youtube thumbnail for each video OR generate a .jpg for each video
4) generate title, description, tags, etc. using AI
4) upload videos to Kaltura with thumbnail, captions, title, description, tags.

TODO:
- extract title, description, thumbnail, and more from JSON
- TRANSLATIONS: run additional languages after the basic tasks (EN captiosn for all) by feeding entire transcript first then line by line + check what languages captions are missing
"""

import os
from dotenv import load_dotenv
load_dotenv()

""" CONFIGURATION """

test = False
verbose = False

project_name = "ca"
source_language = "FR"

download_youtube_videos = False # False to only do post-processing steps from saved files
youtube_channel_url = "https://www.youtube.com/@GroupeCreditAgricole"

max_videos_to_upload = 100
start_with = "longest_first" # "shortest_first" or "longest_first"
new_thumbnail = True # Generate new thumbnail randomly if True, otherwise extract from _json if available (else generate a new one anyway)

# PPTX
pptx_path = "/Users/nic/demo/pharma/pharma-demo-deck.pptx" # filename needs to end with "-deck.pptx"
background_image_path = "/Users/nic/demo/pharma/pharma-empty-background.jpg" # 1920x1080
theme_for_pptx_generation = "write about a random financial topic, in French"
num_presentations = 5

target_languages = [
    "EN",
    # "FR",
    # "DE",
    # "ES",
    # "CN",
    # "IT",
    # "PT",
    # "AR",
]

# KMS
KMS = "CA" # "Pharma" or "MY_KMS" or "CA"

CHANNELS = {
    "Accueil": [],

    "Métiers & Activités": [
        {
            "label": "Banque de détail & Caisses régionales",
            "description": "Vidéos sur les projets, innovations et initiatives locales des Caisses régionales et de la banque de détail, illustrant la proximité avec les clients et les territoires.",
            "image": "https://assets.mediaspace.kaltura.com/5.149.11.755/public/build0/img/addNew/playlist.svg"
        },
        {
            "label": "Banque d’investissement (CACIB)",
            "description": "Contenus relatifs aux activités de financement, marchés de capitaux, et projets structurants menés par Crédit Agricole Corporate & Investment Bank (CACIB).",
            "image": "https://assets.mediaspace.kaltura.com/5.149.11.755/public/build0/img/addNew/playlist.svg"
        },
        {
            "label": "Assurance & Épargne",
            "description": "Présentation des offres, évolutions réglementaires, et formations autour des activités de Crédit Agricole Assurances (CAA) et de Crédit Agricole Titres (CAT).",
            "image": "https://assets.mediaspace.kaltura.com/5.149.11.755/public/build0/img/addNew/playlist.svg"
        },
        {
            "label": "Paiements & Financements spécialisés",
            "description": "Initiatives autour des solutions de paiement, leasing, factoring, et mobilité (CAPS, CALF, CAPFM), incluant témoignages et démonstrations produit.",
            "image": "https://assets.mediaspace.kaltura.com/5.149.11.755/public/build0/img/addNew/playlist.svg"
        }
    ],

    "Paroles d’experts": [
        {
            "label": "Interviews & Regards croisés",
            "description": "Interviews d’experts métiers, dirigeants, ou partenaires sur les grands enjeux du Groupe : transformation digitale, finance durable, cybersécurité, etc.",
            "image": "https://assets.mediaspace.kaltura.com/5.149.11.755/public/build0/img/addNew/playlist.svg"
        },
        {
            "label": "Tables rondes & Débats",
            "description": "Captations de discussions multi-voix entre entités, filiales ou experts externes, pour faire émerger des points de vue croisés sur les grands défis bancaires.",
            "image": "https://assets.mediaspace.kaltura.com/5.149.11.755/public/build0/img/addNew/playlist.svg"
        },
        {
            "label": "Retours d’expérience terrain",
            "description": "Témoignages des collaborateurs sur la mise en œuvre de projets ou d’initiatives concrètes dans les agences, sièges ou centres de services.",
            "image": "https://assets.mediaspace.kaltura.com/5.149.11.755/public/build0/img/addNew/playlist.svg"
        },
        {
            "label": "Sessions Ask-Me-Anything",
            "description": "Séances interactives avec des experts internes, ouvertes aux collaborateurs pour poser des questions en direct sur des sujets métiers ou stratégiques.",
            "image": "https://assets.mediaspace.kaltura.com/5.149.11.755/public/build0/img/addNew/playlist.svg"
        }
    ],

    "Ressources & Formation": [
        {
            "label": "Formations & e-learning",
            "description": "Modules vidéo de formation sur les produits, réglementations (KYC, LCB-FT, RGPD), outils internes, et onboarding des nouveaux collaborateurs.",
            "image": "https://assets.mediaspace.kaltura.com/5.149.11.755/public/build0/img/addNew/playlist.svg"
        },
        {
            "label": "Référentiels métiers & bonnes pratiques",
            "description": "Contenus de référence à destination des équipes métiers : process, guides pratiques, cas d’usage, support à la montée en compétence continue.",
            "image": "https://assets.mediaspace.kaltura.com/5.149.11.755/public/build0/img/addNew/playlist.svg"
        }
    ],

    "Communication interne": [
        {
            "label": "Messages de la Direction",
            "description": "Prises de parole régulières de la direction générale (CA-GIP, CASA, LCL…) sur la stratégie, les priorités ou les résultats du Groupe.",
            "image": "https://assets.mediaspace.kaltura.com/5.149.11.755/public/build0/img/addNew/playlist.svg"
        },
        {
            "label": "Vie du Groupe",
            "description": "Vidéos événementielles, reportages internes, témoignages collaborateurs autour de la culture d’entreprise et de la vie au sein du Groupe CA.",
            "image": "https://assets.mediaspace.kaltura.com/5.149.11.755/public/build0/img/addNew/playlist.svg"
        },
        {
            "label": "RSE & Transition Énergétique",
            "description": "Contenus autour des engagements sociétaux, environnementaux et solidaires du Groupe : transition énergétique, inclusion, finance durable, etc.",
            "image": "https://assets.mediaspace.kaltura.com/5.149.11.755/public/build0/img/addNew/playlist.svg"
        }
    ],

    "En direct & Replays": [
        {
            "label": "Événements à venir",
            "description": "Programmation des lives à venir : townhalls, conférences métiers, lancements produits, webinaires et autres temps forts du Groupe CA.",
            "image": "https://assets.mediaspace.kaltura.com/5.149.11.755/public/build0/img/addNew/playlist.svg"
        },
        {
            "label": "Replays",
            "description": "Accès à la vidéothèque des événements passés, en replay : lives internes, formations, prises de parole stratégiques, etc.",
            "image": "https://assets.mediaspace.kaltura.com/5.149.11.755/public/build0/img/addNew/playlist.svg"
        },
    ]
}

# Credentials
# Set up Kaltura credentials based on the selected KMS
if KMS == "CA":
    USER_SECRET = os.getenv("ca_user_secret")
    ADMIN_SECRET = os.getenv("ca_admin_secret")
    PARTNER_ID = os.getenv("ca_partner_id")
else:
    print(f"❌ Error: Unknown KMS '{KMS}'. Please check your configuration.")
    exit()

OWNER = "nicolas.deville@kaltura.com"

""" END CONFIGURATION """


# Print configuration settings
print("\n\n===== CONFIGURATION =====")
print(f"Project name:\t\t{project_name}")
print(f"Test mode:\t\t{'Enabled' if test else 'Disabled'}")
print(f"Verbose mode:\t\t{'Enabled' if verbose else 'Disabled'}")
print(f"Max videos to upload:\t{max_videos_to_upload}")
print(f"Upload order:\t\t{start_with}")
print(f"Generate new thumbnails\t{'Yes' if new_thumbnail else 'No, use existing when available'}")
print(f"Target languages:\t{', '.join(target_languages)}")
print(f"KMS:\t\t\t{KMS}")
print(f"PPTX path:\t\t{pptx_path}")
print(f"PPTX theme:\t\t{theme_for_pptx_generation}")
print(f"# of presentations:\t{num_presentations}")

# Print channel structure
print("\nChannel structure:")
for category, channels in CHANNELS.items():
    print(f"  {category:30}{len(channels)} channels")

print("\nCredentials:")
print(f"Partner ID: {PARTNER_ID}")
print(f"Owner: {OWNER}")
print("User and Admin secrets: Configured")
print("===========================\n")

# IMPORTS


from datetime import datetime
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


# import utils

import glob
import csv
from pathlib import Path

import os
import json
import requests
from generate_thumbnails import generate_video_thumbnail

import generate_metadata

import ytdownload_videos
import kaltura_video_upload
from generate_captions import generate_en_srt
from generate_metadata import generate_title, generate_description, generate_tags
from generate_thumbnails import generate_video_thumbnail
from generate_translation import generate_translated_srt
from manage_kaltura_channels import get_kaltura_channels, get_channels_parent_id, create_kaltura_channel, generate_channel_description
from kaltura_video_upload import upload_video_to_kaltura
from manage_kaltura_videos import get_all_videos
# from generate_powerpoint_data import generate_pptx
from kaltura_ppt_upload import upload_ppt_to_kaltura

from generate_thumbnails import generate_video_thumbnail

# GLOBAL VARIABLES

count = 0
count_video_uploaded = 0


# CREATE MISSING CHANNELS IN KMS

from kaltura_list_categories import list_kaltura_categories
from kaltura_create_channels import create_multiple_categories

print("\n\n⚙️  Checking for missing channels in KMS...")

# Get existing categories/channels from Kaltura
existing_categories = list_kaltura_categories(show="kms_only", USER_SECRET=USER_SECRET, ADMIN_SECRET=ADMIN_SECRET, PARTNER_ID=PARTNER_ID)

# Create a dictionary of existing category names for easy lookup
existing_category_names = {category.name: category.id for category in existing_categories}

# Prepare list of channels to create
channels_to_create = []

# Check each channel in the CHANNELS dictionary
for main_channel, sub_channels in CHANNELS.items():
    # Check if main channel exists
    if main_channel not in existing_category_names:
        print(f"  ➕ Main channel '{main_channel}' needs to be created")
        channels_to_create.append({
            "name": main_channel,
            "description": generate_channel_description(main_channel) if callable(generate_channel_description) else ""
        })
    
    # Check sub-channels
    for sub_channel in sub_channels:
        if sub_channel["label"] not in existing_category_names:
            print(f"  ➕ Sub-channel '{sub_channel['label']}' needs to be created")
            channels_to_create.append({
                "name": sub_channel["label"],
                "description": sub_channel.get("description", "")
            })

# Create missing channels if any
if channels_to_create:
    print(f"\n⚙️  Creating {len(channels_to_create)} missing channels...")
    created, failed = create_multiple_categories(channels_to_create)
    print(f"  ✅ Successfully created {len(created)} channels")
    if failed:
        print(f"  ❌ Failed to create {len(failed)} channels: {', '.join(failed)}")
else:
    print("  ✅ All channels already exist in KMS")

# Get updated list of channels after creation
all_channels = {category.name: category.id for category in list_kaltura_categories(show="kms_only", USER_SECRET=USER_SECRET, ADMIN_SECRET=ADMIN_SECRET, PARTNER_ID=PARTNER_ID)}
print(f"\n⚙️  Total channels available in KMS: {len(all_channels)}")




# DOWNLOAD YOUTUBE VIDEOS

if download_youtube_videos:
    print(f"\n\n⚙️  Downloading videos from YouTube channel {youtube_channel_url}")
    youtube_download_path_with_files = ytdownload_videos.process_youtube_channel(youtube_channel_url)
    print(f"\n\n{youtube_download_path_with_files=}")
else:
    youtube_download_path_with_files = f"/Users/nic/dl/yt/{project_name}"

if test:
    youtube_download_path_with_files = f"/Users/nic/dl/yt/test"

print(f"\n\n⚙️  Download job finished. Processing files in {youtube_download_path_with_files}\n\n")



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

    count_total_mp4_files_to_process_for_en_captions = len(video_files)

    print(f"\nℹ️  Total MP4 files found: {count_total_mp4_files_to_process_for_en_captions}")

    # Sort video files by duration
    if start_with == "shortest_first":
        video_files.sort(key=lambda x: get_video_duration(x))
    elif start_with == "longest_first":
        video_files.sort(key=lambda x: get_video_duration(x), reverse=True)
    
    if not video_files:
        print(f"No MP4 files found in {download_folder}")
        return results
    
    print(f"ℹ️  generate_captions > found {count_total_mp4_files_to_process_for_en_captions} MP4 files to process")
    
    for mp4_file in video_files:
        count += 1
        video_name = os.path.basename(mp4_file)
        base_path = str(mp4_file).rsplit(".", 1)[0]

        duration = get_video_duration(mp4_file)
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        
        video_results = []
        print(f"\n\n{datetime.now().strftime('%H:%M:%S')} =============== ℹ️  {count}/{count_total_mp4_files_to_process_for_en_captions} > processing captions for {mp4_file} ({minutes}m {seconds}s)'\n")
        
        # Check if SRT already exists
        srt_path = f"{base_path}.srt"
        
        if os.path.exists(srt_path):
            if verbose:
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

    # Skip English if it's in the target languages since we already have English captions
    translation_languages = [lang for lang in target_languages if lang.upper() != "EN"]
    
    # Find all SRT files in the folder that don't have a language tag (like _fr.srt or _de.srt)
    srt_files = []
    all_srt_files = glob.glob(os.path.join(folder_path, "*.srt"))
    for srt_file in all_srt_files:
        # Check if the file doesn't end with a language tag (e.g., _fr.srt, _de.srt)
        if not any(srt_file.lower().endswith(f"_{lang.lower()}.srt") for lang in ["en", "fr", "es", "de", "it", "pt", "ru", "zh", "ja", "ko", "ar", "hi", "nl", "sv", "fi", "da", "no", "pl", "tr", "cs", "hu", "el", "he", "th", "vi", "id", "ms", "ro", "uk", "bg", "hr", "sr", "sk", "sl", "et", "lv", "lt", "fa", "ur"]):
            srt_files.append(srt_file)
    count_total_mp4_files_to_process_for_translated_captions = len(srt_files)
    count = 0
    results = {}
    
    if not srt_files:
        print(f"No SRT files found in {folder_path}")
        return results
    
    print(f"\n\n\n========= generate_translated_captions > found {count_total_mp4_files_to_process_for_translated_captions} SRT files to process")
    

    
    if not translation_languages:
        print("No languages to translate to (English captions already exist)")
        return results
    
    for srt_file in srt_files:
        count += 1
        srt_name = os.path.basename(srt_file)
        base_path = str(srt_file).rsplit(".", 1)[0]
        
        video_results = []
        print(f"\n\n{datetime.now().strftime('%H:%M:%S')} =============== ℹ️  {count}/{count_total_mp4_files_to_process_for_translated_captions} > processing translations for\t{srt_file}\n")
        
        for target_lang in translation_languages:
            # Check if translated SRT already exists
            translated_srt_path = f"{base_path}_{target_lang.lower()}.srt"
            
            if os.path.exists(translated_srt_path):
                if verbose:
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
    if verbose:
        print("\nℹ️  Skipping translations - No additional languages specified")




# TITLE
"""each .mp4 file needs to have a _title.txt file with the title of the video inside"""

# IMPLEMENT LOGIC FOR MAX title LENGTH WITH A LOOP THAT REDOES IT

def generate_titles(folder_path, source_language="EN"):
    
    mp4_files = glob.glob(os.path.join(folder_path, "*.mp4"))
    
    if not mp4_files:
        print(f"No MP4 files found in {folder_path}")
        return {}
    
    total_files_to_process_for_title_generation = len(mp4_files)
    
    print(f"\n==== GENERATING TITLES FOR {total_files_to_process_for_title_generation} MP4 files in {folder_path}\n")
    
    results = {}

    count_file_for_title_generation = 0
    
    for mp4_file in mp4_files:
        count_file_for_title_generation += 1
        video_name = os.path.basename(mp4_file)
        title_file_path = mp4_file.rsplit(".", 1)[0] + "_title.txt"
        
        # Skip if title file already exists
        if os.path.exists(title_file_path):
            if verbose:
                print(f"{count_file_for_title_generation}/{total_files_to_process_for_title_generation} ⏩ Skipping title generation - Title file already exists: {title_file_path}")
            results[mp4_file] = title_file_path
            continue
        
        try:
            print(f"\nTITLE #{count_file_for_title_generation}/{total_files_to_process_for_title_generation}")
            title_file_path = generate_metadata.generate_title(mp4_file, source_language=source_language)
            results[mp4_file] = title_file_path
        except Exception as e:
            print(f"  ❌ Error generating title for {mp4_file}: {str(e)}")
    
    return results

# Generate titles for all MP4 files in the download folder
generate_titles(youtube_download_path_with_files, source_language)



# DESCRIPTION
"""each .mp4 file needs to have a _description.txt file with the description of the video inside"""

def generate_descriptions(folder_path, source_language="EN"):

    import os
    import generate_metadata
    
    mp4_files = glob.glob(os.path.join(folder_path, "*.mp4"))
    
    # Filter out mp4 files that already have a description file
    files_to_process = []
    for mp4_file in mp4_files:
        description_file_path = mp4_file.rsplit(".", 1)[0] + "_description.txt"
        if not os.path.exists(description_file_path):
            files_to_process.append(mp4_file)
    
    if not files_to_process:
        print(f"No MP4 files without description files found in {folder_path}")
        return {}
    
    total_files_to_process_for_description_generation = len(files_to_process)
    mp4_files = files_to_process  # Replace the original list with filtered list
    
    print(f"\n\n\n==== GENERATING DESCRIPTIONS FOR {total_files_to_process_for_description_generation} MP4 files in {folder_path}\n")

    
    results = {}

    count_file_for_description_generation = 0
    
    for mp4_file in mp4_files:
        count_file_for_description_generation += 1
        video_name = os.path.basename(mp4_file)
        description_file_path = mp4_file.rsplit(".", 1)[0] + "_description.txt"
        
        # Skip if description file already exists
        if os.path.exists(description_file_path):
            if verbose:
                print(f"{count_file_for_description_generation}/{total_files_to_process_for_description_generation} ⏩ Skipping title generation - Title file already exists: {description_file_path}")
            results[mp4_file] = description_file_path
            continue
        
        print(f"\nDESCRIPTION #{count_file_for_description_generation}/{total_files_to_process_for_description_generation}\n")
        # try:
        description_file_path = generate_metadata.generate_description(mp4_file, based_on="filename", source_language=source_language)
            # print(f"  ✅ Description generated successfully")
        results[mp4_file] = description_file_path
        # except Exception as e:
            # print(f"  ❌ Error generating description for {video_name}: {str(e)}")
    
    return results

# Generate descriptions for all MP4 files in the download folder
generate_descriptions(youtube_download_path_with_files, source_language)



# TAGS
"""each .mp4 file needs to have a _tags.txt file with the tags of the video inside"""

def generate_tags(folder_path):

    import os
    import generate_metadata
    # Get all MP4 files
    mp4_files = glob.glob(os.path.join(folder_path, "*.mp4"))
    
    if not mp4_files:
        print(f"No MP4 files found in {folder_path}")
        return {}
    
    # Filter to only include MP4 files without corresponding tags files
    files_to_process = []
    for mp4_file in mp4_files:
        tags_file_path = mp4_file.rsplit(".", 1)[0] + "_tags.txt"
        if not os.path.exists(tags_file_path):
            files_to_process.append(mp4_file)
    
    if not files_to_process:
        print(f"No MP4 files without tags files found in {folder_path}")
        return {}
    
    total_files_to_process_for_tags_generation = len(files_to_process)
    mp4_files = files_to_process  # Replace the original list with filtered list
    
    print(f"\n==== GENERATING TAGS FOR {total_files_to_process_for_tags_generation} MP4 files in {folder_path}")
    
    results = {}

    count_file_for_tags_generation = 0
    
    for mp4_file in mp4_files:
        video_name = os.path.basename(mp4_file)
        tags_file_path = mp4_file.rsplit(".", 1)[0] + "_tags.txt"
        count_file_for_tags_generation += 1
        
        # Skip if tags file already exists
        if os.path.exists(tags_file_path):
            if verbose:
                print(f"{count_file_for_tags_generation}/{total_files_to_process_for_tags_generation} ⏩ Skipping title generation - Title file already exists: {tags_file_path}")

            results[mp4_file] = tags_file_path  
            continue
        
        print(f"\nTAGS #{count_file_for_tags_generation}/{total_files_to_process_for_tags_generation}")
        # try:
        tags = generate_metadata.generate_tags(mp4_file, based_on="filename", source_language=source_language)
        #     print(f"  ✅ Tags generated successfully")
        results[mp4_file] = tags_file_path  
        # except Exception as e:
        #     print(f"  ❌ Error generating tags for {video_name}: {str(e)}")
    
    return results

# Generate tags for all MP4 files in the download folder
generate_tags(youtube_download_path_with_files)




# THUMBNAIL
"""
Download official Youtube thumbnail for each .mp4 file, using the JSON file.
OR
Generate a .jpg for each .mp4 file (logic TBC).
"""

if new_thumbnail:
    def generate_thumbnails(folder_path):
        
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
                if verbose:
                    print(f"  ⏩ Skipping thumbnail generation - Thumbnail file already exists: {os.path.basename(thumbnail_file_path)}")
                results[mp4_file] = thumbnail_file_path
                continue
            
            print(f"  🔄 Generating thumbnail for: {video_name}")
            try:
                generate_video_thumbnail(mp4_file)
                # print(f"  ✅ Thumbnail generated successfully")
                results[mp4_file] = thumbnail_file_path
            except Exception as e:
                print(f"  ❌ Error generating thumbnail for {video_name}: {str(e)}")
        
        return results

    # Generate thumbnails for all MP4 files in the download folder
    generate_thumbnails(youtube_download_path_with_files)

else:
    def extract_thumbnails_from_json(folder_path):
        
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
                if verbose:
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
                    generate_video_thumbnail(mp4_file)
                    print(f"  ✅ Thumbnail generated successfully")
                    results[mp4_file] = thumbnail_file_path
                except Exception as e:
                    print(f"  ❌ Error generating thumbnail for {video_name}: {str(e)}")
        
        return results

    # Extract thumbnails from JSON metadata for all MP4 files in the download folder
    extract_thumbnails_from_json(youtube_download_path_with_files)



# CHANNELS IN KALTURA

# Extract categories and channels from CHANNELS dictionary
# Categories
category_names = []
for category_name in CHANNELS.keys():
    category_names.append(category_name)
# Channels
target_channel_names = ['PDF', 'Powerpoint']
for channel_name, subchannels in CHANNELS.items():
    if isinstance(subchannels, list) and len(subchannels) > 0:
        for subchannel in subchannels:
            if isinstance(subchannel, dict) and "label" in subchannel:
                target_channel_names.append(subchannel["label"])
print()
print(category_names)
print()
print(target_channel_names)

# Check existing channels in Kaltura
all_channels = get_kaltura_channels(PARTNER_ID=PARTNER_ID, ADMIN_SECRET=ADMIN_SECRET)
print(f"\nℹ️  {len(all_channels)} existing Kaltura channels: {all_channels}\n")

# Identify channels that are not in Kaltura
channels_not_in_kaltura = [channel for channel in target_channel_names if channel not in all_channels]
print(f"\nℹ️  {len(channels_not_in_kaltura)} channels not in Kaltura: {channels_not_in_kaltura}\n")

parent_id = get_channels_parent_id(PARTNER_ID=PARTNER_ID, ADMIN_SECRET=ADMIN_SECRET)

# Create missing channels in Kaltura
for channel_name in channels_not_in_kaltura:
    create_kaltura_channel(channel_name, parent_id=parent_id, description=generate_channel_description(channel_name), tags=None, PARTNER_ID=PARTNER_ID, ADMIN_SECRET=ADMIN_SECRET, USER_SECRET=USER_SECRET, OWNER=OWNER)


# Check existing channels in Kaltura again
# Filter channels to only include those in target_channel_names
filtered_channels = {channel_name: channel_id for channel_name, channel_id in get_kaltura_channels(PARTNER_ID=PARTNER_ID, ADMIN_SECRET=ADMIN_SECRET).items() 
                    if channel_name in target_channel_names}
channels = filtered_channels
print(f"\nℹ️  {len(channels)} target Kaltura channels:\n")
for channel_name, channel_id in channels.items():
    print(f"{channel_id}\t{channel_name}")








# CHANNEL ID

def assign_channels_to_videos(channels):

    source_folder = youtube_download_path_with_files
    
    print(f"\n📊 Assigning channels to videos in {source_folder}")
    
    # Get all MP4 files in the source folder
    mp4_files = glob.glob(os.path.join(source_folder, "**/*.mp4"), recursive=True)
    
    if not mp4_files:
        print(f"❌ No MP4 files found in {source_folder}")
        return
    
    # Create a list to store the assignments
    assignments = []
    
    # Loop through each video
    for mp4_file in mp4_files:
        video_name = os.path.basename(mp4_file)
        
        # For demonstration purposes, assign a channel based on video name
        # In a real implementation, you might want to use content analysis or metadata
        assigned_channel = None
        assigned_channel_id = None
        
        # First check if channel name appears in the video filename (case insensitive)
        for channel_name, channel_id in channels.items():
            # Skip channels with "PDF" or "Powerpoint" in the name
            if "PDF" in channel_name or "Powerpoint" in channel_name:
                continue
                
            if channel_name.lower() in video_name.lower():
                assigned_channel = channel_name
                assigned_channel_id = channel_id
                break
        
        # If no match found in filename, check the transcript file if it exists
        if not assigned_channel:
            # Get transcript file path (same filename but with .txt extension)
            transcript_path = os.path.splitext(mp4_file)[0] + '.txt'
            
            if os.path.exists(transcript_path):
                try:
                    with open(transcript_path, 'r', encoding='utf-8') as f:
                        transcript_text = f.read().lower()
                        
                    # Check if any channel name appears in the transcript
                    for channel_name, channel_id in channels.items():
                        # Skip channels with "PDF" or "Powerpoint" in the name
                        if "PDF" in channel_name or "Powerpoint" in channel_name:
                            continue
                            
                        if channel_name.lower() in transcript_text:
                            assigned_channel = channel_name
                            assigned_channel_id = channel_id
                            break
                except Exception as e:
                    print(f"  ⚠️ Error reading transcript file: {e}")
        
        # If still no match found, cycle through channels in order
        if not assigned_channel and channels:
            # Get list of channel names, excluding those with "PDF" or "Powerpoint"
            channel_names = [name for name in channels.keys() 
                            if "PDF" not in name and "Powerpoint" not in name]
            
            if channel_names:  # Make sure we have valid channels after filtering
                # Determine index based on the position of the video in the list
                # This will distribute videos across channels
                index = mp4_files.index(mp4_file) % len(channel_names)
                assigned_channel = channel_names[index]
                assigned_channel_id = channels[assigned_channel]
            else:
                print(f"  ⚠️ No suitable channels found for {video_name} after filtering")
        
        # Add to assignments list
        assignments.append({
            'video_path': mp4_file,
            'video_name': video_name,
            'channel_name': assigned_channel,
            'channel_id': assigned_channel_id
        })
        
        print(f"  📌 Assigned '{video_name}' to channel '{assigned_channel}' (ID: {assigned_channel_id})")
    
    # Write assignments to CSV file
    csv_path = os.path.join(source_folder, "_channel_assignments.csv")
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['video_path', 'video_name', 'channel_name', 'channel_id']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for assignment in assignments:
            writer.writerow(assignment)
    
    print(f"✅ Channel assignments saved to: {csv_path}")
    return assignments

# Execute the channel assignment function
video_channel_assignments = assign_channels_to_videos(channels)



# UPLOAD VIDEOS TO KALTURA


videos_already_in_kaltura = videos = get_all_videos(PARTNER_ID, ADMIN_SECRET)

def upload_videos_to_kaltura(folder_path):
    global count_video_uploaded, max_videos_to_upload, videos_already_in_kaltura

    # Find all MP4 files in the folder
    all_mp4_files = glob.glob(os.path.join(folder_path, "*.mp4"))
    
    if not all_mp4_files:
        print(f"No MP4 files found in {folder_path}")
        return
    
    # Filter MP4 files to only include those with all required associated files
    mp4_files = []
    for mp4_file in all_mp4_files:
        base_name = mp4_file.rsplit(".", 1)[0]
        
        # Check if all required files exist
        has_title = os.path.exists(f"{base_name}_title.txt")
        has_srt = os.path.exists(f"{base_name}.srt")
        has_description = os.path.exists(f"{base_name}_description.txt")
        has_tags = os.path.exists(f"{base_name}_tags.txt")
        has_thumbnail = os.path.exists(f"{base_name}.jpg")
        
        # Check if video title already exists in Kaltura
        title_exists_in_kaltura = False
        if has_title:
            with open(f"{base_name}_title.txt", 'r', encoding='utf-8') as f:
                video_title = f.read().strip()
                if video_title in videos_already_in_kaltura:
                    title_exists_in_kaltura = True
                    print(f"ℹ️   Skipping {mp4_file} - already exists in Kaltura")
        
        if has_title and has_srt and has_description and has_tags and has_thumbnail and not title_exists_in_kaltura:
            mp4_files.append(mp4_file)
        else:
            if title_exists_in_kaltura:
                continue
            missing = []
            if not has_title: missing.append("title")
            if not has_srt: missing.append("captions")
            if not has_description: missing.append("description")
            if not has_tags: missing.append("tags")
            if not has_thumbnail: missing.append("thumbnail")
            print(f"⚠️ Skipping {mp4_file} - missing: {', '.join(missing)}")

    
    if not mp4_files:
        print(f"No MP4 files with all required associated files found in {folder_path}")
        return
    
    print(f"\nℹ️  Uploading {len(mp4_files)} videos to Kaltura from {folder_path} (filtered from {len(all_mp4_files)} total videos)")
    
    # Sort videos by duration if needed
    if start_with == "shortest_first":
        # Sort by file size as a proxy for duration (smaller files first)
        mp4_files.sort(key=lambda x: os.path.getsize(x))
    elif start_with == "longest_first":
        # Sort by file size as a proxy for duration (larger files first)
        mp4_files.sort(key=lambda x: os.path.getsize(x), reverse=True)
    
    for mp4_file in mp4_files:
        video_name = os.path.basename(mp4_file)
        base_name = mp4_file.rsplit(".", 1)[0]
        
        print(f"\n\n\n📤 Processing upload  #{count_video_uploaded + 1} of {len(mp4_files)}: {mp4_file}")
        
        # Check for title
        title = None
        title_file_path = f"{base_name}_title.txt"
        if os.path.exists(title_file_path):
            with open(title_file_path, 'r', encoding='utf-8') as f:
                title = f.read().strip()
            print(f"  ✅ Found title: {title}")
        else:
            print(f"  ⚠️ No title file found, will use default")
        
        # Check for description
        description = None
        description_file_path = f"{base_name}_description.txt"
        if os.path.exists(description_file_path):
            with open(description_file_path, 'r', encoding='utf-8') as f:
                description = f.read().strip()
            print(f"  ✅ Found description")
        else:
            print(f"  ⚠️ No description file found, will use default")
        # Check for tags
        tags = []
        tags_file_path = f"{base_name}_tags.txt"
        if os.path.exists(tags_file_path):
            with open(tags_file_path, 'r', encoding='utf-8') as f:
                tags_content = f.read().strip()
                # Split by commas and strip whitespace from each tag
                tags = [tag.strip() for tag in tags_content.split(',') if tag.strip()]
            print(f"  ✅ Found {len(tags)} tags")
        else:
            print(f"  ⚠️ No tags file found, will use default")
        
        # Check for thumbnail
        thumbnail_file_path = f"{base_name}.jpg"
        if os.path.exists(thumbnail_file_path):
            print(f"  ✅ Found thumbnail")
        else:
            thumbnail_file_path = None
            print(f"  ⚠️ No thumbnail file found")
        
        
        # Check for caption files
        caption_files = {}
        # Check for base .srt file (usually English)
        base_srt_path = f"{base_name}.srt"
        if os.path.exists(base_srt_path):
            caption_files["English"] = base_srt_path
        # Check for language-specific .srt files
        for lang in target_languages:
            caption_file_path = f"{base_name}_{lang.lower()}.srt"
            if os.path.exists(caption_file_path):
                # Map language codes to full language names
                language_mapping = {
                    "EN": "English",
                    "DE": "German",
                    "FR": "French",
                    "ES": "Spanish",
                    "IT": "Italian",
                    "PT": "Portuguese",
                    "RU": "Russian",
                    "ZH": "Chinese",
                    "JA": "Japanese",
                    "KO": "Korean"
                }
                full_language_name = language_mapping.get(lang, lang)
                caption_files[full_language_name] = caption_file_path
        
        if caption_files:
            print(f"  ✅ Found {len(caption_files)} caption files: {', '.join(caption_files.keys())} ({', '.join(caption_files.values())})")
        else:
            print(f"  ⚠️ No caption files found")
        

        # Get channel ID from video_channel_assignments
        channel_id = None
        for assignment in video_channel_assignments:
            if assignment['video_name'] == video_name:
                channel_id = assignment['channel_id']
                break


        # Upload the video with all available metadata and retry logic
        if count_video_uploaded < max_videos_to_upload:
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    print(f"\n🔄 Uploading video {count_video_uploaded + 1} of {len(mp4_files)} to Kaltura (attempt {retry_count + 1}/{max_retries}):\nPath:\t{mp4_file}\nTitle:\t{title}\nTags:\t{tags}\nThumbnail:\t{thumbnail_file_path}\nChannel ID:\t{channel_id}\n")
                    
                    # Increase timeout values
                    upload_video_to_kaltura(
                        file_path=mp4_file,
                        title=title,
                        description=description,
                        caption_files=caption_files,
                        thumbnail_file_path=thumbnail_file_path,
                        channel_id=channel_id,
                        USER_SECRET=USER_SECRET,
                        ADMIN_SECRET=ADMIN_SECRET,
                        PARTNER_ID=PARTNER_ID,
                        timeout=300  # Increase timeout to 5 minutes
                    )
                    # print(f"  ✅ Video uploaded successfully")
                    count_video_uploaded += 1
                    break  # Exit retry loop on success
                    
                except Exception as e:
                    retry_count += 1
                    if retry_count < max_retries:
                        wait_time = retry_count * 30  # Exponential backoff: 30s, 60s, 90s
                        print(f"  ⚠️ Upload failed (attempt {retry_count}/{max_retries}): {str(e)}")
                        print(f"  🕐 Waiting {wait_time} seconds before retrying...")
                        time.sleep(wait_time)
                    else:
                        print(f"  ❌ Failed to upload video after {max_retries} attempts: {str(e)}")
                        # Optionally log failed uploads for later retry
                        with open("failed_uploads.txt", "a") as f:
                            f.write(f"{mp4_file}\n")
        else:
            print(f"  ⚠️ Skipping video {video_name} - max videos to upload reached")
            break

upload_videos_to_kaltura(youtube_download_path_with_files)



# POWERRPOINT

# Identify Channel to upload to (with "PPT" in the name)
print(f"\nℹ️  {len(all_channels)} channels found in Kaltura:\n")
for channel_name, channel_id in all_channels.items():
    print(f"{channel_id}\t{channel_name}")

    try:
        target_channel_names = [name for name in channels.keys() if "PPT" in name or "Powerpoint" in name]
        channel_id_for_ppt_upload = channels[target_channel_names[0]]
        print(f"\nℹ️  Uploading to channel ID: {channel_id_for_ppt_upload}")
    except Exception as e:
        print(f"\n❌ Error: No channel found with 'PPT' in the name to upload {num_presentations} PPTX files to. Create one first.")
        print(f"   {e}")
        exit()


from generate_thumbnails import generate_ppt_thumbnail

for x in range(num_presentations):

    target_output_path = f"{pptx_path.rsplit('.', 1)[0]}_{x+1:02d}.jpg"

    ppt_thumbnail_path, title_text, subtitle_text = generate_ppt_thumbnail(background_image_path, theme_for_pptx_generation, output_path=target_output_path)

    print(f"\n{ppt_thumbnail_path=}\n{title_text=}\n{subtitle_text=}\n")

    # UPLOAD PPTX TO KALTURA
    upload_ppt_to_kaltura(pptx_path, channel_id=channel_id_for_ppt_upload, demo_mode=True, ppt_thumbnail_path=ppt_thumbnail_path, title_text=title_text, subtitle_text=subtitle_text, MY_USER_SECRET=USER_SECRET, MY_ADMIN_SECRET=ADMIN_SECRET, MY_PARTNER_ID=PARTNER_ID)



# End Chrono
run_time = time.time() - start_time
minutes = int(run_time // 60)
seconds = int(round(run_time % 60, 0))
print(f"\n\n--------------------------------")
print(f'{os.path.basename(__file__)} finished in {minutes}m{seconds}s at {datetime.now().strftime("%H:%M:%S")}.\n')