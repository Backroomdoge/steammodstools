import json
import shutil
from pathlib import Path
from datetime import datetime
from .collectionfromcsv import run_from_csv_list
from .ui_input import ask_steam_collection_mode, ask_process_confirmation, ask_manual_csv_selection

PROCESSED_DB = "collections_processed.json"
ARCHIVE_DIR = "archived_csv"
LOG_DIR = "log"
LOG_FILE = "processing.log"

#################################
#         LOGGING UTILS
#################################

def ensure_log_dir(base_dir: str) -> Path:
    p = Path(base_dir) / LOG_DIR
    p.mkdir(parents=True, exist_ok=True)
    return p

def log_write(base_dir: str, msg: str):
    log_path = ensure_log_dir(base_dir) / LOG_FILE
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")
    print(msg)

#################################
#       JSON DB UTILITIES
#################################

def load_processed_db(base_dir: str) -> dict:
    db_path = Path(base_dir) / PROCESSED_DB
    if db_path.exists():
        try:
            return json.loads(db_path.read_text(encoding="utf-8"))
        except Exception as e:
            log_write(base_dir, f"[WARN] Failed to read {PROCESSED_DB}: {e}")
    return {}

def save_processed_db(base_dir: str, db: dict):
    db_path = Path(base_dir) / PROCESSED_DB
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4)

#################################
#       ARCHIVE UTILITY
#################################

def archive_csv(base_dir: str, csv_path: str):
    archive_root = Path(base_dir) / ARCHIVE_DIR
    archive_root.mkdir(parents=True, exist_ok=True)
    target = archive_root / Path(csv_path).name
    try:
        shutil.move(csv_path, target)
        log_write(base_dir, f"📦 CSV archived: {target.name}")
    except Exception as e:
        log_write(base_dir, f"[WARN] Failed to archive {Path(csv_path).name}: {e}")

#################################
#   BUSINESS LOGIC - COLLECTIONS
#################################

def process_collections_to_steam_with_input(app_id: int, base_dir: str, categories: list[str]):
    """
    Main entry point for console UI - handles input and business logic.
    Asks user for processing mode and confirmation before proceeding.
    """
    mode = ask_steam_collection_mode()
    
    # Collect CSV files
    work_map = _collect_csv_by_category(base_dir, categories)
    
    if not work_map:
        print("\n⚠ No category with valid CSV.")
        return
    
    # Show summary and ask for confirmation
    summary = {cat: len(csvs) for cat, csvs in work_map.items()}
    if not ask_process_confirmation(summary):
        print("❌ Global processing cancelled.")
        return
    
    # Process collections
    process_collections_to_steam_internal(app_id, base_dir, work_map, mode)


def process_collections_to_steam(app_id: int, base_dir: str, categories: list[str], mode: str = None, confirm: bool = True):
    """
    Core business logic for processing collections to Steam.
    
    Args:
        app_id: Steam app ID
        base_dir: Base directory for data
        categories: List of category names
        mode: Processing mode ("1", "2", "3", or "4"). If None, asks user.
        confirm: Whether to ask for confirmation. If False, proceeds directly.
    """
    if mode is None:
        # Interactive mode - ask user
        process_collections_to_steam_with_input(app_id, base_dir, categories)
        return
    
    # Programmatic mode - mode is specified
    work_map = _collect_csv_by_category(base_dir, categories)
    
    if not work_map:
        print("\n⚠ No category with valid CSV.")
        return
    
    if confirm:
        summary = {cat: len(csvs) for cat, csvs in work_map.items()}
        if not ask_process_confirmation(summary):
            print("❌ Processing cancelled.")
            return
    
    process_collections_to_steam_internal(app_id, base_dir, work_map, mode)


def _collect_csv_by_category(base_dir: str, categories: list[str]) -> dict:
    """
    Internal helper: collects CSV files organized by category.
    
    Returns: Dict mapping category names to lists of CSV file paths
    """
    work_map = {}
    
    for cat in categories:
        csv_dir = Path(base_dir) / "csv" / cat
        if not csv_dir.exists():
            continue
        
        csv_files = sorted(csv_dir.glob("*.csv"))
        if csv_files:
            work_map[cat] = [str(p) for p in csv_files]
    
    return work_map


def process_collections_to_steam_internal(app_id: int, base_dir: str, work_map: dict, mode: str):
    """
    Internal: Processes collections according to mode.
    
    Args:
        app_id: Steam app ID
        base_dir: Base directory for data
        work_map: Dict of category -> CSV file paths
        mode: Processing mode ("1", "2", "3", or "4")
    """
    processed_db = load_processed_db(base_dir)
    
    for cat, csv_list in work_map.items():
        log_write(base_dir, f"\n➡️ Processing for '{cat}'…")
        
        # ensure correct JSON structure
        cat_record = processed_db.get(cat)
        if not isinstance(cat_record, dict):
            log_write(base_dir, f"[WARN] Invalid JSON structure for '{cat}' → reinitialization.")
            cat_record = {"collections": {}, "failed_done": []}
            processed_db[cat] = cat_record
        else:
            if "collections" not in cat_record or not isinstance(cat_record["collections"], dict):
                cat_record["collections"] = {}
            if "failed_done" not in cat_record or not isinstance(cat_record["failed_done"], list):
                cat_record["failed_done"] = []
        
        for csv_path in csv_list:
            csv_name = Path(csv_path).name
            is_failed = "failed" in csv_name.lower()
            
            # --- MODE 4: ONLY failed ---
            if mode == "4" and not is_failed:
                log_write(base_dir, f"[SKIP] '{csv_name}' is not failed (mode 4).")
                continue
            
            # --- MODE 2: only new ---
            if mode == "2" and not is_failed:
                if csv_name in cat_record["collections"]:
                    log_write(base_dir, f"[SKIP] '{csv_name}' already processed.")
                    continue
            
            # --- MODE 3: manual selection ---
            if mode == "3" and not is_failed:
                selected = ask_manual_csv_selection(csv_list)
                if csv_path not in selected:
                    log_write(base_dir, f"[SKIP] '{csv_name}' not manually selected.")
                    continue
            
            # --- processing a failed CSV ---
            if is_failed:
                log_write(base_dir, f"⚠ Processing failed → {csv_name}")
                
                normalized = csv_name.replace("_FAILED", "")
                base_csv = normalized if normalized.endswith(".csv") else f"{normalized}.csv"
                
                collections_map = cat_record["collections"]
                if base_csv not in collections_map:
                    log_write(base_dir, f"[ERROR] Original collection '{base_csv}' not found → skip.")
                    continue
                
                coll_id = collections_map[base_csv].get("collection_id")
                
                log_write(base_dir, f"➡ Adding mods from failed in collection '{base_csv}' (id={coll_id})")
                try:
                    run_from_csv_list(str(app_id), cat, [csv_path], mode="hybrid_failed")
                except Exception as e:
                    log_write(base_dir, f"[ERROR] Failed to add failed '{csv_name}': {e}")
                    continue
                
                archive_csv(base_dir, csv_path)
                
                if csv_name not in cat_record["failed_done"]:
                    cat_record["failed_done"].append(csv_name)
                
                save_processed_db(base_dir, processed_db)
                continue
            
            # --- processing a normal CSV ---
            log_write(base_dir, f"🟢 Normal CSV processing → {csv_name}")
            try:
                run_from_csv_list(str(app_id), cat, [csv_path])
            except Exception as e:
                log_write(base_dir, f"[ERROR] Failed to create / add for '{csv_name}': {e}")
                continue
            
            # update JSON
            collections_map = cat_record.setdefault("collections", {})
            if csv_name not in collections_map:
                collections_map[csv_name] = {"collection_id": None, "added_mods": []}
            
            save_processed_db(base_dir, processed_db)
    
    save_processed_db(base_dir, processed_db)
    log_write(base_dir, "\n✔️ Processing completed for all categories!")
