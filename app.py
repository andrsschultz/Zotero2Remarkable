import os
import bibtexparser
from bibtexparser.bparser import BibTexParser
import shutil

# Parse the BibTeX file

def load_bib_entries(bib_path):

    parser = BibTexParser(common_strings=False)
    parser.ignore_nonstandard_types = False
    #parser.homogenise_fields = False

    with open(bib_path, 'r', encoding='utf-8') as bib_file:
        bib_database = bibtexparser.load(bib_file, parser)
    return bib_database.entries

# File path mapping
#TBD Is this neccessary?
def build_file_map(bib_entries):
    """
    Returns a dict where keys are the BibTeX IDs (entry['id'])
    and values are (file_path, metadata_dict).
    """
    file_map = {}

    for entry in bib_entries:
        bib_id = entry.get("ID")
        if not bib_id:
            print("Warning: No entry ID in bib_entries entry found.")
            continue

        file_path = entry.get("file")
        if not file_path:
            # no attached file? skip
            continue
        
        # Basic metadata from the BibTeX entry
        meta = {
            "bib_id": bib_id,
            "title": entry.get("title", "Untitled"),
            "date": entry.get("date", ""),
            "authors": entry.get("author", ""),  # We'll parse further if needed
            "type": entry.get("type", ""),
            "url": entry.get("url", None),
        }
        
        # Process file path from Zotero which might be in a special format
        # Zotero sometimes uses format like: 'file:/path/to/file.pdf:application/pdf'
        if file_path and ':' in file_path:
            # Split by colon and take the first part if it's a URI format
            parts = file_path.split(':')
            if parts[0].startswith('file'):
                # Remove 'file://' or 'file:/' prefix if present
                clean_path = parts[1].lstrip('/')
                file_path = '/' + clean_path  # Add leading slash back for absolute paths
            else:
                # Just use the first part before any colon if it's not a file:// format
                file_path = parts[0]
        
        # Ensure the file path is absolute and normalized
        file_path = os.path.abspath(os.path.expanduser(file_path))

        # Verify file exists before adding to the map
        if os.path.exists(file_path):
            file_map[bib_id] = (file_path, meta)
        else:
            print(f"Warning: File does not exist at path: {file_path} for {bib_id}")
            # You might still want to include it in the map for tracking purposes
            file_map[bib_id] = (file_path, meta)

    return file_map

def copy_files_to_directory(file_map, target_dir="copied_files"):
    """
    Copy files from file_map to a target directory.
    
    Args:
        file_map: Dictionary with bib_id as keys and (file_path, meta) as values
        target_dir: Directory name where files will be copied (default: "copied_files")
    """
    # Create target directory if it doesn't exist
    os.makedirs(target_dir, exist_ok=True)
    
    copied_count = 0
    failed_count = 0
    skipped_count = 0
    
    for bib_id, (file_path, meta) in file_map.items():
        try:
            # Get the original filename
            filename = os.path.basename(file_path)
            
            # Create destination path
            dest_path = os.path.join(target_dir, filename)
            
            # Handle filename conflicts by appending bib_id
            if os.path.exists(dest_path):
                name, ext = os.path.splitext(filename)
                dest_path = os.path.join(target_dir, f"{name}_{bib_id}{ext}")
                
                # Check if the file with bib_id suffix already exists too
                if os.path.exists(dest_path):
                    print(f"File already exists, skipping: {dest_path}")
                    skipped_count += 1
                    continue
            
            # Copy the file
            if os.path.exists(file_path):
                shutil.copy2(file_path, dest_path)
                print(f"Copied: {filename} -> {dest_path}")
                copied_count += 1
            else:
                print(f"Source file not found: {file_path}")
                failed_count += 1
                
        except Exception as e:
            print(f"Error copying {file_path}: {str(e)}")
            failed_count += 1
    
    print(f"Copy operation completed. {copied_count} files copied, {skipped_count} skipped, {failed_count} failed.")
    return copied_count, failed_count

def main():
    print("Starting app.py...")
    bib_entries = load_bib_entries("send2remarkable.bib")
    print(f"Loaded {len(bib_entries)} BibTeX entries.")
    file_map = build_file_map(bib_entries)
    print(f"Built file map with {len(file_map)} entries.")
    copy_files_to_directory(file_map, target_dir="copied_files")
    print("Files copied to 'copied_files' directory.")

if __name__ == "__main__":
    main()
