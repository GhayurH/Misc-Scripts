def remove_duplicates(input_file, output_file):
  """
  Removes duplicate lines from a text file and saves the unique lines to a new file.

  Args:
      input_file: Path to the text file containing duplicate lines.
      output_file: Path to the output file where unique lines will be saved.
  """
  seen = set()  # Keeps track of seen lines
  with open(input_file, 'r') as in_file, open(output_file, 'w') as out_file:
    for line in in_file:
      if line.strip() not in seen:  # Check for line without trailing whitespace
        seen.add(line.strip())
        out_file.write(line)

# Example usage
input_file = "C:/a/junk/downloaded_videos.txt"
output_file = "C:/a/junk/downloaded_videos2.txt"
remove_duplicates(input_file, output_file)
print(f"Duplicate lines removed and saved to {output_file}")
