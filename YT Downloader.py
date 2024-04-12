import os
import subprocess
import re
from yt_dlp import YoutubeDL

destination_folder = "c:/a"
downloaded_videos_file = r'C:\Users\Ghayur Haider\Desktop\AZ\Git\Slides-Lyrics-Salah_times\Misc. Scripts\downloaded_videos.txt'
skip_keywords = ["interview", "trailer", "promo", "teaser"]  # Keywords to skip downloads for

# Function to load downloaded video URLs from a text file
def load_downloaded_videos():
    downloaded_videos = set()
    if os.path.exists(downloaded_videos_file):
        with open(downloaded_videos_file, 'r') as f:
            for line in f:
                downloaded_videos.add(line.strip())  # Remove trailing newline
    return downloaded_videos

# Function to save downloaded video URLs to a text file
def save_downloaded_videos(urls):
    with open(downloaded_videos_file, 'a') as f:  # Append mode to avoid overwriting
        for url in urls:
            f.write(f"{url}\n")

# Function to extract the video title from a YouTube URL
def get_video_title(url):
  try:
    with YoutubeDL({'skip_download': True}) as ydl:
      info_dict = ydl.extract_info(url, download=False)
      video_title = info_dict.get('title', None)
      return video_title
  except Exception as e:
    print(f"Error getting video title: {e}")
    return None

# Function to extract video URLs from a channel or playlist using yt-dlp
def extract_video_urls(url):
    command = ['yt-dlp', '--skip-download', url]
    result = subprocess.run(command, capture_output=True, text=True)  # Capture output as text
    if result.returncode == 0:
       count = 0
       for line in result.stdout.splitlines():
            if re.search(r"(?:Extracting URL)", line, re.IGNORECASE):
                # Extract the url using regular expression
                match = re.search(r"https?://www\.youtube\.com/watch\?v=([^&]+)", line)
                if match:
                    count = count + 1
                    print(f"######--  {count}  --######")
                    print(f"######--  {count}  --######")
                    # Append the extracted url to the list
                    a = 'https://www.youtube.com/watch?v='+match.group(1)
                    download_and_convert(a)
    else:
        print(f"Error extracting video URLs from {url}")
        return []

# Function to check if a video has already been downloaded or should be skipped
def is_video_skipped_or_downloaded(url):
    downloaded_videos = load_downloaded_videos()
    if url in downloaded_videos:
        print(f"Already downloaded: {url}")
        return True
    else:
        filename = get_video_title(url)  # Extract filename
        for keyword in skip_keywords:
            if keyword in filename.lower():
                save_downloaded_videos([url])  # Add skipped URL for tracking
                print(f"Skipping video: {url}")
                return True

# Function to download and convert a YouTube video using yt-dlp
def download_and_convert(url):
    # Extract video URLs if it's a channel or playlist
    if not url.startswith("https://www.youtube.com/watch?"):
        extract_video_urls(url)
    else:
        # Handle single video URL
        if not is_video_skipped_or_downloaded(url):
            try:
                command = ['yt-dlp', '-f', 'bestaudio/best', '--extract-audio', '--audio-format', 'mp3', '--audio-quality', '192', '--embed-thumbnail', '-o', os.path.join(destination_folder, '%(title)s.%(ext)s'), url]
                subprocess.run(command)  # Execute yt-dlp command
                save_downloaded_videos([url])  # Save downloaded URL to the file
                print(f"Downloaded and converted: {url}")
            except Exception as e:
                print(f"Error downloading {url}: {e}")

# List of YouTube URLs (channels, playlists, or videos)
urls = [
    # "https://www.youtube.com/c/SyedNadeemSarwar/",
    # "https://www.youtube.com/channel/UCaM-L3ytlAtk5_Wg3HIUvIw", # Kazmi Brothers
    # "https://www.youtube.com/channel/UC_qRtpijKZ-iipmWYCndLrA", # Mir Hasan
    # "https://www.youtube.com/c/MAKOfficial",
    # "https://www.youtube.com/c/ShadmanRazaNaqviOfficial", 
    # "https://www.youtube.com/c/AmeerHasanAamir",
    # "https://www.youtube.com/c/ShahidBaltistaniOfficial",
    # "https://www.youtube.com/c/MesumAbbasOfficial",
    # "https://www.youtube.com/c/syedrazaabbaszaidi/",
    # "https://www.youtube.com/c/AhmedRazaNasiriOfficial",
    # "https://www.youtube.com/@pentapure4356/",
    # "https://www.youtube.com/@Azadar110",
    "https://www.youtube.com/@chakwalpartyofficial1702",
    "https://www.youtube.com/@hyderrizvi6524",
    "https://www.youtube.com/@NazimPartyOfficial",
    "https://www.youtube.com/@soazkhuwani6163"
]

# Download and convert each URL (handling channels and playlists)
for url in urls:
    download_and_convert(url)

print("Finished processing all URLs.")