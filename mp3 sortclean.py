import os
from pydub.utils import mediainfo

def delete_mp3_files(directory, min_length=None, max_length=None, delete_contains=None):
    deleted_files = []

    # Traverse through the directory
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".mp3"):
                file_path = os.path.join(root, file)
                try:
                    # Get duration of the mp3 file
                    duration_info = mediainfo(file_path)['duration']
                    length_ms = int(float(duration_info) * 1000)
                    
                    # Check if the file meets deletion criteria
                    if (min_length is not None and length_ms < min_length) or \
                       (max_length is not None and length_ms > max_length) or \
                       (delete_contains and any(substring.lower() in file.lower() for substring in delete_contains)):
                        
                        # Delete the file
                        os.remove(file_path)
                        deleted_files.append((file, length_ms))
                except Exception as e:
                    print(f"Error reading {file}: {e}")

    return deleted_files

def main():
    directory = r'C:\a\b'
    min_length = int(60000)
    max_length = int(3600000)
    delete_contains_str = "promo, trailer, interview"
    delete_contains = [substring.strip() for substring in delete_contains_str.split(",")] if delete_contains_str else None

    deleted_files = delete_mp3_files(directory, min_length=min_length, max_length=max_length, delete_contains=delete_contains)

    if deleted_files:
        with open("deleted_files.txt", "w", encoding="utf-8") as f:  # Specify encoding
            for file, length in deleted_files:
                f.write(f"{file}: {length} ms\n")
        print("Deletion complete. Deleted files logged in deleted_files.txt")
    else:
        print("No files deleted.")

if __name__ == "__main__":
    main()