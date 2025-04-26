"""UPLOAD SINGLE VIDEO FILE TO KALTURA"""

""""
TODO:
- force the reconvert to HD/720 - WEB (H264/2500) as transcoding always fails?
- add chapters
- add tags

"""

from datetime import datetime
import os
ts_time = f"{datetime.now().strftime('%H:%M:%S')}"
ts_file = f"{datetime.now().strftime('%y%m%d-%H%M')}"
print(f"\n---------- {ts_time} starting {os.path.basename(__file__)}")

# Start Chrono
import time
start_time = time.time()

# Credentials management in .env file
from dotenv import load_dotenv
load_dotenv()


# Kaltura Client
from KalturaClient import *
from KalturaClient.Plugins.Core import *
# Add this import for captions
from KalturaClient.Plugins.Caption import *
from KalturaClient.Plugins.Caption import KalturaLanguage, KalturaCaptionAsset, KalturaCaptionType


# FUNCTIONS





def upload_video_to_kaltura(file_path, title=None, description=None, caption_files=None, thumbnail_file_path=None, channel_id=None, USER_SECRET=None, ADMIN_SECRET=None, PARTNER_ID=None, timeout=300): 

    # Kaltura service configuration
    config = KalturaConfiguration(PARTNER_ID)
    config.serviceUrl = "https://www.kaltura.com/"
    config.requestTimeout = timeout  # Increase timeout to 5 minutes
    config.connectionTimeout = timeout  # Add connection timeout
    client = KalturaClient(config)
    
    # Load the Caption plugin with correct capitalization
    client.loadPlugin('Caption')
    
    expiry = 86400
    # privileges = "kms.user=nicolas.deville@kaltura.com"
    privileges = "disableentitlement"

    # Start session
    ks = client.session.start(ADMIN_SECRET, USER_SECRET, KalturaSessionType.ADMIN, PARTNER_ID, expiry, privileges)
    client.setKs(ks)
    
    # Create upload token
    upload_token = KalturaUploadToken()
    upload_token = client.uploadToken.add(upload_token)
    
    # File to upload
    file_data = open(file_path, "rb")
    
    # Upload the file
    resume = False # NOT WORKING when True
    final_chunk = True
    resume_at = -1
    result = client.uploadToken.upload(upload_token.id, file_data, resume, final_chunk, resume_at)

    media_entry = KalturaMediaEntry()
    
    # Media Type
    media_entry.mediaType = KalturaMediaType.VIDEO

    # Reference ID
    media_entry.referenceId = "auto-" + datetime.now().strftime('%Y%m%d%H%M%S')  # Add a reference ID 
    
    # # ✅ FLAVOURS
    # media_entry.flavorParamsIds = "25350252"

    # ✅ NAME
    if title:
        media_entry.name = title
    else:
        media_entry.name = f"test_video_{ts_file}"

    # ✅ DESCRIPTION
    if description:
        media_entry.description = description
    else:
        media_entry.description = "Video uploaded via Kaltura API"
    
    # Set creator and owner information (CRITICAL for media entry to be visible in KMS)
    media_entry.userId = "nicolas.deville@kaltura.com"
    media_entry.creatorId = "nicolas.deville@kaltura.com"
    
    # ADD THE MEDIA ENTRY
    media_entry = client.media.add(media_entry)
    
    # Attach uploaded file to the media entry
    resource = KalturaUploadedFileTokenResource()
    resource.token = upload_token.id
    media_entry = client.media.addContent(media_entry.id, resource)
    
    # ✅ THUMBNAIL
    if thumbnail_file_path:
        try:
            # Create an upload token for the thumbnail
            thumb_token = KalturaUploadToken()
            thumb_token = client.uploadToken.add(thumb_token)
            
            # Upload the thumbnail file
            thumb_file = open(thumbnail_file_path, 'rb')
            client.uploadToken.upload(thumb_token.id, thumb_file)
            thumb_file.close()
            
            # Create a new thumbAsset
            thumb_asset = KalturaThumbAsset()
            
            # Add the thumbnail to the media entry
            result_thumb = client.thumbAsset.add(media_entry.id, thumb_asset)
            
            # Create a resource from the upload token
            thumb_resource = KalturaUploadedFileTokenResource()
            thumb_resource.token = thumb_token.id
            
            # Set the content of the thumbnail
            client.thumbAsset.setContent(result_thumb.id, thumb_resource)
            
            # Set this thumbnail as the default for the media entry
            client.thumbAsset.setAsDefault(result_thumb.id)
            
            print(f"✅ Thumbnail successfully added & set as default")

        except Exception as e:
            print(f"❌ Error adding thumbnail: {e}")
    else:
        print("ℹ️ No thumbnail file provided, using default thumbnail.")

    # ✅ CAPTIONS
    if caption_files:
        # Set first language as default
        is_first_caption = True
        
        for language, caption_file_path in caption_files.items():
            try:
                # Create a caption asset
                caption_asset = KalturaCaptionAsset()
                caption_asset.language = language  # Use the exact string value from the enum list
                caption_asset.format = KalturaCaptionType.SRT
                caption_asset.label = language
                
                # Set first caption as default
                caption_asset.isDefault = KalturaNullableBoolean.TRUE_VALUE if is_first_caption else KalturaNullableBoolean.FALSE_VALUE
                is_first_caption = False
                
                # Add the caption asset to the entry
                caption_asset = client.caption.captionAsset.add(media_entry.id, caption_asset)
                
                # Create a KalturaUploadedFileTokenResource for the caption content
                caption_token = KalturaUploadToken()
                caption_token = client.uploadToken.add(caption_token)
                
                # Upload the caption file to the upload token
                caption_file = open(caption_file_path, 'rb')
                client.uploadToken.upload(caption_token.id, caption_file)
                caption_file.close()
                
                # Create a resource from the upload token
                caption_resource = KalturaUploadedFileTokenResource()
                caption_resource.token = caption_token.id
                
                # Set the content of the caption asset using the resource
                result_caption = client.caption.captionAsset.setContent(caption_asset.id, caption_resource)
                
                print(f"✅ {language} caption successfully added to media entry.")
                
            except Exception as e:
                print(f"❌ Error adding {language} caption: {e}")

    # ✅ CATEGORY (add to a Category so it appears in KMS Channel)
    category_entry = KalturaCategoryEntry()
    category_entry.entryId = media_entry.id
    category_entry.categoryId = channel_id
    
    try:
        client.categoryEntry.add(category_entry)
        print(f"✅ Successfully added entry to category ID: {channel_id}")
    except Exception as e:
        print(f"❌ Error adding to category: {e}")
    

    video_url = f"https://nicolas.mediaspace.kaltura.com/media/{media_entry.id}"
    print(f"\n🎉🎉🎉 Upload successful of {file_path} to {video_url}")

    file_data.close()

    return video_url



if __name__ == "__main__":


    KMS = "Pharma" # "Pharma" or "MY_KMS"

    # Credentials
    if KMS == "MY_KMS":
        USER_SECRET = os.getenv("user_secret")
        ADMIN_SECRET = os.getenv("admin_secret")
        PARTNER_ID = os.getenv("partner_id")
    elif KMS == "Pharma":
        USER_SECRET = os.getenv("pharma_user_secret")
        ADMIN_SECRET = os.getenv("pharma_admin_secret")
        PARTNER_ID = os.getenv("pharma_partner_id")



    # file_path = "/Users/nic/Downloads/temp/test_video.mp4"
    file_path = "/Users/nic/dl/yt/pharma-demo/cancer-symposium_A Time for Questions with Dr. Q.mp4"
    thumbnail_file_path = "/Users/nic/Downloads/temp/thumbnail2.jpg"
    caption_files = {
        # "English": "/Users/nic/Downloads/temp/en.vtt",
        # "German": "/Users/nic/Downloads/temp/de.vtt",
        "English": "/Users/nic/dl/yt/pharma-demo/cancer-symposium_A Time for Questions with Dr. Q.srt",
        "French": "/Users/nic/dl/yt/pharma-demo/cancer-symposium_A Time for Questions with Dr. Q_fr.srt",
    }
    video_title = f"Test Video {ts_file}"
    video_description = "This is a demonstration video uploaded with the Kaltura API, featuring multilingual captions and a custom thumbnail."

    channel_id = 374884222

    print(f"\n\nUploading {file_path} to Kaltura with custom title, description, {len(caption_files)} caption files, and a custom thumbnail...")
    
    upload_video_to_kaltura(file_path, title=video_title, description=video_description, caption_files=caption_files, thumbnail_file_path=thumbnail_file_path, channel_id=channel_id, USER_SECRET=USER_SECRET, ADMIN_SECRET=ADMIN_SECRET, PARTNER_ID=PARTNER_ID)

    # End Chrono
    run_time = time.time() - start_time
    minutes = int(run_time // 60)
    seconds = round(run_time % 60, 3)
    print(f'\n{os.path.basename(__file__)} finished in {minutes}m{seconds}s at {datetime.now().strftime("%H:%M:%S")}.\n')