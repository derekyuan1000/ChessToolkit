import tkinter as tk
import chess
import chess.pgn  # Ensure chess.pgn is imported
from gui import SimpleChessGUI

def display_chess_board(position):
    root = tk.Tk()
    SimpleChessGUI(root, position)
    root.mainloop()

starting_position = chess.STARTING_FEN
display_chess_board(starting_position)
