"""UPLOAD SINGLE VIDEO FILE TO KALTURA"""

from datetime import datetime
import os
ts_time = f"{datetime.now().strftime('%H:%M:%S')}"
ts_file = f"{datetime.now().strftime('%y%m%d-%H%M')}"
print(f"\n---------- {ts_time} starting {os.path.basename(__file__)}")

# Start Chrono
import time
start_time = time.time()

# Credentials
from dotenv import load_dotenv
load_dotenv()
MY_USER_SECRET = os.getenv("user_secret")
MY_ADMIN_SECRET = os.getenv("admin_secret")
MY_PARTNER_ID = os.getenv("partner_id")

# Kaltura Client
from KalturaClient import *
from KalturaClient.Plugins.Core import *

# Upload to Kaltura
def upload_video_to_kaltura(file_path):
    global MY_USER_SECRET, MY_ADMIN_SECRET, MY_PARTNER_ID

    # Kaltura service configuration
    config = KalturaConfiguration()
    config.serviceUrl = "https://www.kaltura.com/"
    client = KalturaClient(config)
    
    expiry = 86400
    privileges = "kms.user=nicolas.deville@kaltura.com"

    # Start session
    ks = client.session.start(MY_ADMIN_SECRET, MY_USER_SECRET, KalturaSessionType.ADMIN, MY_PARTNER_ID, expiry, privileges)
    client.setKs(ks)
    
    # Create upload token
    upload_token = KalturaUploadToken()
    upload_token = client.uploadToken.add(upload_token)
    
    # File to upload
    file_data = open(file_path, "rb")
    
    # Upload the file
    resume = False
    final_chunk = True
    resume_at = -1
    result = client.uploadToken.upload(upload_token.id, file_data, resume, final_chunk, resume_at)

    media_entry = KalturaMediaEntry()

    # Media Type
    media_entry.mediaType = KalturaMediaType.VIDEO

    # Reference ID
    media_entry.referenceId = "auto-" + datetime.now().strftime('%Y%m%d%H%M%S')  # Add a reference ID 
    
    # CATEGORY (add to a Category so it appears in KMS Channel)
    # Use the Category ID to be found in https://kmc.kaltura.com/index.php/kmcng/content/categories/list
    # media_entry.categories = "test_250322-0047" # NOT WORKING
    # media_entry.categoriesIds = "374334092"  # NOT WORKING. ID for test_250322-0047 channel. KalturaClient.exceptions.KalturaException: Category id "374334092" not found (CATEGORY_NOT_FOUND)
    # media_entry.categoriesIds = 374334092  # NOT WORKING. ID for test_250322-0047 channel. KalturaClient.exceptions.KalturaException: Category id "374334092" not found (CATEGORY_NOT_FOUND)
    # media_entry.categories = "MediaSpace/site/channels/Test" # NOT WORKING
    # media_entry.categories = "MediaSpace>site>channels>Test" # NOT WORKING
    # media_entry.categories = "Test" # NOT WORKING
    # media_entry.categories = "374334092" # NOT WORKING
    # media_entry.categories = 374334092 # NOT WORKING
    # media_entry.categories = "MediaSpace/site/channels/test_250322-0047" # NOT WORKING
    # NONE OF THE ABOVE WORK. TRYING WITH OTHER APPROACH BELOW AFTER ADDING MEDIA ENTRY.
    # TODO: Figure out how to add to Category for it to appear in KMS Channel / See below for other approach.

    media_entry.flavorParamsIds = "25350252"  # ✅
    media_entry.name = f"test_video_{ts_file}" # ✅
    media_entry.description = f"I'm adding this description to the video." # ✅
    
    # Thumbnail / Use ID 1_oq7trpiz for tests
    # We'll add the thumbnail after the media entry is created
    # The thumbnailUrl approach doesn't work, so we'll use thumbAsset.add instead
    
    # Add the media entry
    media_entry = client.media.add(media_entry)
    
    # Attach uploaded file to the media entry
    resource = KalturaUploadedFileTokenResource()
    resource.token = upload_token.id
    media_entry = client.media.addContent(media_entry.id, resource)
    


    # THUMBNAIL
    try:
        # Create a KalturaUrlResource for the thumbnail
        thumb_resource = KalturaUrlResource()
        thumb_resource.url = "https://www.kaltura.com/p/{}/sp/{}/thumbnail/entry_id/1_oq7trpiz/width/640/height/360".format(MY_PARTNER_ID, MY_PARTNER_ID)
        
        # Create a new thumbAsset
        thumb_asset = KalturaThumbAsset()
        
        # Add the thumbnail to the media entry
        result_thumb = client.thumbAsset.add(media_entry.id, thumb_asset)
        
        # Set the content of the thumbnail
        client.thumbAsset.setContent(result_thumb.id, thumb_resource)
        
        print(f"✅ Successfully added thumbnail to media entry")

        # TODO: thumbnail gets uploaded but not set as default to media entry.

    except Exception as e:
        print(f"❌ Error adding thumbnail: {e}")



    # CATEGORY (add to a Category so it appears in KMS Channel)
    category_entry = KalturaCategoryEntry()
    category_entry.entryId = media_entry.id
    category_entry.categoryId = 374334092
    
    try:
        client.categoryEntry.add(category_entry)
        print(f"Successfully added entry to category ID: 374334092")
    except Exception as e:
        print(f"Error adding to category: {e}")
    
    print(f"\n✅ Upload successful of test_video_{ts_file}: https://nicolas.mediaspace.kaltura.com/media/{media_entry.id}")

    # 250322-1303 ❌ THIS fails still to add to Category for it to appear in KMS Channel.


    file_data.close()

file_path = "/Users/nic/Downloads/temp/test_video.mp4"
print(f"\n\nUploading {file_path} to Kaltura...")
upload_video_to_kaltura(file_path)

# End Chrono
run_time = round((time.time() - start_time), 3)
print(f'\n{os.path.basename(__file__)} finished in {round(run_time)}s at {datetime.now().strftime("%H:%M:%S")}.\n')