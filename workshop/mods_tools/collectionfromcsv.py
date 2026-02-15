import os
import pandas as pd
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from tqdm import tqdm
from .utils import load_params
from .ui_input import ask_steam_login_confirmation, ask_headless_mode_warning

# Here we import your existing addfromrequest module
# It must define: bulk_add_from_csv(csv_path, collection_id, title)
from .addfromrequest import bulkadd_from_csv

params = load_params()

class CollectionFromCSV:
    def __init__(self, appid: str):
        self.appid = appid
        self.driver = self._init_driver()
        self.collection_url = None
        self.collection_id = None

    def _init_driver(self):
        chrome_options = Options()
        # Chrome profile with Steam logged in
        chrome_options.add_argument(r"--user-data-dir=" + params["data_dir"])
        chrome_options.add_argument("--profile-directory=Default")

        # Options Chrome visibles
        chrome_options.add_argument("--disable-gpu")
        if params.get("headless"):
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")

        return webdriver.Chrome(options=chrome_options)

    def check_steam_logged_in(self) -> bool:
        """
        Checks if Steam is logged in in the Chrome profile.
        """
        self.driver.get("https://steamcommunity.com/")
        try:
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "a.user_avatar"))
            )
            return True
        except TimeoutException:
            return False

    def create_collection(self, name: str, description: str, image_path: str, category: str):
        """
        Creates a Steam Workshop collection with the provided information
        and returns True if successful.
        """
        url = f"https://steamcommunity.com/workshop/editcollection/?appid={self.appid}"
        self.driver.get(url)

        try:
            title_input = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "title"))
            )
            title_input.send_keys(name)

            img_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
            img_input.send_keys(os.path.abspath(image_path))

            desc_input = self.driver.find_element(By.ID, "description")
            desc_input.send_keys(description)

            cats = self.driver.find_elements(By.CSS_SELECTOR, "input[name='tags[]']")
            for c in cats:
                if c.get_attribute("value").strip().lower() == category.strip().lower():
                    self.driver.execute_script("arguments[0].scrollIntoView();", c)
                    c.click()
                    break

            save_btn = self.driver.find_element(
                By.XPATH,
                "//a[contains(@class,'saveCollection') or contains(text(),'Enregistrer') or contains(text(),'Save')]"
            )
            save_btn.click()

            WebDriverWait(self.driver, 10).until(lambda d: d.current_url != url)

            self.collection_url = self.driver.current_url
            # The ID is after &id= in the URL
            if "id=" in self.collection_url:
                self.collection_id = self.collection_url.split("id=")[-1].split("&")[0]
            print(f"[OK] Collection created → {self.collection_url}")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to create collection: {e}")
            return False

    def add_mod_fast(self, mod_id: str, collection_name: str):
        """
        Adds a mod to the collection (selenium mode).
        """
        self.driver.get(f"https://steamcommunity.com/sharedfiles/filedetails/?id={mod_id}")

        try:
            btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "AddToCollectionBtn"))
            )
            btn.click()
        except TimeoutException:
            print(f"[I] No AddToCollection button for {mod_id}")
            return False

        try:
            boxes = WebDriverWait(self.driver, 5).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "input.add_to_collection_dialog_checkbox")
                )
            )
            for box in boxes:
                title_attr = box.get_attribute("data-title")
                if title_attr and title_attr.strip().lower() == collection_name.strip().lower():
                    box.click()
                    break
        except TimeoutException:
            print(f"[I] Collection popup not found for {mod_id}")
            return False

        try:
            ok_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH,
                     "//div[contains(@class,'btn_green_steamui') and contains(@class,'btn_medium')]/span[contains(text(),'OK')]")
                )
            )
            ok_btn.click()
        except TimeoutException:
            print(f"[WARN] OK button not found, assuming the addition succeeded")

        return True

    def quit(self):
        self.driver.quit()


def run_from_csv_list(appid: str, category: str, csv_files: list[str], mode="hybrid"):
    """
    Reads CSV files, creates collection then adds all mods
    according to mode:
      - "selenium"
      - "hybrid" (with addfromrequest.bulk_add_from_csv)
    """

    for idx_csv, csv in enumerate(csv_files, start=1):
        print(f"\nCSV {idx_csv}/{len(csv_files)} → {csv}")

        if not os.path.exists(csv):
            print(f"[WARN] File not found → {csv}")
            continue

        df = pd.read_csv(csv, header=None)
        mods = df[0].dropna().astype(str).tolist()

        if not mods:
            print("[ERROR] No mods to process.")
            continue

        coll_name = os.path.splitext(os.path.basename(csv))[0]
        coll_desc = coll_name

        steam = CollectionFromCSV(appid)

        print("➡️ Checking Steam connection…")
        if not steam.check_steam_logged_in():
            print("❌ Not logged in to Steam in this Chrome profile.")
            if params.get("headless"):
                ask_headless_mode_warning()
            else:
                ask_steam_login_confirmation()
                print("you can now restart the script")
            steam.quit()
            exit()
            return

        print("➡️ Creating collection…")
        if not steam.create_collection(coll_name, coll_desc, params['image_path'], category):
            steam.quit()
            return

        if mode == "hybrid":
            print(f"➡️ Adding mods in hybrid mode ({len(mods)} mods)…")
            try:
                # Call to your external module
                bulkadd_from_csv(csv, steam.collection_id, coll_name)
                print("✔️ bulk_add_from_csv completed.")
            except Exception as e:
                print(f"[ERROR] bulk_add_from_csv: {e}")

        else:
            print(f"➡️ Adding mods in selenium mode ({len(mods)} mods)…")
            timer = params.get("mintimepermods", 0)
            with tqdm(mods, desc="Adding mods") as pbar:
                for mod in pbar:
                    t1 = time.time()
                    steam.add_mod_fast(mod, coll_name)
                    t2 = time.time()
                    dif = t2 - t1
                    if dif < timer:
                        time.sleep(timer - dif)

        # Close driver before moving to next or finishing
        steam.quit()

    print("\n🎉 All CSV files processed!")
