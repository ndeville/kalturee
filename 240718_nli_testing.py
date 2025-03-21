import os
import requests
import xml.etree.ElementTree as ET

def create_chapters(video_id, chapters):
    KALTURA_API_BASE_URL = 'https://www.kaltura.com/api_v3/'
    KALTURA_PARTNER_ID = os.getenv("partner_id")
    KALTURA_ADMIN_SECRET = os.getenv("admin_secret")
    KALTURA_USER_SECRET = os.getenv("user_secret")
    KALTURA_SESSION_TYPE = 2  # Admin session
    KALTURA_EXPIRY = 86400  # 24 hours

    def generate_ks():
        payload = {
            'service': 'session',
            'action': 'start',
            'partnerId': KALTURA_PARTNER_ID,
            'secret': KALTURA_ADMIN_SECRET,
            'userId': KALTURA_USER_SECRET,
            'type': KALTURA_SESSION_TYPE,
            'expiry': KALTURA_EXPIRY
        }
        response = requests.post(KALTURA_API_BASE_URL, data=payload)
        try:
            root = ET.fromstring(response.text)
            return root.find('result').text
        except ET.ParseError:
            print("Failed to parse XML response from Kaltura API")
            print("Response text:", response.text)
            return None

    def check_entry_exists(entry_id, ks):
        payload = {
            'service': 'media',
            'action': 'get',
            'ks': ks,
            'entryId': entry_id
        }
        response = requests.post(KALTURA_API_BASE_URL, data=payload)
        try:
            root = ET.fromstring(response.text)
            if root.find('.//error'):
                return False
            return True
        except ET.ParseError:
            print("Failed to parse XML response while checking entry existence")
            print("Response text:", response.text)
            return False

    def list_videos(ks):
        videos = []
        page_index = 1
        page_size = 30  # Adjust as needed

        while True:
            payload = {
                'service': 'media',
                'action': 'list',
                'ks': ks,
                'filter:mediaTypeEqual': 1,  # Filter for video entries
                'filter:statusIn': '2,3',  # Include all statuses (2: Ready, 3: Deleted)
                'pager': {
                    'pageIndex': page_index,
                    'pageSize': page_size
                }
            }
            response = requests.post(KALTURA_API_BASE_URL, json=payload)
            try:
                root = ET.fromstring(response.text)
                if root.find('.//error'):
                    print("Failed to list videos")
                    print("Response text:", response.text)
                    return videos
                items = root.findall('.//item')
                if not items:
                    break
                for item in items:
                    video_id = item.find('id').text
                    name = item.find('name').text
                    videos.append({'id': video_id, 'name': name})
                page_index += 1
            except ET.ParseError:
                print("Failed to parse XML response while listing videos")
                print("Response text:", response.text)
                return videos

        return videos

    ks = generate_ks()
    if not ks:
        print("Failed to generate Kaltura session.")
        return

    # List all videos in the account
    videos = list_videos(ks)
    print("Videos in the account:")
    for video in videos:
        print(f"ID: {video['id']}, Name: {video['name']}")

    if not check_entry_exists(video_id, ks):
        print(f"Entry ID '{video_id}' not found.")
        return

    for chapter in chapters:
        payload = {
            'service': 'annotation_annotation',
            'action': 'add',
            'ks': ks,
            'annotation': {
                'objectType': 'KalturaAnnotation',
                'entryId': video_id,
                'startTime': chapter['start_time'] * 1000,  # Kaltura expects milliseconds
                'endTime': chapter['end_time'] * 1000,      # Kaltura expects milliseconds
                'tags': 'chapter',
                'text': chapter['title'],
                'annotationType': 'chapter'
            }
        }
        response = requests.post(KALTURA_API_BASE_URL, json=payload)
        try:
            root = ET.fromstring(response.text)
            if response.status_code != 200 or root.find('.//error'):
                print(f"Failed to create chapter '{chapter['title']}'")
                print("Response text:", response.text)
                continue
            print(f"Chapter '{chapter['title']}' created successfully.")
        except ET.ParseError:
            print(f"Failed to parse XML response for chapter '{chapter['title']}'")
            print("Response text:", response.text)

# Example usage
video_id = "1_vgw9hjgx"
chapters = [
    {"start_time": 5, "end_time": 10, "title": "The First One"},
    {"start_time": 15, "end_time": 30, "title": "The Second One"}
]

create_chapters(video_id, chapters)