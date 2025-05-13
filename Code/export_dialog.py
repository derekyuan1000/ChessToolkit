import customtkinter as ctk

class ExportDialog:
    def __init__(self, parent, pgn_text):
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Export PGN")
        self.window.geometry("600x400")
        self.parent = parent
        
        # Make the window modal
        self.window.transient(parent)
        self.window.grab_set()
        
        # Bind the close button and window close event
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Create main container
        self.main_container = ctk.CTkFrame(self.window, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Add instructions label
        instruction_label = ctk.CTkLabel(
            self.main_container,
            text="Copy the PGN text below:",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        )
        instruction_label.pack(pady=(0, 10), anchor="w")
        
        # Create text area
        self.pgn_text = ctk.CTkTextbox(
            self.main_container,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            wrap="none"
        )
        self.pgn_text.pack(fill="both", expand=True)
        
        # Insert the PGN text
        self.pgn_text.insert("1.0", pgn_text)
        
        # Create button container
        button_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))
        
        # Add Copy and Close buttons
        copy_button = ctk.CTkButton(
            button_frame,
            text="Copy to Clipboard",
            width=120,
            command=self.copy_to_clipboard
        )
        copy_button.pack(side="left", padx=(0, 10))
        
        close_button = ctk.CTkButton(
            button_frame,
            text="Close",
            width=120,
            command=self.on_close
        )
        close_button.pack(side="left")

    def on_close(self):
        self.window.grab_release()  # Release the grab before destroying
        self.window.destroy()
        
    def copy_to_clipboard(self):
        pgn_content = self.pgn_text.get("1.0", "end-1c")
        self.window.clipboard_clear()
        self.window.clipboard_append(pgn_content)
