from datetime import datetime
import os
ts_db = f"{datetime.now().strftime('%Y-%m-%d %H:%M')}"
ts_time = f"{datetime.now().strftime('%H:%M:%S')}"
print(f"\n---------- {ts_time} starting {os.path.basename(__file__)}")
import time
start_time = time.time()

from dotenv import load_dotenv
load_dotenv()
DB_BTOB = os.getenv("DB_BTOB")
DB_MAILINGEE = os.getenv("DB_MAILINGEE")

import pprint
pp = pprint.PrettyPrinter(indent=4)

####################
# DOWNLOAD WEBSITE ASSETS FOR BUILDING DEMO ENVIRONMENT - IMAGES & PDFs


"""
TODO
- download CSS file, extract colours & font & generate style guide JSON (to be used to create a custom configuration file)
"""


# IMPORTS

import my_utils
# from DB.tools import select_all_records, update_record, create_record, delete_record
import sqlite3


import os
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

import os
from pathlib import Path
from PIL import Image
import imagehash


import os
import re
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup



# GLOBALS

test = 1
verbose = 1

count_row = 0
count_total = 0
count = 0


# FUNCTIONS


# DOWNLOAD CSS FILE

def download_css_file(url, output_path):
    session = requests.Session()
    resp = session.get(url)
    resp.raise_for_status()
    ctype = resp.headers.get('Content-Type', '').split(';')[0]
    # if it's already a CSS URL or returns CSS
    if ctype == 'text/css' or urlparse(url).path.lower().endswith('.css'):
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(resp.content)
        return

    # parse HTML for <link rel="stylesheet">
    soup = BeautifulSoup(resp.text, 'html.parser')
    links = soup.find_all('link', rel=lambda v: v and 'stylesheet' in v.lower())
    css_urls = [urljoin(resp.url, l['href']) for l in links if l.get('href')]
    if not css_urls:
        raise ValueError(f'No CSS files found at {url}')

    visited = set()
    def fetch_css(css_url):
        if css_url in visited:
            return ''
        visited.add(css_url)
        r = session.get(css_url)
        r.raise_for_status()
        text = r.text
        # handle @import statements
        imports = re.findall(r'@import\s+(?:url\()?["\']?([^"\')]+)["\']?\)?', text)
        content = ''
        for imp in imports:
            content += fetch_css(urljoin(css_url, imp))
        return content + '\n' + text

    combined = ''
    for css_url in css_urls:
        combined += fetch_css(css_url) + '\n'

    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(combined)



# DELETE DUPLICATE IMAGES
def perceptual_hash(image_path):
    try:
        with Image.open(image_path) as img:
            return imagehash.phash(img)
    except Exception:
        return None

def delete_duplicate_images(folder_path, threshold=5):
    seen_hashes = {}
    folder = Path(folder_path)
    files_deleted = 0
    files_kept = 0

    for ext in ('*.jpg', '*.jpeg', '*.png'):
        for image_path in folder.rglob(ext):
            img_hash = perceptual_hash(image_path)
            if img_hash is None:
                continue

            duplicate_found = False
            for existing_hash in seen_hashes:
                if abs(img_hash - existing_hash) <= threshold:
                    os.remove(image_path)
                    files_deleted += 1
                    duplicate_found = True
                    break

            if not duplicate_found:
                seen_hashes[img_hash] = image_path
                files_kept += 1
    print(f"\nDuplicate image removal complete:")
    print(f"- {files_deleted} duplicate files deleted")
    print(f"- {files_kept} unique files kept")
    
    return files_deleted, files_kept



def download_file(session, url, folder, file_type='image'):
    """Download a file (image or PDF) to the specified folder"""
    try:
        response = session.get(url, stream=True)
        response.raise_for_status()
        
        # Get content type from response headers
        content_type = response.headers.get('content-type', '').lower()
        
        # For PDFs, check content type
        if file_type == 'pdf' and not content_type.endswith('pdf'):
            print(f"ℹ️  Skipping non-PDF file: {url} (Content-Type: {content_type})")
            return
            
        # For images, check content type
        if file_type == 'image' and not content_type.startswith('image/'):
            print(f"ℹ️  Skipping non-image file: {url} (Content-Type: {content_type})")
            return
            
        # Get original filename
        filename = os.path.basename(urlparse(url).path)
        if not filename:
            filename = "file"
            
        # Handle PDFs
        if file_type == 'pdf':
            # Add appropriate extension if missing
            if not filename.lower().endswith('.pdf'):
                filename += '.pdf'
            
            filepath = os.path.join(folder, filename)
            
            # Check if file already exists
            if os.path.exists(filepath):
                print(f"ℹ️  Skipping existing file: {filepath}")
                return
                
            count = 1
            original_filepath = filepath
            while os.path.exists(filepath):
                name, ext = os.path.splitext(original_filepath)
                filepath = f"{name}_{count}{ext}"
                count += 1
                
            # Save the PDF
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"✅ Downloaded PDF: {filepath}")
            return
            
        # Handle images
        if file_type == 'image':
            # Handle SVG files differently
            if url.lower().endswith('.svg') or content_type.endswith('svg+xml'):
                filepath = os.path.join(folder, filename)
                # Check if file already exists
                if os.path.exists(filepath):
                    print(f"ℹ️  Skipping existing file: {filepath}")
                    return
                # Save SVG directly
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                print(f"✅ Downloaded SVG: {filepath}")
                return
                
            try:
                # For raster images, process dimensions
                img = Image.open(BytesIO(response.content))
                width, height = img.size
                
                # Skip if image is too small
                if width < 1000 and height < 1000:
                    print(f"Skipping {url}: Image too small ({width}x{height})")
                    return

                # Resize image if larger than 1920x1080 while maintaining aspect ratio
                if width > 1920 or height > 1080:
                    ratio = min(1920 / width, 1080 / height)
                    new_width = int(width * ratio)
                    new_height = int(height * ratio)
                    img = img.resize((new_width, new_height), Image.LANCZOS)
                    width, height = img.size
                    print(f"Resized image to {width}x{height}")

                # Add width to filename
                name, ext = os.path.splitext(filename)
                
                # Convert webp to jpg
                if ext.lower() == '.webp':
                    ext = '.jpg'
                    # Convert to RGB mode if needed (for PNG/WEBP with transparency)
                    if img.mode in ('RGBA', 'LA', 'P'):
                        img = img.convert('RGB')
                
                filename = f"{width}x{height}_{name}{ext}"
                
                filepath = os.path.join(folder, filename)
                # Check if file already exists
                if os.path.exists(filepath):
                    print(f"ℹ️  Skipping existing file: {filepath}")
                    return
                    
                count = 1
                original_filepath = filepath
                while os.path.exists(filepath):
                    name, ext = os.path.splitext(original_filepath)
                    filepath = f"{width}x{height}_{name}_{count}{ext}"
                    count += 1
                
                # Save the image
                img.save(filepath)
                print(f"✅ Downloaded image: {filepath} ({width}x{height})")
                
            except Exception as e:
                # If PIL can't process the image, save it as-is
                print(f"ℹ️  Saving image without processing: {url}")
                filepath = os.path.join(folder, filename)
                # Check if file already exists
                if os.path.exists(filepath):
                    print(f"ℹ️  Skipping existing file: {filepath}")
                    return
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                print(f"✅ Downloaded image: {filepath}")
                
    except Exception as e:
        print(f"❌ Failed to download {url}: {str(e)}")


def get_domain(url):
    """Extract the domain from a URL"""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def get_all_links(session, url, base_domain):
    """Extract all links from a page that belong to the same domain"""
    try:
        response = session.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = set()
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(url, href)
            
            # Only include links from the same domain
            if full_url.startswith(base_domain):
                links.add(full_url)
        
        return links
    except Exception as e:
        print(f"❌ Failed to get links from {url}: {e}")
        return set()

def extract_background_images(soup, base_url):
    """Extract background images from style attributes and CSS"""
    background_images = set()
    
    # Find elements with style attributes containing background-image
    for element in soup.find_all(style=True):
        style = element['style']
        if 'background-image' in style:
            # Extract URL from background-image property
            import re
            urls = re.findall(r'url\(["\']?(.*?)["\']?\)', style)
            for url in urls:
                full_url = urljoin(base_url, url)
                background_images.add(full_url)
    
    return background_images

def extract_pdf_links(soup, base_url):
    """Extract PDF links from the page"""
    pdf_urls = set()
    
    # Find all links
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if href.lower().endswith('.pdf'):
            full_url = urljoin(base_url, href)
            pdf_urls.add(full_url)
            
    return pdf_urls

def download_all_images(website_url, max_pages=100):
    # Extract the root domain without the TLD
    parsed_url = urlparse(website_url)
    domain_parts = parsed_url.netloc.split('.')
    if len(domain_parts) > 1:
        slug = domain_parts[-2]  # Get the part before the TLD
    else:
        slug = domain_parts[0]  # Fallback if there's only one part
    
    # Create main folder and PDF subfolder
    main_folder = f"/Users/nic/demo/{slug}/"
    pdf_folder = os.path.join(main_folder, "pdf")
    os.makedirs(main_folder, exist_ok=True)
    os.makedirs(pdf_folder, exist_ok=True)
    
    session = requests.Session()
    base_domain = get_domain(website_url)
    
    # Track visited and pending pages
    visited_pages = set()
    pending_pages = {website_url}
    
    while pending_pages and len(visited_pages) < max_pages:
        current_url = pending_pages.pop()
        
        if current_url in visited_pages:
            continue
            
        print(f"\nℹ️  Processing page: {current_url}")
        visited_pages.add(current_url)
        
        # Get all links from the current page
        new_links = get_all_links(session, current_url, base_domain)
        pending_pages.update(new_links - visited_pages)
        
        try:
            # Download images from the current page
            response = session.get(current_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Get regular img tags
            img_tags = soup.find_all('img')
            img_urls = set()
            for img in img_tags:
                img_url = img.attrs.get('src') or img.attrs.get('data-src')
                if img_url:
                    full_url = urljoin(current_url, img_url)
                    img_urls.add(full_url)
            
            # Get background images
            background_urls = extract_background_images(soup, current_url)
            
            # Get PDF links
            pdf_urls = extract_pdf_links(soup, current_url)
            
            # Combine all image URLs
            all_image_urls = img_urls.union(background_urls)
            
            # Download images
            for url in all_image_urls:
                download_file(session, url, main_folder, 'image')
                
            # Download PDFs
            for url in pdf_urls:
                download_file(session, url, pdf_folder, 'pdf')
                
        except Exception as e:
            print(f"❌ Failed to process page {current_url}: {e}")
            continue
        
        print(f"Processed {len(visited_pages)} pages. {len(pending_pages)} pages remaining in queue.")

    return main_folder


# MAIN

# website = "https://www.viterra.com"
website = input("\nEnter the website URL: ")

# vpn_connection = my_utils.connect_vpn()

# download CSS file
# Create output directory based on root domain
parsed_url = urlparse(website)
root_domain = parsed_url.netloc.replace('www.', '').split('.')[0]
output_dir = os.path.join('/Users/nic/demo', root_domain)
os.makedirs(output_dir, exist_ok=True)
print(f"\nCreated output directory: {output_dir}")

download_css_file(website, os.path.join(output_dir, "style.css"))

# if vpn_connection:
output_path = download_all_images(website, max_pages=3000)  
# else:
    # print("\n❌ Failed to connect to VPN")

delete_duplicate_images(output_path)


# my_utils.disconnect_vpn()





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