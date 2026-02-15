"""
Console Settings Interface
==========================
Provides console-based UI for editing application settings.
"""

import os
import shutil
from .settings_manager import (
    load_params, save_params, update_param, get_param,
    reset_params, load_game_history, add_game_to_history
)
from .api import fetch_game_name

def show_settings_menu():
    """Display main settings menu."""
    while True:
        params = load_params()
        
        print("\n" + "="*60)
        print(" APPLICATION SETTINGS")
        print("="*60)
        print("\n  [1] API Settings")
        print("  [2] GUI/Console Settings")
        print("  [3] Chrome Settings")
        print("  [4] Mod Processing Settings")
        print("  [5] View All Settings")
        print("  [6] Reset to Defaults")
        print("  [7] Data & Cache Management")
        print("  [q] Back to Main Menu")
        print("="*60)
        
        choice = input("\nSelect option: ").strip().lower()
        
        if choice == "1":
            _edit_api_settings(params)
        elif choice == "2":
            _edit_ui_settings(params)
        elif choice == "3":
            _edit_chrome_settings(params)
        elif choice == "4":
            _edit_processing_settings(params)
        elif choice == "5":
            _view_all_settings(params)
        elif choice == "6":
            print("\n" + "="*60)
            print(" WARNING: Reset Settings to Defaults?")
            print("="*60)
            print("This action CANNOT be undone. All your settings will be reset.")
            confirm = input("\nAre you absolutely sure? (yes/no): ").lower()
            if confirm in ["yes", "y"]:
                if reset_params():
                    print("\n[SUCCESS] Settings reset to defaults")
                else:
                    print("\n[ERROR] Failed to reset settings")
            else:
                print("\n[INFO] Operation cancelled")
        elif choice == "7":
            _show_deletion_menu()
        elif choice == "q":
            break
        else:
            print("Invalid option")


def _edit_api_settings(params: dict):
    """Edit API-related settings."""
    print("\n" + "="*50)
    print("API SETTINGS")
    print("="*50)
    
    sessionid = params.get("sessionid", "")
    securelogin = params.get("securelogin", "")
    
    print(f"\nCurrent Session ID: {sessionid[:20]}..." if sessionid else "\nCurrent Session ID: Not set")
    print(f"Current Secure Login: {securelogin[:20]}..." if securelogin else "Current Secure Login: Not set")
    
    if input("\nEdit Session ID? (yes/no): ").lower() == "yes":
        sessionid = input("Enter new Session ID: ").strip()
        update_param("sessionid", sessionid)
        print("✅ Session ID updated")
    
    if input("Edit Secure Login? (yes/no): ").lower() == "yes":
        securelogin = input("Enter new Secure Login: ").strip()
        update_param("securelogin", securelogin)
        print("✅ Secure Login updated")


def _edit_ui_settings(params: dict):
    """Edit UI/Console settings."""
    print("\n" + "="*50)
    print("GUI/CONSOLE SETTINGS")
    print("="*50)
    
    use_gui = params.get("use_gui", False)
    headless = params.get("headless", True)
    
    print(f"\nCurrent UI Mode: {'GUI (Tkinter)' if use_gui else 'Console'}")
    print(f"Current Headless Mode: {'Yes' if headless else 'No'}")
    
    if input("\nChange UI Mode? (yes/no): ").lower() == "yes":
        mode = input("Use GUI? (yes/no): ").lower() == "yes"
        update_param("use_gui", mode)
        print(f"✅ UI Mode set to {'GUI' if mode else 'Console'}")
    
    if input("Change Headless Mode? (yes/no): ").lower() == "yes":
        headless = input("Headless mode (yes/no, no=see browser): ").lower() == "yes"
        update_param("headless", headless)
        print(f"✅ Headless Mode set to {'Yes' if headless else 'No'}")


def _edit_chrome_settings(params: dict):
    """Edit Chrome-related settings."""
    print("\n" + "="*50)
    print("CHROME SETTINGS")
    print("="*50)
    
    data_dir = params.get("data_dir", "")
    image_path = params.get("image_path", "")
    
    print(f"\nCurrent Chrome Data Dir: {data_dir if data_dir else 'Not set'}")
    print(f"Current Image Path: {image_path if image_path else 'Not set'}")
    
    if input("\nEdit Chrome Data Dir? (yes/no): ").lower() == "yes":
        data_dir = input("Enter Chrome User Data Directory path: ").strip()
        update_param("data_dir", data_dir)
        print("✅ Chrome Data Dir updated")
    
    if input("Edit Collection Image Path? (yes/no): ").lower() == "yes":
        image_path = input("Enter image path for collections: ").strip()
        update_param("image_path", image_path)
        print("✅ Image Path updated")


def _edit_processing_settings(params: dict):
    """Edit mod processing settings."""
    print("\n" + "="*50)
    print("MOD PROCESSING SETTINGS")
    print("="*50)
    
    mods_per_page = params.get("mods_per_page", 100)
    mods_per_csv = params.get("mods_per_csv", 750)
    request_delay = params.get("request_delay", 1)
    mintimepermods = params.get("mintimepermods", 3)
    
    print(f"\nCurrent Mods Per Page: {mods_per_page}")
    print(f"Current Mods Per CSV: {mods_per_csv}")
    print(f"Current Request Delay (seconds): {request_delay}")
    print(f"Current Min Time Per Mod (seconds): {mintimepermods}")
    
    if input("\nEdit Mods Per Page? (yes/no): ").lower() == "yes":
        try:
            value = int(input("Enter new value: ").strip())
            update_param("mods_per_page", value)
            print("✅ Mods Per Page updated")
        except ValueError:
            print("❌ Invalid value")
    
    if input("Edit Mods Per CSV? (yes/no): ").lower() == "yes":
        try:
            value = int(input("Enter new value: ").strip())
            update_param("mods_per_csv", value)
            print("✅ Mods Per CSV updated")
        except ValueError:
            print("❌ Invalid value")
    
    if input("Edit Request Delay? (yes/no): ").lower() == "yes":
        try:
            value = float(input("Enter new value (seconds): ").strip())
            update_param("request_delay", value)
            print("✅ Request Delay updated")
        except ValueError:
            print("❌ Invalid value")
    
    if input("Edit Min Time Per Mod? (yes/no): ").lower() == "yes":
        try:
            value = float(input("Enter new value (seconds): ").strip())
            update_param("mintimepermods", value)
            print("✅ Min Time Per Mod updated")
        except ValueError:
            print("❌ Invalid value")


def _view_all_settings(params: dict):
    """Display all current settings."""
    print("\n" + "="*50)
    print("ALL SETTINGS")
    print("="*50)
    
    for key, value in params.items():
        # Mask sensitive data
        if key in ["sessionid", "securelogin"]:
            display_value = f"{str(value)[:15]}..." if value else "Not set"
        else:
            display_value = value
        
        print(f"{key}: {display_value}")


def select_game_from_list() -> tuple[int, str]:
    """
    Let user select a game from history or enter new one.
    Returns: (app_id, game_name)
    """
    from .api import fetch_game_name
    
    games = load_game_history()
    
    if games:
        print("\n" + "="*60)
        print(" KNOWN GAMES")
        print("="*60)
        
        for i, game in enumerate(games, 1):
            print(f"  [{i}] {game['name']}")
            print(f"      └─ AppID: {game['app_id']}\n")
        
        print(f"  [{len(games) + 1}] Enter a new App ID")
        print("="*60)
        
        choice = input("\nSelect game (enter number): ").strip()
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(games):
                game = games[idx]
                app_id = int(game["app_id"])
                name = game["name"]
                add_game_to_history(app_id, name)
                print(f"\n[SUCCESS] Selected: {name}\n")
                return app_id, name
        except ValueError:
            pass
    
    # Manual entry
    print("\n" + "="*60)
    print(" ENTER NEW GAME")
    print("="*60)
    
    while True:
        print("\nHow to find your game's App ID:")
        print("  1. Go to store.steampowered.com")
        print("  2. Search for your game")
        print("  3. The App ID is in the URL after 'app/'")
        print("  Example: store.steampowered.com/app/123456 → ID is 123456\n")
        
        app_id_str = input("Enter Steam App ID: ").strip()
        if not app_id_str.isdigit():
            print("[ERROR] Invalid ID - please enter a number (digits only)")
            continue
        
        print("\n[INFO] Fetching game information...")
        app_id = int(app_id_str)
        name = fetch_game_name(app_id)
        
        if not name:
            print("[ERROR] Unable to retrieve game name for this ID")
            print("        Please verify the App ID and try again\n")
            continue
        
        print(f"\n[SUCCESS] Game found: {name}")
        confirm = input("Is this correct? (yes/no): ").strip().lower()
        
        if confirm in ("yes", "y"):
            normalized_name = name.replace(" ", "_")
            add_game_to_history(app_id, name)
            return app_id, normalized_name
        
        print("Please try again")

# ================================
# DATA & CACHE MANAGEMENT
# ================================

def _show_deletion_menu():
    """Show menu for deleting data and cache."""
    while True:
        print("\n" + "="*50)
        print("🗑️  DATA & CACHE MANAGEMENT")
        print("="*50)
        print("\n1 - Delete Current Game Data (keeps parameters)")
        print("2 - Delete All Data Folder (keeps parameters)")
        print("3 - Delete Everything (data + parameters)")
        print("q - Back")
        
        choice = input("\nSelect option: ").strip().lower()
        
        if choice == "1":
            _delete_current_game_data()
        elif choice == "2":
            _delete_all_data()
        elif choice == "3":
            _delete_everything()
        elif choice == "q":
            break
        else:
            print("Invalid option")


def _delete_current_game_data():
    """Delete CSV and data for the current game only."""
    app_id_str = input("\nEnter App ID to delete (or leave empty to cancel): ").strip()
    
    if not app_id_str:
        print("❌ Cancelled")
        return
    
    try:
        app_id = int(app_id_str)
        game_name = input("Enter game name (as shown in data folder): ").strip()
        
        if not game_name:
            print("❌ Cancelled")
            return
        
        folder = f"data/{app_id}_{game_name}"
        
        if not os.path.exists(folder):
            print(f"⚠️  Folder not found: {folder}")
            return
        
        confirm = input(f"Delete '{folder}'? (yes/no): ").strip().lower()
        
        if confirm in ("yes", "y"):
            shutil.rmtree(folder)
            print(f"✅ Deleted: {folder}")
        else:
            print("❌ Cancelled")
    
    except ValueError:
        print("⚠️  Invalid App ID")


def _delete_all_data():
    """Delete entire data folder but keep parameters."""
    confirm = input("Delete entire 'data' folder? (all games) (yes/no): ").strip().lower()
    
    if confirm not in ("yes", "y"):
        print("❌ Cancelled")
        return
    
    if os.path.exists("data"):
        shutil.rmtree("data")
        print("✅ Data folder deleted")
    else:
        print("⚠️  Data folder not found")
    
    print("✓ Parameters saved in: workshop/mods_tools/parameter/params.json")


def _delete_everything():
    """Delete all data and parameters."""
    print("\n⚠️  WARNING: This will delete EVERYTHING including parameters!")
    confirm = input("Are you absolutely sure? (yes/no): ").strip().lower()
    
    if confirm not in ("yes", "y"):
        print("❌ Cancelled")
        return
    
    final_confirm = input("Type 'DELETE ALL' to confirm: ").strip()
    
    if final_confirm != "DELETE ALL":
        print("❌ Cancelled")
        return
    
    # Delete data folder
    if os.path.exists("data"):
        shutil.rmtree("data")
        print("✅ Data folder deleted")
    
    # Reset parameters to defaults
    if reset_params():
        print("✅ Parameters reset to defaults")
    
    print("✅ All cleaned up!")