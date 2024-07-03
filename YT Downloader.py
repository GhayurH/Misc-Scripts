import os
import sys
from yt_dlp import YoutubeDL
import concurrent.futures

destination_folder = r'C:\a'
downloaded_videos_file = r'C:\Users\Ghayur Haider\Desktop\AZ\Git\Misc-Scripts\downloaded_videos.txt'
log_file = r'C:\a\download_log.txt'
skip_keywords = ["interview", "trailer", "promo", "teaser"]  # Keywords to skip downloads for

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

# Function to extract the video title from a YouTube URL
def get_video_title(url):
    try:
        with YoutubeDL({'skip_download': True}) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            return info_dict.get('title', None)
    except Exception as e:
        print(f"Error getting video title: {e}")
        return None

# Function to extract video URLs from a channel or playlist using yt-dlp
def extract_video_urls(url):
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

# Function to check if a video has already been downloaded or should be skipped
def is_video_skipped_or_downloaded(url, downloaded_videos, new_downloaded_videos):
    if url in downloaded_videos or url in new_downloaded_videos:
        print(f"Already downloaded: {url}")
        return True
    else:
        filename = get_video_title(url)  # Extract filename
        if filename:
            for keyword in skip_keywords:
                if keyword in filename.lower():
                    new_downloaded_videos.add(url)  # Add skipped URL for tracking
                    print(f"Skipping video: {url}")
                    return True
    return False

# Function to download and convert a YouTube video using yt-dlp
def download_and_convert(url, downloaded_videos, new_downloaded_videos):
    # Extract video URLs if it's a channel or playlist
    if not url.startswith("https://www.youtube.com/watch?"):
        video_urls = extract_video_urls(url)
        for video_url in video_urls:
            download_and_convert(video_url, downloaded_videos, new_downloaded_videos)
    else:
        # Handle single video URL
        if not is_video_skipped_or_downloaded(url, downloaded_videos, new_downloaded_videos):
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

# Main function to handle concurrent downloads
def main(urls):
    downloaded_videos = load_downloaded_videos()
    new_downloaded_videos = set()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(download_and_convert, url, downloaded_videos, new_downloaded_videos) for url in urls]
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
        
        # Reset stdout and stderr to default
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        print("Logs have been saved to", log_file)