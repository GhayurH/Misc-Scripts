import os
import subprocess
import logging
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def download_gallery_with_gallery_dl(url, save_directory="images"):
    """
    Uses gallery-dl to download all images from a single gallery URL.

    :param url: A gallery URL.
    :param save_directory: The directory where images will be saved.
    :return: True if download was successful, otherwise False.
    """
    command = ["gallery-dl", "-d", save_directory, url]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        logging.info(f"Downloaded gallery from {url} to {save_directory}. Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to download gallery from {url}: {e}. Error Output: {e.stderr.strip()}")
        return False
    except FileNotFoundError:
        logging.error("Error: gallery-dl is not installed. Install it using 'pip install gallery-dl'.")
        return False

def download_gallery_task(index, total, url, save_directory):
    # Print progress message before starting the download
    logging.info(f"downloading {index} of {total}")
    return download_gallery_with_gallery_dl(url, save_directory)

def download_galleries_multithreaded(urls, save_directory="images", max_threads=4):
    """
    Downloads multiple galleries using multithreading.

    :param urls: A list of gallery URLs.
    :param save_directory: The directory where images will be saved.
    :param max_threads: The maximum number of threads to use.
    """
    os.makedirs(save_directory, exist_ok=True)
    total = len(urls)
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [executor.submit(download_gallery_task, i, total, url, save_directory)
                   for i, url in enumerate(urls, start=1)]
        for future in futures:
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error occurred during download: {e}")

if __name__ == "__main__":
    urls_input = input("Enter the gallery URLs (comma-separated): ")
    urls = [url.strip() for url in urls_input.split(',') if url.strip()]
    output_directory = input("Enter the directory to save images (default: 'images'): ") or "images"
    
    try:
        max_threads_input = input("Enter the number of threads to use (default: 4): ") or "4"
        max_threads = int(max_threads_input)
    except ValueError:
        logging.warning("Invalid input for number of threads. Defaulting to 4.")
        max_threads = 4

    download_galleries_multithreaded(urls, output_directory, max_threads)