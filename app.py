import os
import bibtexparser
from bibtexparser.bparser import BibTexParser
import shutil
import subprocess
import sys

# Local rmapi binary path
LOCAL_RMAPI_PATH = os.path.join(os.path.dirname(__file__), "rmapi")

# Parse the BibTeX file
def load_bib_entries(bib_path):
    parser = BibTexParser(common_strings=False)
    parser.ignore_nonstandard_types = False
    with open(bib_path, 'r', encoding='utf-8') as bib_file:
        bib_database = bibtexparser.load(bib_file, parser)
    return bib_database.entries

# Build file map from BibTeX entries to actual file paths
def build_file_map(bib_entries):
    file_map = {}
    for entry in bib_entries:
        bib_id = entry.get("ID")
        if not bib_id:
            print("Warning: No entry ID found in a BibTeX entry.")
            continue
        file_path = entry.get("file")
        if not file_path:
            continue  # skip entries without attached files
        # Handle Zotero-style URIs: "file:/path/to/file.pdf:application/pdf"
        if ':' in file_path:
            parts = file_path.split(':')
            if parts[0].startswith('file'):
                clean_path = parts[1].lstrip('/')
                file_path = '/' + clean_path
            else:
                file_path = parts[0]
        file_path = os.path.abspath(os.path.expanduser(file_path))
        meta = {
            'bib_id': bib_id,
            'title': entry.get('title', 'Untitled'),
            'authors': entry.get('author', ''),
            'date': entry.get('date', ''),
            'url': entry.get('url', None),
        }
        if os.path.exists(file_path):
            file_map[bib_id] = (file_path, meta)
        else:
            print(f"Warning: File does not exist at path: {file_path} for {bib_id}")
            file_map[bib_id] = (file_path, meta)
    return file_map

# Copy files locally to a staging directory
def copy_files_to_directory(file_map, target_dir="copied_files"):
    os.makedirs(target_dir, exist_ok=True)
    copied, failed, skipped = 0, 0, 0
    for bib_id, (src_path, _) in file_map.items():
        filename = os.path.basename(src_path)
        dest_path = os.path.join(target_dir, filename)
        try:
            if os.path.exists(dest_path):
                print(f"File already exists, skipping: {dest_path}")
                skipped += 1
            else:
                if os.path.exists(src_path):
                    shutil.copy2(src_path, dest_path)
                    print(f"Copied: {filename}")
                    copied += 1
                else:
                    print(f"Source file not found: {src_path}")
                    failed += 1
        except Exception as e:
            print(f"Error copying {src_path}: {e}")
            failed += 1
    print(f"Copy completed: {copied} copied, {skipped} skipped, {failed} failed.")
    return copied, failed

# Upload a single file via local rmapi
def upload_with_rmapi(local_path, remote_folder="/"):
    filename = os.path.basename(local_path)
    
    # Check for supported file extensions
    supported_extensions = {'.pdf', '.epub', '.txt', '.md'}
    file_ext = os.path.splitext(filename)[1].lower()
    
    if file_ext not in supported_extensions:
        print(f"⚠️  Skipping {filename}: Unsupported format ({file_ext})")
        print(f"   📝 Supported formats: {', '.join(supported_extensions)}")
        return "skipped"
    
    try:
        subprocess.run(
            [LOCAL_RMAPI_PATH, "put", local_path, remote_folder],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"✅ Uploaded: {filename} via rmapi")
        return True
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip()
        if "already exists" in error_msg:
            print(f"📄 Already exists: {filename} (skipping)")
            return "exists"
        elif "unsupported file extension" in error_msg:
            print(f"⚠️  Unsupported format: {filename}")
            return "unsupported"
        else:
            print(f"❌ Upload failed for {filename}: {error_msg}")
            return False

# Walk staging directory and send each file via rmapi
def transfer_files_via_rmapi(source_dir="copied_files", remote_folder="/"):
    if not os.path.isdir(source_dir):
        print(f"❌ Source directory '{source_dir}' not found.")
        return
    files = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f))]
    if not files:
        print(f"❌ No files to upload in '{source_dir}'.")
        return
    
    success, failed, skipped, exists, unsupported = 0, 0, 0, 0, 0
    
    for fname in files:
        local_path = os.path.join(source_dir, fname)
        result = upload_with_rmapi(local_path, remote_folder)
        
        if result is True:
            success += 1
        elif result == "skipped":
            skipped += 1
        elif result == "exists":
            exists += 1
        elif result == "unsupported":
            unsupported += 1
        else:
            failed += 1
    
    print(f"\n📊 Upload Summary:")
    print(f"   ✅ Uploaded: {success}")
    print(f"   📄 Already existed: {exists}")
    print(f"   ⚠️  Unsupported format: {unsupported}")
    print(f"   ⏭️  Pre-filtered: {skipped}")
    print(f"   ❌ Failed: {failed}")
    
    total_processed = success + exists
    if total_processed > 0:
        print(f"\n🎉 {total_processed} files are now available on your reMarkable tablet!")

# Check if rmapi is authenticated and authenticate if needed
def ensure_rmapi_authenticated():
    """
    Check if rmapi is authenticated and prompt for authentication if needed.
    Returns True if authenticated successfully, False otherwise.
    """
    print("🔐 Checking rmapi authentication...")
    try:
        # Try a simple command that requires authentication
        result = subprocess.run(
            [LOCAL_RMAPI_PATH, "ls"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print("✅ rmapi is already authenticated")
            return True
        else:
            print("❌ rmapi authentication required")
            return authenticate_rmapi()
            
    except subprocess.TimeoutExpired:
        print("⚠️  rmapi command timed out, likely waiting for authentication")
        return authenticate_rmapi()
    except Exception as e:
        print(f"❌ Error checking rmapi authentication: {e}")
        return False

def authenticate_rmapi():
    """
    Handle rmapi authentication interactively.
    Returns True if authentication succeeds, False otherwise.
    """
    print("\n" + "="*50)
    print("🔐 rmapi Authentication Required")
    print("="*50)
    print("You need to authenticate with reMarkable Cloud.")
    print("1. A browser will open to https://my.remarkable.com/device/browser/connect")
    print("2. You'll get a one-time code to enter")
    print("3. Follow the instructions on the website")
    print()
    
    proceed = input("Press Enter to start authentication, or 'q' to quit: ").strip().lower()
    if proceed == 'q':
        print("❌ Authentication cancelled by user")
        return False
    
    try:
        print("🌐 Starting rmapi authentication...")
        print("(Enter the one-time code when prompted)")
        
        # Run rmapi interactively for authentication
        result = subprocess.run([LOCAL_RMAPI_PATH, "ls"], text=True)
        
        if result.returncode == 0:
            print("✅ Authentication successful!")
            return True
        else:
            print("❌ Authentication failed")
            return False
            
    except KeyboardInterrupt:
        print("\n❌ Authentication cancelled by user")
        return False
    except Exception as e:
        print(f"❌ Error during authentication: {e}")
        return False

# Main entry point
def main():
    if not os.path.exists(LOCAL_RMAPI_PATH) or not os.access(LOCAL_RMAPI_PATH, os.X_OK):
        print("Error: local 'rmapi' binary not found or not executable.")
        print("Please download it from https://github.com/ddvk/rmapi/releases and place it in the project root.")
        sys.exit(1)
    bib_entries = load_bib_entries("send2remarkable.bib")
    print(f"Loaded {len(bib_entries)} BibTeX entries.")
    file_map = build_file_map(bib_entries)
    print(f"Built file map with {len(file_map)} entries.")
    copy_files_to_directory(file_map, target_dir="copied_files")
    
    print("\n" + "="*50)
    print("🚀 Starting reMarkable Upload Process")
    print("="*50)
    
    # Ensure rmapi is authenticated before proceeding
    if not ensure_rmapi_authenticated():
        print("❌ Cannot proceed without rmapi authentication. Exiting.")
        sys.exit(1)
    
    print("\n📤 Starting upload via rmapi...")
    transfer_files_via_rmapi(source_dir="copied_files", remote_folder="/")

if __name__ == "__main__":
    main()
