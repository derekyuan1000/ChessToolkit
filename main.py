import chess
import tkinter as tk
from tkinter import ttk


def get_piece_symbol(piece):
    symbols = {
        'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
        'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'
    }
    return symbols.get(piece.symbol(), '')


class SimpleChessGUI:
    def __init__(self, root, position):
        self.root = root
        self.root.title("Simple Chess")

        self.board = chess.Board(position)
        self.square_size = 60

        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            self.main_frame,
            width=8 * self.square_size,
            height=8 * self.square_size,
            bg='white'
        )
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)

        self.draw_board()
        self.canvas.bind("<Button-1>", self.on_square_clicked)

    def draw_board(self):
        self.canvas.delete("all")

        for row in range(8):
            for col in range(8):
                x1 = col * self.square_size
                y1 = row * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size

                color = "#f0d9b5" if (row + col) % 2 == 0 else "#b58863"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

                square = chess.square(col, 7 - row)
                piece = self.board.piece_at(square)
                if piece:
                    text = get_piece_symbol(piece)
                    self.canvas.create_text(
                        x1 + self.square_size // 2,
                        y1 + self.square_size // 2,
                        text=text,
                        font=("Arial", 32),
                        fill="black" if piece.color == chess.BLACK else "white"
                    )

    def on_square_clicked(self, event):
        col = event.x // self.square_size
        row = 7 - (event.y // self.square_size)
        square = chess.square(col, row)
        print(f"Clicked square: {chess.square_name(square)}")


def display_chess_board(position):
    """
    Displays a chess board in a GUI with 1 parameter of a certain position
    """
    root = tk.Tk()
    SimpleChessGUI(root, position)
    root.mainloop()


    starting_position = chess.STARTING_FEN
    display_chess_board(starting_position)