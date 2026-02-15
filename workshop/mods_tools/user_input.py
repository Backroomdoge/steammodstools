"""
User Input Module (Legacy - now uses ui_input.py)
For backwards compatibility, this module re-exports from ui_input.
"""

from .ui_input import ask_for_valid_game

__all__ = ['ask_for_valid_game']

