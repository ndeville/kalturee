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






from KalturaClient import *
from KalturaClient.Plugins.Core import *

config = KalturaConfiguration()
config.serviceUrl = "https://www.kaltura.com/"
client = KalturaClient(config)

adminSecret = MY_ADMIN_SECRET
userId = ''  # Can be left empty for admin sessions
type = KalturaSessionType.ADMIN  # Specify an admin session
partnerId = MY_PARTNER_ID  # Your partner ID
expiry = 86400  # Session duration in seconds
privileges = ''  # Additional privileges can be specified here

ks = client.session.start(adminSecret, userId, type, partnerId, expiry, privileges)
client.setKs(ks)

filter = KalturaCategoryFilter()
# filter.fullNameStartsWith = "MediaSpace/site/channels"
pager = KalturaFilterPager()

result = client.category.list(filter, pager)

for category in result.objects:
    print(f"Category ID: {category.id}, Name: {category.name}, Full Name: {category.fullName}")








########################################################################################################

if __name__ == '__main__':
    print('\n\n-------------------------------')
    print(f"\ncount_row:\t{count_row:,}")
    print(f"count_total:\t{count_total:,}")
    print(f"count:\t\t{count:,}")
    run_time = round((time.time() - start_time), 3)
    if run_time < 1:
        print(f'\n{os.path.basename(__file__)} finished in {round(run_time*1000)}ms at {datetime.now().strftime("%H:%M:%S")}.\n')
    elif run_time < 60:
        print(f'\n{os.path.basename(__file__)} finished in {round(run_time)}s at {datetime.now().strftime("%H:%M:%S")}.\n')
    elif run_time < 3600:
        print(f'\n{os.path.basename(__file__)} finished in {round(run_time/60)}mns at {datetime.now().strftime("%H:%M:%S")}.\n')
    else:
        print(f'\n{os.path.basename(__file__)} finished in {round(run_time/3600, 2)}hrs at {datetime.now().strftime("%H:%M:%S")}.\n')