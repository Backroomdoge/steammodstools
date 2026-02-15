"""
Settings Manager Module
=======================
Centralized management of application settings.
Handles parameter editing, game history tracking, and progress callbacks.
"""

import json
import os
from pathlib import Path
from typing import Any, Callable, Dict, Optional, List


# Use dynamic path relative to this file
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARAMS_PATH = os.path.join(CURRENT_DIR, "parameter", "params.json")
GAMES_HISTORY_PATH = "known_games.json"


def get_params_path() -> str:
    """Get the full path to params.json"""
    return PARAMS_PATH


def load_params() -> dict:
    """Load parameters from JSON file."""
    try:
        with open(PARAMS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_params(params: dict) -> bool:
    """Save parameters to JSON file."""
    try:
        Path(PARAMS_PATH).parent.mkdir(parents=True, exist_ok=True)
        with open(PARAMS_PATH, "w", encoding="utf-8") as f:
            json.dump(params, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving params: {e}")
        return False


def update_param(key: str, value: Any) -> bool:
    """Update a single parameter."""
    params = load_params()
    params[key] = value
    return save_params(params)


def get_param(key: str, default: Any = None) -> Any:
    """Get a single parameter value."""
    params = load_params()
    return params.get(key, default)


def get_all_params() -> dict:
    """Get all parameters."""
    return load_params()


def reset_params() -> bool:
    """Reset parameters to defaults."""
    default_params = {
        "mods_per_page": 100,
        "mods_per_csv": 750,
        "data_dir": "",
        "headless": True,
        "image_path": "workshop\\mods_tools\\parameter\\image.png",
        "mintimepermods": 3,
        "request_delay": 1,
        "sessionid": "",
        "securelogin": "",
        "use_gui": False
    }
    return save_params(default_params)


# ================================
# GAME HISTORY MANAGEMENT
# ================================

def load_game_history() -> List[Dict[str, str]]:
    """Load known games from history file."""
    try:
        if Path(GAMES_HISTORY_PATH).exists():
            with open(GAMES_HISTORY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return []


def save_game_history(games: List[Dict[str, str]]) -> bool:
    """Save known games to history file."""
    try:
        with open(GAMES_HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(games, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving game history: {e}")
        return False


def add_game_to_history(app_id: int, game_name: str) -> bool:
    """Add a game to the history if not already there."""
    games = load_game_history()
    
    # Check if game already exists
    for game in games:
        if game.get("app_id") == str(app_id):
            return True
    
    # Add new game
    games.insert(0, {"app_id": str(app_id), "name": game_name})
    
    # Keep only last 20 games
    games = games[:20]
    
    return save_game_history(games)


def get_known_games() -> List[Dict[str, str]]:
    """Get list of known games from history."""
    return load_game_history()


# ================================
# PROGRESS TRACKING
# ================================

class ProgressTracker:
    """Tracks progress and calls registered callbacks."""
    
    def __init__(self):
        self.callbacks: List[Callable[[int], None]] = []
        self.current: int = 0
        self.total: int = 0
        self.message: str = ""
    
    def register_callback(self, callback: Callable[[int, int, str], None]) -> None:
        """
        Register a callback for progress updates.
        Callback signature: callback(current, total, message)
        """
        self.callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable) -> None:
        """Unregister a callback."""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def set_total(self, total: int) -> None:
        """Set total items to process."""
        self.total = total
        self.current = 0
        self._notify()
    
    def update(self, amount: int = 1, message: str = "") -> None:
        """Update progress by amount."""
        self.current += amount
        if message:
            self.message = message
        self._notify()
    
    def set_message(self, message: str) -> None:
        """Set progress message."""
        self.message = message
        self._notify()
    
    def reset(self) -> None:
        """Reset progress."""
        self.current = 0
        self.total = 0
        self.message = ""
        self._notify()
    
    def _notify(self) -> None:
        """Notify all registered callbacks."""
        for callback in self.callbacks:
            try:
                callback(self.current, self.total, self.message)
            except Exception as e:
                print(f"Error in progress callback: {e}")
    
    def get_percentage(self) -> int:
        """Get progress as percentage."""
        if self.total == 0:
            return 0
        return int((self.current / self.total) * 100)


# Global progress tracker instance
progress_tracker = ProgressTracker()


def get_progress_tracker() -> ProgressTracker:
    """Get the global progress tracker instance."""
    return progress_tracker
