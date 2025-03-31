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

# Credentials
from dotenv import load_dotenv
load_dotenv()


# Kaltura Client
from KalturaClient import *
from KalturaClient.Plugins.Core import *
# Add this import for captions
from KalturaClient.Plugins.Caption import *
from KalturaClient.Plugins.Caption import KalturaLanguage, KalturaCaptionAsset, KalturaCaptionType

import subprocess
import json

# FUNCTIONS

# TODO

def get_kaltura_channels(PARTNER_ID=None, ADMIN_SECRET=None):

    # Configure the Kaltura client
    config = KalturaConfiguration(int(PARTNER_ID))
    config.serviceUrl = "https://www.kaltura.com/"
    client = KalturaClient(config)
    
    # Start a Kaltura session
    ks = client.session.start(
        ADMIN_SECRET,
        None,
        KalturaSessionType.ADMIN,
        int(PARTNER_ID),
        86400,  # expiry in seconds (24 hours)
        "disableentitlement"
    )
    client.setKs(ks)
    
    # Create a filter for category listing
    filter = KalturaCategoryFilter()
    # You can add additional filters if needed
    # filter.parentIdEqual = 0  # Only get top-level categories
    
    # Create a pager for pagination
    pager = KalturaFilterPager()
    pager.pageSize = 500  # Adjust based on your needs
    
    try:
        # Get the list of categories (channels)
        result = client.category.list(filter, pager)
        
        # Create a dictionary of channel names and IDs
        channels = {}
        for category in result.objects:
            channels[category.name] = category.id
            
        print(f"\n✅ Successfully fetched {len(channels)} Kaltura channels\n")
        return channels
    
    except Exception as e:
        print(f"❌ Error fetching Kaltura channels: {str(e)}")
        return {}



def create_kaltura_channel(channel_name, parent_id=None, description=None, tags=None, PARTNER_ID=None, ADMIN_SECRET=None, USER_SECRET=None, OWNER=None):

    # Configure the Kaltura client
    config = KalturaConfiguration(int(PARTNER_ID))
    config.serviceUrl = "https://www.kaltura.com/"
    client = KalturaClient(config)
    
    # Start a Kaltura session
    ks = client.session.start(
        ADMIN_SECRET,
        None,
        KalturaSessionType.ADMIN,
        int(PARTNER_ID),
        86400,  # expiry in seconds (24 hours)
        "disableentitlement"
    )
    client.setKs(ks)
    
    # Create a new category object
    category = KalturaCategory()
    category.name = channel_name
    
    # Set optional parameters if provided
    if parent_id is not None:
        category.parentId = parent_id
    if description is not None:
        category.description = description
    if tags is not None:
        category.tags = tags
    if OWNER is not None:
        category.owner = OWNER
    
    # Add necessary permissions and settings
    category.appearInList = KalturaAppearInListType.PARTNER_ONLY
    category.contributionPolicy = KalturaContributionPolicyType.ALL
    category.privacy = KalturaPrivacyType.ALL
    category.moderation = KalturaNullableBoolean.FALSE_VALUE
    category.defaultPermissionLevel = KalturaCategoryUserPermissionLevel.MANAGER
    category.inheritanceType = KalturaInheritanceType.MANUAL
    
    # Add CategoryAdditionalInfo for thumbnail
    # Set the channel thumbnail using partnerData field which supports JSON
    category.partnerData = '{"channelThumbnailEntry":"1_txdk0h2r"}'
    
    # Alternatively, you can use adminTags to store this information
    category.adminTags = 'channelThumbnailEntry=1_txdk0h2r'
    
    try:
        # Add the category
        result = client.category.add(category)
        print(f"\n✅ Successfully created channel '{channel_name}' with ID {result.id}")
        return result.id
    
    except Exception as e:
        print(f"❌ Error creating Kaltura channel '{channel_name}': {str(e)}")
        return None



def get_channels_parent_id(PARTNER_ID=None, ADMIN_SECRET=None):

    # Get all channels
    channels = get_kaltura_channels(PARTNER_ID=PARTNER_ID, ADMIN_SECRET=ADMIN_SECRET)
    
    # Look for the "channels" category
    if "channels" in channels:
        channels_id = channels["channels"]
        print(f"\n✅ Found 'channels' category with ID: {channels_id}")
        return int(channels_id)
    else:
        print("\n❌ 'channels' category not found")
        return None


model_for_channel_description = "llama3.2"

def generate_channel_description(channel_name):
    global model_for_channel_description
    
    try:
        # Prepare the prompt for Ollama
        prompt = f"Write a concise, professional description (2 sentences maximum) for a video channel called '{channel_name}' that would appear in a medical education platform. The description should explain what type of content viewers can expect to find in this channel. Only return the description, nothing else. Remove any quotes or markdown formatting."
        
        # Call Ollama using subprocess
        result = subprocess.run(
            ["ollama", "run", model_for_channel_description, prompt],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Get the output and clean it up
        description = result.stdout.strip()
        
        # # Limit to a reasonable length if needed
        # if len(description) > 500:
        #     description = description[:497] + "..."
            
        print(f"\n✅ Generated description for channel '{channel_name}': {description}")
        return description
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating description with Ollama: {str(e)}")
        # Fallback description
        return f"A collection of videos related to {channel_name}, providing educational content and resources for medical professionals."
    
    except Exception as e:
        print(f"❌ Unexpected error generating description: {str(e)}")
        # Fallback description
        return f"A collection of videos related to {channel_name}, providing educational content and resources for medical professionals."





def assign_kaltura_channel_id(video_id, channel_id):
    """
    Assign a Kaltura channel ID to a video.
    """
    pass






if __name__ == "__main__":

    KMS = "Pharma" # "Pharma" or "MY_KMS"

    # Credentials
    OWNER = "nicolas.deville@kaltura.com"

    if KMS == "MY_KMS":
        USER_SECRET = os.getenv("user_secret")
        ADMIN_SECRET = os.getenv("admin_secret")
        PARTNER_ID = os.getenv("partner_id")
    elif KMS == "Pharma":
        USER_SECRET = os.getenv("pharma_user_secret")
        ADMIN_SECRET = os.getenv("pharma_admin_secret")
        PARTNER_ID = os.getenv("pharma_partner_id")


    channel_name = f"test_{datetime.now().strftime('%y%m%d-%H%M')}"
    description = f"Test channel created at {datetime.now().strftime('%y%m%d-%H%M')}"
    tags = "test, channel, kaltura"
    parent_id = get_channels_parent_id(PARTNER_ID=PARTNER_ID, ADMIN_SECRET=ADMIN_SECRET) # ID of "channels" category

    create_kaltura_channel(channel_name, parent_id=parent_id, description=description, tags=tags, PARTNER_ID=PARTNER_ID, ADMIN_SECRET=ADMIN_SECRET, USER_SECRET=USER_SECRET, OWNER=OWNER)

    print(f"\nCreated channel: {channel_name}")

    channels = get_kaltura_channels(PARTNER_ID=PARTNER_ID, ADMIN_SECRET=ADMIN_SECRET)
    
    for channel_name, channel_id in channels.items():
        print(f"{channel_id}\t{channel_name}")

    if channel_name in channels:
        print(f"\n✅ Channel '{channel_name}' found with ID: {channels[channel_name]}")
    else:
        print(f"\n❌ Channel '{channel_name}' not found")

    print()
