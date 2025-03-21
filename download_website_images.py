import os
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

def download_image(session, url, folder):
    try:
        # Check image dimensions first
        response = session.get(url, stream=True)
        response.raise_for_status()
        
        # Get image dimensions using PIL
        img = Image.open(BytesIO(response.content))
        width, height = img.size
        
        # Skip if image is too small
        if width < 500 and height < 500:
            print(f"Skipping {url}: Image too small ({width}x{height})")
            return

        # Get original filename
        filename = os.path.basename(urlparse(url).path)
        if not filename:
            filename = "image"
            
        # Add width to filename
        name, ext = os.path.splitext(filename)
        filename = f"{width}_{name}{ext}"
        
        filepath = os.path.join(folder, filename)
        count = 1
        original_filepath = filepath
        while os.path.exists(filepath):
            name, ext = os.path.splitext(original_filepath)
            filepath = f"{name}_{count}{ext}"
            count += 1
        
        # Save the image we already loaded
        img.save(filepath)
        print(f"Downloaded: {filepath} ({width}x{height})")
    except Exception as e:
        print(f"Failed to download {url}: {e}")

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
        print(f"Failed to get links from {url}: {e}")
        return set()

def download_all_images(website_url, max_pages=100):
    # Extract the root domain without the TLD
    parsed_url = urlparse(website_url)
    domain_parts = parsed_url.netloc.split('.')
    if len(domain_parts) > 1:
        slug = domain_parts[-2]  # Get the part before the TLD
    else:
        slug = domain_parts[0]  # Fallback if there's only one part
    
    folder = f"/Users/nic/Downloads/temp/downloaded_images/{slug}/"
    os.makedirs(folder, exist_ok=True)
    session = requests.Session()
    base_domain = get_domain(website_url)
    
    # Track visited and pending pages
    visited_pages = set()
    pending_pages = {website_url}
    
    while pending_pages and len(visited_pages) < max_pages:
        current_url = pending_pages.pop()
        
        if current_url in visited_pages:
            continue
            
        print(f"\nProcessing page: {current_url}")
        visited_pages.add(current_url)
        
        # Get all links from the current page
        new_links = get_all_links(session, current_url, base_domain)
        pending_pages.update(new_links - visited_pages)
        
        try:
            # Download images from the current page
            response = session.get(current_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            img_tags = soup.find_all('img')
            
            img_urls = set()
            for img in img_tags:
                img_url = img.attrs.get('src') or img.attrs.get('data-src')
                if img_url:
                    full_url = urljoin(current_url, img_url)
                    img_urls.add(full_url)
            
            for url in img_urls:
                download_image(session, url, folder)
                
        except Exception as e:
            print(f"Failed to process page {current_url}: {e}")
            continue
        
        print(f"Processed {len(visited_pages)} pages. {len(pending_pages)} pages remaining in queue.")

# Example usage
website = "https://www.fnacdarty.com/"
download_all_images(website, max_pages=50)  # Limit to 50 pages by default