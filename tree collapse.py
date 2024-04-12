import os
import shutil

def move_files(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            src_file = os.path.join(root, file)
            dest_file = os.path.join(directory, file)
            if os.path.exists(dest_file):
                print(f"File '{file}' already exists in the main directory.")
            else:
                shutil.move(src_file, dest_file)


# Replace 'directory_path' with the path of your directory
directory_path = r'D:\Audio\Zainab'
move_files(directory_path)
