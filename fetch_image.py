import requests
import os
import hashlib
from urllib.parse import urlparse
import uuid

def get_filename_from_url(url: str) -> str:
    """Extract filename from URL or generate one if missing."""
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    if not filename:
        filename = f"image_{uuid.uuid4().hex}.jpg"
    return filename

def file_already_exists(content: bytes, save_dir: str) -> bool:
    """Check if an identical file already exists in the directory."""
    # Compute hash of the downloaded content
    new_file_hash = hashlib.md5(content).hexdigest()
    
    for existing_file in os.listdir(save_dir):
        existing_path = os.path.join(save_dir, existing_file)
        if os.path.isfile(existing_path):
            with open(existing_path, "rb") as f:
                existing_hash = hashlib.md5(f.read()).hexdigest()
                if existing_hash == new_file_hash:
                    return True
    return False

def fetch_image(url: str, save_dir: str = "Fetched_Images"):
    """Download a single image with precautions and error handling."""
    try:
        os.makedirs(save_dir, exist_ok=True)

        # Fetch with headers for better community respect
        headers = {"User-Agent": "UbuntuImageFetcher/1.0"}
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()

        # Check content type before saving
        content_type = response.headers.get("Content-Type", "")
        if not content_type.startswith("image/"):
            print(f"✗ Skipped {url} (not an image, got {content_type})")
            return

        # Avoid duplicate downloads
        if file_already_exists(response.content, save_dir):
            print(f"⚠ Duplicate detected. Skipped: {url}")
            return

        # Extract/generate filename
        filename = get_filename_from_url(url)
        filepath = os.path.join(save_dir, filename)

        # Save image
        with open(filepath, "wb") as f:
            f.write(response.content)

        print(f"✓ Successfully fetched: {filename}")
        print(f"✓ Saved to {filepath}")

    except requests.exceptions.RequestException as e:
        print(f"✗ Network issue with {url}: {e}")
    except Exception as e:
        print(f"✗ Error while handling {url}: {e}")

def main():
    print("🌍 Welcome to the Ubuntu Image Fetcher")
    print("A tool for mindfully collecting images from the web.\n")

    # Accept multiple URLs (space-separated or comma-separated)
    urls = input("Enter one or more image URLs (separated by spaces or commas): ").replace(",", " ").split()

    for url in urls:
        fetch_image(url.strip())

    print("\n✨ Task completed. Images organized in 'Fetched_Images'.")

if __name__ == "__main__":
    main()
