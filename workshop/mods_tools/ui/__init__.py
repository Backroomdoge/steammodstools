"""
UI module (User Interfaces)
===========================
Contains both console and GUI implementations.
Each provides access to the same business logic.
"""

from .console import *
from .gui import *

__all__ = [
    'run_console_mode',
    'run_gui',
]
