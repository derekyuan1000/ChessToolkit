import customtkinter as ctk
import chess.pgn
import io

class ImportDialog:
    def __init__(self, parent, callback):
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Import PGN")
        self.window.geometry("600x400")
        self.parent = parent
        self.callback = callback
        
        # Make the window modal
        self.window.transient(parent)
        self.window.grab_set()
        
        # Bind the close button
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Create main container
        self.main_container = ctk.CTkFrame(self.window, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Add instructions label
        instruction_label = ctk.CTkLabel(
            self.main_container,
            text="Paste your PGN text below:",
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
        
        # Create button container
        button_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))
        
        # Add Import and Cancel buttons
        import_button = ctk.CTkButton(
            button_frame,
            text="Import Game",
            width=120,
            command=self.validate_and_import
        )
        import_button.pack(side="left", padx=(0, 10))
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            width=120,
            command=self.on_close
        )
        cancel_button.pack(side="left")

        # Add status label
        self.status_label = ctk.CTkLabel(
            button_frame,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#ff6b6b"  # Red color for errors
        )
        self.status_label.pack(side="left", padx=(20, 0))

    def validate_and_import(self):
        pgn_content = self.pgn_text.get("1.0", "end-1c").strip()
        if not pgn_content:
            self.status_label.configure(text="Please paste a PGN game first")
            return

        try:
            # Validate PGN
            pgn_io = io.StringIO(pgn_content)
            game = chess.pgn.read_game(pgn_io)
            if game is None:
                self.status_label.configure(text="Invalid PGN format")
                return

            # If validation passes, call the callback
            self.callback(pgn_content)
            self.on_close()
            
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}")

    def on_close(self):
        self.window.grab_release()
        self.window.destroy()
