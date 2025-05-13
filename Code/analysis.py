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

    def go_back():
        root.destroy()
        from Code.main_menu import main_menu
        main_menu()

    back_button = ctk.CTkButton(gui.main_container, text="Back", command=go_back, corner_radius=10)
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
