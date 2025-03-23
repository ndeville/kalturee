"""UPLOAD SINGLE POWERPOINT FILE TO KALTURA"""

"""
TODO:
- generate thumbnail from first slide
- generate title from first slide
- generate description from overall content
"""

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
# Import Document plugin
from KalturaClient.Plugins.Document import *

# Upload to Kaltura
def upload_ppt_to_kaltura(file_path, title=None, description=None, thumbnail_file_path=None, channel_id=None):
    """
    Upload a PowerPoint document to Kaltura with optional thumbnail
    
    Args:
        file_path (str): Path to the PowerPoint file to upload
        title (str, optional): Title for the document entry. Defaults to "ppt_document_[timestamp]"
        description (str, optional): Description for the document entry
        thumbnail_file_path (str, optional): Path to the thumbnail image file
        channel_id (int, optional): Kaltura category ID (channel). Defaults to 374334092
    """
    global MY_USER_SECRET, MY_ADMIN_SECRET, MY_PARTNER_ID

    # Kaltura service configuration
    config = KalturaConfiguration()
    config.serviceUrl = "https://www.kaltura.com/"
    client = KalturaClient(config)
    
    # Load the Document plugin
    client.loadPlugin('Document')
    
    expiry = 86400
    privileges = "disableentitlement"

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

    # Create document entry instead of media entry
    document_entry = KalturaDocumentEntry()
    
    # Document Type - specify PowerPoint
    document_entry.documentType = KalturaDocumentType.DOCUMENT
    
    # Reference ID
    document_entry.referenceId = "auto-" + datetime.now().strftime('%Y%m%d%H%M%S')
    
    # ✅ NAME
    if title:
        document_entry.name = title
    else:
        document_entry.name = f"ppt_document_{ts_file}"

    # ✅ DESCRIPTION
    if description:
        document_entry.description = description
    else:
        document_entry.description = "PowerPoint document uploaded via Kaltura API"
    
    # Set creator and owner information
    document_entry.userId = "nicolas.deville@kaltura.com"
    document_entry.creatorId = "nicolas.deville@kaltura.com"
    
    # Add this before using the document service to see what methods are available
    print("Available methods on client.document:")
    for method in dir(client.document):
        if not method.startswith('_'):
            print(method)
    
    # ADD THE DOCUMENT ENTRY
    document_entry = client.baseEntry.add(document_entry)
    
    # Attach uploaded file to the document entry
    resource = KalturaUploadedFileTokenResource()
    resource.token = upload_token.id
    document_entry = client.baseEntry.addContent(document_entry.id, resource)
    
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
            
            # Add the thumbnail to the document entry
            result_thumb = client.thumbAsset.add(document_entry.id, thumb_asset)
            
            # Create a resource from the upload token
            thumb_resource = KalturaUploadedFileTokenResource()
            thumb_resource.token = thumb_token.id
            
            # Set the content of the thumbnail
            client.thumbAsset.setContent(result_thumb.id, thumb_resource)
            
            # Set this thumbnail as the default for the document entry
            client.thumbAsset.setAsDefault(result_thumb.id)
            
            print(f"✅ Thumbnail successfully added & set as default")

        except Exception as e:
            print(f"❌ Error adding thumbnail: {e}")
    else:
        print("ℹ️ No thumbnail file provided, using default thumbnail.")

    # ✅ CATEGORY (add to a Category so it appears in KMS Channel)
    category_entry = KalturaCategoryEntry()
    category_entry.entryId = document_entry.id
    category_entry.categoryId = channel_id
    
    try:
        client.categoryEntry.add(category_entry)
        print(f"✅ Successfully added entry to category ID: {channel_id}")
    except Exception as e:
        print(f"❌ Error adding to category: {e}")
    
    print(f"\n✅ Upload successful of '{document_entry.name}': https://nicolas.mediaspace.kaltura.com/media/{document_entry.id}")

    file_data.close()


if __name__ == "__main__":

    file_path = "/Users/nic/Downloads/temp/test-ppt-upload.pptx"
    thumbnail_file_path = "/Users/nic/Downloads/temp/ppt-thumbnail-test.jpg"
    document_title = f"PowerPoint Document {ts_file}"
    document_description = "This is a PowerPoint document uploaded with the Kaltura API and a custom thumbnail."

    channel_id = 374334092

    print(f"\n\nUploading {file_path} to Kaltura with custom title, description, and a custom thumbnail...")
    upload_ppt_to_kaltura(file_path, document_title, document_description, thumbnail_file_path, channel_id)
    print(f"\n\n✅ File uploaded successfully to Kaltura")

    # End Chrono
    run_time = round((time.time() - start_time), 3)
    print(f'\n{os.path.basename(__file__)} finished in {round(run_time)}s at {datetime.now().strftime("%H:%M:%S")}.\n')

# Debugging code to print available document types
for attr in dir(KalturaDocumentType):
    if not attr.startswith('_'):
        print(attr)