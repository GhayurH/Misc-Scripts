import os
import re

# Replace 'directory_path' with the path of your directory
directory_path = r'C:\a'
log_file_path = os.path.join(directory_path, 'name_changes_log.txt')

def rename_and_clean_files(directory):
    # Open the log file with UTF-8 encoding
    with open(log_file_path, 'w', encoding='utf-8') as log_file:
        # Iterate through each file in the directory
        for filename in os.listdir(directory):
            old_filepath = os.path.join(directory, filename)
            
            # Skip the log file itself
            if old_filepath == log_file_path or not os.path.isfile(old_filepath):
                continue

            # Split the filename into name and extension
            name, extension = os.path.splitext(filename)

            # Remove preceding underscores and punctuation from the name
            new_name = re.sub(r'^[_.\s-]+', '', name)
            # Remove Hindi characters from the name
            new_name = re.sub(r'[\u0900-\u097F]+', ' ', new_name)

            # Define all patterns to be replaced and replace them with a space
            patterns = ['_', '｜', '|', '⧸', '/', ' ع ', '(ع)', '＂', '：', '"', ':', '(س)', '(as)', '(sa)', '(A S )', 'a s', '(a.s)', '(a.s.)', ' س ', 'ﷺ', ' ص ', '(ص)', 's a w w', 'new', 'NEW', '( )']
            pattern = '|'.join(map(re.escape, patterns))
            new_name = re.sub(pattern, ' ', new_name)

            # Replace special characters with spaces in the name, remove leading and trailing spaces, and collapse multiple spaces
            new_name = ' '.join(re.sub(r'[^\w\s\u0080-\uFFFF()]+', ' ', new_name).split())

            # Append the extension to the modified name
            new_name_ext = new_name + extension

            # Check if the new name is different from the original filename
            if new_name_ext != filename:
                new_filepath = os.path.join(directory, new_name_ext)

                # If a file with the new name already exists, append a number to make it unique
                count = 1
                while os.path.exists(new_filepath):
                    new_name_ext = f"{new_name}_{count}{extension}"
                    new_filepath = os.path.join(directory, new_name_ext)
                    count += 1

                # Rename the file with the new filepath
                os.rename(old_filepath, new_filepath)

                # Log the name change
                log_file.write(f"{old_filepath} -> {new_filepath}\n")
                print(f"{old_filepath} -> {new_filepath}")

rename_and_clean_files(directory_path)