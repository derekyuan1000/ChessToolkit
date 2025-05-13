import customtkinter as ctk
from gui import ModernChessGUI
import chess
import chess.engine
import os

engine_path = os.path.abspath("../engines/Stockfish17.exe")


def display_chess_board(position):
    # Create and initialize the root window properly
    root = ctk.CTk()
    root.title("Chess Analysis")

    # Initialize the GUI with the root window
    gui = ModernChessGUI(root, position, engine_path=engine_path)

    # Start the main loop
    root.mainloop()

    # After the window is closed, get the final position
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