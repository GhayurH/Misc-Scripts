import os
import sys
from yt_dlp import YoutubeDL
import concurrent.futures

destination_folder = os.path.join('./Audio', 'mp3')
downloaded_videos_file = os.path.join('./Audio', 'downloaded_videos.txt')
log_file = os.path.join('./Audio', 'download_log.txt')
skip_keywords = set(["interview", "trailer", "promo", "teaser"])  # Keywords to skip downloads for

def load_downloaded_videos():
    """
    Load downloaded video URLs from a text file into a set
    """
    downloaded_videos = set()
    if os.path.exists(downloaded_videos_file):
        with open(downloaded_videos_file, 'r') as f:
            downloaded_videos.update(line.strip() for line in f)
    return downloaded_videos

def save_downloaded_videos(new_downloaded_videos):
    """
    Save new downloaded video URLs to the text file
    """
    with open(downloaded_videos_file, 'a') as f:
        for url in new_downloaded_videos:
            f.write(f"{url}\n")

def get_video_info(url):
    """
    Extract video info from a YouTube URL using yt-dlp
    """
    try:
        with YoutubeDL({'skip_download': True}) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            return info_dict
    except Exception as e:
        print(f"Error getting video info: {e}")
        return None

def extract_video_urls(url):
    """
    Extract video URLs from a channel or playlist using yt-dlp
    """
    ydl_opts = {
        'extract_flat': True,
        'skip_download': True
    }
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        if 'entries' in info_dict:
            return [entry['url'] for entry in info_dict['entries']]
        else:
            return []

def is_video_skipped_or_downloaded(url, info_dict, downloaded_videos, new_downloaded_videos):
    """
    Check if a video has already been downloaded or should be skipped
    """
    if url in downloaded_videos or url in new_downloaded_videos:
        print(f"Already downloaded: {url}")
        return True
    else:
        title = info_dict.get('title', None)
        if title:
            for keyword in skip_keywords:
                if keyword in title.lower():
                    new_downloaded_videos.add(url)  # Add skipped URL for tracking
                    print(f"Skipping video: {url}")
                    return True
    return False

def download_and_convert(url, info_dict, downloaded_videos, new_downloaded_videos):
    """
    Download and convert a YouTube video using yt-dlp
    """
    if not is_video_skipped_or_downloaded(url, info_dict, downloaded_videos, new_downloaded_videos):
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }, {
                    'key': 'EmbedThumbnail',
                }],
                'outtmpl': os.path.join(destination_folder, '%(title)s.%(ext)s')
            }
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            new_downloaded_videos.add(url)  # Save downloaded URL to the set
            print(f"Downloaded and converted: {url}")
        except Exception as e:
            print(f"Error downloading {url}: {e}")

def main(urls):
    """
    Main function to handle concurrent downloads
    """
    downloaded_videos = load_downloaded_videos()
    new_downloaded_videos = set()
    video_info_dict = {}

    # Extract video info for all URLs
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_video_info, url) for url in urls]
        for future in concurrent.futures.as_completed(futures):
            url = futures[future]
            info_dict = future.result()
            if info_dict:
                video_info_dict[url] = info_dict

    # Download and convert videos
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(download_and_convert, url, info_dict, downloaded_videos, new_downloaded_videos) for url, info_dict in video_info_dict.items()]
        concurrent.futures.wait(futures)

    save_downloaded_videos(new_downloaded_videos)
    print("Finished processing all URLs.")

if __name__ == "__main__":
    # Redirect stdout and stderr to a log file
    with open(log_file, 'w') as f:
        sys.stdout = f
        sys.stderr = f
        
        # List of YouTube URLs (channels, playlists, or videos)
        urls = [
            "https://www.youtube.com/@SyedNadeem Sarwar/videos",
            "https://www.youtube.com/@kazmibrothers1107/videos",
            "https://www.youtube.com /watch?v=dQw4w9WgXcQ"
        ]
        
        main(urls)