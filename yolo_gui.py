import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk, ImageOps
import os
import threading
from pcb_detection.inference import Detector
from pcb_detection import ROOT

class PCBDefectDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ShanAI - PCB Defect Detection")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Colors and theme
        self.dark_mode = False
        self.theme_colors = {
            "light": {
                "bg": "#f5f5f5",
                "sidebar_bg": "#343a40",
                "sidebar_fg": "white",
                "main_bg": "white",
                "text": "#212529",
                "accent": "#0275d8",
                "button_bg": "#0275d8",
                "button_fg": "white",
                "canvas_bg": "#e9ecef"
            },
            "dark": {
                "bg": "#212529",
                "sidebar_bg": "#343a40",
                "sidebar_fg": "#f8f9fa",
                "main_bg": "#2c3034",
                "text": "#f8f9fa",
                "accent": "#0d6efd",
                "button_bg": "#0d6efd",
                "button_fg": "white",
                "canvas_bg": "#343a40"
            }
        }
        self.current_theme = "light"
        
        self.detector = Detector(os.getenv("PCB_MODEL_PATH", str(ROOT / "best.pt")),
                                 os.getenv("PCB_CONFIDENCE", "0.25"),
                                 os.getenv("PCB_DEVICE", "cpu"))
        self.pending_result = None
        self.pending_error = None
        self.running = False

        # Variables
        self.current_image_path = None
        self.original_image = None
        self.result_image = None
        self.detection_results = None
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        current_colors = self.theme_colors[self.current_theme]
        self.root.configure(bg=current_colors["bg"])
        
        # Main layout frames
        self.main_frame = tk.Frame(self.root, bg=current_colors["bg"])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header with logo and title
        self.header_frame = tk.Frame(self.main_frame, bg=current_colors["bg"], height=80)
        self.header_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.title_label = tk.Label(
            self.header_frame, 
            text="PCB Defect Detection System", 
            font=("Helvetica", 20, "bold"),
            bg=current_colors["bg"], 
            fg=current_colors["text"]
        )
        self.title_label.pack(side=tk.LEFT, padx=20, pady=20)
        
        # Theme toggle button
        self.theme_btn = tk.Button(
            self.header_frame, 
            text="🌙 Dark Mode" if self.current_theme == "light" else "☀️ Light Mode", 
            command=self.toggle_theme,
            bg=current_colors["button_bg"], 
            fg=current_colors["button_fg"],
            relief=tk.FLAT,
            padx=10
        )
        self.theme_btn.pack(side=tk.RIGHT, padx=20, pady=20)
        
        # Content area - split into sidebar and main area
        self.content_frame = tk.Frame(self.main_frame, bg=current_colors["bg"])
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar
        self.sidebar_frame = tk.Frame(self.content_frame, bg=current_colors["sidebar_bg"], width=200)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.sidebar_frame.pack_propagate(False)
        
        sidebar_title = tk.Label(
            self.sidebar_frame, 
            text="Controls", 
            bg=current_colors["sidebar_bg"], 
            fg=current_colors["sidebar_fg"],
            font=("Helvetica", 14, "bold"),
            pady=10
        )
        sidebar_title.pack(fill=tk.X)
        
        # Sidebar buttons
        btn_styles = {
            "bg": current_colors["sidebar_bg"], 
            "fg": current_colors["sidebar_fg"],
            "font": ("Helvetica", 11),
            "relief": tk.FLAT,
            "activebackground": current_colors["accent"],
            "activeforeground": current_colors["sidebar_fg"],
            "bd": 0,
            "padx": 10,
            "pady": 8,
            "anchor": "w",
            "width": 20
        }
        
        self.select_btn = tk.Button(
            self.sidebar_frame, 
            text="Select Image", 
            command=self.select_image,
            **btn_styles
        )
        self.select_btn.pack(fill=tk.X, pady=5, padx=5)
        
        self.detect_btn = tk.Button(
            self.sidebar_frame, 
            text="Detect Defects", 
            command=self.run_detection,
            state=tk.DISABLED,
            **btn_styles
        )
        self.detect_btn.pack(fill=tk.X, pady=5, padx=5)
        
        self.save_btn = tk.Button(
            self.sidebar_frame, 
            text="Save Results", 
            command=self.save_results,
            state=tk.DISABLED,
            **btn_styles
        )
        self.save_btn.pack(fill=tk.X, pady=5, padx=5)
        
        self.clear_btn = tk.Button(
            self.sidebar_frame, 
            text="Clear", 
            command=self.clear_results,
            state=tk.DISABLED,
            **btn_styles
        )
        self.clear_btn.pack(fill=tk.X, pady=5, padx=5)
        
        # Information section in sidebar
        info_frame = tk.Frame(self.sidebar_frame, bg=current_colors["sidebar_bg"], pady=20)
        info_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        info_text = tk.Label(
            info_frame,
            text="PCB Defect Types:\n- Missing Hole\n- Mouse Bite\n- Open Circuit\n- Short\n- Spur\n- Spurious Copper",
            bg=current_colors["sidebar_bg"],
            fg=current_colors["sidebar_fg"],
            font=("Helvetica", 10),
            justify=tk.LEFT,
            padx=10
        )
        info_text.pack(fill=tk.X)
        
        # Main content area
        self.main_content = tk.Frame(self.content_frame, bg=current_colors["main_bg"])
        self.main_content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Image display area
        self.image_frame = tk.Frame(self.main_content, bg=current_colors["canvas_bg"], bd=2, relief=tk.SUNKEN)
        self.image_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(
            self.image_frame, 
            bg=current_colors["canvas_bg"],
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Drop instruction label
        self.drop_label = tk.Label(
            self.canvas,
            text="Select an image to begin detection",
            font=("Helvetica", 14),
            bg=current_colors["canvas_bg"],
            fg=current_colors["text"]
        )
        self.drop_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Results area
        self.results_frame = tk.Frame(self.main_content, bg=current_colors["main_bg"], height=200)
        self.results_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        results_title = tk.Label(
            self.results_frame, 
            text="Detection Results", 
            bg=current_colors["main_bg"], 
            fg=current_colors["text"],
            font=("Helvetica", 12, "bold")
        )
        results_title.pack(anchor="w", pady=(10, 5))
        
        self.results_text = tk.Text(
            self.results_frame, 
            bg=current_colors["canvas_bg"], 
            fg=current_colors["text"],
            height=8, 
            wrap=tk.WORD,
            font=("Consolas", 10),
            state=tk.DISABLED
        )
        self.results_text.pack(fill=tk.X, expand=False)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = tk.Label(
            self.main_frame, 
            textvariable=self.status_var, 
            bd=1, 
            relief=tk.SUNKEN, 
            anchor=tk.W,
            bg=current_colors["bg"],
            fg=current_colors["text"],
            font=("Helvetica", 9)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.main_frame, 
            orient=tk.HORIZONTAL, 
            length=100, 
            mode='indeterminate',
            variable=self.progress_var
        )
        self.progress_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
        self.progress_bar.pack_forget()  # Hide initially
    
    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.theme_btn.config(text="🌙 Dark Mode" if self.current_theme == "light" else "☀️ Light Mode")
        self.update_theme()
    
    def update_theme(self):
        # Update all UI elements with the current theme
        current_colors = self.theme_colors[self.current_theme]
        
        self.root.configure(bg=current_colors["bg"])
        self.main_frame.configure(bg=current_colors["bg"])
        self.header_frame.configure(bg=current_colors["bg"])
        self.content_frame.configure(bg=current_colors["bg"])
        self.main_content.configure(bg=current_colors["main_bg"])
        self.results_frame.configure(bg=current_colors["main_bg"])
        self.image_frame.configure(bg=current_colors["canvas_bg"])
        self.canvas.configure(bg=current_colors["canvas_bg"])
        self.sidebar_frame.configure(bg=current_colors["sidebar_bg"])
        
        self.title_label.configure(bg=current_colors["bg"], fg=current_colors["text"])
        self.theme_btn.configure(bg=current_colors["button_bg"], fg=current_colors["button_fg"])
        self.status_bar.configure(bg=current_colors["bg"], fg=current_colors["text"])
        self.results_text.configure(bg=current_colors["canvas_bg"], fg=current_colors["text"])
        
        # Update sidebar buttons
        sidebar_buttons = [self.select_btn, self.detect_btn, self.save_btn, self.clear_btn]
        for btn in sidebar_buttons:
            btn.configure(
                bg=current_colors["sidebar_bg"], 
                fg=current_colors["sidebar_fg"],
                activebackground=current_colors["accent"]
            )
            
        # Refresh any images if needed
        self.update_image_display()
    
    def select_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.status_var.set(f"Image selected: {os.path.basename(file_path)}")
            
            try:
                with Image.open(file_path) as image:
                    self.original_image = ImageOps.exif_transpose(image).convert("RGB")
                self.current_image_path = file_path
                self.result_image = None
                self.detection_results = None
                self.save_btn.config(state=tk.DISABLED)
                self.update_image_display()
                self.detect_btn.config(state=tk.NORMAL)
                self.clear_btn.config(state=tk.NORMAL)
                self.drop_label.place_forget()  # Hide the drop instruction
                
                # Clear previous results
                self.update_results_text("Select 'Detect Defects' to analyze the image.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open image: {str(e)}")
    
    def update_image_display(self):
        if self.original_image is None:
            return
        
        # Get the display image (either original or result)
        display_image = self.result_image if self.result_image else self.original_image
        
        # Calculate the scaled image size to fit the canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:  # Canvas not yet drawn
            self.root.update_idletasks()
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
        
        img_width, img_height = display_image.size
        scale = min(canvas_width/img_width, canvas_height/img_height)
        new_width = max(1, int(img_width * scale))
        new_height = max(1, int(img_height * scale))
        
        # Resize image to fit canvas
        self.display_image = display_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.photo_image = ImageTk.PhotoImage(self.display_image)
        
        # Clear canvas and display new image
        self.canvas.delete("all")
        self.canvas.create_image(
            canvas_width//2, canvas_height//2,
            image=self.photo_image,
            anchor=tk.CENTER
        )
    
    def run_detection(self):
        if not self.current_image_path or self.running:
            return
            
        # Start progress indication
        self.status_var.set("Detecting defects...")
        self.progress_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
        self.progress_bar.start(10)
        self.detect_btn.config(state=tk.DISABLED)
        
        self.running = True
        self.select_btn.config(state=tk.DISABLED)
        self.clear_btn.config(state=tk.DISABLED)
        self.save_btn.config(state=tk.DISABLED)
        self.root.after(50, self._poll_detection)
        # Run detection in a separate thread
        threading.Thread(target=self._run_detection_thread, daemon=True).start()
    
    def _run_detection_thread(self):
        try:
            self.pending_result = self.detector.detect(self.current_image_path)
        except Exception as exc:
            self.pending_error = str(exc)

    def _poll_detection(self):
        # Only the main Tk thread reads or changes widgets.
        if self.pending_result is None and self.pending_error is None:
            self.root.after(50, self._poll_detection)
            return
        self.running = False
        self.select_btn.config(state=tk.NORMAL)
        self.clear_btn.config(state=tk.NORMAL)
        self.detect_btn.config(state=tk.NORMAL)
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        if self.pending_error is not None:
            message, self.pending_error = self.pending_error, None
            self._show_error(message)
            return
        self.result_image, self.detection_results = self.pending_result
        self.pending_result = None
        self.update_image_display()
        details = self.detection_results
        lines = [details["diagnostic"], f"Inference: {details['inference_ms']:.1f} ms"]
        for defect in details["detections"]:
            lines.append(f"{defect['class']}: {defect['confidence']:.1%}")
        self.update_results_text("\n".join(lines))
        self.status_var.set("Detection complete")
        self.save_btn.config(state=tk.NORMAL)

    def _show_error(self, message):
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.status_var.set("Error")
        messagebox.showerror("Detection Error", message)
        self.detect_btn.config(state=tk.NORMAL)
    
    def update_results_text(self, text):
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, text)
        self.results_text.config(state=tk.DISABLED)
    
    def save_results(self):
        if self.result_image:
            save_path = filedialog.asksaveasfilename(
                defaultextension=".jpg",
                filetypes=[
                    ("JPEG files", "*.jpg"),
                    ("PNG files", "*.png"),
                    ("All files", "*.*")
                ]
            )
            if save_path:
                try:
                    self.result_image.save(save_path)
                    self.status_var.set(f"Results saved to {os.path.basename(save_path)}")
                except Exception as e:
                    messagebox.showerror("Save Error", f"Failed to save image: {str(e)}")
    
    def clear_results(self):
        self.result_image = None
        self.detection_results = None
        self.update_image_display()
        self.update_results_text("Select 'Detect Defects' to analyze the image.")
        self.save_btn.config(state=tk.DISABLED)
        self.status_var.set("Ready")

# Initialize the application
if __name__ == "__main__":
    root = tk.Tk()
    app = PCBDefectDetectionApp(root)
    # Bind resize event to update image display
    root.bind("<Configure>", lambda event: app.update_image_display() if event.widget == root else None)
    root.mainloop()
