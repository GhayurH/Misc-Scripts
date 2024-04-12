import os
import re

def replace_special_characters(filename):
    # Replace irregular characters like ☆ with a space, excluding brackets ()
    return re.sub(r'[^\w\s\u0080-\uFFFF()]+', ' ', filename)

def replace_multiple_spaces(directory):
    for filename in os.listdir(directory):
        old_filepath = os.path.join(directory, filename)
        if os.path.isfile(old_filepath):
            # Split filename into base name and extension
            base_name, extension = os.path.splitext(filename)
            # Replace special characters with a space in the base name
            new_base_name = replace_special_characters(base_name)
            # Replace multiple spaces with a single space in the base name
            new_base_name = ' '.join(new_base_name.split())
            # Concatenate the modified base name with the original extension
            new_filename = new_base_name + extension
            # Rename the file if the new name is different
            if new_filename != filename:
                new_filepath = os.path.join(directory, new_filename)
                os.rename(old_filepath, new_filepath)

# Replace 'directory_path' with the path of your directory
directory_path = r'C:\Audio\a'
replace_multiple_spaces(directory_path)
