"""CREATE CHANNELS IN KALTURA KMS"""
"""AS CHANNELS IN KMC"""


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

# Parent category ID for KMS channels
PARENT_CATEGORY_ID = 376311372

def create_kaltura_category(name, description="", parent_id=PARENT_CATEGORY_ID):

    # Kaltura Client
    config = KalturaConfiguration()
    config.serviceUrl = "https://www.kaltura.com/"
    client = KalturaClient(config)

    # Start session
    adminSecret = MY_ADMIN_SECRET
    userId = ''  
    type = KalturaSessionType.ADMIN  
    partnerId = MY_PARTNER_ID  
    expiry = 86400  
    privileges = 'disableentitlement'

    ks = client.session.start(adminSecret, userId, type, partnerId, expiry, privileges)
    client.setKs(ks)

    # Create category
    category = KalturaCategory()
    category.name = name
    category.description = description
    category.parentId = parent_id

    try:
        result = client.category.add(category)
        print(f"✅ Successfully created category: {name}")
        return result
    except Exception as e:
        print(f"❌ Error creating category {name}: {str(e)}")
        return None

def create_multiple_categories(category_list):
    """
    Creates multiple categories from a list of dictionaries containing name and description.
    
    Args:
        category_list (list): List of dictionaries with 'name' and 'description' keys
    """
    created_categories = []
    failed_categories = []

    for category in category_list:
        result = create_kaltura_category(
            name=category['name'],
            description=category.get('description', '')
        )
        if result:
            created_categories.append(result)
        else:
            failed_categories.append(category['name'])

    return created_categories, failed_categories

# Example usage when script is run directly
if __name__ == "__main__":
    # Example categories to create
    categories_to_create = [
        {"name": "Test Channel 1", "description": "First test channel"},
        {"name": "Test Channel 2", "description": "Second test channel"},
    ]

    print(f"\nCreating categories under parent ID {PARENT_CATEGORY_ID}...\n")
    created, failed = create_multiple_categories(categories_to_create)
    
    print(f"\nResults:")
    print(f"✅ Successfully created {len(created)} categories")
    if failed:
        print(f"❌ Failed to create {len(failed)} categories: {', '.join(failed)}")

    # End timing
    run_time = round((time.time() - start_time), 3)
    print(f'\nOperation finished in {round(run_time*1000)}ms at {datetime.now().strftime("%H:%M:%S")}.\n')