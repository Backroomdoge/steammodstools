import requests
from tqdm import tqdm

from .utils import save_json, load_json, load_params

params = load_params() 
STEAM_API_KEY = None

def init_api(key: str):
    global STEAM_API_KEY
    STEAM_API_KEY = key

QUERY_URL = "https://api.steampowered.com/IPublishedFileService/QueryFiles/v1/"
DETAILS_URL = "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"
APP_DETAILS_URL = "https://store.steampowered.com/api/appdetails"

def fetch_game_name(app_id: int) -> str:
    try:
        r = requests.get(APP_DETAILS_URL, params={"appids": app_id})
        data = r.json()
        return data.get(str(app_id), {}).get("data", {}).get("name")
    except:
        return None

def fetch_all_mod_ids(app_id: int):
    if not STEAM_API_KEY:
        raise ValueError("API key not set!")
    init = requests.get(QUERY_URL, params={
        "key": STEAM_API_KEY,
        "appid": app_id,
        "numperpage": 1,
        "page": 1
    }).json()
    total = init["response"].get("total", 0)

    mod_ids = []
    per_page = params["mods_per_page"]
    page = 1
    progress = tqdm(total=total, desc="IDs retrieved", unit="mod")

    while True:
        r = requests.get(QUERY_URL, params={
            "key": STEAM_API_KEY,
            "appid": app_id,
            "numperpage": per_page,
            "page": page,
            "return_details": True
        }).json()

        details = r["response"].get("publishedfiledetails", [])
        if not details:
            break
        for item in details:
            mod_ids.append(item["publishedfileid"])
            progress.update(1)

        if len(details) < per_page:
            break
        page += 1

    progress.close()
    return mod_ids

def fetch_mod_details(mod_ids: list[int]):
    total = len(mod_ids)
    mods = []
    progress = tqdm(range(0, total, 100), desc="Downloading metadata", unit="batch")
    for i in progress:
        chunk = mod_ids[i:i+100]
        payload = {
            "itemcount": len(chunk),
            **{f"publishedfileids[{j}]": mid for j, mid in enumerate(chunk)}
        }
        try:
            r = requests.post(DETAILS_URL, data=payload).json()
            mods.extend(r["response"]["publishedfiledetails"])
        except:
            continue
    return mods
