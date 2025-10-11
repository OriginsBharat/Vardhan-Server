import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os
import winshell
from win32com.client import Dispatch

# --- Configuration ---
APP_NAME = "My AI World - Setup Wizard"
GEOMETRY = "800x750"
THEME = "dark-blue"
CHARACTER_CANON_PATH = "data/character_canon.json"
ENV_PATH = ".env"
KINKS_PATH = "data/character_kinks.json"
VOICE_DIR = "data/voices"
STARTUP_DIR = winshell.startup()

class SetupWizard(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Setup ---
        self.title(APP_NAME)
        self.geometry(GEOMETRY)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme(THEME)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.row = 0
        self.entries = {}

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        scrollable_frame = ctk.CTkScrollableFrame(main_frame, label_text="Vardhan Server Configuration")
        scrollable_frame.pack(pady=10, padx=10, fill="both", expand=True)
        scrollable_frame.grid_columnconfigure(1, weight=1)

        # --- Create Widgets ---
        self._create_section_header(scrollable_frame, "Discord Secrets")
        self._create_entry(scrollable_frame, "DISCORD_BOT_TOKEN", "Your bot's unique token.")
        self._create_entry(scrollable_frame, "DISCORD_GUILD_ID", "The ID of your Discord server.")
        self._create_entry(scrollable_frame, "USER_ID", "Your personal Discord user ID.")

        self._create_section_header(scrollable_frame, "AI Service Configuration")
        self._create_entry(scrollable_frame, "OLLAMA_API_URL", "URL for the Ollama server.", "http://127.0.0.1:11434")
        self._create_entry(scrollable_frame, "COMFYUI_API_URL", "URL for the ComfyUI server.", "http://127.0.0.1:8188")
        self._create_path_entry(scrollable_frame, "COMFYUI_PATH", "Path to your ComfyUI installation folder.")

        self._create_section_header(scrollable_frame, "Cloud Memory (Pinecone)")
        self._create_entry(scrollable_frame, "PINECONE_API_KEY", "Your API key from pinecone.io.")
        self._create_entry(scrollable_frame, "PINECONE_HOST", "Your index host from pinecone.io.")

        self._create_character_kink_entries(scrollable_frame)

        self._create_section_header(scrollable_frame, "Voice Files (Manual Step)")
        os.makedirs(VOICE_DIR, exist_ok=True)
        info_label = ctk.CTkLabel(scrollable_frame, text=f"Place one .wav file for each character inside the '{os.path.abspath(VOICE_DIR)}' folder.\n(e.g., Maya.wav, Eka.wav, etc.)", wraplength=700, justify="left")
        info_label.grid(row=self.row, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="w")
        self.row += 1

        setup_button = ctk.CTkButton(main_frame, text="Begin World Setup", command=self.run_setup)
        setup_button.pack(pady=10, padx=10)

    def _create_section_header(self, parent, text):
        header = ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(size=14, weight="bold"))
        header.grid(row=self.row, column=0, columnspan=2, pady=(15, 5), padx=10, sticky="w")
        self.row += 1

    def _create_entry(self, parent, key, placeholder, default_value="", key_override=None):
        label = ctk.CTkLabel(parent, text=key)
        label.grid(row=self.row, column=0, padx=10, pady=5, sticky="w")
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder, width=400)
        entry.insert(0, default_value)
        entry.grid(row=self.row, column=1, padx=10, pady=5, sticky="ew")
        storage_key = key_override if key_override else key
        self.entries[storage_key] = entry
        self.row += 1

    def _create_path_entry(self, parent, key, placeholder):
        label = ctk.CTkLabel(parent, text=key)
        label.grid(row=self.row, column=0, padx=10, pady=5, sticky="w")
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=self.row, column=1, padx=10, pady=5, sticky="ew")
        frame.grid_columnconfigure(0, weight=1)
        entry = ctk.CTkEntry(frame, placeholder_text=placeholder)
        entry.grid(row=0, column=0, sticky="ew")
        button = ctk.CTkButton(frame, text="Browse...", width=80, command=lambda: self._browse_folder(entry))
        button.grid(row=0, column=1, padx=(5,0))
        self.entries[key] = entry
        self.row += 1

    def _browse_folder(self, entry_widget):
        folder_path = filedialog.askdirectory()
        if folder_path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, folder_path)

    def _create_character_kink_entries(self, parent):
        self._create_section_header(parent, "Character Kink Profiles")
        try:
            with open(CHARACTER_CANON_PATH, "r") as f:
                characters = json.load(f)
            for name in characters.keys():
                placeholder = f"Comma-separated list of kinks for {name}"
                self._create_entry(parent, name, placeholder, key_override=f"KINK_{name}")
        except FileNotFoundError:
            error_label = ctk.CTkLabel(parent, text=f"ERROR: '{CHARACTER_CANON_PATH}' not found!", text_color="red")
            error_label.grid(row=self.row, column=0, columnspan=2, padx=10, pady=5, sticky="w")
            self.row += 1

    def run_setup(self):
        try:
            # --- Create .env file ---
            with open(ENV_PATH, "w") as f:
                for key, widget in self.entries.items():
                    if not key.startswith("KINK_"):
                        f.write(f"{key.upper()}={widget.get()}\n")

            # --- Create character_kinks.json ---
            kinks_data = {}
            for key, widget in self.entries.items():
                if key.startswith("KINK_"):
                    character_name = key.replace("KINK_", "")
                    kinks_list = [k.strip() for k in widget.get().split(',') if k.strip()]
                    kinks_data[character_name] = kinks_list
            with open(KINKS_PATH, "w") as f:
                json.dump(kinks_data, f, indent=4)

            # --- Create start_world.bat ---
            comfyui_path = self.entries["COMFYUI_PATH"].get()
            start_script_content = f"""@echo off
echo Starting AI services... Please wait.
start "Ollama" /B ollama serve
timeout /t 10 > nul
start "ComfyUI" /B /D "{comfyui_path}" run_nvidia_gpu.bat --listen
timeout /t 20 > nul
echo Starting AI World Bot...
python src/main.py
"""
            with open("start_world.bat", "w") as f:
                f.write(start_script_content)

            # --- Create invisible_launcher.vbs ---
            vbs_content = f'CreateObject("Wscript.Shell").Run "cmd /c start /min \\"AI_WORLD\\" \\"{os.path.abspath("start_world.bat")}\\"", 0, True'
            with open("invisible_launcher.vbs", "w") as f:
                f.write(vbs_content)

            # --- Create shortcut in Startup folder ---
            shortcut_path = os.path.join(STARTUP_DIR, "Start_AI_World.lnk")
            vbs_path = os.path.abspath("invisible_launcher.vbs")
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = vbs_path
            shortcut.WorkingDirectory = os.path.abspath(".")
            shortcut.save()

            messagebox.showinfo("Success", "World setup is complete! The AI World will now start automatically with your PC. You can close all these windows now.")
            self.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during setup:\n\n{e}")

if __name__ == "__main__":
    wizard = SetupWizard()
    wizard.mainloop()