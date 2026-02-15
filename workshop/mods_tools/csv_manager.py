import os, csv
from .utils import load_params

params = load_params()
MAX_MODS_PER_CSV = params["mods_per_csv"]

def write_csv_for_category(base_dir: str, game_name: str, cat_name: str, mods_list: list[int], add_new: bool):
    csv_dir = os.path.join(base_dir, "csv", cat_name)
    if not add_new:
        if os.path.exists(csv_dir):
            for f in os.listdir(csv_dir):
                os.remove(os.path.join(csv_dir, f))
        os.makedirs(csv_dir, exist_ok=True)

    existing = set()
    if add_new and os.path.exists(csv_dir):
        for fname in os.listdir(csv_dir):
            with open(os.path.join(csv_dir, fname), "r", encoding="utf-8") as f:
                for row in f:
                    existing.add(row.strip())

    new_mods = [m for m in mods_list if str(m) not in existing]
    if not new_mods:
        return

    files = sorted(os.listdir(csv_dir)) if os.path.exists(csv_dir) else []
    next_idx = 1
    for f in files:
        try:
            idx = int(f.split("_")[-1].split(".")[0])
            next_idx = max(next_idx, idx+1)
        except:
            pass

    idx=next_idx; chunk=[]
    for m in new_mods:
        chunk.append(m)
        if len(chunk)>=MAX_MODS_PER_CSV:
            fname=f"{game_name}_{cat_name}_{idx}.csv"
            with open(os.path.join(csv_dir, fname),"w",newline="",encoding="utf-8") as fw:
                w=csv.writer(fw)
                for mm in chunk: w.writerow([mm])
            idx+=1; chunk=[]
    if chunk:
        fname=f"{game_name}_{cat_name}_{idx}.csv"
        with open(os.path.join(csv_dir, fname),"w",newline="",encoding="utf-8") as fw:
            w=csv.writer(fw)
            for mm in chunk: w.writerow([mm])
