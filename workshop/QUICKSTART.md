# Quick Start Guide

## 5-Minute Setup

### 1. Install
```bash
pip install -r workshop/requirements.txt
```

### 2. Run
```bash
python workshop/main.py
```

### 3. Configure
The app will create `workshop/mods_tools/parameter/params.json`

Edit it and add your Steam credentials:
```json
{
  "sessionid": "YOUR_SESSIONID_HERE",
  "securelogin": "YOUR_SECURELOGIN_HERE",
  "headless": true,
  "use_gui": false
}
```

### 4. Done!
Run again and start using the app.

---

## Getting Steam Credentials

### Chrome/Chromium:
1. Go to `steamcommunity.com`
2. Open DevTools (`F12`)
3. Go to `Storage` → `Cookies` → `https://steamcommunity.com`
4. Find and copy:
   - `sessionid` - paste into `params.json`
   - `steamLoginSecure` - paste into `securelogin` in `params.json`

### Firefox:
1. Go to `steamcommunity.com`
2. Open DevTools (`F12`)
3. Go to `Storage` → `Cookies`
4. Find `steamcommunity.com`
5. Copy `sessionid` and `steamLoginSecure`

---

## First Steps

### Console Mode (Default)
```
0 - Change Game        → Select a Steam game
1 - Download & Sort    → Fetch mods and organize by category
4 - Generate CSV       → Create CSV files for categories
5 - Steam Collection   → Upload mods to Steam collections
7 - Settings           → Configure the app
```

### GUI Mode
1. Edit `params.json`: set `"use_gui": true`
2. Run `python workshop/main.py`
3. Click tabs to access features
4. Select a game to start

---

## Example Workflow

### Console:
```
Main Menu: 0
→ Select game from history or enter App ID
Main Menu: 1
→ Download mods (shows progress bar)
Main Menu: 4
→ Select categories to export to CSV
Main Menu: 5
→ Select categories to create Steam collections
```

### GUI:
```
Start → Select Game → Download & Sort tab → Click "Start"
→ Generate CSV tab → Select categories → "Generate Selected CSV"
→ Steam Collections tab → Select categories → "Create Collections"
```

---

## Data Organization

Files are stored in `data/{app_id}_{game_name}/`:
- `mods_raw.json` - All downloaded mods
- `mods_by_category.json` - Mods organized by tag
- `csv/` - Generated CSV files
- `log/` - Operation logs

---

## Troubleshooting

### "Failed to connect"
- Check your Steam credentials are correct and recent
- Verify internet connection
- Try increasing `request_delay` in settings

### "No mods found"
- Game might not have Workshop enabled
- Verify App ID is correct
- Check Steam isn't blocking the request

### Progress bar not showing
- This is normal for fast operations
- For console: ensure terminal supports ANSI colors
- For GUI: wait a bit, it updates asynchronously

---

## Need Help?

1. Check `README.md` for full documentation
2. Review logs in `data/{app_id}_{name}/log/processing.log`
3. Look at example workflows in `EXAMPLES.md` (if available)
4. Create an issue on GitHub

---

**Enjoy managing your Steam mods! 🎮**
