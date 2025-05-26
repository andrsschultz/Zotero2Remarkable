# Zotero2Remarkable

A Python tool that automatically syncs PDF attachments from Zotero to your reMarkable tablet. Export your Zotero library to BibTeX, and this tool will upload all attached PDFs directly to your reMarkable device using rmapi.

## Current bugs 🐞

Bibtex parsing fails if Zotero entry contains more than a PDF file (e.g. a HTML snapshot)

## Features

- 📚 **Automatic PDF Sync**: Extract and upload PDF attachments from Zotero BibTeX exports
- 🔐 **Secure Authentication**: Integrated rmapi authentication with guided setup
- 📁 **Organized Storage**: Uploads files to a dedicated `/Zotero2Remarkable` folder
- 👀 **File Watching**: Automatic triggering when BibTeX files change
- 🚀 **Direct Integration**: Works with Better BibTeX for seamless Zotero automation
- 📊 **Detailed Feedback**: Comprehensive upload summaries with success/failure reports
- 🔮 **Planned**: Syncing back from reMarkable to Zotero including annotations; automated conversion of unsupported files to PDF

## Prerequisites

- Python 3.6 or higher
- [rmapi](https://github.com/ddvk/rmapi) binary (included or downloaded separately)
- reMarkable tablet with cloud sync enabled
- Zotero with [Better BibTeX](https://retorque.re/zotero-better-bibtex/) plugin (optional, for automation)

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/Zotero2Remarkable.git
   cd Zotero2Remarkable
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Download rmapi** (if not included):
   - Download the appropriate binary from [rmapi releases](https://github.com/ddvk/rmapi/releases)
   - Place the `rmapi` binary in the project root directory
   - Make it executable: `chmod +x rmapi`

## Quick Start

### Basic Usage

1. **Export your Zotero library**:
   - In Zotero, select collection to be synced
   - Right click → Export Collection
   - Choose "Better BibLaTeX" or "Better BibTeX" format
   - Save as `send2remarkable.bib` in the project directory (or any other file name. in this case make sure to update the paths in watch.bib accordingly. see below)

2. **Run the sync**:
   ```bash
   python app.py
   ```

3. **Follow authentication prompts** (first time only):
   - The tool will guide you through rmapi authentication
   - A browser will open to connect your reMarkable account
   - Enter the one-time code when prompted

### Automated Workflow

For automatic syncing when your BibTeX file changes:

1. **Start the file watcher**:
   ```bash
   python watch_bib.py
   ```

2. **Configure Better BibTeX** (optional):
   - In Zotero, select collection to be synced
   - Right click → Export Collection
   - Choose "Better BibLaTeX" or "Better BibTeX" format
   - Select "Keep updated"
   - Save as `send2remarkable.bib` in the project directory (or any other file name. in this case make sure to update the paths in watch.bib accordingly. see below)

## Configuration

### File Paths

Update paths in `watch_bib.py` to match your setup:

```python
BIB_PATH = "/path/to/your/send2remarkable.bib"
PYTHON = "/path/to/your/python"  # or venv python
SCRIPT = "/path/to/your/app.py"
```

### Supported File Formats

The tool automatically filters and uploads:
- ✅ PDF files (.pdf)
- ✅ EPUB files (.epub)
- Feature to come: Automated File conversion

### Output Example
```
🚀 Starting reMarkable Upload Process
==================================================
🔐 Checking rmapi authentication...
✅ rmapi is already authenticated

📁 Found 5 entries to process:
📄 Processing: research_paper_2023.pdf
   📚 Title: Advanced Machine Learning Techniques
✅ Uploaded: research_paper_2023.pdf via rmapi

📄 Processing: methodology_guide.pdf
   📚 Title: Research Methodology Handbook
📄 Already exists: methodology_guide.pdf (skipping)

📊 Upload Summary:
   ✅ Uploaded: 3
   📄 Already existed: 2
   ⚠️  Unsupported format: 0
   📂 File not found: 0
   ❌ Failed: 0

🎉 5 files are now available on your reMarkable tablet!
```

## Troubleshooting

### Common Issues

**Authentication Problems**:
- Ensure your reMarkable has cloud sync enabled
- Try running `./rmapi ls` manually to test authentication
- Clear authentication: `./rmapi help` (look for auth reset options)

**File Not Found Errors**:
- Check that file paths in BibTeX are absolute paths
- Verify Zotero attachment settings export full paths
- Ensure files haven't been moved after export

**Permission Errors**:
- Make rmapi executable: `chmod +x rmapi`
- Check Python virtual environment activation
- Verify file system permissions

**File Watcher Not Working**:
- Update absolute paths in `watch_bib.py`
- Test manual runs first: `python app.py`
- Check if BibTeX file is actually being modified


