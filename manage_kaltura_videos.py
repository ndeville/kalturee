"""FETCH BASIC VIDEO INFO FROM KALTURA"""

from datetime import datetime
import os
import time
from dotenv import load_dotenv
from KalturaClient import *
from KalturaClient.Plugins.Core import *
import json

def initialize_kaltura_client(partner_id, admin_secret):
    """Initialize Kaltura client with admin session"""
    try:
        config = KalturaConfiguration(partner_id)
        config.serviceUrl = "https://www.kaltura.com/"
        client = KalturaClient(config)
        
        # print(f"Attempting to connect with Partner ID: {partner_id}")
        ks = client.session.start(
            admin_secret,
            None,
            KalturaSessionType.ADMIN,
            partner_id,
            86400,
            "disableentitlement"
        )
        client.setKs(ks)
        # print("Successfully authenticated with Kaltura")
        return client
    except Exception as e:
        # print(f"Error initializing Kaltura client: {str(e)}")
        raise

def get_all_videos(PARTNER_ID, ADMIN_SECRET, batch_size=1000):
    """Fetch basic video information from Kaltura"""

    client = initialize_kaltura_client(PARTNER_ID, ADMIN_SECRET)

    try:
        print("Setting up video filter...")
        filter = KalturaMediaEntryFilter()
        filter.mediaTypeEqual = KalturaMediaType.VIDEO
        
        pager = KalturaFilterPager()
        pager.pageSize = batch_size
        pager.pageIndex = 1
        
        print(f"Attempting to fetch first batch of {batch_size} videos...")
        result = client.media.list(filter, pager)
        print(f"Total videos available: {result.totalCount}")
        
        all_videos = []
        total_count = 0
        
        while True:
            result = client.media.list(filter, pager)
            if not result.objects:
                break
                
            for video in result.objects:
                # video_data = {
                #     'id': video.id,
                #     'name': video.name,
                #     'created_at': datetime.fromtimestamp(video.createdAt).strftime('%Y-%m-%d %H:%M:%S')
                # }
                # all_videos.append(video_data)
                all_videos.append(video.name)

                total_count += 1
                print(f"\rFetched data for {total_count} videos...", end='')
            
            pager.pageIndex += 1
        
        return all_videos
    except Exception as e:
        print(f"Error in get_all_videos: {str(e)}")
        return []



def save_to_json(videos, filename):
    """Save video data to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    # Start timing
    start_time = time.time()
    print(f"\n---------- {datetime.now().strftime('%H:%M:%S')} Starting video data fetch")
    
    # Load environment variables
    load_dotenv()
    
    # Configure which KMS to use
    KMS = "Pharma"  # "Pharma" or "MY_KMS"
    
    # Get credentials based on KMS
    if KMS == "MY_KMS":
        ADMIN_SECRET = os.getenv("admin_secret")
        PARTNER_ID = int(os.getenv("partner_id"))
    elif KMS == "Pharma":
        ADMIN_SECRET = os.getenv("pharma_admin_secret")
        PARTNER_ID = int(os.getenv("pharma_partner_id"))
    
    # Add debug information for credentials
    print(f"Using KMS: {KMS}")
    # print(f"Partner ID: {PARTNER_ID}")
    # print(f"Admin Secret length: {len(ADMIN_SECRET) if ADMIN_SECRET else 0} characters")
    
    try:

        
        # Fetch all videos
        videos = get_all_videos(PARTNER_ID, ADMIN_SECRET)

        print(f"\n\n{len(videos)} videos found:")
        for video in videos:
            print(f"\t- {video}")
        print()
        # # Save results
        # timestamp = datetime.now().strftime('%y%m%d-%H%M')
        # filename = f'kaltura_videos_{timestamp}.json'
        # save_to_json(videos, filename)
        
        # Print summary
        # print(f"\n\nFetch complete!")
        # print(f"Total videos found: {len(videos)}")
        # print(f"Data saved to: {filename}")
        print(f"Time taken: {time.time() - start_time:.2f} seconds\n")
    
    except Exception as e:
        print(f"\nScript failed with error: {str(e)}")
