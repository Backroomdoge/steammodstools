# Project Architecture & Developer Guide

## Overview

This project is organized into three main modules plus utilities, each with a clear responsibility.

```
Steam Workshop Toolkit
│
├── core/                 # Business Logic (Pure Python, no UI)
│   ├── api.py           # Steam API interactions
│   ├── categories.py    # Category organization
│   ├── csv_manager.py   # CSV file operations
│   ├── steam_collection.py  # Collection management
│   └── collectionfromcsv.py # Bulk add to collections
│
├── ui/                  # User Interfaces (Present data, get input)
│   ├── console.py       # Terminal/CLI interface
│   └── gui.py           # Tkinter GUI interface
│
├── utils/               # Utilities (Support functions)
│   ├── settings_manager.py  # Config + progress tracking
│   ├── file_utils.py       # JSON I/O
│   └── input_handlers.py    # User input dialogs
│
└── Legacy files         # Original files (for compatibility)
    ├── console_commands.py
    ├── console_settings.py
    ├── ui_gui.py
    └── others...
```

## Module Breakdown

### 1. CORE Module (Business Logic)

**Purpose:** Process data without caring about UI. Pure functions.

#### api.py - Steam API Interactions
**What it does:**
- Connects to Steam's website
- Fetches list of mods for a game
- Gets detailed info about each mod
- Looks up game names by App ID

**Key functions:**
```python
init_api(api_key)                    # Initialize Selenium browser
fetch_all_mod_ids(app_id)            # Get all mod IDs
fetch_mod_details(mod_ids)           # Get mod info (title, tags, etc.)
fetch_game_name(app_id)              # Get game name from ID
```

**How it works:**
1. Uses Selenium to automate browser
2. Navigates to Steam Workshop pages
3. Parses HTML to extract mod data
4. Returns structured data (JSON-friendly)

#### categories.py - Organization
**What it does:**
- Takes mod data and organizes by tags
- Extracts unique tags from all mods
- Groups mods under their tags

**Key functions:**
```python
extract_tags(mods)                   # Get unique tags from all mods
build_by_category(mods, tags)        # Group mods by tag
```

**How it works:**
1. Analyzes all mod tags
2. Creates category -> [mod_ids] mapping
3. Returns organized structure

#### csv_manager.py - CSV Export
**What it does:**
- Creates CSV files from organized mods
- One category = multiple CSV files (if needed)
- Follows Steam's CSV format for bulk upload

**Key functions:**
```python
write_csv_for_category(base_dir, game_name, category, mods, append)
```

**How it works:**
1. Takes mods from one category
2. Splits into chunks (if > mods_per_csv)
3. Writes each chunk to CSV file
4. Files stored in: `data/{app_id}_{game_name}/csv/{category}/`

#### steam_collection.py - Collection Management
**What it does:**
- Manages the workflow of creating Steam collections
- Coordinates CSV processing
- Tracks which collections are created/failed

**Key functions:**
```python
process_collections_to_steam(app_id, base_dir, categories, mode, confirm)
```

**Modes:**
- Mode 1: Process all CSV files
- Mode 2: Only process new CSV (not already done)
- Mode 4: Only retry failed uploads

**How it works:**
1. Loads JSON database of processed collections
2. For each category, finds CSV files
3. Calls bulk add function for each CSV
4. Tracks success/failure in JSON DB
5. Saves state for resume capability

#### collectionfromcsv.py - Bulk Operations
**What it does:**
- Creates a Steam collection
- Adds mods from CSV to the collection
- Handles errors and retries

**Key functions:**
```python
run_from_csv_list(appid, category, csv_files, mode)
```

**How it works:**
1. Uses Selenium to create collection
2. Reads CSV file
3. Adds each mod to collection via Steam UI
4. On error: saves to "_FAILED" CSV for retry
5. Logs all operations

---

### 2. UI Module (User Interfaces)

**Purpose:** Get user input and present results. Delegates to core.

#### console.py - Terminal Interface
**What it does:**
- Menu-driven terminal interface
- Displays progress bars (tqdm)
- Gets user input

**How it works:**
1. Shows numbered menu options
2. Gets user choice
3. Calls appropriate core function
4. Shows progress with tqdm bar
5. Repeats until user quits

**Menu flow:**
```
0 - Change Game          → select_game_from_list()
1 - Download & Sort      → download_and_sort_mods()
4 - Generate CSV         → generate_csv_for_categories()
5 - Steam Collection     → process_steam_collections()
```

#### gui.py - Tkinter Interface
**What it does:**
- Tab-based GUI window
- Real-time progress bars
- Game selection dialog
- Settings editor

**Tabs:**
1. **Download & Sort** - Shows progress, downloads mods
2. **Generate CSV** - Select categories, generate CSVs
3. **Steam Collections** - Select categories, create collections
4. **Settings** - Edit configuration, data cleanup

**How it works:**
1. Creates Tkinter window with tabs
2. Each tab has controls + progress bar
3. Operations run in background threads
4. Progress callbacks update GUI in real-time
5. User can switch tabs while processing

---

### 3. UTILS Module (Support Functions)

#### settings_manager.py - Configuration
**What it does:**
- Loads/saves `params.json`
- Manages game history
- Provides progress tracking with callbacks

**Key classes:**
```python
class ProgressTracker:
    set_total(total)                 # Set number of items
    update(amount, message)          # Add progress
    register_callback(callback)      # Register progress listener
    get_percentage()                 # Get progress %
```

**How it works:**
1. Reads JSON config file
2. Caches in memory
3. Notifies all registered callbacks on changes
4. Callbacks used by console (tqdm) and GUI (Progressbar)

#### file_utils.py - File I/O
**What it does:**
- Load/save JSON files

**Key functions:**
```python
load_json(path)      # Parse JSON file → dict
save_json(path, data)  # Write dict → JSON file
```

#### input_handlers.py - User Input
**What it does:**
- Game selection dialog
- History management

**Key functions:**
```python
select_game_from_list()  # Shows history, gets game selection
```

---

## Data Flow Example

### Workflow: Download mods for a game

```
User selects option 1 (Download & Sort)
    ↓
run_console_mode() calls download_and_sort_mods()
    ↓
api.py:
  - init_api() → starts Selenium
  - fetch_all_mod_ids(app_id) → scrapes Steam for mod IDs
  - fetch_mod_details(mod_ids) → gets info for each mod
    ↓
categories.py:
  - extract_tags(mods) → finds all unique tags
  - build_by_category(mods, tags) → groups by tag
    ↓
utils/settings_manager.py:
  - progress_tracker.update() → notifies console + GUI
    ↓
Files saved:
  - data/{app_id}_{game_name}/mods_raw.json
  - data/{app_id}_{game_name}/mods_by_category.json
  - data/{app_id}_{game_name}/tags_list.json
    ↓
User sees: Progress bar → 100% → "Download complete!"
```

### Workflow: Generate CSVs

```
User selects option 4 (Generate CSV)
    ↓
console.py asks: "Which categories?"
    ↓
csv_manager.py:
  - For each selected category:
    - Reads mods from mods_by_category.json
    - Splits into chunks of mods_per_csv
    - Writes each chunk to CSV
    ↓
Files created:
  - data/{app_id}_{game_name}/csv/{category}/Category_1.csv
  - data/{app_id}_{game_name}/csv/{category}/Category_2.csv
    ↓
User sees: Progress bar → "CSV for Category saved"
```

### Workflow: Create Steam Collections

```
User selects option 5 (Steam Collection)
    ↓
console.py asks: "Which categories?"
    ↓
steam_collection.py:
  - Loads collections_processed.json (tracks what's done)
  - For each category:
    - Finds all CSVs in data/{app_id}_{game_name}/csv/{category}/
    ↓
For each CSV file:
  - collectionfromcsv.py:
    - Creates new Steam collection
    - Reads CSV
    - Adds each mod to collection (Selenium)
    - On error: saves "_FAILED" CSV for retry
    ↓
Collections created on Steam!
    ↓
JSON updated to track completion
```

---

## File Structure at Runtime

```
workshop/
├── main.py                          # Entry point
├── requirements.txt                 # Dependencies
├── setup.py                         # Package config
├── README.md                        # User documentation
├── QUICKSTART.md                    # Quick setup guide
├── CONTRIBUTING.md                  # Developer guide
├── LICENSE                          # MIT License
│
├── mods_tools/
│   ├── __init__.py                  # Package init
│   ├── parameter/
│   │   └── params.json              # User config (IGNORED BY GIT)
│   │
│   ├── core/                        # Business logic
│   │   ├── __init__.py
│   │   ├── api.py
│   │   ├── categories.py
│   │   ├── csv_manager.py
│   │   ├── steam_collection.py
│   │   └── collectionfromcsv.py
│   │
│   ├── ui/                          # Interfaces
│   │   ├── __init__.py
│   │   ├── console.py
│   │   └── gui.py
│   │
│   ├── utils/                       # Utilities
│   │   ├── __init__.py
│   │   ├── settings_manager.py
│   │   ├── file_utils.py
│   │   └── input_handlers.py
│   │
│   └── [Legacy files]               # Original files
│       ├── console_commands.py
│       ├── console_settings.py
│       ├── ui_gui.py
│       └── ...
│
└── data/                            # Generated at runtime (IGNORED BY GIT)
    └── {app_id}_{game_name}/
        ├── mods_raw.json
        ├── mods_by_category.json
        ├── tags_list.json
        ├── collections_processed.json
        ├── csv/
        │   └── {category}/
        │       ├── Category_1.csv
        │       └── Category_2.csv
        └── log/
            └── processing.log
```

---

## Getting Started - For Users

### 1. Installation
```bash
# Clone the repo
git clone https://github.com/username/steam-workshop-toolkit.git
cd steam-workshop-toolkit

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r workshop/requirements.txt
```

### 2. Configuration
```bash
# Run once to create config
python workshop/main.py

# Edit the created params.json
# Add your Steam credentials (sessionid, securelogin)
```

### 3. First Run
```bash
python workshop/main.py

# Console: Follow the menu
# or set "use_gui": true in params.json for GUI
```

---

## Getting Started - For Developers

### Setup Development Environment
```bash
git clone https://github.com/username/steam-workshop-toolkit.git
cd steam-workshop-toolkit

python -m venv .venv
source .venv/bin/activate

pip install -r workshop/requirements.txt
```

### Understanding the Code
1. Start with `main.py` - entry point
2. Look at `mods_tools/__init__.py` - package structure
3. Explore `core/` - pure logic, no UI
4. Check `ui/` - how logic is presented
5. Review `utils/` - support functions

### Making Changes
- **Adding a new feature?** Add to `core/`, expose in `__init__.py`
- **Improving UI?** Modify `ui/console.py` or `ui_gui.py`
- **Adding settings?** Update `utils/settings_manager.py`
- **Need a new utility?** Add to `utils/`

### Testing Changes
```bash
# Test console
python workshop/main.py

# Test GUI
# Edit params.json: set "use_gui": true
python workshop/main.py
```

### Common Tasks

**Add a new API function:**
1. Add to `core/api.py`
2. Export in `core/__init__.py`
3. Call from `console.py` or `gui.py`

**Add a new console menu option:**
1. Add to `console_commands.py` main loop
2. Create handler function
3. Call core functions as needed
4. Show results to user

**Add a new GUI tab:**
1. Create method `_create_X_tab()` in `ModManagerGUI`
2. Add to `_setup_ui()`
3. Add thread handler `_X_thread()`
4. Use progress tracker for updates

---

## Progress Tracking System

Both console and GUI use the same **ProgressTracker** for synchronized progress:

```python
# In core function:
tracker = get_progress_tracker()
tracker.set_total(100)
tracker.update(10, "Step 1...")
tracker.update(30, "Step 2...")

# Console sees: tqdm bar [████░░] 40%
# GUI sees: Progressbar at 40%
# Both show same message
```

**Key: Core functions update tracker, UI just displays it.**

---

## Important Concepts

### Separation of Concerns
- **core/** = What to do (logic)
- **ui/** = How to show it (presentation)
- **utils/** = Helper functions

### Threading
- Long operations run in background threads
- GUI remains responsive
- Progress callbacks update UI in real-time

### Configuration
- `params.json` is user-specific (ignored by git)
- Contains credentials and settings
- Loaded on startup, can be edited at runtime

### Data Persistence
- All downloads saved to `data/` folder
- JSON files used for tracking state
- Can resume operations from saved state

---

## Troubleshooting Development Issues

### "Module not found" error
- Check `__init__.py` has proper imports
- Verify module is in `__all__`
- Ensure relative imports are correct

### Progress bar not showing
- Check `ProgressTracker` is registered
- Verify callback is called with (current, total, message)
- In GUI: ensure `root.after()` is used for thread safety

### Settings not persisting
- Verify `save_params()` is called
- Check `params.json` path is correct
- Ensure JSON is valid (no syntax errors)

### GUI not responding
- Check operations run in background threads
- Verify callbacks use `root.after()` for safety
- Don't do blocking operations on main thread

---

**Happy coding! 🚀**
