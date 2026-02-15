"""
Steam Workshop Collection Toolkit
==================================

A comprehensive tool for managing Steam Workshop mods:
- Download and organize mods by category
- Generate CSV files for bulk operations
- Create and manage Steam collections
- Available in both console and GUI modes

Author: nonog
License: MIT

Project Structure:
- core/     : Business logic and API interactions
- ui/       : User interfaces (console + GUI)
- utils/    : Utilities (settings, file I/O, progress tracking)
"""

import os
from .utils import save_json, load_json

__version__ = "1.0.0"
__author__ = "nonog"

# ================================
# INITIALIZATION & SETUP
# ================================

def _initialize_config():
    """Initialize configuration file if it doesn't exist."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "parameter", "params.json")
    
    if load_json(config_path) is None:
        print("[CONFIG] No config file found - creating new one...")
        os.makedirs(os.path.join(current_dir, "parameter"), exist_ok=True)
        
        default_config = {
            "mods_per_page": 100,
            "mods_per_csv": 750,
            "data_dir": "",
            "headless": True,
            "image_path": os.path.join(current_dir, "parameter", "image.png"),
            "mintimepermods": 3,
            "request_delay": 1,
            "sessionid": "",
            "securelogin": "",
            "use_gui": False
        }
        
        save_json(config_path, default_config)
        print("\n[CONFIG] Configuration file created!")
        print("[INFO] Please complete the setup in: mods_tools/parameter/params.json")
        print("   - Set 'sessionid' and 'securelogin' with your Steam session data")
        print("   - Adjust other settings as needed")
        exit(0)


# Initialize on import
_initialize_config()

# ================================
# PUBLIC API
# ================================

# Import UI entry points
from .ui import run_console_mode, run_gui

# Import utilities
from .utils import (
    load_params,
    save_params,
    add_game_to_history,
    get_known_games,
    get_progress_tracker,
)

# Import core functionality
from .core import (
    init_api,
    fetch_all_mod_ids,
    fetch_mod_details,
    fetch_game_name,
    build_by_category,
    extract_tags,
    write_csv_for_category,
    process_collections_to_steam,
    run_from_csv_list,
)

__all__ = [
    # Version
    '__version__',
    '__author__',
    
    # UI
    'run_console_mode',
    'run_gui',
    
    # Utils
    'load_params',
    'save_params',
    'add_game_to_history',
    'get_known_games',
    'get_progress_tracker',
    
    # Core API
    'init_api',
    'fetch_all_mod_ids',
    'fetch_mod_details',
    'fetch_game_name',
    'build_by_category',
    'extract_tags',
    'write_csv_for_category',
    'process_collections_to_steam',
    'run_from_csv_list',
]

print("[OK] Welcome to the Steam Workshop Collection Toolkit")
print(f"[v{__version__}]")
