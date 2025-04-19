import os
from datetime import datetime
import time

# Credentials management in .env file
from dotenv import load_dotenv
load_dotenv()

# Start Chrono
start_time = time.time()
ts_time = f"{datetime.now().strftime('%H:%M:%S')}"
ts_file = f"{datetime.now().strftime('%y%m%d-%H%M')}"
print(f"\n---------- {ts_time} starting {os.path.basename(__file__)}")

# Ensure all videos have all flavours

from KalturaClient import *
from KalturaClient.Plugins.Core import *

KMS = "MY_KMS"

# Credentials
# Set up Kaltura credentials based on the selected KMS
if KMS == "MY_KMS":
    USER_SECRET = os.getenv("user_secret")
    ADMIN_SECRET = os.getenv("admin_secret")
    PARTNER_ID = os.getenv("partner_id")
elif KMS == "Pharma":
    USER_SECRET = os.getenv("pharma_user_secret")
    ADMIN_SECRET = os.getenv("pharma_admin_secret")
    PARTNER_ID = os.getenv("pharma_partner_id")
elif KMS == "ABB":
    USER_SECRET = os.getenv("abb_user_secret")
    ADMIN_SECRET = os.getenv("abb_admin_secret")
    PARTNER_ID = os.getenv("abb_partner_id")
else:
    print(f"❌ Error: Unknown KMS '{KMS}'. Please check your configuration.")
    exit()

# PHARMA
# USER_SECRET = os.getenv("user_secret")
# ADMIN_SECRET = os.getenv("admin_secret")
# PARTNER_ID = os.getenv("partner_id")



def check_and_force_flavors(client, entry_id):
    # Get flavor assets for the video
    flavor_assets = client.flavorAsset.getByEntryId(entry_id)
    # print(f"\nℹ️  Found {len(flavor_assets)} flavor assets for entry {entry_id}:")
    # for flavor in flavor_assets:
        # status_text = "READY" if flavor.status == KalturaFlavorAssetStatus.READY else "NOT READY"
        # print(f"  - ID: {flavor.id}, Format: {flavor.fileExt}, Resolution: {flavor.width}x{flavor.height}, Bitrate: {flavor.bitrate}kbps, Status: {status_text}")
    # print()
    
    # Define required flavors
    required_flavors = {
        # 301991: {"name": "Mobile (3GP)", "found": False},
        # 487111: {"name": "WebM", "found": False},
        487061: {"name": "SD/Small", "found": False},
        487071: {"name": "SD/Large", "found": False},
        487081: {"name": "HD/720", "found": False},
        487091: {"name": "HD/1080", "found": False},
    }
    
    # Just mark which flavors exist (regardless of status)
    for flavor in flavor_assets:
        flavor_params_id = flavor.flavorParamsId
        if flavor_params_id in required_flavors:
            required_flavors[flavor_params_id]["found"] = True
            print(f"\nℹ️  {required_flavors[flavor_params_id]['name']} exists - skipping")
    
    # Only create completely missing flavors
    missing_flavors = False
    for flavor_params_id, flavor_info in required_flavors.items():
        if not flavor_info["found"]:
            missing_flavors = True
            # print(f"\nℹ️  No {flavor_info['name']} flavor found for entry {entry_id}")
            try:
                result = client.flavorAsset.convert(entry_id, flavor_params_id)
                print(f"\n✅ {flavor_info['name']}: triggered conversion")
            except Exception as e:
                print(f"\n❌ Error triggering conversion for {flavor_info['name']}: {e}")
    
    if not missing_flavors:
        print(f"\n✅ All required flavors exist")

def main():
    # Initialize Kaltura client
    config = KalturaConfiguration(PARTNER_ID)
    config.serviceUrl = "https://www.kaltura.com/"
    config.requestTimeout = 120
    client = KalturaClient(config)
    
    # Start session
    expiry = 86400
    privileges = "disableentitlement"
    ks = client.session.start(
        ADMIN_SECRET,
        USER_SECRET,
        KalturaSessionType.ADMIN,
        PARTNER_ID,
        expiry,
        privileges
    )
    client.setKs(ks)
    
    # Set maximum number of videos to check
    max_videos_to_check = 1000  # Adjust this value as needed

    print(f"\n\n\n========== Starting to check {max_videos_to_check} last videos...")
    
    # Get list of videos
    filter = KalturaMediaEntryFilter()
    filter.orderBy = KalturaMediaEntryOrderBy.CREATED_AT_DESC
    # Only get video entries
    filter.mediaTypeEqual = 1  # 1 = VIDEO in Kaltura
    pager = KalturaFilterPager()
    pager.pageSize = max_videos_to_check
    
    result = client.media.list(filter, pager)
    print(f"\nℹ️  Found {result.totalCount} videos in total, checking up to {max_videos_to_check}")
    
    if result.totalCount == 0:
        print("No videos found")
        return
        
    for count_video, video in enumerate(result.objects):
        print(f"\n\n\n========== Processing video #{count_video+1}/{result.totalCount} >>> {video.id} - {video.name}")
        try:
            check_and_force_flavors(client, video.id)
            # print(f"\n✅ Checked flavors for entry {video.id}")
        except Exception as e:
            print(f"\n❌ Error processing entry {video.id}: {e}")
            continue

if __name__ == "__main__":
    main()

    print(f"\n\n")

    # End Chrono
    run_time = time.time() - start_time
    minutes = int(run_time // 60)
    seconds = round(run_time % 60, 3)
    print(f'\n{"-" * 50}\n{os.path.basename(__file__)} finished in {minutes}m{seconds}s at {datetime.now().strftime("%H:%M:%S")}.\n')
