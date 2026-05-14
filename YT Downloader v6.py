#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import subprocess
import json
import re
import shutil
from yt_dlp import YoutubeDL


# Configuration file
config_file = 'config.ini'


def load_config():
    config = {}

    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()

                if not line or line.startswith('#'):
                    continue

                if '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()

    return config


def load_downloaded_videos(downloaded_videos_file):
    downloaded = set()

    if os.path.exists(downloaded_videos_file):
        with open(downloaded_videos_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    downloaded.add(line)

    return downloaded


def save_downloaded_videos(downloaded_videos_file, urls):
    if not urls:
        return

    with open(downloaded_videos_file, 'a', encoding='utf-8') as f:
        for url in urls:
            f.write(url + '\n')


def parse_cookies_from_browser(value):
    """
    Supports:
      firefox
      firefox:/path/to/profile

    Returns yt-dlp compatible tuple:
      (browser, profile, keyring, container)
    """

    if not value:
        return None

    if ':' in value:
        browser, profile = value.split(':', 1)
        return (browser, profile, None, None)

    return (value, None, None, None)


def get_playlist_or_channel_urls(
    url,
    cookies_file=None,
    cookies_from_browser=None,
    js_runtime='deno',
    remote_components=None
):
    """
    Expands a channel/playlist URL into individual YouTube video URLs.
    If expansion fails, caller can treat original URL as direct video URL.
    """

    command = [
        'yt-dlp',
        '--flat-playlist',
        '--dump-json',
    ]

    if js_runtime and shutil.which(js_runtime):
        command += ['--js-runtimes', js_runtime]

    if remote_components:
        command += ['--remote-components', remote_components]

    if cookies_file and os.path.exists(cookies_file):
        command += ['--cookies', cookies_file]
    elif cookies_from_browser:
        command += ['--cookies-from-browser', cookies_from_browser]

    command.append(url)

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )

        videos = [
            json.loads(line)
            for line in result.stdout.splitlines()
            if line.strip()
        ]

        video_urls = [
            f"https://www.youtube.com/watch?v={video['id']}"
            for video in videos
            if video.get('id')
        ]

        return video_urls

    except subprocess.CalledProcessError as e:
        logging.error(f"Error expanding URL with yt-dlp: {url}")
        logging.error(e.stderr.strip())

    except Exception as e:
        logging.error(f"Unexpected error fetching URLs from {url}: {e}")

    return []


def clean_title(title, remove_phrases):
    """
    Cleans the video title for filename use.
    """

    for phrase in remove_phrases:
        title = re.sub(re.escape(phrase), ' ', title, flags=re.IGNORECASE)

    title = re.sub(r'\s+', ' ', title).strip()

    # Keeps English letters, numbers, underscores, hyphens, and spaces.
    # This strips Arabic/Urdu from filenames. Change this regex if you want to preserve them.
    title = re.sub(r'[^a-zA-Z0-9_\- ]', ' ', title)

    title = re.sub(r'\s+', ' ', title).strip()

    if not title:
        title = 'untitled'

    return title + '.mp3'


def download_video(url, ydl_opts):
    try:
        with YoutubeDL(ydl_opts) as ydl:
            result = ydl.download([url])

        if result == 0:
            logging.info(f"Downloaded successfully: {url}")
            return True

        logging.error(f"yt-dlp returned non-zero result for {url}: {result}")
        return False

    except Exception as e:
        logging.error(f"Error downloading {url}: {e}")
        return False


def process_downloaded_files(destination_folder, skip_keywords, remove_phrases):
    """
    Deletes unwanted MP3s and renames remaining MP3s.
    """

    if not os.path.exists(destination_folder):
        logging.warning(f"Destination folder does not exist: {destination_folder}")
        return

    for filename in os.listdir(destination_folder):
        full_path = os.path.join(destination_folder, filename)

        if not os.path.isfile(full_path):
            continue

        if not filename.lower().endswith('.mp3'):
            continue

        lower_name = filename.lower()

        if any(kw in lower_name for kw in skip_keywords):
            os.remove(full_path)
            logging.info(f"Deleted file due to skip keyword: {filename}")
            continue

        base_title, _ = os.path.splitext(filename)
        new_name = clean_title(base_title, remove_phrases)

        base_name, ext = os.path.splitext(new_name)
        count = 1

        while os.path.exists(os.path.join(destination_folder, new_name)):
            new_name = f"{base_name} {count}{ext}"
            count += 1

        new_full_path = os.path.join(destination_folder, new_name)

        if new_full_path != full_path:
            os.rename(full_path, new_full_path)
            logging.info(f"Renamed {filename} to {new_name}")


def main():
    config = load_config()

    destination_folder = config.get(
        'destination_folder',
        '/home/ghayur/Desktop/AZ/Git/Misc-Scripts/a'
    )

    downloaded_videos_file = config.get(
        'downloaded_videos_file',
        '/home/ghayur/Desktop/AZ/Git/Misc-Scripts/downloaded_videos.txt'
    )

    log_file = config.get(
        'log_file',
        '/home/ghayur/Desktop/AZ/Git/Misc-Scripts/download_log.txt'
    )

    cookies_file = config.get('cookies_file', None)
    cookies_from_browser = config.get('cookies_from_browser', None)
    js_runtime = config.get('js_runtime', 'deno')
    remote_components = config.get('remote_components', None)

    os.makedirs(destination_folder, exist_ok=True)
    os.makedirs(os.path.dirname(downloaded_videos_file), exist_ok=True)
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s:%(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    logging.info("Script started.")

    skip_keywords = [
        kw.strip().lower()
        for kw in config.get(
            'skip_keywords',
            'interview,trailer,promo,teaser'
        ).split(',')
        if kw.strip()
    ]

    remove_phrases = [
        ph.strip()
        for ph in config.get(
            'remove_phrases',
            '(as),(sa),(A S ),a s,(a.s),(a.s.), س ,ﷺ, ص ,(ص),(),s a w w,new,NEW'
        ).split(',')
        if ph.strip()
    ]

    urls = [
        "https://www.youtube.com/@SyedNadeemSarwar/videos",
        "https://www.youtube.com/@kazmibrothers1107/videos",
        "https://www.youtube.com/@MirHasanMir/videos",
        "https://www.youtube.com/@MAKOfficial/videos",
        "https://www.youtube.com/@ShadmanRazaofficial/videos",
        # "https://www.youtube.com/@AmeerHasanAamir/videos",
        "https://www.youtube.com/@ShahidBaltistaniOfficial/videos",
        # "https://www.youtube.com/@MesumAbbas/videos",
        "https://www.youtube.com/@syedrazaabbaszaidi/videos",
        "https://www.youtube.com/@AhmedRazaNasiriOfficial/videos",
        "https://www.youtube.com/@pentapure4356/videos",
        "https://www.youtube.com/@Azadar110/videos",
        # "https://www.youtube.com/@chakwalpartyofficial/videos",
        "https://www.youtube.com/@hyderrizvi6524/videos",
        "https://www.youtube.com/@NazimPartyOfficial/videos",
        # "https://www.youtube.com/@soazkhuwani6163/videos",
    ]

    all_video_urls = []

    for u in urls:
        logging.info(f"Expanding URL: {u}")

        expanded = get_playlist_or_channel_urls(
            u,
            cookies_file=cookies_file,
            cookies_from_browser=cookies_from_browser,
            js_runtime=js_runtime,
            remote_components=remote_components
        )

        if expanded:
            all_video_urls.extend(expanded)
            logging.info(f"Expanded {u} into {len(expanded)} video URLs.")
        else:
            all_video_urls.append(u)
            logging.warning(f"Could not expand URL; treating as direct video URL: {u}")

    # Remove duplicates while preserving order
    all_video_urls = list(dict.fromkeys(all_video_urls))

    logging.info(f"Total unique URLs found: {len(all_video_urls)}")

    downloaded_videos = load_downloaded_videos(downloaded_videos_file)

    filtered_urls = [
        url
        for url in all_video_urls
        if url not in downloaded_videos
    ]

    logging.info(f"URLs left after filtering already-downloaded videos: {len(filtered_urls)}")

    ydl_opts = {
        'format': 'bestaudio/best',
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
        'outtmpl': os.path.join(destination_folder, '%(title)s [%(id)s].%(ext)s'),
        'ignoreerrors': False,
        'noplaylist': True,
    }

    if js_runtime and shutil.which(js_runtime):
        ydl_opts['js_runtimes'] = {js_runtime: {}}
        logging.info(f"Using JS runtime: {js_runtime}")
    else:
        logging.warning(f"JS runtime not found or not configured: {js_runtime}")

    if remote_components:
        ydl_opts['remote_components'] = [remote_components]
        logging.info(f"Using remote components: {remote_components}")

    if cookies_file and os.path.exists(cookies_file):
        ydl_opts['cookiefile'] = cookies_file
        logging.info(f"Using cookies file: {cookies_file}")
    elif cookies_from_browser:
        ydl_opts['cookiesfrombrowser'] = parse_cookies_from_browser(cookies_from_browser)
        logging.info(f"Using cookies from browser: {cookies_from_browser}")
    else:
        logging.warning("No cookies configured.")

    newly_downloaded = []

    total = len(filtered_urls)

    for index, url in enumerate(filtered_urls, start=1):
        logging.info(f"Downloading {index}/{total}: {url}")
        success = download_video(url, ydl_opts)

        if success:
            newly_downloaded.append(url)

    save_downloaded_videos(downloaded_videos_file, newly_downloaded)

    process_downloaded_files(
        destination_folder,
        skip_keywords,
        remove_phrases
    )

    logging.info(f"Newly downloaded videos: {len(newly_downloaded)}")
    logging.info("All processing finished.")


if __name__ == "__main__":
    main()
    print("Logs have been saved.")