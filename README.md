# Zotero2Remarkable

A Python tool that automatically syncs PDF attachments from Zotero to your reMarkable tablet. Export your Zotero library to BibTeX, and this tool will upload all attached PDFs directly to your reMarkable device using rmapi.

## Features

- 📚 **Automatic PDF Sync**: Extract and upload PDF attachments from Zotero BibTeX exports
- 🔐 **Secure Authentication**: Integrated rmapi authentication with guided setup
- 📁 **Organized Storage**: Uploads files to a dedicated `/Zotero2Remarkable` folder
- 🎯 **Smart Filtering**: Supports PDF, EPUB, TXT, and Markdown files
- 👀 **File Watching**: Automatic triggering when BibTeX files change
- 🚀 **Direct Integration**: Works with Better BibTeX for seamless Zotero automation
- 📊 **Detailed Feedback**: Comprehensive upload summaries with success/failure reports

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
   - In Zotero, select items or collections
   - Go to File → Export Library
   - Choose "Better BibTeX" format (or standard BibTeX)
   - Save as `send2remarkable.bib` in the project directory

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
   - In Zotero preferences, go to Better BibTeX → Export
   - Set up automatic export to `send2remarkable.bib`
   - Enable postscript to trigger sync automatically

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
- ✅ Text files (.txt)
- ✅ Markdown files (.md)

### Remote Folder Structure

Files are organized on your reMarkable in:
```
/Zotero2Remarkable/
├── document1.pdf
├── document2.pdf
└── ...
```

## Better BibTeX Integration

For seamless automation with Zotero:

1. **Install Better BibTeX plugin** in Zotero
2. **Configure automatic export**:
   - Preferences → Better BibTeX → Export
   - Set "Export directory" to your project folder
   - Enable "Export on change"
   - Choose filename: `send2remarkable.bib`

3. **Add postscript** (optional):
   ```javascript
   // Trigger Zotero2Remarkable sync after export
   const { exec } = require('child_process');
   exec('python /path/to/Zotero2Remarkable/app.py');
   ```

## Usage Examples

### Manual Sync
```bash
# Basic sync with default settings
python app.py

# Check authentication status
python app.py --check-auth
```

### Automated Monitoring
```bash
# Watch for BibTeX file changes and auto-sync
python watch_bib.py
```

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

### Debug Mode

For detailed debugging information:
```bash
# Check rmapi status
./rmapi ls

# Test BibTeX parsing
python -c "from app import load_bib_entries; print(load_bib_entries('send2remarkable.bib'))"

# Verify file paths
python -c "from app import build_file_map, load_bib_entries; print(build_file_map(load_bib_entries('send2remarkable.bib')))"
```

## Architecture

### Core Components

- **`app.py`**: Main application with BibTeX parsing and rmapi integration
- **`watch_bib.py`**: File system watcher for automatic triggering
- **`rmapi`**: Binary for reMarkable cloud communication
- **`send2remarkable.bib`**: BibTeX input file from Zotero

### Workflow

1. **Parse**: Extract file paths and metadata from BibTeX
2. **Validate**: Check file existence and format support
3. **Authenticate**: Ensure rmapi cloud connection
4. **Upload**: Transfer files directly to reMarkable
5. **Report**: Provide detailed success/failure summary

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [rmapi](https://github.com/ddvk/rmapi) for reMarkable cloud integration
- [Better BibTeX](https://retorque.re/zotero-better-bibtex/) for enhanced Zotero exports
- [Zotero](https://www.zotero.org/) for reference management
- [reMarkable](https://remarkable.com/) for the amazing e-paper tablet

## Support

If you encounter issues:

1. Check the [troubleshooting section](#troubleshooting)
2. Search existing [GitHub issues](https://github.com/yourusername/Zotero2Remarkable/issues)
3. Create a new issue with:
   - Your operating system
   - Python version
   - Error messages
   - Steps to reproduce

---

**Happy reading on your reMarkable! 📚✨**
