"""
Utilities module
================
Contains helper functions for:
- Settings and configuration management
- File I/O operations
- User input handling
- Progress tracking
"""

from .settings_manager import *
from .file_utils import *
from .input_handlers import *

__all__ = [
    # Settings
    'load_params',
    'save_params',
    'get_progress_tracker',
    'add_game_to_history',
    'get_known_games',
    
    # File utilities
    'load_json',
    'save_json',
    
    # Input
    'select_game_from_list',
]
