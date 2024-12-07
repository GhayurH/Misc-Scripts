import os
import logging
import subprocess
import json
import re
from yt_dlp import YoutubeDL

# Configuration file (optional)
config_file = 'config.ini'

def load_config():
    config = {}
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    config[key.strip()] = value.strip()
    return config

def load_downloaded_videos(downloaded_videos_file):
    downloaded = set()
    if os.path.exists(downloaded_videos_file):
        with open(downloaded_videos_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    downloaded.add(line)
    return downloaded

def save_downloaded_videos(downloaded_videos_file, urls):
    if not urls:
        return
    with open(downloaded_videos_file, 'a') as f:
        for url in urls:
            f.write(url + '\n')

def get_playlist_or_channel_urls(url, cookies_file=None):
    # Runs yt-dlp to get a flat list of video IDs if this is a channel/playlist
    command = [
        'yt-dlp',
        '--flat-playlist',
        '--dump-json'
    ]
    if cookies_file and os.path.exists(cookies_file):
        command += ['--cookies', cookies_file]

    command.append(url)

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        videos = [json.loads(line) for line in result.stdout.splitlines() if line.strip()]
        video_urls = [f"https://www.youtube.com/watch?v={video['id']}" for video in videos if 'id' in video]
        return video_urls
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running yt-dlp on {url}: {e.stderr.strip()}")
    except Exception as e:
        logging.error(f"Unexpected error fetching URLs from {url}: {e}")
    return []

def clean_title(title, remove_phrases):
    """
    Cleans the video title by removing unwanted phrases and characters,
    preserving original case where possible, and then prepares it for use
    as a filename (with .mp3 extension).
    """
    # Remove phrases in a case-insensitive manner:
    for phrase in remove_phrases:
        title = re.sub(re.escape(phrase), ' ', title, flags=re.IGNORECASE)

    # Normalize spaces and remove non-allowed characters, but do not force lowercasing
    title = re.sub(r'\s+', ' ', title).strip()
    title = re.sub(r'[^a-zA-Z0-9_\- ]', ' ', title)
    title = re.sub(r'\s+', ' ', title).strip()

    return title + '.mp3'

def download_video(url, ydl_opts):
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        logging.info(f"Downloaded successfully: {url}")
        return True
    except Exception as e:
        logging.error(f"Error downloading {url}: {e}")
        return False

def main():
    config = load_config()

    destination_folder = config.get('destination_folder', r'C:\a')
    downloaded_videos_file = config.get('downloaded_videos_file', r'C:\Users\YourName\Desktop\downloaded_videos.txt')
    log_file = config.get('log_file', r'C:\a\download_log.txt')
    cookies_file = config.get('cookies_file', None)

    # Parse skip_keywords and remove_phrases from config
    skip_keywords = [kw.strip().lower() for kw in config.get('skip_keywords', "interview,trailer,promo,teaser").split(',') if kw.strip()]
    remove_phrases = [ph.strip() for ph in config.get('remove_phrases', '(as),(sa),(A S ),a s,(a.s),(a.s.), س ,ﷺ, ص ,(ص),(),s a w w,new,NEW').split(',') if ph.strip()]

    # Set up logging
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

    # Initial list of URLs (replace with your actual URLs)
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
        "https://www.youtube.com/@soazkhuwani6163/videos",
    ]

    # Expand mixed URLs into a list of only video URLs
    all_video_urls = []
    for u in urls:
        expanded = get_playlist_or_channel_urls(u, cookies_file)
        if expanded:
            all_video_urls.extend(expanded)
        else:
            # If not expanded, assume it's already a direct video URL
            all_video_urls.append(u)

    # Remove duplicates
    all_video_urls = list(set(all_video_urls))

    # Load previously downloaded
    downloaded_videos = load_downloaded_videos(downloaded_videos_file)

    # Filter out URLs already downloaded
    filtered_urls = [url for url in all_video_urls if url not in downloaded_videos]

    # Set yt-dlp options for best audio as mp3
    ydl_opts = {
        'format': 'bestaudio',
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            },
            {
                'key': 'EmbedThumbnail'
            }
        ],
        'outtmpl': os.path.join(destination_folder, '%(title)s.%(ext)s'),
        'ignoreerrors': True
    }

    if cookies_file and os.path.exists(cookies_file):
        ydl_opts['cookiefile'] = cookies_file

    # Download each video
    newly_downloaded = []
    for url in filtered_urls:
        success = download_video(url, ydl_opts)
        if success:
            newly_downloaded.append(url)

    # Save the newly downloaded URLs
    save_downloaded_videos(downloaded_videos_file, newly_downloaded)

    # After all downloads, process files:
    # 1. Delete files containing skip_keywords
    # 2. Rename remaining files using clean_title logic
    for filename in os.listdir(destination_folder):
        full_path = os.path.join(destination_folder, filename)
        if not os.path.isfile(full_path):
            continue

        # Check if file is mp3
        if not filename.lower().endswith('.mp3'):
            continue

        # Check if any skip keyword is in the filename (case-insensitive check)
        lower_name = filename.lower()
        if any(kw in lower_name for kw in skip_keywords):
            # Delete file
            os.remove(full_path)
            logging.info(f"Deleted file due to skip keyword: {filename}")
        else:
            # Rename file using clean_title
            base_title, _ = os.path.splitext(filename)
            new_name = clean_title(base_title, remove_phrases)

            # If a file with the cleaned name already exists, append an index
            base_name, ext = os.path.splitext(new_name)
            count = 1
            while os.path.exists(os.path.join(destination_folder, new_name)):
                new_name = f"{base_name}{count}{ext}"
                count += 1

            new_full_path = os.path.join(destination_folder, new_name)

            if new_full_path != full_path:
                os.rename(full_path, new_full_path)
                logging.info(f"Renamed {filename} to {new_name}")

    logging.info("All processing finished.")

if __name__ == "__main__":
    main()
    print("Logs have been saved.")
