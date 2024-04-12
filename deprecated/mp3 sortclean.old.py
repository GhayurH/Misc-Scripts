import os
from collections import defaultdict
from pydub.utils import mediainfo

def delete_mp3_files(directory, min_length=None, max_length=None, delete_contains=None):#, output_path=None):
    deleted_files = []
    file_dict = defaultdict(list)

    # Collect files and their durations
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".mp3"):
                file_path = os.path.join(root, file)
                try:
                    duration_info = mediainfo(file_path)['duration']
                    length_ms = int(float(duration_info) * 1000)
                    file_dict[file.split('.')[1].strip() if '.' in file else file].append((file_path, length_ms))
                except Exception as e:
                    print(f"Error reading {file}: {e}")

    # Delete files containing any of the specified strings in their names
    if delete_contains:
        for name, files in file_dict.items():
            for substring in delete_contains:
                if substring in name:
                    for file_path, _ in files:
                        os.remove(file_path)
                        deleted_files.append((os.path.basename(file_path), f"Contains '{substring}'"))

    # Delete all but one file with the same name
    for name, files in file_dict.items():
        if len(files) > 1:
            sorted_files = sorted(files, key=lambda x: x[1])  # Sort by duration
            for file_path, _ in sorted_files[1:]:
                os.remove(file_path)
                deleted_files.append((os.path.basename(file_path), "Duplicate name"))

    # Delete files based on length criteria
    for files in file_dict.values():
        for file_path, length_ms in files:
            if (min_length is not None and length_ms < min_length) or \
               (max_length is not None and length_ms > max_length):
                os.remove(file_path)
                deleted_files.append((os.path.basename(file_path), length_ms))

    # # Save deleted files info to a text file
    # if output_path:
    #     with open(output_path, "w") as f:
    #         for file_info in deleted_files:
    #             f.write(f"{file_info[0]}: {file_info[1]}\n")

    return deleted_files

def main():
    directory = "d:/audio"
    min_length = int(60000)
    max_length = int(3600000)
    delete_contains_str = "promo, trailer"
    ### output_path = "C:/Users/Ghayur Haider"
    # directory = input("Enter the directory path: ")
    # delete_contains_str = input("Enter a comma-separated list of strings to delete files containing any of them in the name, or leave empty: ")
    delete_contains = [substring.strip() for substring in delete_contains_str.split(",")] if delete_contains_str else None
    # min_length = int(input("Enter the minimum length (in milliseconds), or 0 for no minimum: "))
    # max_length = int(input("Enter the maximum length (in milliseconds), or 0 for no maximum: "))
    # output_path = input("Enter the file path to save the deletion log (e.g., deleted_files.txt): ")

    deleted_files = delete_mp3_files(directory, min_length=min_length, max_length=max_length, delete_contains=delete_contains)#, output_path=output_path)

    print("Deletion complete.")

    with open("deleted_files.txt", "w") as f:
        for file, length in deleted_files:
            f.write(f"{file}: {length} ms\n")
    
    print("Deletion complete. Deleted files logged in deleted_files.txt")

if __name__ == "__main__":
    main()