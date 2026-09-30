import os
import sys
import re
import pickle
import zipfile
from collections import defaultdict

def clean_token(token):
    # Normalize token: lowercase and strip punctuation boundaries
    token = token.lower().strip(".,!?;:()[]{}'\"`*_-")
    return token if re.match(r'^[a-z0-9]+$', token) else None

def build_mode(folder_path, output_zip_name):
    if not os.path.isdir(folder_path):
        print("INVALID FOLDER")
        return

    # Inverted Index structure: unique_token -> set of (filename, line_number)
    inverted_index = defaultdict(set)
    
    total_files = 0
    total_lines = 0
    log_files = []

    # Scan the target folder for regular log files
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.log') or file.endswith('.txt'):
                log_files.append(os.path.join(root, file))

    total_files = len(log_files)

    for file_path in log_files:
        filename = os.path.basename(file_path)
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_idx, line in enumerate(f, 1):
                    total_lines += 1
                    # Extract tokens using regular expression word splits
                    tokens = line.split()
                    for t in tokens:
                        normalized = clean_token(t)
                        if normalized:
                            inverted_index[normalized].add((filename, line_idx))
        except Exception:
            continue

    # Convert sets to sorted lists for serialization predictability
    serializable_index = {token: sorted(list(postings)) for token, postings in inverted_index.items()}
    unique_tokens = len(serializable_index)

    # Serialize the inverted index to a temporary binary file
    index_filename = "index.pkl"
    with open(index_filename, 'wb') as pkl_file:
        pickle.dump(serializable_index, pkl_file, protocol=pickle.HIGHEST_PROTOCOL)

    # Package everything inside the zipped archive stream
    with zipfile.ZipFile(output_zip_name, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
        # Add original source logs
        for file_path in log_files:
            zipf.write(file_path, os.path.relpath(file_path, os.path.dirname(folder_path)))
        # Add binary index mapping file
        zipf.write(index_filename, index_filename)

    # Remove temporary artifact from workspace disk
    if os.path.exists(index_filename):
        os.remove(index_filename)

    print(f"FILES {total_files}")
    print(f"LINES {total_lines}")
    print(f"TOKENS {unique_tokens}")

def search_mode(pickle_path, query_tokens):
    if not os.path.exists(pickle_path):
        print("INVALID INDEX PATH")
        return

    try:
        with open(pickle_path, 'rb') as pkl_file:
            inverted_index = pickle.load(pkl_file)
    except Exception:
        print("INVALID INDEX FORMAT")
        return

    for token in query_tokens:
        normalized = token.lower()
        print(f"Query: {token}")
        if normalized in inverted_index:
            matches = inverted_index[normalized]
            for filename, line_num in matches:
                print(f"{filename}:{line_num}")
        else:
            print("NO MATCHES FOUND")

def solve():
    input_data = sys.stdin.read().splitlines()
    if not input_data:
        return

    first_line = input_data[0].strip().split()
    if not first_line:
        return

    mode = first_line[0].upper()

    if mode == "BUILD":
        if len(first_line) < 3:
            return
        folder_path = first_line[1]
        output_zip_name = first_line[2]
        build_mode(folder_path, output_zip_name)
        
    elif mode == "SEARCH":
        if len(first_line) < 2:
            return
        pickle_path = first_line[1]
        # Collect query tokens from remaining slice elements
        query_tokens = first_line[2:]
        search_mode(pickle_path, query_tokens)

if __name__ == '__main__':
    solve()
