import requests
import time
import os
import csv
from tqdm import tqdm
from .utils import load_params

params = load_params()

waittime = params["request_delay"]
SESSIONID = params["sessionid"]
SECURE = params["securelogin"]

COOKIE = f"sessionid={SESSIONID}; steamLoginSecure={SECURE}"

ADD_URL = "https://steamcommunity.com/sharedfiles/ajaxaddtocollections"
MAX_RETRIES = 3


# ==============================
# STEAM REQUEST
# ==============================

def add_to_collec(mod_id, collection_id, title="auto"):

    headers = {
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": COOKIE,
        "Referer": f"https://steamcommunity.com/sharedfiles/filedetails/?id={mod_id}",
    }

    data = {
        "sessionID": SESSIONID,
        "publishedfileid": mod_id,
        f"collections[{collection_id}][add]": "true",
        f"collections[{collection_id}][title]": title,
    }

    try:
        r = requests.post(ADD_URL, headers=headers, data=data, timeout=20)
        return r.json()
    except:
        return {"success": 0}


# ==============================
# CSV HELPERS
# ==============================

def read_mods_from_csv(path):
    mods = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if row:
                mods.append(row[0].strip())
    return mods


def save_errors(csv_path, errors):
    if not errors:
        return

    err_path = csv_path.replace(".csv", "_FAILED.csv")

    with open(err_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        for e in errors:
            w.writerow([e])

    print(f"\n⚠️ Failed mods saved → {err_path}")


# ==============================
# BULK FROM ONE CSV
# ==============================

def bulkadd_from_csv(csv_path, collection_id, title="auto"):

    if not os.path.exists(csv_path):
        print(f"❌ CSV not found: {csv_path}")
        return

    mods = read_mods_from_csv(csv_path)
    total_mods = len(mods)

    print(f"\n📄 CSV selected: {os.path.basename(csv_path)}")
    print(f"📦 {total_mods} mods detected\n")

    success_count = 0
    fail_count = 0
    errors = []

    start_time = time.time()

    bar = tqdm(mods, desc="Adding mods", unit="mod")

    for mod in bar:

        success = False

        for attempt in range(MAX_RETRIES):
            t1 = time.time()

            result = add_to_collec(mod, collection_id, title)

            if result.get("success") == 1:
                success = True
                break

            time.sleep(2)

        if success:
            success_count += 1
        else:
            fail_count += 1
            errors.append(mod)

        # ETA calculation
        elapsed = time.time() - start_time
        rate = bar.n / elapsed if elapsed > 0 else 0
        remaining = (total_mods - bar.n) / rate if rate else 0

        bar.set_postfix(
            ETA=f"{int(remaining//60)}m {int(remaining%60)}s",
            OK=success_count,
            ERR=fail_count
        )

        # respect rate limit
        dif = time.time() - t1
        if dif < waittime:
            time.sleep(waittime - dif)

    bar.close()

    save_errors(csv_path, errors)

    print("\n==============================")
    print("✅ BULK COMPLETED")
    print(f"✔ Success: {success_count}")
    print(f"❌ Failures: {fail_count}")
    print("==============================")


