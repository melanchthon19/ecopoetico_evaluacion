import os
import unicodedata
import re

# Function to normalize file names
def normalize_filename(file_name):
    # 1. Normalize the file name by removing accents and special characters
    nfkd_form = unicodedata.normalize('NFKD', file_name)
    without_accents = nfkd_form.encode('ASCII', 'ignore').decode('utf-8')

    # 2. Replace spaces with hyphens and convert to lowercase
    normalized = re.sub(r'\s+', '-', without_accents).lower()

    return normalized

# Function to traverse the corpus directory and normalize file names
def normalize_corpus_file_names(corpus_dir):
    # Traverse the directory and subdirectories
    for root, dirs, files in os.walk(corpus_dir):
        for file_name in files:
            # Skip non-text files if needed
            if not file_name.endswith('.txt'):
                continue
            
            # Get the full original path
            original_path = os.path.join(root, file_name)
            
            # Normalize the file name
            normalized_file_name = normalize_filename(file_name)
            
            # If the name changes, rename the file
            if file_name != normalized_file_name:
                new_path = os.path.join(root, normalized_file_name)
                print(f"Renaming: {original_path} -> {new_path}")
                os.rename(original_path, new_path)

# Example usage:
corpus_dir = '/home/echopoetic/ecopoetico_evaluacion/corpus'
normalize_corpus_file_names(corpus_dir)

