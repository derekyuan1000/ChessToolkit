import tkinter as tk
import chess.pgn
from gui import SimpleChessGUI
import chess.engine

engine_path = "engines/Stockfish17.exe"

def display_chess_board(position):
    root = tk.Tk()
    gui = SimpleChessGUI(root, position)
    root.mainloop()
    current_fen = gui.board.fen()
    print("\nFinal FEN:", current_fen)

    with chess.engine.SimpleEngine.popen_uci(engine_path) as engine:
        board = chess.Board(current_fen)
        info = engine.analyse(board, chess.engine.Limit(time=2))
        print("Engine Analysis:", info)

starting_position = chess.STARTING_FEN
display_chess_board(starting_position)
