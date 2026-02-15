import json
import shutil
from pathlib import Path
from datetime import datetime

from .collectionfromcsv import run_from_csv_list
from .ui_input import (
    ask_steam_collection_mode,
    ask_process_confirmation,
    ask_manual_csv_selection,
)

PROCESSED_DB = "collections_processed.json"
ARCHIVE_DIR = "archived_csv"
LOG_DIR = "log"
LOG_FILE = "processing.log"


#################################
#         LOGGING
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
#         JSON DB
#################################

def load_processed_db(base_dir: str) -> dict:
    db_path = Path(base_dir) / PROCESSED_DB
    if db_path.exists():
        return json.loads(db_path.read_text(encoding="utf-8"))
    return {}


def save_processed_db(base_dir: str, db: dict):
    db_path = Path(base_dir) / PROCESSED_DB
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4)


#################################
#         ARCHIVE
#################################

def archive_csv(base_dir: str, csv_path: str):
    archive_root = Path(base_dir) / ARCHIVE_DIR
    archive_root.mkdir(parents=True, exist_ok=True)

    target = archive_root / Path(csv_path).name
    shutil.move(csv_path, target)

    log_write(base_dir, f"📦 Archived: {target.name}")


#################################
#         MAIN ENTRY
#################################

def process_collections_to_steam_with_input(app_id, base_dir, categories):

    mode = ask_steam_collection_mode()

    work_map = _collect_csv_by_category(base_dir, categories)

    if not work_map:
        print("⚠ No CSV found")
        return

    summary = {c: len(v) for c, v in work_map.items()}

    if not ask_process_confirmation(summary):
        return

    process_collections_to_steam_internal(app_id, base_dir, work_map, mode)


def process_collections_to_steam(app_id, base_dir, categories, mode=None):

    if mode is None:
        process_collections_to_steam_with_input(app_id, base_dir, categories)
        return

    work_map = _collect_csv_by_category(base_dir, categories)

    process_collections_to_steam_internal(app_id, base_dir, work_map, mode)


#################################
#         COLLECT CSV
#################################

def _collect_csv_by_category(base_dir, categories):

    work_map = {}

    for cat in categories:
        csv_dir = Path(base_dir) / "csv" / cat
        if not csv_dir.exists():
            continue

        files = sorted(csv_dir.glob("*.csv"))

        if files:
            work_map[cat] = [str(p) for p in files]

    return work_map


#################################
#         CORE LOGIC
#################################

def process_collections_to_steam_internal(app_id, base_dir, work_map, mode):

    db = load_processed_db(base_dir)

    for cat, csv_list in work_map.items():

        log_write(base_dir, f"\n➡ Category: {cat}")

        cat_record = db.setdefault(cat, {"collections": {}, "failed_done": []})

        to_process = []
        failed_to_process = []

        # ---------- BUILD LISTS ----------
        for csv_path in csv_list:

            name = Path(csv_path).name
            is_failed = "failed" in name.lower()

            if is_failed:
                if mode == "4":
                    failed_to_process.append(csv_path)
                continue

            if mode == "2" and name in cat_record["collections"]:
                continue

            if mode == "3":
                selected = ask_manual_csv_selection(csv_list)
                if csv_path not in selected:
                    continue

            to_process.append(csv_path)

        # ---------- NORMAL CSV BATCH ----------
        if to_process:
            log_write(base_dir, f"🟢 Processing {len(to_process)} CSV in batch")

            try:
                run_from_csv_list(str(app_id), cat, to_process)
            except Exception as e:
                log_write(base_dir, f"[ERROR] Batch failed: {e}")

            for path in to_process:
                name = Path(path).name
                cat_record["collections"][name] = {"collection_id": None}

        # ---------- FAILED CSV ----------
        for failed in failed_to_process:

            fname = Path(failed).name

            log_write(base_dir, f"⚠ Handling FAILED → {fname}")

            base_name = fname.replace("_FAILED", "")

            if not base_name.endswith(".csv"):
                base_name += ".csv"

            if base_name not in cat_record["collections"]:
                log_write(base_dir, f"[SKIP] No parent collection found")
                continue

            try:
                run_from_csv_list(str(app_id), cat, [failed], mode="hybrid_failed")
                archive_csv(base_dir, failed)
                cat_record["failed_done"].append(fname)
            except Exception as e:
                log_write(base_dir, f"[ERROR] Failed import: {e}")

        save_processed_db(base_dir, db)

    log_write(base_dir, "\n✔ ALL DONE")
