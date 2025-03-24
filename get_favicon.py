import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import tldextract

def get_resource_urls(website_url):
    # Send a request to the website
    response = requests.get(website_url)
    if response.status_code != 200:
        return [], [], []

    # Parse the website content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Look for all icon link tags
    icon_links = soup.find_all("link", rel=lambda x: x and 'icon' in x.lower())
    
    # Look for all stylesheet link tags
    stylesheet_links = soup.find_all("link", rel=lambda x: x and 'stylesheet' in x.lower())

    # Look for font files in link and style tags
    font_links = []
    for link in soup.find_all("link", href=True):
        if any(ext in link['href'] for ext in ['.woff', '.woff2', '.ttf', '.otf']):
            font_links.append(link['href'])
    for style in soup.find_all("style"):
        for ext in ['.woff', '.woff2', '.ttf', '.otf']:
            if ext in style.string:
                font_links.append(style.string)

    # Convert relative URLs to absolute
    favicon_urls = [urljoin(website_url, link.get("href")) for link in icon_links]
    stylesheet_urls = [urljoin(website_url, link.get("href")) for link in stylesheet_links]
    font_urls = [urljoin(website_url, url) for url in font_links]

    # If no icons found, try the default /favicon.ico
    if not favicon_urls:
        default_favicon = urljoin(website_url, '/favicon.ico')
        favicon_urls.append(default_favicon)

    return favicon_urls, stylesheet_urls, font_urls

def download_favicon(favicon_url, website_url, output_dir='/Users/nic/Dropbox/Design/Favicons'):
    # Create directory if not exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Extract domain without TLD
    extracted = tldextract.extract(website_url)
    domain_without_tld = extracted.domain

    # Get the file extension from the favicon URL
    _, ext = os.path.splitext(urlparse(favicon_url).path)
    if not ext:
        ext = '.ico'  # Default to .ico if no extension is found

    # Create the new filename using the domain without TLD
    favicon_name = f"{domain_without_tld}{ext}"
    file_path = os.path.join(output_dir, favicon_name)

    # Check if file already exists
    if os.path.exists(file_path):
        print(f"⏭️  Favicon already exists: {file_path}")
        return True

    # Download the favicon
    response = requests.get(favicon_url, stream=True)
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"✅ Favicon saved at: {file_path}")
        return True
    else:
        print(f"❌ Failed to download favicon: {favicon_url}")
        return False

# Example usage
website_url = input("\nEnter the website URL: ")
favicon_urls, stylesheet_urls, font_urls = get_resource_urls(website_url)

if favicon_urls:
    print(f"\nFound {len(favicon_urls)} favicon variants:")
    for url in favicon_urls:
        print(f"- {url}")

if stylesheet_urls:
    print(f"\nFound {len(stylesheet_urls)} stylesheets:")
    for url in stylesheet_urls:
        print(f"- {url}")

if font_urls:
    print(f"\nFound {len(font_urls)} font files:")
    for url in font_urls:
        print(f"- {url}")

print("\nDownloading resources...")
for url in favicon_urls + stylesheet_urls + font_urls:
    download_favicon(url, website_url)
