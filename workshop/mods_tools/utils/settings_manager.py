"""
Settings Manager
================
Central management for:
- Application parameters (JSON persistence)
- Game history tracking
- Progress tracking with callbacks
"""

from ..settings_manager import *

__all__ = [
    'load_params',
    'save_params',
    'update_param',
    'get_param',
    'get_all_params',
    'reset_params',
    'load_game_history',
    'save_game_history',
    'add_game_to_history',
    'get_known_games',
    'ProgressTracker',
    'get_progress_tracker',
]
