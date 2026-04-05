import customtkinter as ctk
import requests
import json
import threading
from tkinter import filedialog, messagebox

# Settings
BASE_URL = "http://localhost:8000"
APP_NAME = "AutoTests"
THEME_COLOR = "#3B8ED0"  # Premium Blue
BG_COLOR = "#1a1a1a"    # Dark Slate

class AutoTestsApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(f"{APP_NAME} - AI Test Generator")
        self.geometry("900x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Layout configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar / Navigation (Simulated)
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text=APP_NAME, font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.pack(padx=20, pady=(30, 10))
        
        self.tagline_label = ctk.CTkLabel(self.sidebar_frame, text="Next Gen Testing", font=ctk.CTkFont(size=12))
        self.tagline_label.pack(padx=20, pady=(0, 30))

        # Demo Mode Switch
        self.demo_mode = ctk.BooleanVar(value=False)
        self.demo_switch = ctk.CTkSwitch(self.sidebar_frame, text="Demo Mode", variable=self.demo_mode)
        self.demo_switch.pack(pady=20)

        # Main Content Area
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Header
        self.header_label = ctk.CTkLabel(self.main_frame, text="Generate New Test", font=ctk.CTkFont(size=20, weight="bold"))
        self.header_label.pack(pady=(20, 10))

        # Form Container
        self.form_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.form_frame.pack(fill="x", padx=40, pady=10)

        # Topic
        self.topic_label = ctk.CTkLabel(self.form_frame, text="Subject / Topic")
        self.topic_label.pack(anchor="w")
        self.topic_entry = ctk.CTkEntry(self.form_frame, placeholder_text="e.g. Present Simple, Space Exploration, History of Art...", height=40)
        self.topic_entry.pack(fill="x", pady=(5, 15))

        # Split Row: Language & Level
        self.row_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.row_frame.pack(fill="x")
        self.row_frame.grid_columnconfigure((0, 1), weight=1)

        # Language
        self.lang_label = ctk.CTkLabel(self.row_frame, text="Language")
        self.lang_label.grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.lang_menu = ctk.CTkOptionMenu(self.row_frame, values=["English (en)", "German (de)"], height=35)
        self.lang_menu.grid(row=1, column=0, sticky="ew", padx=(0, 10))

        # Level
        self.level_label = ctk.CTkLabel(self.row_frame, text="Level")
        self.level_label.grid(row=0, column=1, sticky="w", padx=(10, 0))
        self.level_menu = ctk.CTkOptionMenu(self.row_frame, values=["A1", "A2", "B1", "B2", "C1", "C2"], height=35)
        self.level_menu.grid(row=1, column=1, sticky="ew", padx=(10, 0))

        # Group Count
        self.group_label = ctk.CTkLabel(self.form_frame, text="Number of Groups (1-5)")
        self.group_label.pack(anchor="w", pady=(15, 0))
        self.group_slider = ctk.CTkSlider(self.form_frame, from_=1, to=5, number_of_steps=4)
        self.group_slider.set(2)
        self.group_slider.pack(fill="x", pady=5)

        # Generate Button
        self.gen_button = ctk.CTkButton(self.main_frame, text="Generate Test", 
                                        font=ctk.CTkFont(size=15, weight="bold"),
                                        height=45, corner_radius=8,
                                        command=self.start_generation)
        self.gen_button.pack(pady=20, padx=40, fill="x")

        # Loading Spinner (Progress Bar)
        self.progress_bar = ctk.CTkProgressBar(self.main_frame, mode="indeterminate")
        self.progress_bar.set(0)

        # Output Area
        self.output_label = ctk.CTkLabel(self.main_frame, text="Results", font=ctk.CTkFont(weight="bold"))
        self.output_label.pack(pady=(10, 0))
        
        self.result_box = ctk.CTkTextbox(self.main_frame, height=250, corner_radius=10, 
                                        border_width=1, border_color="#333")
        self.result_box.pack(fill="both", expand=True, padx=40, pady=(5, 10))

        # Action Buttons
        self.actions_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.actions_frame.pack(fill="x", padx=40, pady=(0, 20))
        
        self.save_button = ctk.CTkButton(self.actions_frame, text="Save JSON", width=120, command=self.save_to_json)
        self.save_button.pack(side="left", padx=5)
        
        self.clear_button = ctk.CTkButton(self.actions_frame, text="Clear", width=80, fg_color="#444", hover_color="#555", command=self.clear_results)
        self.clear_button.pack(side="right", padx=5)

    def log(self, message):
        self.result_box.insert("end", message + "\n")
        self.result_box.see("end")

    def clear_results(self):
        self.result_box.delete("1.0", "end")

    def start_generation(self):
        topic = self.topic_entry.get().strip()
        if not topic:
            messagebox.showwarning("Warning", "Please enter a topic.")
            return

        self.gen_button.configure(state="disabled", text="Generating...")
        self.progress_bar.pack(fill="x", padx=40, pady=5)
        self.progress_bar.start()
        self.clear_results()
        self.log(f"[*] Starting generation for topic: {topic}...")

        # Run in thread to not freeze UI
        threading.Thread(target=self.generate_task, daemon=True).start()

    def generate_task(self):
        topic = self.topic_entry.get()
        lang_val = self.lang_menu.get().split("(")[1].strip(")")
        level = self.level_menu.get()
        groups = int(self.group_slider.get())

        if self.demo_mode.get():
            import time
            time.sleep(2)
            mock_data = {
                "groups": [
                    {
                        "questions": [
                            {"instruction": "Choose the correct form", "text": "I ___ to school every day.", "type": "multiple_choice", "correct_answer": "go"},
                            {"instruction": "Translate to " + lang_val, "text": "The cat is on the table.", "type": "open_ended", "correct_answer": "..."}
                        ],
                        "answers": ["go", "..."]
                    }
                ]
            }
            self.display_result(mock_data)
        else:
            try:
                payload = {
                    "language": lang_val,
                    "level": level,
                    "topic": topic,
                    "group_count": groups
                }
                response = requests.post(f"{BASE_URL}/v1/generator/generate", json=payload, timeout=300)
                if response.status_code == 200:
                    self.display_result(response.json())
                else:
                    self.log(f"[!] Error {response.status_code}: {response.text}")
            except Exception as e:
                self.log(f"[!] Connection failed: {str(e)}")
        
        self.after(0, self.finish_generation)

    def display_result(self, data):
        self.log("[+] Test successfully generated!")
        formatted_json = json.dumps(data, indent=4, ensure_ascii=False)
        self.log("\n" + formatted_json)

    def finish_generation(self):
        self.gen_button.configure(state="normal", text="Generate Test")
        self.progress_bar.stop()
        self.progress_bar.pack_forget()

    def save_to_json(self):
        content = self.result_box.get("1.0", "end").strip()
        if not content or "[+]" not in content:
            messagebox.showinfo("Info", "Nothing to save.")
            return
            
        json_str = content.split("[+] Test successfully generated!")[-1].strip()
        try:
            # Validate JSON
            data = json.loads(json_str)
            file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                messagebox.showinfo("Success", f"Test saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")

if __name__ == "__main__":
    app = AutoTestsApp()
    app.mainloop()
