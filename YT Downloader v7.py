#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import json
import re
import shutil
from pathlib import Path
from yt_dlp import YoutubeDL


# Always load config.ini from the same folder as this script
SCRIPT_DIR = Path(__file__).resolve().parent
config_file = SCRIPT_DIR / 'config.ini'


def load_config():
    config = {}

    if config_file.exists():
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

    downloaded_videos_file = Path(downloaded_videos_file)

    if downloaded_videos_file.exists():
        with open(downloaded_videos_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    downloaded.add(line)

    return downloaded


def save_downloaded_videos(downloaded_videos_file, urls):
    if not urls:
        return

    downloaded_videos_file = Path(downloaded_videos_file)
    downloaded_videos_file.parent.mkdir(parents=True, exist_ok=True)

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


def build_common_ydl_opts(
    cookies_file=None,
    cookies_from_browser=None,
    js_runtime='deno',
    remote_components=None,
):
    """
    Shared yt-dlp options used for both extraction and downloading.
    """

    opts = {}

    if js_runtime and shutil.which(js_runtime):
        opts['js_runtimes'] = {js_runtime: {}}
        logging.info(f"Using JS runtime: {js_runtime}")
    elif js_runtime:
        logging.warning(f"JS runtime not found or not configured: {js_runtime}")

    if remote_components:
        opts['remote_components'] = [remote_components]
        logging.info(f"Using remote components: {remote_components}")

    if cookies_file and Path(cookies_file).exists():
        opts['cookiefile'] = str(cookies_file)
        logging.info(f"Using cookies file: {cookies_file}")
    elif cookies_from_browser:
        opts['cookiesfrombrowser'] = parse_cookies_from_browser(cookies_from_browser)
        logging.info(f"Using cookies from browser: {cookies_from_browser}")
    else:
        logging.warning("No cookies configured.")

    return opts


def get_playlist_or_channel_urls(url, common_ydl_opts):
    """
    Expands a channel/playlist URL into individual YouTube video URLs
    using yt-dlp's Python API instead of subprocess.
    """

    extract_opts = {
        **common_ydl_opts,
        'extract_flat': 'in_playlist',
        'skip_download': True,
        'quiet': True,
        'no_warnings': False,
        'ignoreerrors': True,
    }

    try:
        with YoutubeDL(extract_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        if not info:
            return []

        entries = info.get('entries')

        if not entries:
            video_id = info.get('id')

            if video_id:
                return [f"https://www.youtube.com/watch?v={video_id}"]

            return []

        video_urls = []

        for entry in entries:
            if not entry:
                continue

            video_id = entry.get('id')

            if video_id:
                video_urls.append(f"https://www.youtube.com/watch?v={video_id}")

        return video_urls

    except Exception as e:
        logging.error(f"Unexpected error fetching URLs from {url}: {e}")
        return []


def clean_title(title, remove_phrases):
    """
    Cleans the video title for filename use while preserving Arabic/Urdu.
    """

    for phrase in remove_phrases:
        title = re.sub(re.escape(phrase), ' ', title, flags=re.IGNORECASE)

    # Remove characters that are problematic in filenames
    title = re.sub(r'[\\/:*?"<>|]', ' ', title)

    # Normalize whitespace
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

    destination_folder = Path(destination_folder)

    if not destination_folder.exists():
        logging.warning(f"Destination folder does not exist: {destination_folder}")
        return

    for file_path in destination_folder.iterdir():
        if not file_path.is_file():
            continue

        if file_path.suffix.lower() != '.mp3':
            continue

        filename = file_path.name
        lower_name = filename.lower()

        if any(kw in lower_name for kw in skip_keywords):
            file_path.unlink()
            logging.info(f"Deleted file due to skip keyword: {filename}")
            continue

        base_title = file_path.stem
        new_name = clean_title(base_title, remove_phrases)
        new_path = destination_folder / new_name

        base_name = new_path.stem
        ext = new_path.suffix
        count = 1

        while new_path.exists() and new_path != file_path:
            new_path = destination_folder / f"{base_name} {count}{ext}"
            count += 1

        if new_path != file_path:
            file_path.rename(new_path)
            logging.info(f"Renamed {filename} to {new_path.name}")


def delete_leftover_thumbnails(destination_folder):
    """
    Deletes leftover thumbnail files created by yt-dlp after embedding.
    Since this is your raw download folder, all image thumbnails here are treated as disposable.
    """

    destination_folder = Path(destination_folder)

    thumbnail_extensions = {
        '.webp',
        '.jpg',
        '.jpeg',
        '.png',
    }

    for file_path in destination_folder.iterdir():
        if not file_path.is_file():
            continue

        if file_path.suffix.lower() in thumbnail_extensions:
            file_path.unlink()
            logging.info(f"Deleted leftover thumbnail file: {file_path.name}")


def main():
    config = load_config()

    destination_folder = Path(config.get(
        'destination_folder',
        str(SCRIPT_DIR / 'a')
    )).expanduser()

    downloaded_videos_file = Path(config.get(
        'downloaded_videos_file',
        str(SCRIPT_DIR / 'downloaded_videos.txt')
    )).expanduser()

    log_file = Path(config.get(
        'log_file',
        str(SCRIPT_DIR / 'download_log.txt')
    )).expanduser()

    cookies_file = config.get('cookies_file', None)
    cookies_from_browser = config.get('cookies_from_browser', None)
    js_runtime = config.get('js_runtime', 'deno')
    remote_components = config.get('remote_components', None)

    destination_folder.mkdir(parents=True, exist_ok=True)
    downloaded_videos_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.parent.mkdir(parents=True, exist_ok=True)

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

    common_ydl_opts = build_common_ydl_opts(
        cookies_file=cookies_file,
        cookies_from_browser=cookies_from_browser,
        js_runtime=js_runtime,
        remote_components=remote_components,
    )

    all_video_urls = []

    for u in urls:
        logging.info(f"Expanding URL: {u}")

        expanded = get_playlist_or_channel_urls(
            u,
            common_ydl_opts=common_ydl_opts
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
        **common_ydl_opts,

        'format': 'bestaudio/best',
        'outtmpl': str(destination_folder / '%(title)s [%(id)s].%(ext)s'),
        'ignoreerrors': False,
        'noplaylist': True,

        # Filename handling
        'restrictfilenames': False,
        'windowsfilenames': True,

        # Thumbnail + metadata
        'writethumbnail': True,
        'embedmetadata': True,

        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            },
            {
                'key': 'FFmpegMetadata',
                'add_metadata': True,
            },
            {
                'key': 'EmbedThumbnail',
                'already_have_thumbnail': False,
            },
        ],
    }

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

    delete_leftover_thumbnails(destination_folder)

    logging.info(f"Newly downloaded videos: {len(newly_downloaded)}")
    logging.info("All processing finished.")

    print(f"Done. Downloaded {len(newly_downloaded)} new files.")
    print(f"Destination: {destination_folder}")
    print(f"Downloaded list: {downloaded_videos_file}")
    print(f"Log file: {log_file}")


if __name__ == "__main__":
    main()