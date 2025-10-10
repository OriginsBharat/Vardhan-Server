import os
import sys
import subprocess
import json
import winshell
from win32com.client import Dispatch
import customtkinter as ctk
from tkinter import filedialog
import threading
import shutil

# --- GUI Setup ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class SetupApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("My AI World - One-Time Setup")
        self.geometry("800x950")
        self.grid_columnconfigure(0, weight=1)

        # --- Title ---
        self.header_label = ctk.CTkLabel(self, text="Welcome, Master. Configure Your World.", font=ctk.CTkFont(size=20, weight="bold"))
        self.header_label.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        # --- System Status Frame ---
        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.status_frame.grid_columnconfigure(1, weight=1)
        self.status_header = ctk.CTkLabel(self.status_frame, text="System Status", font=ctk.CTkFont(size=16, weight="bold"))
        self.status_header.grid(row=0, column=0, columnspan=2, padx=10, pady=(5,0), sticky="w")

        self.ollama_status_label = ctk.CTkLabel(self.status_frame, text="Ollama Status:")
        self.ollama_status_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.ollama_status_value = ctk.CTkLabel(self.status_frame, text="Checking...", text_color="yellow")
        self.ollama_status_value.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        self.comfy_status_label = ctk.CTkLabel(self.status_frame, text="ComfyUI Status:")
        self.comfy_status_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.comfy_status_value = ctk.CTkLabel(self.status_frame, text="Pending Path...", text_color="yellow")
        self.comfy_status_value.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        self.ollama_ok = False
        self.comfy_ok = False

        # --- Secrets Frame ---
        self.secrets_frame = ctk.CTkFrame(self)
        self.secrets_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
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
        self.comfy_path_entry = ctk.CTkEntry(self.secrets_frame, placeholder_text="Select your ComfyUI portable installation folder...")
        self.comfy_path_entry.grid(row=5, column=1, padx=10, pady=5, sticky="ew")
        self.browse_button = ctk.CTkButton(self.secrets_frame, text="Browse...", command=self.browse_folder)
        self.browse_button.grid(row=5, column=2, padx=10, pady=5)

        # --- Kinks Frame ---
        self.kinks_header = ctk.CTkLabel(self, text="Character Kinks (comma-separated)", font=ctk.CTkFont(size=16, weight="bold"))
        self.kinks_header.grid(row=3, column=0, padx=20, pady=(20, 5), sticky="w")

        self.kinks_scroll_frame = ctk.CTkScrollableFrame(self, height=250)
        self.kinks_scroll_frame.grid(row=4, column=0, padx=20, pady=5, sticky="nsew")
        self.kinks_scroll_frame.grid_columnconfigure(1, weight=1)
        self.kink_entries = {}
        self.load_characters_for_kinks()

        # --- Log & Action Frame ---
        self.log_frame = ctk.CTkFrame(self)
        self.log_frame.grid(row=5, column=0, padx=20, pady=10, sticky="ew")
        self.log_frame.grid_columnconfigure(0, weight=1)

        self.log_textbox = ctk.CTkTextbox(self.log_frame, height=150, state="disabled")
        self.log_textbox.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.setup_button = ctk.CTkButton(self, text="Waiting for System Status...", command=self.start_setup_thread, height=40, font=ctk.CTkFont(size=16, weight="bold"), state="disabled")
        self.setup_button.grid(row=6, column=0, padx=20, pady=20, sticky="ew")

        self.check_prerequisites()

    def check_prerequisites(self):
        # Check for Ollama
        if shutil.which("ollama"):
            self.ollama_status_value.configure(text="DETECTED", text_color="lightgreen")
            self.ollama_ok = True
        else:
            self.ollama_status_value.configure(text="NOT FOUND. Please install from ollama.com", text_color="red")
            self.ollama_ok = False
        self.update_setup_button_state()

    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.comfy_path_entry.delete(0, "end")
            self.comfy_path_entry.insert(0, folder_path)
            self.verify_comfy_path(folder_path)

    def verify_comfy_path(self, path):
        # A simple check for a key file in a ComfyUI installation
        expected_file = os.path.join(path, "main.py")
        if os.path.isfile(expected_file):
            self.comfy_status_value.configure(text="Verified!", text_color="lightgreen")
            self.comfy_ok = True
        else:
            self.comfy_status_value.configure(text="Invalid Path (main.py not found)", text_color="red")
            self.comfy_ok = False
        self.update_setup_button_state()

    def update_setup_button_state(self):
        if self.ollama_ok and self.comfy_ok:
            self.setup_button.configure(state="normal", text="Begin World Setup")
        else:
            self.setup_button.configure(state="disabled", text="Waiting for System Status...")

    def load_characters_for_kinks(self):
        try:
            # Ensure data directory exists
            os.makedirs("data", exist_ok=True)
            # Create character canon if it doesn't exist
            self.canon_path = "data/character_canon.json"
            if not os.path.exists(self.canon_path):
                # This data should match your project blueprint
                default_canon = {
                    "Maya": {}, "Eka": {}, "Dvi": {}, "Tri": {}, "Chatur": {},
                    "Panch": {}, "Shash": {}, "Sapt": {}, "Asht": {}, "Nav": {}, "Dash": {}
                }
                with open(self.canon_path, "w") as f:
                    json.dump(default_canon, f, indent=4)

            with open(self.canon_path, "r") as f:
                self.characters = json.load(f)
            for i, name in enumerate(self.characters.keys()):
                label = ctk.CTkLabel(self.kinks_scroll_frame, text=name)
                label.grid(row=i, column=0, padx=10, pady=5, sticky="w")
                entry = ctk.CTkEntry(self.kinks_scroll_frame, placeholder_text="e.g. gentle, praise, teasing")
                entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
                self.kink_entries[name] = entry
        except Exception as e:
            self.log_message(f"[ERROR] Failed to load character data: {e}")

    def log_message(self, message):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", message + "\n")
        self.log_textbox.configure(state="disabled")
        self.log_textbox.see("end")
        self.update_idletasks()

    def start_setup_thread(self):
        self.setup_button.configure(state="disabled", text="Setup in Progress...")
        setup_thread = threading.Thread(target=self.run_full_setup)
        setup_thread.start()

    def run_full_setup(self):
        # --- Step 1: Configure .env file ---
        self.log_message("[STEP 1] Creating .env file...")
        secrets = {
            "DISCORD_BOT_TOKEN": self.token_entry.get(),
            "DISCORD_GUILD_ID": self.guild_id_entry.get(),
            "USER_ID": self.user_id_entry.get(),
            "COMFYUI_PATH": self.comfy_path_entry.get(),
            "PINECONE_API_KEY": self.pinecone_key_entry.get(),
            "PINECONE_HOST": self.pinecone_host_entry.get(),
        }

        if not all(secrets.values()):
            self.log_message("[ERROR] All secret fields are required. Please fill them all out.")
            self.setup_button.configure(state="normal", text="Begin World Setup")
            return

        with open(".env", "w") as f:
            for key, value in secrets.items():
                f.write(f"{key}={value}\n")

        self.log_message("✅ .env file created successfully.")

        # --- Step 2: Configure Kinks ---
        self.log_message("\n[STEP 2] Saving character kinks...")
        kink_data = {}
        for name, entry in self.kink_entries.items():
            kinks = entry.get()
            kink_data[name] = [k.strip() for k in kinks.split(",") if k.strip()]

        os.makedirs("data", exist_ok=True)
        with open("data/character_kinks.json", "w") as f:
            json.dump(kink_data, f, indent=4)
        self.log_message("✅ Character kinks saved successfully.")

        # --- Step 3: Place Startup Shortcut ---
        self.log_message("\n[STEP 3] Placing invisible launcher in Windows Startup folder...")
        try:
            startup_folder = winshell.startup()
            script_path = os.path.join(os.getcwd(), "invisible_launcher.vbs")
            shortcut_path = os.path.join(startup_folder, "MyAIWorldLauncher.lnk")

            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = script_path
            shortcut.WorkingDirectory = os.getcwd()
            shortcut.IconLocation = sys.executable
            shortcut.save()
            self.log_message("✅ Shortcut created successfully in your Startup folder.")
        except Exception as e:
            self.log_message(f"[ERROR] Could not create startup shortcut: {e}")
            self.log_message("  > You may need to run this as admin or create the shortcut manually.")

        # --- Step 4: Voice File Instructions ---
        self.log_message("\n[STEP 4] Voice File Instructions...")
        voices_dir = "data/voices"
        os.makedirs(voices_dir, exist_ok=True)
        self.log_message(f"✅ '{voices_dir}' directory created.")
        self.log_message("To enable voice generation, add a .wav file for each character into this directory.")
        self.log_message("The required filenames are:")
        for name in self.characters.keys():
            self.log_message(f"  - {name}.wav")

        # --- Final Message ---
        self.log_message("\n\n" + "="*50)
        self.log_message("SETUP COMPLETE!")
        self.log_message("Your world is forged. Reboot to start it automatically,")
        self.log_message("or double-click 'start_world.bat' to start it now.")
        self.setup_button.configure(state="normal", text="Setup Complete!")

if __name__ == "__main__":
    # This helps with potential pathing issues when run from batch
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    app = SetupApp()
    app.mainloop()