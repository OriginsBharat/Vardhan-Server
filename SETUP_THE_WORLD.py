import os
import sys
import subprocess
import json
import winshell
from win32com.client import Dispatch
import customtkinter as ctk
from tkinter import filedialog
import threading

# --- GUI Setup ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class SetupApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("My AI World - One-Time Setup")
        self.geometry("800x900")
        self.grid_columnconfigure(0, weight=1)

        # --- Title ---
        self.header_label = ctk.CTkLabel(self, text="Welcome, Master. Configure Your World.", font=ctk.CTkFont(size=20, weight="bold"))
        self.header_label.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        # --- Secrets Frame ---
        self.secrets_frame = ctk.CTkFrame(self)
        self.secrets_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.secrets_frame.grid_columnconfigure(1, weight=1)

        self.token_label = ctk.CTkLabel(self.secrets_frame, text="DISCORD_BOT_TOKEN")
        self.token_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.token_entry = ctk.CTkEntry(self.secrets_frame, width=400)
        self.token_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        self.guild_id_label = ctk.CTkLabel(self.secrets_frame, text="DISCORD_GUILD_ID")
        self.guild_id_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.guild_id_entry = ctk.CTkEntry(self.secrets_frame)
        self.guild_id_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        self.user_id_label = ctk.CTkLabel(self.secrets_frame, text="USER_ID")
        self.user_id_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.user_id_entry = ctk.CTkEntry(self.secrets_frame)
        self.user_id_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        self.pinecone_key_label = ctk.CTkLabel(self.secrets_frame, text="PINECONE_API_KEY")
        self.pinecone_key_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.pinecone_key_entry = ctk.CTkEntry(self.secrets_frame)
        self.pinecone_key_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        self.pinecone_host_label = ctk.CTkLabel(self.secrets_frame, text="PINECONE_HOST")
        self.pinecone_host_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.pinecone_host_entry = ctk.CTkEntry(self.secrets_frame)
        self.pinecone_host_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

        # --- ComfyUI Path ---
        self.comfy_path_label = ctk.CTkLabel(self.secrets_frame, text="COMFYUI_PATH")
        self.comfy_path_label.grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.comfy_path_entry = ctk.CTkEntry(self.secrets_frame)
        self.comfy_path_entry.grid(row=5, column=1, padx=10, pady=5, sticky="ew")
        self.browse_button = ctk.CTkButton(self.secrets_frame, text="Browse...", command=self.browse_folder)
        self.browse_button.grid(row=5, column=2, padx=10, pady=5)

        # --- Kinks Frame ---
        self.kinks_header = ctk.CTkLabel(self, text="Character Kinks (comma-separated)", font=ctk.CTkFont(size=16, weight="bold"))
        self.kinks_header.grid(row=2, column=0, padx=20, pady=(20, 5), sticky="w")

        self.kinks_scroll_frame = ctk.CTkScrollableFrame(self, height=300)
        self.kinks_scroll_frame.grid(row=3, column=0, padx=20, pady=5, sticky="nsew")
        self.kinks_scroll_frame.grid_columnconfigure(1, weight=1)
        self.kink_entries = {}
        self.load_characters_for_kinks()

        # --- Status & Action Frame ---
        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        self.status_frame.grid_columnconfigure(0, weight=1)

        self.status_textbox = ctk.CTkTextbox(self.status_frame, height=150, state="disabled")
        self.status_textbox.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.setup_button = ctk.CTkButton(self, text="Begin World Setup", command=self.start_setup_thread, height=40, font=ctk.CTkFont(size=16, weight="bold"))
        self.setup_button.grid(row=5, column=0, padx=20, pady=20, sticky="ew")

    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.comfy_path_entry.delete(0, "end")
            self.comfy_path_entry.insert(0, folder_path)

    def load_characters_for_kinks(self):
        try:
            with open("data/character_canon.json", "r") as f:
                characters = json.load(f)
            for i, name in enumerate(characters.keys()):
                label = ctk.CTkLabel(self.kinks_scroll_frame, text=name)
                label.grid(row=i, column=0, padx=10, pady=5, sticky="w")
                entry = ctk.CTkEntry(self.kinks_scroll_frame)
                entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
                self.kink_entries[name] = entry
        except FileNotFoundError:
            self.log_status("[ERROR] `data/character_canon.json` not found. Cannot configure kinks.")

    def log_status(self, message):
        self.status_textbox.configure(state="normal")
        self.status_textbox.insert("end", message + "\n")
        self.status_textbox.configure(state="disabled")
        self.status_textbox.see("end")
        self.update_idletasks()

    def start_setup_thread(self):
        self.setup_button.configure(state="disabled", text="Setup in Progress...")
        setup_thread = threading.Thread(target=self.run_full_setup)
        setup_thread.start()

    def run_full_setup(self):
        # --- Step 1: Install Dependencies ---
        self.log_status("[STEP 1] Installing Python dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            self.log_status("✅ Dependencies installed successfully.")
        except subprocess.CalledProcessError as e:
            self.log_status(f"[ERROR] Failed to install dependencies: {e}")
            self.setup_button.configure(state="normal", text="Begin World Setup")
            return

        # --- Step 2: Configure .env file ---
        self.log_status("\n[STEP 2] Creating .env file...")
        secrets = {
            "DISCORD_BOT_TOKEN": self.token_entry.get(),
            "DISCORD_GUILD_ID": self.guild_id_entry.get(),
            "USER_ID": self.user_id_entry.get(),
            "COMFYUI_PATH": self.comfy_path_entry.get(),
            "PINECONE_API_KEY": self.pinecone_key_entry.get(),
            "PINECONE_HOST": self.pinecone_host_entry.get(),
        }

        if not all(secrets.values()):
            self.log_status("[ERROR] All secret fields are required. Please fill them all out.")
            self.setup_button.configure(state="normal", text="Begin World Setup")
            return

        with open(".env", "w") as f:
            for key, value in secrets.items():
                f.write(f"{key}={value}\n")

        os.makedirs("data", exist_ok=True)
        with open("data/.comfyui_path", "w") as f:
            f.write(secrets["COMFYUI_PATH"])
        self.log_status("✅ .env file created successfully.")

        # --- Step 3: Configure Kinks ---
        self.log_status("\n[STEP 3] Saving character kinks...")
        kink_data = {}
        for name, entry in self.kink_entries.items():
            kinks = entry.get()
            kink_data[name] = [k.strip() for k in kinks.split(",")] if kinks else []
        with open("data/character_kinks.json", "w") as f:
            json.dump(kink_data, f, indent=4)
        self.log_status("✅ Character kinks saved successfully.")

        # --- Step 4: Place Startup Shortcut ---
        self.log_status("\n[STEP 4] Placing invisible launcher in Windows Startup folder...")
        try:
            startup_folder = winshell.startup()
            script_path = os.path.join(os.getcwd(), "invisible_launcher.vbs")
            shortcut_path = os.path.join(startup_folder, "MyAIWorldLauncher.lnk")

            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = script_path
            shortcut.WorkingDirectory = os.getcwd()
            shortcut.IconLocation = script_path
            shortcut.save()
            self.log_status("✅ Shortcut created successfully in your Startup folder.")
        except Exception as e:
            self.log_status(f"[ERROR] Could not create startup shortcut: {e}")
            self.log_status("  > You may need to run this as admin or create the shortcut manually.")

        # --- Final Message ---
        self.log_status("\n\n" + "="*50)
        self.log_status("SETUP COMPLETE!")
        self.log_status("Your world is forged. Reboot to start it automatically,")
        self.log_status("or double-click 'start_world.bat' to start it now.")
        self.setup_button.configure(state="normal", text="Setup Complete!")

if __name__ == "__main__":
    app = SetupApp()
    app.mainloop()