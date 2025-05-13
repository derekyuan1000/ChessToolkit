import tkinter as tk
import chess.pgn
from gui import ModernChessGUI
import chess.engine
import os

engine_path = os.path.abspath("../engines/Stockfish17.exe")

def display_chess_board(position):
    root = tk.Tk()
    gui = ModernChessGUI(root, position, engine_path=engine_path)
    root.mainloop()
    current_fen = gui.board.fen()
    print("\nFinal FEN:", current_fen)

    if not os.path.exists(engine_path):
        print(f"Error: Engine not found at {engine_path}")
        return

    with chess.engine.SimpleEngine.popen_uci(engine_path) as engine:
        board = chess.Board(current_fen)
        info = engine.analyse(board, chess.engine.Limit(time=2))
        print("Engine Analysis:", info)

starting_position = chess.STARTING_FEN
display_chess_board(starting_position)
