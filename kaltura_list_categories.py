"""LIST CATEGORIES FROM KALTURA KMS"""


from datetime import datetime
import os
import time
from dotenv import load_dotenv
from KalturaClient import *
from KalturaClient.Plugins.Core import *

# Start timing
start_time = time.time()
ts_time = f"{datetime.now().strftime('%H:%M:%S')}"

# Credentials
load_dotenv()
# MY_USER_SECRET = os.getenv("user_secret")
# MY_ADMIN_SECRET = os.getenv("admin_secret")
# MY_PARTNER_ID = os.getenv("partner_id")
MY_USER_SECRET = os.getenv("ca_user_secret")
MY_ADMIN_SECRET = os.getenv("ca_admin_secret")
MY_PARTNER_ID = os.getenv("ca_partner_id")


def list_kaltura_categories(show="all",USER_SECRET=None, ADMIN_SECRET=None, PARTNER_ID=None):
    """
    Lists categories from Kaltura KMS, focusing on those within the KMS Channel.
    
    Args:
        print_output (bool): Whether to print results to console. Default True.
        
    Returns:
        list: List of category objects that match the channel criteria
    """

    # Kaltura Client
    config = KalturaConfiguration()
    config.serviceUrl = "https://www.kaltura.com/"
    client = KalturaClient(config)

    adminSecret = MY_ADMIN_SECRET
    userId = ''  
    type = KalturaSessionType.ADMIN  
    partnerId = MY_PARTNER_ID  
    expiry = 86400  
    privileges = 'disableentitlement'  # Disables entitlement to allow listing all categories

    ks = client.session.start(adminSecret, userId, type, partnerId, expiry, privileges)
    client.setKs(ks)

    filter = KalturaCategoryFilter()
    pager = KalturaFilterPager()

    result = client.category.list(filter, pager)

    # Filter for categories within KMS Channel
    channel_categories = []
    for category in result.objects:
        if show == "all":
            print(f"\nℹ️  Showing all categories. Update the 'show' argument to 'kms_only' to show only categories within KMS Channel.")
            channel_categories.append(category)
            print(f"{category.id:<15}{category.name:<40}{category.fullName}")
        elif show == "kms_only": 
            print(f"\nℹ️  Showing only categories within KMS Channel. Update the 'show' argument to 'all' to show all categories.")
            if category.fullName.startswith("MediaSpace>site>channels"):
                channel_categories.append(category)
                print(f"{category.id:<15}{category.name:<40}{category.fullName}")



    return channel_categories

# Example usage when script is run directly
if __name__ == "__main__":

    print(f"\n\nPRINTING ONLY CATEGORIES WITHIN KMS CHANNEL:\n")
    categories = list_kaltura_categories(show="all", USER_SECRET=MY_USER_SECRET, ADMIN_SECRET=MY_ADMIN_SECRET, PARTNER_ID=MY_PARTNER_ID)
    print(f"\n{len(categories)} categories found in KMS\n")

    # print(type(categories))
    # print(categories)
    # "category.id:<15}{category.name:<40}{category.fullName"

    # End timing
    run_time = round((time.time() - start_time), 3)
    print(f'\nOperation finished in {round(run_time*1000)}ms at {datetime.now().strftime("%H:%M:%S")}.\n')