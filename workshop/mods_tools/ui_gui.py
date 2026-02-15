"""
GUI Module using Tkinter
========================
User-friendly graphical interface for Steam Workshop Mod Manager.
Provides the same functionality as console_commands but with a modern GUI.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from typing import Optional, Callable
import os

from .console_commands import (
    download_and_sort_mods,
    generate_csv_for_categories,
    clear_all_data,
)
from .steam_collection import process_collections_to_steam
from .utils import load_json, load_params
from .settings_manager import (
    load_params as load_all_params,
    save_params,
    get_known_games,
    add_game_to_history,
    get_progress_tracker,
)
from .api import fetch_game_name


class ModManagerGUI:
    """Main GUI window for the Steam Workshop Mod Manager."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Steam Workshop Mod Manager - GUI")
        self.root.geometry("900x700")
        
        self.app_id = None
        self.game_name = None
        self.base_dir = None
        self.params = load_all_params()
        
        # Setup progress tracker callback
        self.progress_tracker = get_progress_tracker()
        self.progress_tracker.register_callback(self._on_progress_update)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        self._setup_ui()
        self._select_game_dialog()
    
    def _setup_ui(self):
        """Setup the main UI layout."""
        # Header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.game_label = ttk.Label(header_frame, text="No game selected", 
                                     font=("Arial", 12, "bold"))
        self.game_label.pack(side=tk.LEFT)
        
        change_btn = ttk.Button(header_frame, text="Change Game", 
                               command=self._select_game_dialog)
        change_btn.pack(side=tk.RIGHT, padx=5)
        
        # Notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self._create_download_tab()
        self._create_csv_tab()
        self._create_collections_tab()
        self._create_settings_tab()
    
    def _select_game_dialog(self):
        """Show game selection dialog."""
        SelectGameWindow(self.root, self._on_game_selected)
    
    def _on_game_selected(self, app_id: int, game_name: str):
        """Callback when game is selected."""
        self.app_id = app_id
        self.game_name = game_name
        self.base_dir = f"data/{app_id}_{game_name}"
        os.makedirs(self.base_dir, exist_ok=True)
        self.game_label.config(text=f"Game: {game_name} (AppID {app_id})")
        add_game_to_history(app_id, game_name)
    
    # ================================
    # DOWNLOAD & SORT TAB
    # ================================
    
    def _create_download_tab(self):
        """Create the Download & Sort tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Download & Sort")
        
        # Description
        desc = ttk.Label(frame, text="Download all mods and sort them by category",
                        wraplength=400, font=("Arial", 10))
        desc.pack(padx=20, pady=20)
        
        # Button
        download_btn = ttk.Button(frame, text="Start Download & Sort",
                                 command=self._on_download_click)
        download_btn.pack(pady=10)
        
        # Progress bar
        self.download_progress = ttk.Progressbar(frame, length=400, mode='determinate')
        self.download_progress.pack(pady=20, padx=20, fill=tk.X)
        
        # Percentage label
        self.download_percent = ttk.Label(frame, text="0%")
        self.download_percent.pack()
        
        # Status label
        self.download_status = ttk.Label(frame, text="Ready", wraplength=400)
        self.download_status.pack(padx=20, pady=10)
    
    def _on_download_click(self):
        """Handle download & sort button click."""
        if not self._check_game_selected():
            return
        
        thread = threading.Thread(target=self._download_thread)
        thread.daemon = True
        thread.start()
    
    def _download_thread(self):
        """Background thread for download & sort."""
        try:
            self.download_status.config(text="Starting download...")
            self.root.after(0, lambda: self.root.update_idletasks())
            
            raw_file = os.path.join(self.base_dir, "mods_raw.json")
            tags_file = os.path.join(self.base_dir, "tags_list.json")
            sorted_file = os.path.join(self.base_dir, "mods_by_category.json")
            
            # Pass progress tracker to the function
            download_and_sort_mods(self.app_id, raw_file, tags_file, sorted_file, 
                                 progress_tracker=self.progress_tracker)
            
            self.root.after(0, lambda: messagebox.showinfo("Success", "Download and sort completed!"))
            self.root.after(0, lambda: self.download_status.config(text="Completed!"))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Download failed: {str(e)}"))
            self.root.after(0, lambda: self.download_status.config(text="Failed"))
        finally:
            self.root.after(0, lambda: (
                self.download_progress.__setitem__('value', 0),
                self.download_percent.config(text="0%")
            ))
    
    # ================================
    # CSV GENERATION TAB
    # ================================
    
    def _create_csv_tab(self):
        """Create the Generate CSV tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Generate CSV")
        
        # Description
        desc = ttk.Label(frame, text="Select categories to generate CSV files",
                        wraplength=400, font=("Arial", 10))
        desc.pack(padx=20, pady=10)
        
        # Mode selection
        mode_frame = ttk.LabelFrame(frame, text="Generation Mode", padding=10)
        mode_frame.pack(padx=20, pady=5, fill=tk.X)
        
        self.csv_mode = tk.StringVar(value="1")
        ttk.Radiobutton(mode_frame, text="Overwrite existing CSV", 
                       variable=self.csv_mode, value="1").pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="Add to existing CSV", 
                       variable=self.csv_mode, value="2").pack(anchor=tk.W)
        
        # Main content frame
        content_frame = ttk.Frame(frame)
        content_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        # Left: Categories listbox
        left_frame = ttk.LabelFrame(content_frame, text="Available Categories (Ctrl+Click to select multiple)", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        scrollbar = ttk.Scrollbar(left_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.csv_categories = tk.Listbox(left_frame, yscrollcommand=scrollbar.set,
                                         selectmode=tk.MULTIPLE, font=("Arial", 9))
        self.csv_categories.pack(fill=tk.BOTH, expand=True)
        self.csv_categories.bind('<<ListboxSelect>>', self._on_category_selection_changed)
        scrollbar.config(command=self.csv_categories.yview)
        
        # Right: Preview panel
        right_frame = ttk.LabelFrame(content_frame, text="Preview - CSV Files to Create", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        preview_scroll = ttk.Scrollbar(right_frame)
        preview_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.csv_preview = tk.Text(right_frame, height=20, width=30, 
                                   yscrollcommand=preview_scroll.set, state=tk.DISABLED)
        self.csv_preview.pack(fill=tk.BOTH, expand=True)
        preview_scroll.config(command=self.csv_preview.yview)
        
        # Buttons frame
        button_frame = ttk.Frame(frame)
        button_frame.pack(padx=20, pady=10, fill=tk.X)
        
        refresh_btn = ttk.Button(button_frame, text="Refresh Categories", 
                                command=self._load_categories_for_csv)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        generate_btn = ttk.Button(button_frame, text="Generate Selected CSV",
                                 command=self._on_csv_click)
        generate_btn.pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.csv_progress = ttk.Progressbar(frame, length=400, mode='determinate')
        self.csv_progress.pack(pady=10, padx=20, fill=tk.X)
        
        self.csv_status = ttk.Label(frame, text="Ready", font=("Arial", 9))
        self.csv_status.pack(padx=20, pady=5)
        
        # Load categories on tab activation
        self.notebook.bind("<<NotebookTabChanged>>", self._on_csv_tab_activate)
    
    def _on_csv_tab_activate(self, event=None):
        """Load categories when CSV tab is activated."""
        try:
            if self.notebook.index(self.notebook.select()) == 1:  # CSV tab index
                self._load_categories_for_csv()
        except:
            pass
    
    def _load_categories_for_csv(self):
        """Load categories from sorted mods."""
        self.csv_categories.delete(0, tk.END)
        self.csv_preview.config(state=tk.NORMAL)
        self.csv_preview.delete("1.0", tk.END)
        self.csv_preview.config(state=tk.DISABLED)
        
        if not self.app_id:
            self.csv_status.config(text="[ERROR] No game selected")
            return
        
        sorted_file = os.path.join(self.base_dir, "mods_by_category.json")
        cats = load_json(sorted_file) or {}
        
        if not cats:
            self.csv_status.config(text="[ERROR] No categories found. Download & sort first!")
            return
        
        for cat in sorted(cats.keys()):
            self.csv_categories.insert(tk.END, cat)
        
        self.csv_status.config(text=f"✓ Found {len(cats)} categories")
    
    def _on_category_selection_changed(self, event=None):
        """Update preview when selection changes."""
        selected_indices = self.csv_categories.curselection()
        
        self.csv_preview.config(state=tk.NORMAL)
        self.csv_preview.delete("1.0", tk.END)
        
        if not selected_indices:
            self.csv_preview.insert(tk.END, "Select categories to see\nwhich CSV files will be\ncreated...")
            self.csv_preview.config(state=tk.DISABLED)
            return
        
        # Get selected categories
        selected_cats = [self.csv_categories.get(i) for i in selected_indices]
        
        # Show what will be created
        preview_text = "CSV Files to Create:\n" + "="*28 + "\n\n"
        
        for cat in selected_cats:
            preview_text += f"📁 {cat}/\n"
            preview_text += f"   └─ {cat}_1.csv\n"
            preview_text += f"   └─ {cat}_2.csv (if needed)\n"
            preview_text += f"   └─ ... etc\n\n"
        
        preview_text += f"\nTotal: {len(selected_cats)} categories"
        
        self.csv_preview.insert("1.0", preview_text)
        self.csv_preview.config(state=tk.DISABLED)

    def _on_csv_click(self):
        """Handle CSV generation button click."""
        if not self._check_game_selected():
            return
        
        selected_indices = self.csv_categories.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "Please select at least one category")
            return
        
        # Show what will be created
        selected_cats = [self.csv_categories.get(i) for i in selected_indices]
        msg = f"Generate CSV for these {len(selected_cats)} categories:\n\n"
        msg += "\n".join([f"  • {cat}" for cat in selected_cats])
        msg += f"\n\nMode: {'Overwrite existing' if self.csv_mode.get() == '1' else 'Add to existing'}"
        
        if messagebox.askyesno("Confirm", msg):
            overwrite = self.csv_mode.get() == "1"
            self.csv_status.config(text="⏳ Generating CSV files...")
            
            thread = threading.Thread(target=self._csv_thread, 
                                     args=(list(selected_indices), overwrite))
            thread.daemon = True
            thread.start()
    
    def _csv_thread(self, indices, overwrite):
        """Background thread for CSV generation."""
        try:
            sorted_file = os.path.join(self.base_dir, "mods_by_category.json")
            generate_csv_for_categories(self.base_dir, self.game_name, sorted_file, 
                                       indices, overwrite, progress_tracker=self.progress_tracker)
            
            self.root.after(0, lambda: self.csv_status.config(text="[OK] CSV generation completed!"))
            self.root.after(0, lambda: messagebox.showinfo("Success", "CSV generation completed!"))
            
        except Exception as e:
            self.root.after(0, lambda: self.csv_status.config(text="[ERROR] CSV generation failed"))
            self.root.after(0, lambda: messagebox.showerror("Error", f"CSV generation failed: {str(e)}"))
        finally:
            self.root.after(0, lambda: self.csv_progress.__setitem__('value', 0))
    
    # ================================
    # STEAM COLLECTIONS TAB
    # ================================
    
    def _create_collections_tab(self):
        """Create the Steam Collections tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Steam Collections")
        
        # Description
        desc = ttk.Label(frame, text="Create Steam collections from CSV files",
                        wraplength=400, font=("Arial", 10))
        desc.pack(padx=20, pady=10)
        
        # Mode selection
        mode_frame = ttk.LabelFrame(frame, text="Processing Mode", padding=10)
        mode_frame.pack(padx=20, pady=5, fill=tk.X)
        
        self.collection_mode = tk.StringVar(value="1")
        ttk.Radiobutton(mode_frame, text="Process all CSV", 
                       variable=self.collection_mode, value="1").pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="Only new CSV", 
                       variable=self.collection_mode, value="2").pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="Only failed CSV", 
                       variable=self.collection_mode, value="4").pack(anchor=tk.W)
        
        # Category selection
        cat_frame = ttk.LabelFrame(frame, text="Categories to Process (Ctrl+Click to select multiple)", padding=10)
        cat_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(cat_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.collection_categories = tk.Listbox(cat_frame, yscrollcommand=scrollbar.set,
                                               selectmode=tk.MULTIPLE, font=("Arial", 9))
        self.collection_categories.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.collection_categories.yview)
        
        # Summary label
        self.collection_summary = ttk.Label(frame, text="", font=("Arial", 9))
        self.collection_summary.pack(padx=20, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(padx=20, pady=10, fill=tk.X)
        
        refresh_btn = ttk.Button(button_frame, text="Refresh Categories",
                                command=self._load_categories_for_collections)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        process_btn = ttk.Button(button_frame, text="Create Collections",
                                command=self._on_collections_click)
        process_btn.pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.collection_progress = ttk.Progressbar(frame, length=400, mode='determinate')
        self.collection_progress.pack(pady=10, padx=20, fill=tk.X)
        
        self.collection_status = ttk.Label(frame, text="Ready", font=("Arial", 9))
        self.collection_status.pack(padx=20, pady=5)
        
        # Load categories when tab is activated
        self.notebook.bind("<<NotebookTabChanged>>", self._on_collections_tab_activate)
    
    def _on_collections_tab_activate(self, event=None):
        """Load categories when Collections tab is activated."""
        try:
            if self.notebook.index(self.notebook.select()) == 2:  # Collections tab index
                self._load_categories_for_collections()
        except:
            pass
    
    def _load_categories_for_collections(self):
        """Load categories from sorted mods with CSV files."""
        self.collection_categories.delete(0, tk.END)
        
        if not self.app_id:
            self.collection_summary.config(text="[ERROR] No game selected")
            return
        
        sorted_file = os.path.join(self.base_dir, "mods_by_category.json")
        cats = load_json(sorted_file) or {}
        
        if not cats:
            self.collection_summary.config(text="[ERROR] No categories found. Download & sort first!")
            return
        
        # Check which categories have CSV files
        csv_cats = []
        for cat in sorted(cats.keys()):
            csv_dir = os.path.join(self.base_dir, "csv", cat)
            if os.path.exists(csv_dir) and os.listdir(csv_dir):
                csv_count = len([f for f in os.listdir(csv_dir) if f.endswith('.csv')])
                csv_cats.append((cat, csv_count))
                self.collection_categories.insert(tk.END, f"{cat} ({csv_count} CSV)")
        
        if csv_cats:
            self.collection_summary.config(text=f"[OK] Found {len(csv_cats)} categories with CSV files")
        else:
            self.collection_summary.config(text="[ERROR] No CSV files found. Generate CSV first!")
    
    def _on_collections_click(self):
        """Handle collections processing button click."""
        if not self._check_game_selected():
            return
        
        selected_indices = self.collection_categories.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "Please select at least one category")
            return
        
        # Get selected categories
        selected_items = [self.collection_categories.get(i) for i in selected_indices]
        selected_cats = [item.split(" (")[0] for item in selected_items]  # Remove CSV count
        
        mode_text = {
            "1": "Process all CSV",
            "2": "Only new CSV",
            "4": "Only failed CSV"
        }
        
        msg = f"Create collections for these {len(selected_cats)} categories:\n\n"
        msg += "\n".join([f"  • {cat}" for cat in selected_cats])
        msg += f"\n\nMode: {mode_text[self.collection_mode.get()]}"
        
        if messagebox.askyesno("Confirm", msg):
            self.collection_status.config(text="⏳ Creating collections...")
            mode = self.collection_mode.get()
            
            thread = threading.Thread(target=self._collections_thread, 
                                     args=(selected_cats, mode))
            thread.daemon = True
            thread.start()
    
    def _collections_thread(self, selected_cats, mode):
        """Background thread for collections processing."""
        try:
            if not selected_cats:
                self.root.after(0, lambda: messagebox.showwarning("Warning", "No categories selected"))
                self.root.after(0, lambda: self.collection_status.config(text="[ERROR] No categories selected"))
                return
            
            self.root.after(0, lambda: self.collection_progress.__setitem__('value', 0))
            
            process_collections_to_steam(self.app_id, self.base_dir, selected_cats, mode=mode, confirm=False)
            
            self.root.after(0, lambda: self.collection_status.config(text="[OK] Collections created successfully!"))
            self.root.after(0, lambda: messagebox.showinfo("Success", "Collections processing completed!"))
            
        except Exception as e:
            self.root.after(0, lambda: self.collection_status.config(text="[ERROR] Collections processing failed"))
            self.root.after(0, lambda: messagebox.showerror("Error", f"Collections processing failed: {str(e)}"))
        finally:
            self.root.after(0, lambda: self.collection_progress.__setitem__('value', 0))
    
    # ================================
    # SETTINGS TAB
    # ================================
    
    def _create_settings_tab(self):
        """Create the Settings tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Settings")
        
        # Create a canvas with scrollbar for settings
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # API Settings
        api_frame = ttk.LabelFrame(scrollable_frame, text="API Settings", padding=10)
        api_frame.pack(padx=10, pady=10, fill=tk.X)
        
        ttk.Label(api_frame, text="Session ID:").pack(anchor=tk.W)
        self.sessionid_var = tk.StringVar(value=self.params.get("sessionid", ""))
        ttk.Entry(api_frame, textvariable=self.sessionid_var, width=40).pack(anchor=tk.W, padx=5)
        
        ttk.Label(api_frame, text="Secure Login:").pack(anchor=tk.W, pady=(10, 0))
        self.securelogin_var = tk.StringVar(value=self.params.get("securelogin", ""))
        ttk.Entry(api_frame, textvariable=self.securelogin_var, width=40).pack(anchor=tk.W, padx=5)
        
        # UI Settings
        ui_frame = ttk.LabelFrame(scrollable_frame, text="UI Settings", padding=10)
        ui_frame.pack(padx=10, pady=10, fill=tk.X)
        
        self.headless_var = tk.BooleanVar(value=self.params.get("headless", True))
        ttk.Checkbutton(ui_frame, text="Headless Mode (hide browser)", variable=self.headless_var).pack(anchor=tk.W)
        
        # Processing Settings
        proc_frame = ttk.LabelFrame(scrollable_frame, text="Processing Settings", padding=10)
        proc_frame.pack(padx=10, pady=10, fill=tk.X)
        
        ttk.Label(proc_frame, text="Mods Per Page:").pack(anchor=tk.W)
        self.mods_per_page_var = tk.StringVar(value=str(self.params.get("mods_per_page", 100)))
        ttk.Spinbox(proc_frame, from_=10, to=500, textvariable=self.mods_per_page_var, width=10).pack(anchor=tk.W, padx=5)
        
        ttk.Label(proc_frame, text="Mods Per CSV:").pack(anchor=tk.W, pady=(10, 0))
        self.mods_per_csv_var = tk.StringVar(value=str(self.params.get("mods_per_csv", 750)))
        ttk.Spinbox(proc_frame, from_=100, to=2000, textvariable=self.mods_per_csv_var, width=10).pack(anchor=tk.W, padx=5)
        
        ttk.Label(proc_frame, text="Request Delay (seconds):").pack(anchor=tk.W, pady=(10, 0))
        self.request_delay_var = tk.StringVar(value=str(self.params.get("request_delay", 1)))
        ttk.Spinbox(proc_frame, from_=0.1, to=10, textvariable=self.request_delay_var, width=10).pack(anchor=tk.W, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(padx=10, pady=20, fill=tk.X)
        
        ttk.Button(button_frame, text="Save Settings", command=self._save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset to Defaults", command=self._reset_settings).pack(side=tk.LEFT, padx=5)
        
        # Data management frame
        data_frame = ttk.LabelFrame(scrollable_frame, text="Data & Cache Management", padding=10)
        data_frame.pack(padx=10, pady=10, fill=tk.X)
        
        ttk.Button(data_frame, text="Delete Current Game Data", 
                  command=self._delete_current_game_data_gui).pack(side=tk.LEFT, padx=5)
        ttk.Button(data_frame, text="Delete All Data Folder", 
                  command=self._delete_all_data_gui).pack(side=tk.LEFT, padx=5)
        ttk.Button(data_frame, text="Delete Everything", 
                  command=self._delete_everything_gui).pack(side=tk.LEFT, padx=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _save_settings(self):
        """Save settings to params.json."""
        try:
            params = load_all_params()
            params["sessionid"] = self.sessionid_var.get()
            params["securelogin"] = self.securelogin_var.get()
            params["headless"] = self.headless_var.get()
            params["mods_per_page"] = int(self.mods_per_page_var.get())
            params["mods_per_csv"] = int(self.mods_per_csv_var.get())
            params["request_delay"] = float(self.request_delay_var.get())
            
            if save_params(params):
                messagebox.showinfo("Success", "Settings saved successfully!")
                self.params = params
            else:
                messagebox.showerror("Error", "Failed to save settings")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid value: {str(e)}")
    
    def _reset_settings(self):
        """Reset settings to defaults."""
        if messagebox.askyesno("Confirm", "Reset all settings to defaults?"):
            from .settings_manager import reset_params
            if reset_params():
                messagebox.showinfo("Success", "Settings reset!")
                self.params = load_all_params()
                # Update UI
                self.sessionid_var.set(self.params.get("sessionid", ""))
                self.securelogin_var.set(self.params.get("securelogin", ""))
                self.headless_var.set(self.params.get("headless", True))
                self.mods_per_page_var.set(str(self.params.get("mods_per_page", 100)))
                self.mods_per_csv_var.set(str(self.params.get("mods_per_csv", 750)))
                self.request_delay_var.set(str(self.params.get("request_delay", 1)))
    
    def _delete_current_game_data_gui(self):
        """Delete data for current game through GUI."""
        if not self.app_id:
            messagebox.showwarning("Warning", "No game selected")
            return
        
        if messagebox.askyesno("Confirm", f"Delete data for {self.game_name}? (App ID: {self.app_id})"):
            try:
                import shutil
                if os.path.exists(self.base_dir):
                    shutil.rmtree(self.base_dir)
                    messagebox.showinfo("Success", f"Deleted: {self.base_dir}")
                else:
                    messagebox.showwarning("Warning", "Data folder not found")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete: {str(e)}")
    
    def _delete_all_data_gui(self):
        """Delete all data but keep parameters through GUI."""
        if messagebox.askyesno("Confirm", "Delete ALL data? (Parameters will be kept)"):
            try:
                import shutil
                if os.path.exists("data"):
                    shutil.rmtree("data")
                    messagebox.showinfo("Success", "Data folder deleted! Parameters saved.")
                else:
                    messagebox.showwarning("Warning", "Data folder not found")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete: {str(e)}")
    
    def _delete_everything_gui(self):
        """Delete all data and parameters through GUI."""
        if messagebox.askyesno("Confirm", "⚠️ Delete EVERYTHING including parameters?"):
            if messagebox.askyesno("Final Confirm", "Are you absolutely sure?"):
                try:
                    import shutil
                    from .settings_manager import reset_params
                    
                    if os.path.exists("data"):
                        shutil.rmtree("data")
                    
                    if reset_params():
                        messagebox.showinfo("Success", "Everything deleted and reset!")
                    else:
                        messagebox.showwarning("Warning", "Data deleted but failed to reset params")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed: {str(e)}")
    
    # ================================
    # HELPER METHODS
    # ================================
    
    def _check_game_selected(self) -> bool:
        """Check if a game is selected."""
        if self.app_id is None:
            messagebox.showwarning("Warning", "Please select a game first!")
            return False
        return True
    
    def _on_progress_update(self, current: int, total: int, message: str):
        """Callback for progress tracker updates - thread-safe."""
        if total > 0:
            percentage = int((current / total) * 100)
            
            # Use root.after() to make GUI updates thread-safe
            def update_gui():
                try:
                    active_tab = self.notebook.index(self.notebook.select())
                    if active_tab == 0:  # Download tab
                        self.download_progress['value'] = percentage
                        self.download_percent.config(text=f"{percentage}%")
                        if message:
                            self.download_status.config(text=message)
                    elif active_tab == 1:  # CSV tab
                        self.csv_progress['value'] = percentage
                        self.csv_status.config(text=f"{message} ({percentage}%)" if message else f"{percentage}%")
                    elif active_tab == 2:  # Collections tab
                        self.collection_progress['value'] = percentage
                        self.collection_status.config(text=f"{message} ({percentage}%)" if message else f"{percentage}%")
                    
                    self.root.update_idletasks()
                except:
                    pass
            
            self.root.after(0, update_gui)


class SelectGameWindow:
    """Dialog for selecting a game."""
    
    def __init__(self, parent, callback: Callable[[int, str], None]):
        self.callback = callback
        
        self.window = tk.Toplevel(parent)
        self.window.title("Select Game")
        self.window.geometry("400x400")
        
        # Known games
        games = get_known_games()
        
        if games:
            ttk.Label(self.window, text="Known Games:", font=("Arial", 10, "bold")).pack(padx=10, pady=10)
            
            scrollbar = ttk.Scrollbar(self.window)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            self.games_listbox = tk.Listbox(self.window, yscrollcommand=scrollbar.set)
            self.games_listbox.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
            scrollbar.config(command=self.games_listbox.yview)
            
            for game in games:
                self.games_listbox.insert(tk.END, f"{game['name']} (ID: {game['app_id']})")
            
            self.games_listbox.bind('<Double-Button-1>', self._on_game_selected)
            
            ttk.Button(self.window, text="Select", command=self._select_game).pack(pady=5)
            
            ttk.Separator(self.window, orient='horizontal').pack(fill=tk.X, padx=10, pady=10)
        
        # Manual entry
        ttk.Label(self.window, text="Or enter App ID:", font=("Arial", 10, "bold")).pack(padx=10, pady=10)
        
        self.appid_entry = ttk.Entry(self.window, width=20)
        self.appid_entry.pack(padx=10, pady=5)
        
        ttk.Button(self.window, text="Look up Game", command=self._lookup_game).pack(pady=5)
        
        self.lookup_result = ttk.Label(self.window, text="", wraplength=300)
        self.lookup_result.pack(padx=10, pady=5)
        
        self.window.transient(parent)
        self.window.grab_set()
    
    def _on_game_selected(self, event):
        """Handle double-click on game."""
        self._select_game()
    
    def _select_game(self):
        """Select the highlighted game."""
        try:
            idx = self.games_listbox.curselection()[0]
            games = get_known_games()
            game = games[idx]
            
            app_id = int(game["app_id"])
            name = game["name"].replace(" ", "_")
            
            self.callback(app_id, name)
            self.window.destroy()
        except:
            messagebox.showwarning("Warning", "Please select a game")
    
    def _lookup_game(self):
        """Look up a game by App ID."""
        try:
            app_id = int(self.appid_entry.get().strip())
            name = fetch_game_name(app_id)
            
            if name:
                self.lookup_result.config(text=f"Found: {name}", foreground="green")
                
                # Ask to confirm
                if messagebox.askyesno("Confirm", f"Use '{name}'?"):
                    normalized_name = name.replace(" ", "_")
                    add_game_to_history(app_id, name)
                    self.callback(app_id, normalized_name)
                    self.window.destroy()
            else:
                self.lookup_result.config(text="Game not found", foreground="red")
        except ValueError:
            self.lookup_result.config(text="Invalid App ID", foreground="red")


def run_gui():
    """Launch the GUI application."""
    root = tk.Tk()
    app = ModManagerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
