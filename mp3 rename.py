import os
import re

def rename_and_clean_files(directory):
    # Function to replace special characters in a filename with spaces
    def replace_special_characters(filename):
        return re.sub(r'[^\w\s\u0080-\uFFFF()]+', ' ', filename)

    # Function to remove Hindi characters from a string
    def remove_hindi_characters(string):
        return re.sub(r'[\u0900-\u097F]+', '', string)

    # Iterate through each file in the directory
    for filename in os.listdir(directory):
        old_filepath = os.path.join(directory, filename)
        if os.path.isfile(old_filepath):
            # Split the filename into name and extension
            name, extension = os.path.splitext(filename)
            # Remove preceding numbers, underscores, and punctuation from the name
            # new_name = re.sub(r'^[\d\s._-]+', '', name)

            # Remove underscores and punctuation from the name, but keep preceding numbers
            new_name = re.sub(r'^[_.\s-]+', '', name)
            # Remove Hindi characters from the name
            new_name = remove_hindi_characters(new_name)
            # Replace underscores with spaces in the name
            new_name = re.sub(r'_', ' ', new_name)
            # Remove all instances of "｜" and "|" from the name 
            new_name = new_name.replace('｜', ' ').replace('|', ' ').replace('⧸', ' ').replace('/', ' ').replace(' ع ', ' ').replace('(ع)', ' ').replace('＂', ' ').replace('：', ' ').replace('"', ' ').replace(':', ' ').replace('(س)', ' ').replace('(as)', ' ').replace('(sa)', ' ').replace('(A S )', ' ').replace(' س ', ' ').replace('ﷺ', ' ').replace(' ص ', ' ').replace('(ص)', ' ').replace('s a w w', ' ').replace('new', ' ').replace('NEW', ' ').replace('a s', ' ').replace('( )', ' ')
            # Replace special characters with spaces in the name
            new_name = replace_special_characters(new_name)
            # Remove spaces at the start of the name
            new_name = new_name.lstrip()
            # Replace multiple spaces with a single space in the name
            new_name = ' '.join(new_name.split())
            # Append the extension to the modified name
            new_name_ext = new_name + extension
            
            # Check if the new name is different from the original filename
            if new_name_ext != filename:
                print(name)
                print(new_name)
                new_filepath = os.path.join(directory, new_name_ext)
                
                # If a file with the new name already exists, append a number to make it unique
                count = 1
                while os.path.exists(new_filepath):
                    new_name_ext = new_name + str(count) + extension
                    new_filepath = os.path.join(directory, new_name_ext)
                    count += 1
                
                # Rename the file with the new filepath
                os.rename(old_filepath, new_filepath)

# Replace 'directory_path' with the path of your directory
directory_path = r'C:\Audio'
rename_and_clean_files(directory_path)
