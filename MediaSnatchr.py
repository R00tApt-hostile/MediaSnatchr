import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import tqdm  # For progress bar

def download_file(url, folder):
    """Download a file from a URL and save it to the specified folder."""
    try:
        media_response = requests.get(url, stream=True)
        media_response.raise_for_status()  # Raise an error for bad responses

        # Get the media file name
        media_name = os.path.join(folder, url.split('/')[-1])

        # Handle file name conflicts
        base, extension = os.path.splitext(media_name)
        counter = 1
        while os.path.exists(media_name):
            media_name = f"{base}_{counter}{extension}"
            counter += 1

        # Save the media file with a progress bar
        with open(media_name, 'wb') as media_file:
            total_size = int(media_response.headers.get('content-length', 0))
            with tqdm(total=total_size, unit='B', unit_scale=True, desc=media_name) as pbar:
                for data in media_response.iter_content(chunk_size=1024):
                    media_file.write(data)
                    pbar.update(len(data))

        print(f"Downloaded: {media_name}")

    except Exception as e:
        print(f"Failed to download {url}: {e}")

def download_media(url, folder):
    """Download all media from the specified website."""
    # Create a folder to save media
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Send a GET request to the URL
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage: {url}")
        return

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all image, video, audio, and source tags
    media_tags = soup.find_all(['img', 'video', 'audio', 'source'])

    for tag in media_tags:
        media_url = None
        if tag.name == 'img':
            media_url = tag.get('src') or tag.get('data-src')  # Check for lazy-loaded images
        elif tag.name in ['video', 'audio']:
            media_url = tag.get('src')
        elif tag.name == 'source':
            media_url = tag.get('src')

        if media_url:
            # Resolve relative URLs
            media_url = urljoin(url, media_url)
            download_file(media_url, folder)

if __name__ == "__main__":
    website_url = input("Enter the website URL: ")
    download_folder = input("Enter the folder name to save media: ")
    download_media(website_url, download_folder)
