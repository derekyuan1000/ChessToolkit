import os
import chess
import chess.engine
import customtkinter as ctk
from gui import ModernChessGUI

engine_path = os.path.abspath("../engines/Stockfish17.exe")

def display_chess_board(position, fullscreen=False):  # Add fullscreen parameter
    root = ctk.CTk()
    root.title("Chess Analysis")
    if fullscreen:
        root.attributes("-fullscreen", True)  # Set fullscreen if requested

    gui = ModernChessGUI(root, position, engine_path=engine_path)

    def confirm_back():
        confirm_window = ctk.CTkToplevel(root)
        confirm_window.title("Confirm")
        confirm_window.geometry("300x150")

        # Center the dialog over the main tab
        confirm_window.transient(root)
        confirm_window.grab_set()

        label = ctk.CTkLabel(confirm_window, text="Are you sure you want to go back?", font=("Segoe UI", 14))
        label.pack(pady=20)

        def go_back():
            confirm_window.destroy()
            root.destroy()
            from Code.main_menu import main_menu
            main_menu()

        yes_button = ctk.CTkButton(confirm_window, text="Yes", command=go_back)
        yes_button.pack(side="left", padx=20, pady=10)

        no_button = ctk.CTkButton(confirm_window, text="No", command=confirm_window.destroy)
        no_button.pack(side="right", padx=20, pady=10)

    back_button = ctk.CTkButton(gui.main_container, text="Back", command=confirm_back, corner_radius=10)
    back_button.pack(side="bottom", pady=10)

    root.mainloop()
    current_fen = gui.board.fen()
    print("\nFinal FEN:", current_fen)

    if not os.path.exists(engine_path):
        print(f"Error: Engine not found at {engine_path}")
        return

    try:
        with chess.engine.SimpleEngine.popen_uci(engine_path) as engine:
            board = chess.Board(current_fen)
            info = engine.analyse(board, chess.engine.Limit(time=2))
            print("Engine Analysis:", info)
    except Exception as e:
        print(f"Error analyzing final position: {str(e)}")
