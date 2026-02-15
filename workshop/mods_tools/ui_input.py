"""
UI Input Module
===============
Centralized module for all user input/UI interactions.
Separates console UI from business logic.
Use this module for console-based input, or replace with your own UI implementation.
"""

import requests
from pathlib import Path

from .api import fetch_game_name


# ================================
# GAME SELECTION INPUT
# ================================

def ask_for_valid_game() -> tuple[int, str]:
    """
    Asks the user to enter a valid Steam App ID
    and returns (app_id, game_name_normalized).
    
    Can be replaced with UI implementation.
    """
    while True:
        ans = input("Enter the Steam game ID: ").strip()
        if not ans.isdigit():
            print("⚠ Invalid ID — please enter a number.")
            continue

        app_id = int(ans)
        name = fetch_game_name(app_id)
        if not name:
            print("⚠ Unable to retrieve game name for this ID.")
            continue

        print(f"This game is: {name}")
        confirm = input("Is this the correct game? (o/n): ").strip().lower()
        if confirm in ("o", "oui", "y", "yes"):
            normalized = name.replace(" ", "_")
            return app_id, normalized

        print("Please re-enter the App ID.")


# ================================
# STEAM COLLECTION INPUT
# ================================

def ask_steam_collection_mode() -> str:
    """
    Asks user to choose global processing mode for Steam collections.
    Returns: "1", "2", "3", or "4"
    """
    print("\n=== Global processing mode choice ===")
    print("  1 → Process all (create collection for all CSV)")
    print("  2 → Only new CSV")
    print("  3 → Choose CSV manually")
    print("  4 → Add only FAILED CSV")
    return input("Your choice (1,2,3 or 4): ").strip()


def ask_process_confirmation(summary: dict) -> bool:
    """
    Shows summary of CSV to be processed and asks for confirmation.
    
    Args:
        summary: Dict with category names as keys and CSV file counts as values
    
    Returns: True if user confirms, False otherwise
    """
    print("\n📋 Summary of available CSV:")
    for cat, count in summary.items():
        print(f"  • {cat} → {count} files")
    
    return input("\n➡ Confirm execution? (o/n): ").lower() in ("o", "oui", "y", "yes")


def ask_manual_csv_selection(csv_list: list[str]) -> list[str]:
    """
    Prompts user to manually select CSV files from a list.
    
    Args:
        csv_list: List of CSV file paths
    
    Returns: List of selected CSV file paths
    """
    print("\nCSV available for selection:")
    for i, csv in enumerate(csv_list, 1):
        print(f"  {i} — {Path(csv).name}")
    
    sel = input("Select (ex: 1,3): ").split(",")
    chosen = []
    for p in sel:
        if p.strip().isdigit():
            idx = int(p.strip()) - 1
            if 0 <= idx < len(csv_list):
                chosen.append(csv_list[idx])
    return chosen


# ================================
# STEAM LOGIN INPUT
# ================================

def ask_steam_login_confirmation() -> bool:
    """
    Asks user to confirm they have logged into Steam in Selenium browser.
    
    Returns: True when user is ready to continue
    """
    input("Press enter once you have connected to steam on selenium: ")
    return True


def ask_headless_mode_warning() -> None:
    """
    Warns user that headless mode needs to be disabled for first sign-in.
    """
    print('Please restart the script using headless=false to proceed to the first sign in')


# ================================
# DATA CLEARING INPUT
# ================================

def ask_clear_data_confirmation() -> bool:
    """
    Asks user to confirm clearing all data and resetting params.
    
    Returns: True if user confirms "yes", False otherwise
    """
    confirm = input("Are you sure you want to delete all data and reset params? (yes/no): ").strip().lower()
    return confirm == "yes"
