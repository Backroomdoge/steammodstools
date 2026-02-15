# Steam Workshop Collection Toolkit

A powerful, user-friendly tool for managing Steam Workshop mods with support for both CLI and GUI interfaces.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

## ⚠️ DISCLAIMER - UNOFFICIAL API

**This tool uses unofficial Steam API methods and web scraping techniques.**

- **Not officially supported by Valve/Steam**
- May break at any time if Steam changes their website/API
- Could violate Steam's Terms of Service
- Use at your own risk
- May result in account restrictions or bans (unlikely but possible)
- The author is not responsible for any damage or account issues

**Use responsibly and with caution.** Consider this a personal tool for your own account only.

---

## Features

✨ **Download & Organize**
- Fetch all mods for a game from Steam Workshop
- Automatically organize by tags/categories
- Save as JSON for further processing

📊 **CSV Generation**
- Generate CSV files from mod categories
- Support for bulk operations
- Multiple export modes (overwrite/append)

🎮 **Steam Collections**
- Create Steam collections from CSV data
- Bulk add mods to collections
- Handle failed uploads automatically

🖥️ **Dual Interface**
- **Console Mode**: Terminal interface with progress bars
- **GUI Mode**: Tkinter graphical interface
- Full feature parity between both modes

⚙️ **Smart Settings**
- Persistent configuration via JSON
- Game history tracking
- Granular data cleanup options
- Progress tracking with callbacks

## Project Structure

```
steam-workshop-toolkit/
├── workshop/
│   ├── main.py                 # Entry point
│   ├── requirements.txt        # Dependencies
│   └── mods_tools/
│       ├── __init__.py         # Package initialization
│       ├── parameter/
│       │   └── params.json     # Configuration (user-specific)
│       ├── core/               # Business logic
│       │   ├── __init__.py
│       │   ├── api.py          # Steam API interactions
│       │   ├── categories.py   # Category management
│       │   ├── csv_manager.py  # CSV operations
│       │   ├── steam_collection.py
│       │   └── collectionfromcsv.py
│       ├── ui/                 # User interfaces
│       │   ├── __init__.py
│       │   ├── console.py      # CLI interface
│       │   └── gui.py          # GUI interface
│       ├── utils/              # Utilities
│       │   ├── __init__.py
│       │   ├── settings_manager.py
│       │   ├── file_utils.py
│       │   └── input_handlers.py
│       ├── [legacy files]      # Original files (for compatibility)
│       └── data/               # Generated data (created at runtime)
└── README.md
```

## Installation

### Prerequisites
- Python 3.8+
- Steam account with API access

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/steam-workshop-toolkit.git
cd steam-workshop-toolkit
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r workshop/requirements.txt
```

4. **Configure settings**
```bash
python workshop/main.py
```
The app will create `params.json` on first run. You'll need to:
- Set `sessionid` and `securelogin` from your Steam session
- Adjust other settings as needed

## Usage

### Console Mode (Default)

```bash
python workshop/main.py
```

Menu options:
- **0** - Change Game (select a different Steam app)
- **1** - Download & Sort (fetch and organize mods)
- **2** - Create/Modify Categories (custom organization)
- **3** - Modify Custom Category (edit existing categories)
- **4** - Generate CSV (export categories to CSV)
- **5** - Steam Collection (upload to Steam collections)
- **6** - Clear All Data (cleanup downloaded data)
- **7** - Settings (configure the app)
- **q** - Quit

### GUI Mode

Set in `params.json`:
```json
{
  "use_gui": true
}
```

Then run:
```bash
python workshop/main.py
```

Features:
- Tab-based interface (Download, CSV, Collections, Settings)
- Real-time progress bars
- Game selection with history
- Interactive category selection
- One-click cleanup operations

## API Reference

### Core Functions

```python
from mods_tools.core import (
    init_api,
    fetch_all_mod_ids,
    fetch_mod_details,
    build_by_category,
    process_collections_to_steam,
)

# Initialize API
init_api(api_key)

# Fetch mods for a game
mod_ids = fetch_all_mod_ids(app_id)
mods = fetch_mod_details(mod_ids)

# Organize by category
categories = build_by_category(mods, tags)

# Create collections
process_collections_to_steam(app_id, base_dir, categories)
```

### Settings & Progress

```python
from mods_tools.utils import (
    load_params,
    save_params,
    get_progress_tracker,
    add_game_to_history,
)

# Load/save settings
params = load_params()
params['headless'] = False
save_params(params)

# Track progress
tracker = get_progress_tracker()
tracker.register_callback(lambda current, total, msg: print(f"{msg}: {current}/{total}"))
tracker.set_total(100)
tracker.update(10, "Processing...")
```

## Configuration

### params.json

Located at `workshop/mods_tools/parameter/params.json`

| Setting | Type | Description |
|---------|------|-------------|
| `sessionid` | string | Steam session ID (required) |
| `securelogin` | string | Steam secure login cookie (required) |
| `headless` | boolean | Hide browser window (default: true) |
| `mods_per_page` | int | Mods to fetch per API request (default: 100) |
| `mods_per_csv` | int | Mods per CSV file (default: 750) |
| `request_delay` | float | Delay between requests in seconds (default: 1) |
| `use_gui` | boolean | Use GUI instead of console (default: false) |
| `image_path` | string | Collection cover image path |

## Getting Steam Credentials

1. Log into your Steam account
2. Open DevTools (F12) → Storage → Cookies
3. Find and copy:
   - `sessionid` cookie value
   - `steamLoginSecure` cookie value (use for `securelogin`)
4. Add to `params.json`

## Data Cleanup Options

### Console (Settings → 7 - Data & Cache Management)
1. Delete Current Game Data (keeps parameters)
2. Delete All Data Folder (keeps parameters)
3. Delete Everything (resets all)

### GUI (Settings Tab → Data & Cache Management)
Same three options with confirmation dialogs

## Progress Tracking

Both console and GUI show real-time progress:
- Console: tqdm progress bars with mod counts
- GUI: Animated progress bars with percentage
- Synchronized across both interfaces
- Based on actual mods processed, not arbitrary steps

## Troubleshooting

### "No config file found"
- Run the app once to create `params.json`
- Add your Steam credentials
- Run again

### "Failed to fetch mods"
- Check `sessionid` and `securelogin` are correct
- Verify API key if using API mode
- Check internet connection
- Increase `request_delay` if being rate-limited

### Progress bar not showing
- For console: ensure terminal supports ANSI colors
- For GUI: check that progress callbacks are registered
- May be normal for very fast operations

### Steam collections not uploading
- Verify you have collection creation permissions
- Check mod IDs are valid
- Review logs in `data/{app_id}_{name}/log/`

## Performance Tips

1. **Adjust request delays** in settings to avoid rate-limiting
2. **Use headless mode** for faster browser automation (default: true)
3. **Batch operations** - process multiple games sequentially
4. **Use CSV mode** to save intermediate results

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License - see LICENSE file for details

## Changelog

### v1.0.0 (Current)
- ✨ Full console and GUI implementation
- 🔄 Real-time progress tracking
- 📊 CSV generation and management
- 🎮 Steam collection automation
- ⚙️ Settings management with persistence
- 🗑️ Granular data cleanup options

## Support

For issues, questions, or suggestions:
- Create an issue on GitHub
- Check existing documentation
- Review logs in `data/{app_id}_{name}/log/`

## Acknowledgments

- Steam Workshop API documentation
- Selenium for browser automation
- tqdm for console progress bars
- Tkinter for GUI framework

---

**Made with ❤️ for the Steam modding community**
