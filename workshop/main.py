"""
Steam Workshop Collection Toolkit - Main Entry Point
=====================================================

Start the Steam Workshop Mod Manager in console or GUI mode.

Usage:
    python main.py              # Start in default mode (console or GUI based on params.json)
    python main.py --gui        # Force GUI mode
    python main.py --console    # Force console mode

Configuration:
    Edit workshop/mods_tools/parameter/params.json to customize settings
"""

import sys
from mods_tools import run_console_mode, run_gui, load_params

def main():
    """Main entry point."""
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--gui":
            print("[GUI] Starting GUI mode...")
            run_gui()
            return
        elif sys.argv[1] == "--console":
            print("[CONSOLE] Starting console mode...")
            run_console_mode()
            return
        else:
            print("Usage: python main.py [--gui|--console]")
            sys.exit(1)
    
    # Use setting from params.json
    params = load_params()
    use_gui = params.get("use_gui", False)
    
    if use_gui:
        print("[GUI] Starting GUI mode...")
        run_gui()
    else:
        print("[CONSOLE] Starting console mode...")
        run_console_mode()

if __name__ == "__main__":
    main()
