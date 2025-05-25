import os
import bibtexparser
from bibtexparser.bparser import BibTexParser
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

# Upload files directly from file_map via rmapi
def upload_files_directly(file_map, remote_folder="/Zotero2Remarkable"):
    """
    Upload files directly from their original locations using rmapi.
    
    Args:
        file_map: Dictionary with bib_id as keys and (file_path, meta) as values
        remote_folder: Remote folder path on reMarkable
    """
    if not file_map:
        print("❌ No files to upload.")
        return
    
    # Create the remote folder if it doesn't exist
    if remote_folder != "/":
        print(f"📁 Ensuring folder exists: {remote_folder}")
        try:
            subprocess.run(
                [LOCAL_RMAPI_PATH, "mkdir", remote_folder],
                capture_output=True,
                text=True
            )
            print(f"✅ Folder ready: {remote_folder}")
        except Exception as e:
            print(f"⚠️  Note: Could not create folder {remote_folder} (may already exist)")
    
    print(f"📁 Found {len(file_map)} entries to process:")
    
    success, failed, skipped, exists, unsupported, missing = 0, 0, 0, 0, 0, 0
    
    for bib_id, (file_path, meta) in file_map.items():
        filename = os.path.basename(file_path)
        title = meta.get('title', 'Untitled')
        
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"❌ File not found: {filename} (from {title})")
            missing += 1
            continue
        
        print(f"📄 Processing: {filename}")
        print(f"   📚 Title: {title}")
        
        result = upload_with_rmapi(file_path, remote_folder)
        
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
    print(f"   📂 File not found: {missing}")
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
    
    print("\n" + "="*50)
    print("🚀 Starting reMarkable Upload Process")
    print("="*50)
    
    # Ensure rmapi is authenticated before proceeding
    if not ensure_rmapi_authenticated():
        print("❌ Cannot proceed without rmapi authentication. Exiting.")
        sys.exit(1)
    
    print("\n📤 Uploading files directly to reMarkable...")
    upload_files_directly(file_map, remote_folder="/Zotero2Remarkable")

if __name__ == "__main__":
    main()
