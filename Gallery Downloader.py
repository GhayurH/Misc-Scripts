import os
import subprocess
from concurrent.futures import ThreadPoolExecutor

def download_gallery_with_gallery_dl(url, save_directory="images"):
    """
    Uses gallery-dl to download all images from a single gallery URL.

    :param url: A gallery URL.
    :param save_directory: The directory where images will be saved.
    """
    try:
        # Run the gallery-dl command for the URL
        command = ["gallery-dl", "-d", save_directory, url]
        subprocess.run(command, check=True)
        print(f"Gallery downloaded successfully from {url} to {save_directory}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to download gallery from {url}: {e}")
    except FileNotFoundError:
        print("Error: gallery-dl is not installed. Install it using 'pip install gallery-dl'.")

def download_galleries_multithreaded(urls, save_directory="images", max_threads=4):
    """
    Downloads multiple galleries using multithreading.

    :param urls: A list of gallery URLs.
    :param save_directory: The directory where images will be saved.
    :param max_threads: The maximum number of threads to use.
    """
    # Ensure the save directory exists
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    with ThreadPoolExecutor(max_threads) as executor:
        futures = [executor.submit(download_gallery_with_gallery_dl, url, save_directory) for url in urls]
        for future in futures:
            try:
                future.result()  # Wait for thread to complete
            except Exception as e:
                print(f"Error occurred during download: {e}")

if __name__ == "__main__":
    # Example usage
    urls = input("Enter the gallery URLs (comma-separated): ").split(',')
    urls = [url.strip() for url in urls if url.strip()]
    output_directory = input("Enter the directory to save images (default: 'images'): ") or "images"
    max_threads = int(input("Enter the number of threads to use (default: 4): ") or 4)
    download_galleries_multithreaded(urls, output_directory, max_threads)
