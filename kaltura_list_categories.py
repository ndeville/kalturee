"""LIST CATEGORIES FROM KALTURA KMS"""

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

config = KalturaConfiguration()
config.serviceUrl = "https://www.kaltura.com/"
client = KalturaClient(config)

adminSecret = MY_ADMIN_SECRET
userId = ''  
type = KalturaSessionType.ADMIN  
partnerId = MY_PARTNER_ID  
expiry = 86400  
privileges = 'disableentitlement'  # Disables entitlement to allow listing all categories
# Note: 'kms.user=nicolas.deville@kaltura.com' is used for user-specific operations
# For listing categories, we need to disable entitlement restrictions

ks = client.session.start(adminSecret, userId, type, partnerId, expiry, privileges)
client.setKs(ks)

filter = KalturaCategoryFilter()
pager = KalturaFilterPager()

result = client.category.list(filter, pager)

print(f"\n\nPRINTING ONLY CATEGORIES WITHIN KMS CHANNEL:\n")

for category in result.objects:
    if category.fullName.startswith("MediaSpace>site>channels"):
        print(f"{category.id:<15}{category.name:<40}{category.fullName}")

# End Chrono
run_time = round((time.time() - start_time), 3)
print(f'\n{os.path.basename(__file__)} finished in {round(run_time*1000)}ms at {datetime.now().strftime("%H:%M:%S")}.\n')
# print(f'\n{os.path.basename(__file__)} finished in {round(run_time)}s at {datetime.now().strftime("%H:%M:%S")}.\n')

