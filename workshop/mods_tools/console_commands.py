from .api import *
from .categories import *
from .csv_manager import *
from .steam_collection import process_collections_to_steam
from .utils import save_json, load_json
from .ui_input import ask_for_valid_game, ask_clear_data_confirmation
from .console_settings import show_settings_menu, select_game_from_list
from .settings_manager import add_game_to_history, get_progress_tracker
import shutil
import os
from tqdm import tqdm

# ================================
# BUSINESS LOGIC FUNCTIONS (No user input)
# ================================

def download_and_sort_mods(app_id: int, raw_file: str, tags_file: str, sorted_file: str, progress_tracker=None):
    """Downloads and sorts mods by category with real progress tracking."""
    if progress_tracker is None:
        progress_tracker = get_progress_tracker()
    
    try:
        print("🔄 Initializing API...")
        init_api(os.environ.get("STEAM_API_KEY"))
        
        print("🔄 Fetching mod IDs...")
        mod_ids = fetch_all_mod_ids(app_id)
        total_mods = len(mod_ids)
        progress_tracker.set_total(total_mods)
        
        print(f"🔄 Fetching details for {total_mods} mods...")
        mods = fetch_mod_details(mod_ids)
        
        # Update progress based on mods fetched
        progress_tracker.update(total_mods, f"Processing {total_mods} mods...")
        
        print("💾 Saving raw data...")
        save_json(raw_file, mods)
        
        print("🏷️  Extracting tags...")
        tags = extract_tags(mods)
        save_json(tags_file, sorted(tags))
        
        print("📁 Building categories...")
        tag_cats = build_by_category(mods, tags)
        save_json(sorted_file, tag_cats)
        
        progress_tracker.update(0, f"✔️ Download and sort completed! {total_mods} mods processed.")
        print(f"✔️ Download and sort completed! {total_mods} mods processed.")
    except Exception as e:
        progress_tracker.reset()
        raise

def generate_csv_for_categories(base_dir: str, game_name: str, sorted_file: str, selected_indices: list[int], overwrite: bool, progress_tracker=None):
    """Generates CSV files for selected categories."""
    if progress_tracker is None:
        progress_tracker = get_progress_tracker()
    
    try:
        cats = load_json(sorted_file) or {}
        if not cats:
            print("⚠ No categories available. Sort first (option 1).")
            return
        
        keys = list(cats.keys())
        total = len(selected_indices)
        
        progress_tracker.set_total(total)
        
        for i, idx in enumerate(selected_indices):
            if 0 <= idx < len(keys):
                cat_name = keys[idx]
                progress_tracker.update(1, f"Generating CSV for '{cat_name}'...")
                write_csv_for_category(base_dir, game_name, cat_name, cats[cat_name], not overwrite)
        
        progress_tracker.update(0, f"✔️ CSV generation completed for {total} category(ies).")
        print(f"✔️ CSV generation completed for {len(selected_indices)} category(ies).")
    except Exception as e:
        progress_tracker.reset()
        raise

def process_steam_collections(app_id: int, base_dir: str, sorted_file: str, selected_indices: list[int]):
    """Processes Steam collections for selected categories."""
    cats = load_json(sorted_file) or {}
    if not cats:
        print("⚠ No categories available. Sort first (option 1).")
        return
    
    keys = list(cats.keys())
    if not selected_indices:  # Empty list means "all"
        chosen = keys
    else:
        chosen = [keys[idx] for idx in selected_indices if 0 <= idx < len(keys)]
    
    process_collections_to_steam(app_id, base_dir, chosen)

def clear_all_data():
    """Clears all data folder and resets params.json to defaults."""
    # Clear data folder
    if os.path.exists("data"):
        shutil.rmtree("data")
        print("[OK] Data folder cleared.")
    
    # Reset params.json
    import os as os_module
    current_dir = os_module.path.dirname(os_module.path.abspath(__file__))
    params_path = os_module.path.join(current_dir, "parameter", "params.json")
    if os_module.path.exists(params_path):
        basedata = {
            "mods_per_page": 100,
            "mods_per_csv": 750,
            "data_dir": "",
            "headless": True,
            "image_path": "workshop\\mods_tools\\parameter\\image.png",
            "mintimepermods": 3,
            "request_delay": 1,
            "sessionid": "",
            "securelogin": ""
        }
        save_json(params_path, basedata)
        print("✔️ Parameters reset to defaults.")
    
    print("✅ All data cleared successfully.")

# ================================
# USER INPUT FUNCTIONS (Console only)
# ================================

def ask_generate_csv(sorted_file: str) -> tuple[list[int], bool]:
    """Prompts user to select categories for CSV generation."""
    cats = load_json(sorted_file) or {}
    if not cats:
        return [], False
    
    keys = list(cats.keys())
    print("\nCategories:")
    for i, cat in enumerate(keys, 1):
        print(f"{i} — {cat}")
    
    sel = input("Select ex:1,3: ").strip().split(",")
    selected = []
    for p in sel:
        try:
            idx = int(p) - 1
            if 0 <= idx < len(keys):
                selected.append(idx)
        except ValueError:
            pass
    
    mode = input("1=Overwrite | 2=Add: ").strip()
    overwrite = mode == "1"
    
    return selected, overwrite

def ask_steam_collections(sorted_file: str) -> list[int]:
    """Prompts user to select categories for Steam collections."""
    cats = load_json(sorted_file) or {}
    if not cats:
        return []
    
    keys = list(cats.keys())
    print("\nCategories:")
    print("0 - All")
    for i, cat in enumerate(keys, 1):
        print(f"{i} — {cat}")
    
    sel = input("Select (ex:1,3 or 0): ").strip()
    
    if sel == "0":
        return []  # Empty list means "all"
    
    selected = []
    for x in sel.split(","):
        try:
            idx = int(x.strip()) - 1
            if 0 <= idx < len(keys):
                selected.append(idx)
        except ValueError:
            pass
    
    return selected

def ask_clear_data_confirmation() -> bool:
    """Prompts user to confirm clearing all data."""
    confirm = input("Are you sure you want to delete all data and reset params? (yes/no): ").strip().lower()
    return confirm == "yes"

# ================================
# CONSOLE PROGRESS TRACKING
# ================================

_console_progress_bar = None

def _console_progress_callback(current: int, total: int, message: str) -> None:
    """Console progress bar callback."""
    global _console_progress_bar
    
    if total == 0:
        return
    
    # Create progress bar on first call or if total changed
    if _console_progress_bar is None or _console_progress_bar.total != total:
        if _console_progress_bar is not None:
            _console_progress_bar.close()
        _console_progress_bar = tqdm(total=total, desc="Progress", unit="mod")
    
    # Update bar position
    if current >= _console_progress_bar.n:
        _console_progress_bar.update(current - _console_progress_bar.n)
    
    # Update message
    if message:
        _console_progress_bar.set_description(f"Progress - {message}")

def _close_console_progress_bar() -> None:
    """Close the console progress bar."""
    global _console_progress_bar
    if _console_progress_bar is not None:
        _console_progress_bar.close()
        _console_progress_bar = None
# ================================
# MAIN CONSOLE UI
# ================================

def _print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def _print_menu(options, title="Main Menu"):
    """Print a formatted menu with options."""
    _print_header(title)
    for key, description in options:
        print(f"  [{key}] {description}")
    print("=" * 60)

def _print_status(message, status="info"):
    """Print a status message with formatting."""
    if status == "success":
        print(f"\n[SUCCESS] {message}")
    elif status == "error":
        print(f"\n[ERROR] {message}")
    elif status == "warning":
        print(f"\n[WARNING] {message}")
    else:
        print(f"\n[INFO] {message}")

def run_console_mode():
    # Register console progress callback
    progress_tracker = get_progress_tracker()
    progress_tracker.register_callback(_console_progress_callback)
    
    try:
        _print_header("Steam Workshop Collection Toolkit")
        print("Welcome! Let's get started.\n")
        
        app_id, game_name = select_game_from_list()
        add_game_to_history(app_id, game_name)
        base_dir = f"data/{app_id}_{game_name}"
        os.makedirs(base_dir, exist_ok=True)

        tags_file = os.path.join(base_dir, "tags_list.json")
        raw_file = os.path.join(base_dir, "mods_raw.json")
        sorted_file = os.path.join(base_dir, "mods_by_category.json")

        while True:
            # Display current game and status
            print(f"\n┌─ Current Game: {game_name} (AppID: {app_id})")
            print("│")
            
            # Check which files exist for status
            has_raw = os.path.exists(raw_file)
            has_sorted = os.path.exists(sorted_file)
            has_csv = os.path.exists(os.path.join(base_dir, "csv"))
            
            status_text = []
            if has_raw:
                status_text.append("Raw data: [OK]")
            if has_sorted:
                status_text.append("Categories: [OK]")
            if has_csv:
                status_text.append("CSV: [OK]")
            
            if status_text:
                print(f"│ Status: {' | '.join(status_text)}")
            else:
                print("│ Status: No data downloaded yet")
            print("└─────────────────────────────────\n")
            
            # Menu options
            menu_options = [
                ("0", "Change Game"),
                ("1", "Download & Sort Mods"),
                ("2", "Create/Modify Categories"),
                ("3", "Modify Custom Category"),
                ("4", "Generate CSV"),
                ("5", "Create Steam Collection"),
                ("6", "Clear All Data"),
                ("7", "Settings"),
                ("q", "Quit")
            ]
            
            _print_menu(menu_options, "What would you like to do?")
            cmd = input("\nEnter your choice: ").strip().lower()

            if cmd == "0":
                app_id, game_name = select_game_from_list()
                add_game_to_history(app_id, game_name)
                base_dir = f"data/{app_id}_{game_name}"
                os.makedirs(base_dir, exist_ok=True)
                tags_file = os.path.join(base_dir, "tags_list.json")
                raw_file = os.path.join(base_dir, "mods_raw.json")
                sorted_file = os.path.join(base_dir, "mods_by_category.json")
                _print_status(f"Switched to: {game_name}", "success")

            elif cmd == "1":
                _print_header("Download & Sort Mods")
                print("This will download all mods and sort them by category.")
                print("This may take a while depending on the number of mods.\n")
                confirm = input("Continue? (yes/no): ").strip().lower()
                if confirm in ["yes", "y"]:
                    try:
                        download_and_sort_mods(app_id, raw_file, tags_file, sorted_file)
                        _print_status("Download and sort completed!", "success")
                    except Exception as e:
                        _print_status(f"Failed: {str(e)}", "error")
                else:
                    _print_status("Operation cancelled", "warning")

            elif cmd == "2":
                _print_header("Create/Modify Categories")
                if not os.path.exists(sorted_file):
                    _print_status("No category data found. Download & Sort first!", "error")
                else:
                    print("Opening category modification tool...")
                    # Placeholder - would call category editing function

            elif cmd == "3":
                _print_header("Modify Custom Category")
                print("This allows you to rename or customize categories.")
                # Placeholder - would call custom category editing

            elif cmd == "4":
                _print_header("Generate CSV")
                if not os.path.exists(sorted_file):
                    _print_status("No category data found. Download & Sort first!", "error")
                else:
                    selected, overwrite = ask_generate_csv(sorted_file)
                    if selected:
                        try:
                            generate_csv_for_categories(base_dir, game_name, sorted_file, selected, overwrite)
                            _print_status(f"CSV generated for {len(selected)} categories", "success")
                        except Exception as e:
                            _print_status(f"Failed: {str(e)}", "error")
                    else:
                        _print_status("No categories selected", "warning")

            elif cmd == "5":
                _print_header("Create Steam Collection")
                if not os.path.exists(sorted_file):
                    _print_status("No category data found. Download & Sort first!", "error")
                else:
                    selected = ask_steam_collections(sorted_file)
                    if selected:
                        try:
                            process_steam_collections(app_id, base_dir, sorted_file, selected)
                            _print_status("Collection creation completed!", "success")
                        except Exception as e:
                            _print_status(f"Failed: {str(e)}", "error")
                    else:
                        _print_status("No categories selected", "warning")

            elif cmd == "6":
                _print_header("Clear All Data")
                print("WARNING: This will delete all downloaded data and CSV files for this game.")
                confirm = input("Are you sure? (yes/no): ").strip().lower()
                if confirm in ["yes", "y"]:
                    try:
                        clear_all_data()
                        _print_status("All data cleared successfully", "success")
                    except Exception as e:
                        _print_status(f"Failed to clear data: {str(e)}", "error")
                else:
                    _print_status("Operation cancelled", "warning")

            elif cmd == "7":
                show_settings_menu()

            elif cmd == "q":
                print("\n" + "=" * 60)
                print(" Thank you for using Steam Workshop Collection Toolkit!")
                print("=" * 60 + "\n")
                break
            
            else:
                _print_status("Invalid choice. Please try again.", "warning")
    finally:
        # Clean up progress bar
        _close_console_progress_bar()
        progress_tracker.unregister_callback(_console_progress_callback)