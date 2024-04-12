import os
import csv
from difflib import SequenceMatcher

# this code is extremely slow and (largely) useless. need to refine

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def compare_and_flag(directory):
    filenames = os.listdir(directory)
    filenames.sort()  # Sort filenames

    flagged_groups = []

    for i in range(len(filenames)):
        current_group = []
        for j in range(i + 1, len(filenames)):
            similarity = similar(filenames[i], filenames[j])
            if similarity >= 0.8:
                if filenames[i] not in current_group:
                    current_group.append(filenames[i])
                if filenames[j] not in current_group:
                    current_group.append(filenames[j])
        if current_group and current_group not in flagged_groups:
            flagged_groups.append(current_group)

    output_file_path = os.path.join(directory, 'similar_filenames.csv')
    with open(output_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for group in flagged_groups:
            for filename in group:
                writer.writerow([filename])
            writer.writerow([])  # Blank row after each group of similar names

# Replace 'directory_path' with the path of your directory
directory_path = r'C:\Audio\a'
compare_and_flag(directory_path)