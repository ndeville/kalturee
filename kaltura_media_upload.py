from datetime import datetime
import os
ts_db = f"{datetime.now().strftime('%Y-%m-%d %H:%M')}"
ts_time = f"{datetime.now().strftime('%H:%M:%S')}"
print(f"\n---------- {ts_time} starting {os.path.basename(__file__)}")
import time
start_time = time.time()

from dotenv import load_dotenv
load_dotenv()
# DB_TWITTER = os.getenv("DB_TWITTER")
# DB_BTOB = os.getenv("DB_BTOB")
# DB_MAILINGEE = os.getenv("DB_MAILINGEE")

import pprint
pp = pprint.PrettyPrinter(indent=4)

####################
# UPLOAD TO KALTURA

# IMPORTS (script-specific)

import my_utils
from DB.tools import select_all_records, update_record, create_record, delete_record
from tqdm import tqdm
import os

MY_USER_SECRET = os.getenv("user_secret")
MY_ADMIN_SECRET = os.getenv("admin_secret")
MY_PARTNER_ID = os.getenv("partner_id")

# GLOBALS

test = 1
verbose = 1

count_row = 0
count_total = 0
count = 0


# FUNCTIONS



# MAIN

""" ChatGPT:
Based on Kaltura's API here: https://developer.kaltura.com/api-docs
Write a python function that takes in a local path to a video file and uploads it to Kaltura
"""



from KalturaClient import *
from KalturaClient.Plugins.Core import *

def upload_video_to_kaltura(file_path):
    global MY_USER_SECRET, MY_ADMIN_SECRET, MY_PARTNER_ID

    # Kaltura service configuration
    config = KalturaConfiguration()
    config.serviceUrl = "https://www.kaltura.com/"
    client = KalturaClient(config)
    
    # Administrator secret and user ID (use None for user ID if not applicable)
    admin_secret = MY_ADMIN_SECRET
    user_id = MY_USER_SECRET
    partner_id = MY_PARTNER_ID
    expiry = 86400
    privileges = ""

    # Start session
    ks = client.session.start(admin_secret, user_id, KalturaSessionType.ADMIN, partner_id, expiry, privileges)
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

    # Create media entry and set it to "unlisted" category
    media_entry = KalturaMediaEntry()
    media_entry.mediaType = KalturaMediaType.VIDEO
    # media_entry.categories = 324250232  # use the Category ID to be found in https://kmc.kaltura.com/index.php/kmcng/content/categories/list
    # media_entry.categoriesIds = 324250232  # use the Category ID to be found in https://kmc.kaltura.com/index.php/kmcng/content/categories/list
    # media_entry.categoriesIds = "324250232"  # use the Category ID to be found in https://kmc.kaltura.com/index.php/kmcng/content/categories/list
    # media_entry.categories = "324250232"  # use the Category ID to be found in https://kmc.kaltura.com/index.php/kmcng/content/categories/list
    # media_entry.categories = 'MediaSpace>unlisted'  # use the Category ID to be found in https://kmc.kaltura.com/index.php/kmcng/content/categories/list
    media_entry.categories = 'MediaSpace'  # use the Category ID to be found in https://kmc.kaltura.com/index.php/kmcng/content/categories/list
    media_entry = client.media.add(media_entry)
    
    # Attach uploaded file to the media entry
    resource = KalturaUploadedFileTokenResource()
    resource.token = upload_token.id
    media_entry = client.media.addContent(media_entry.id, resource)
    
    print(f"\n\nUpload successful: https://nicolas.mediaspace.kaltura.com/media/{media_entry.id}")

    # Close the file
    file_data.close()


# Example usage
file_path = "/Users/nic/Movies/Recordings/240211-133436.mp4"
upload_video_to_kaltura(file_path)




# config = KalturaConfiguration()
# config.serviceUrl = "https://www.kaltura.com/"
# client = KalturaClient(config)

# admin_secret = MY_ADMIN_SECRET
# user_id = MY_USER_SECRET
# partner_id = MY_PARTNER_ID
# expiry = 86400
# privileges = ""

# # Start session
# ks = client.session.start(admin_secret, user_id, KalturaSessionType.ADMIN, partner_id, expiry, privileges)
# client.setKs(ks)

# entryId = "1_s99sc35x"
# categoryId = "324250232"

# mediaEntry = KalturaMediaEntry()
# mediaEntry.categoriesIds = str(categoryId)  # Set the category IDs as a comma-separated string

# updatedEntry = client.media.update(entryId, mediaEntry)
# print(f"Updated Entry ID: {updatedEntry.id} is now assigned to Category ID: {categoryId}")






# from KalturaClient import *
# from KalturaClient.Plugins.Core import *

# config = KalturaConfiguration()
# config.serviceUrl = "https://www.kaltura.com/"
# client = KalturaClient(config)

# adminSecret = MY_ADMIN_SECRET
# userId = ''  # Can be left empty for admin sessions
# type = KalturaSessionType.ADMIN  # Specify an admin session
# partnerId = MY_PARTNER_ID  # Your partner ID
# expiry = 86400  # Session duration in seconds
# privileges = ''  # Additional privileges can be specified here

# ks = client.session.start(adminSecret, userId, type, partnerId, expiry, privileges)
# client.setKs(ks)

# filter = KalturaCategoryFilter()
# # filter.fullNameStartsWith = "MediaSpace"  # Adjust as necessary
# pager = KalturaFilterPager()

# result = client.category.list(filter, pager)

# for category in result.objects:
#     print(f"Category ID: {category.id}, Name: {category.name}, Full Name: {category.fullName}")






# # List all categories
# filter = KalturaCategoryFilter()
# pager = KalturaFilterPager()

# result = client.category.list(filter, pager)

# for category in result.objects:
#     print(f"Category ID: {category.id}, Name: {category.name}, Full Name: {category.fullName}")


# # List all categories within the MediaSpace parent category
# filter = KalturaCategoryFilter()
# filter.parentIdEqual = "MediaSpace"  # Set the parent category ID
# pager = KalturaFilterPager()

# result = client.category.list(filter, pager)

# for category in result.objects:
#     print(f"Category ID: {category.id}, Name: {category.name}, Full Name: {category.fullName}")


"""
Categories under MediaSpace don't get listed
"""



########################################################################################################

if __name__ == '__main__':
    print('\n\n-------------------------------')
    # print(f"\ncount_row:\t{count_row:,}")
    # print(f"count_total:\t{count_total:,}")
    # print(f"count:\t{count:,}")
    run_time = round((time.time() - start_time), 3)
    if run_time < 1:
        print(f'\n{os.path.basename(__file__)} finished in {round(run_time*1000)}ms at {datetime.now().strftime("%H:%M:%S")}.\n')
    elif run_time < 60:
        print(f'\n{os.path.basename(__file__)} finished in {round(run_time)}s at {datetime.now().strftime("%H:%M:%S")}.\n')
    elif run_time < 3600:
        print(f'\n{os.path.basename(__file__)} finished in {round(run_time/60)}mns at {datetime.now().strftime("%H:%M:%S")}.\n')
    else:
        print(f'\n{os.path.basename(__file__)} finished in {round(run_time/3600, 2)}hrs at {datetime.now().strftime("%H:%M:%S")}.\n')