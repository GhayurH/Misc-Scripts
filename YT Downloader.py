import os
from yt_dlp import YoutubeDL
import concurrent.futures
import logging

destination_folder = r'C:\a'
downloaded_videos_file = r'C:\Users\Ghayur Haider\Desktop\AZ\Git\Misc-Scripts\downloaded_videos.txt'
log_file = r'C:\a\download_log.txt'
skip_keywords = ["interview", "trailer", "promo", "teaser"]  # Keywords to skip downloads for

# Set up logging
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

# Function to load downloaded video URLs from a text file
def load_downloaded_videos():
    downloaded_videos = set()
    if os.path.exists(downloaded_videos_file):
        with open(downloaded_videos_file, 'r') as f:
            downloaded_videos.update(line.strip() for line in f)
    return downloaded_videos

# Function to save downloaded video URLs to a text file
def save_downloaded_videos(new_urls):
    with open(downloaded_videos_file, 'a') as f:  # Append mode to avoid overwriting
        for url in new_urls:
            f.write(f"{url}\n")

# Function to flatten info_dicts and extract video entries
def flatten_info_dict(info_dict):
    video_info_dicts = []
    if 'entries' in info_dict:
        for entry in info_dict['entries']:
            if entry is None:
                continue
            if 'entries' in entry:
                video_info_dicts.extend(flatten_info_dict(entry))
            else:
                video_info_dicts.append(entry)
    else:
        video_info_dicts.append(info_dict)
    return video_info_dicts

# Function to process and download a single video
def process_video_info(info_dict, downloaded_videos, new_downloaded_videos):
    url = info_dict.get('webpage_url')
    if not url:
        logging.error("No URL found in info_dict")
        return
    if url in downloaded_videos or url in new_downloaded_videos:
        logging.info(f"Already downloaded: {url}")
        return
    title = info_dict.get('title', '').lower()
    if any(keyword in title for keyword in skip_keywords):
        new_downloaded_videos.add(url)  # Add skipped URL for tracking
        logging.info(f"Skipping video: {url}")
        return
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [
                {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'},
                {'key': 'EmbedThumbnail'},
            ],
            'outtmpl': os.path.join(destination_folder, '%(title)s.%(ext)s'),
            'ignoreerrors': True,
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.process_ie_result(info_dict, download=True)
        new_downloaded_videos.add(url)  # Save downloaded URL to the set
        logging.info(f"Downloaded and converted: {url}")
    except Exception as e:
        logging.error(f"Error downloading {url}: {e}")

# Main function to handle concurrent downloads
def main(urls):
    downloaded_videos = load_downloaded_videos()
    new_downloaded_videos = set()
    video_info_dicts = []
    ydl_opts = {'ignoreerrors': True, 'extract_flat': False, 'skip_download': True}
    with YoutubeDL(ydl_opts) as ydl:
        for url in urls:
            try:
                info_dict = ydl.extract_info(url, download=False)
                if info_dict:
                    video_info_dicts.extend(flatten_info_dict(info_dict))
            except Exception as e:
                logging.error(f"Error extracting info from {url}: {e}")

    # Remove any None entries from video_info_dicts
    video_info_dicts = [info for info in video_info_dicts if info]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(process_video_info, info_dict, downloaded_videos, new_downloaded_videos)
            for info_dict in video_info_dicts
        ]
        concurrent.futures.wait(futures)
    save_downloaded_videos(new_downloaded_videos)
    logging.info("Finished processing all URLs.")

if __name__ == "__main__":
    # List of YouTube URLs (channels, playlists, or videos)
    urls = [
        "https://www.youtube.com/@SyedNadeemSarwar/videos",
        "https://www.youtube.com/@kazmibrothers1107/videos",
        "https://www.youtube.com/@MirHasanMir/videos",
        "https://www.youtube.com/@MAKOfficial/videos",
        "https://www.youtube.com/@ShadmanRazaofficial/videos",
        "https://www.youtube.com/@AmeerHasanAamir/videos",
        "https://www.youtube.com/@ShahidBaltistaniOfficial/videos",
        "https://www.youtube.com/@MesumAbbas/videos",
        "https://www.youtube.com/@syedrazaabbaszaidi/videos",
        "https://www.youtube.com/@AhmedRazaNasiriOfficial/videos",
        "https://www.youtube.com/@pentapure4356/videos",
        "https://www.youtube.com/@Azadar110/videos",
        "https://www.youtube.com/@chakwalpartyofficial/videos",
        "https://www.youtube.com/@hyderrizvi6524/videos",
        "https://www.youtube.com/@NazimPartyOfficial/videos",
        "https://www.youtube.com/@soazkhuwani6163/videos"
    ]

    # Start processing
    main(urls)

    print("Logs have been saved to", log_file)