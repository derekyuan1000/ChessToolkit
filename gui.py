import chess
import chess.pgn
import chess.engine  # Import the chess engine module
import tkinter as tk
from tkinter import ttk
import re
from utils import get_piece_symbol

engine_path = "engines/KomodoDragon3.3.exe"  # Path to the chess engine

class SimpleChessGUI:
    def __init__(self, root, position):
        self.root = root
        self.root.title("Chess Toolkit")
        self.board = chess.Board(position)
        self.square_size = 60
        self.selected_square = None
        self.hover_square = None
        self.game = chess.pgn.Game()
        self.node = self.game
        self.current_move_index = -1  # Track the current move index

        # Modernize the main frame
        self.main_frame = ttk.Frame(root, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Add a frame to hold the board and labels
        self.board_frame = ttk.Frame(self.main_frame)
        self.board_frame.pack(side=tk.LEFT, padx=10, pady=(0, 10), fill=tk.BOTH, expand=True)  # Reduced top padding to 0

        # Chessboard canvas with resizing
        self.canvas = tk.Canvas(self.board_frame,
                                bg='white',
                                highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0), pady=(20, 0))
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        self.canvas.bind("<Button-1>", self.on_square_clicked)
        self.canvas.bind("<Motion>", self.on_square_hover)

        # PGN frame
        self.pgn_frame = ttk.Frame(self.main_frame, padding=10)
        self.pgn_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)

        self.turn_label = ttk.Label(self.pgn_frame, font=("Arial", 12, "italic"))
        self.turn_label.pack(pady=(0, 10))  # Move turn label above PGN display

        self.pgn_label = ttk.Label(self.pgn_frame, text="PGN History", font=("Arial", 14, "bold"))
        self.pgn_label.pack(pady=(0, 10))

        # Add a divider line for better separation
        self.divider = ttk.Separator(self.pgn_frame, orient=tk.HORIZONTAL)
        self.divider.pack(fill=tk.X, pady=(0, 10))

        self.pgn_canvas = tk.Canvas(self.pgn_frame, bg="#f9f9f9", highlightthickness=0)
        self.pgn_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = ttk.Scrollbar(self.pgn_frame, orient=tk.VERTICAL, command=self.pgn_canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.pgn_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.pgn_inner_frame = ttk.Frame(self.pgn_canvas)
        self.pgn_inner_frame.bind("<Configure>", lambda e: self.pgn_canvas.configure(scrollregion=self.pgn_canvas.bbox("all")))

        self.pgn_window = self.pgn_canvas.create_window((0, 0), window=self.pgn_inner_frame, anchor="nw", width=self.pgn_canvas.winfo_width())

        self.pgn_canvas.bind("<Configure>", self._resize_pgn_inner_frame)
        self.pgn_canvas.bind("<Button-1>", self.on_pgn_click)  # Bind click event to PGN canvas

        self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")

        # Adjust canvas size to include padding for coordinates
        board_size = 8 * self.square_size
        total_size = board_size + 40
        self.canvas.config(width=total_size, height=total_size)

        # Draw rounded rectangle as background
        self.draw_rounded_rectangle(20, 20, board_size + 20, board_size + 20, radius=20, fill="#d9d9d9")

        # Draw chess squares and pieces FIRST
        for row in range(8):
            for col in range(8):
                x1 = col * self.square_size + 20
                y1 = row * self.square_size + 20
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                color = "#f0d9b5" if (row + col) % 2 == 0 else "#b58863"
                square = chess.square(col, 7 - row)
                if self.selected_square == square:
                    color = "#ff6961"
                elif self.hover_square == square:
                    color = "#f4a261"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
                piece = self.board.piece_at(square)
                if piece:
                    text = get_piece_symbol(piece)
                    self.canvas.create_text(x1 + self.square_size // 2,
                                            y1 + self.square_size // 2,
                                            text=text,
                                            font=("Arial", int(self.square_size * 0.5), "bold"),
                                            fill="black" if piece.color == chess.BLACK else "white")

        # Draw coordinates ON TOP of everything else
        self.draw_coordinates()

        # Update game status display
        if self.board.is_checkmate():
            self.turn_label.config(text=f"Checkmate! {'White' if not self.board.turn else 'Black'} wins!",
                                   foreground="red")
        elif self.board.is_check():
            self.turn_label.config(text=f"Check! {'White' if self.board.turn else 'Black'} to move.",
                                   foreground="orange")
        else:
            self.turn_label.config(text=f"Turn: {'White' if self.board.turn else 'Black'}", foreground="black")


        for row in range(8):
            for col in range(8):
                x1 = col * self.square_size + 20
                y1 = row * self.square_size + 20
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                color = "#f0d9b5" if (row + col) % 2 == 0 else "#b58863"
                square = chess.square(col, 7 - row)
                if self.selected_square == square:
                    color = "#ff6961"  # Highlight selected square
                elif self.hover_square == square:
                    color = "#f4a261"  # Highlight hovered square
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
                piece = self.board.piece_at(square)
                if piece:
                    text = get_piece_symbol(piece)
                    self.canvas.create_text(x1 + self.square_size // 2,
                                            y1 + self.square_size // 2,
                                            text=text, font=("Arial", int(self.square_size * 0.5), "bold"),
                                            fill="black" if piece.color == chess.BLACK else "white")
        self.draw_coordinates()
        # Update turn label with check or checkmate messages
        if self.board.is_checkmate():
            self.turn_label.config(text=f"Checkmate! {'White' if not self.board.turn else 'Black'} wins!",
                                   foreground="red")
        elif self.board.is_check():
            self.turn_label.config(text=f"Check! {'White' if self.board.turn else 'Black'} to move.",
                                   foreground="orange")
        else:
            self.turn_label.config(text=f"Turn: {'White' if self.board.turn else 'Black'}", foreground="black")

    def draw_rounded_rectangle(self, x1, y1, x2, y2, radius=20, **kwargs):
        """
        Draws a rounded rectangle on the canvas.
        :param x1: Top-left x-coordinate
        :param y1: Top-left y-coordinate
        :param x2: Bottom-right x-coordinate
        :param y2: Bottom-right y-coordinate
        :param radius: Radius of the corners
        :param kwargs: Additional arguments for the canvas.create_polygon method
        """
        points = [
            (x1 + radius, y1),
            (x2 - radius, y1),
            (x2, y1 + radius),
            (x2, y2 - radius),
            (x2 - radius, y2),
            (x1 + radius, y2),
            (x1, y2 - radius),
            (x1, y1 + radius)
        ]
        self.canvas.create_polygon(points, smooth=True, **kwargs)

    def draw_coordinates(self):
        """
        Draws rank (1-8) and file (a-h) labels around the chessboard.
        """
        for i in range(8):
            # Rank labels (1-8) on the left
            rank_label = 8 - i
            self.canvas.create_text(
                10, i * self.square_size + self.square_size // 2 + 20,
                text=str(rank_label), font=("Arial", int(self.square_size * 0.3), "bold"),
                anchor="w"
            )
            # File labels (a-h) on the bottom
            file_label = chr(ord('a') + i)
            self.canvas.create_text(
                i * self.square_size + self.square_size // 2 + 20, 8 * self.square_size + 30,
                text=file_label, font=("Arial", int(self.square_size * 0.3), "bold"),
                anchor="s"
            )

    def _resize_pgn_inner_frame(self, event):
        """
        Resizes the PGN inner frame to match the width of the canvas.
        """
        canvas_width = event.width
        self.pgn_canvas.itemconfig(self.pgn_window, width=canvas_width)

    def on_canvas_resize(self, event):
        """
        Handles resizing of the canvas and redraws the board with updated dimensions.
        """
        new_size = min(event.width - 40, event.height - 40) // 8  # Adjust for padding
        self.square_size = new_size
        self.draw_board()

    def update_pgn_display(self):
        """
        Updates the PGN display with each move split into two columns (white and black).
        """
        for widget in self.pgn_inner_frame.winfo_children():
            widget.destroy()

        pgn_str = self.get_pgn()
        moves = pgn_str.split("\n")

        for idx, move in enumerate(moves):
            move_frame = ttk.Frame(self.pgn_inner_frame)
            move_frame.pack(fill=tk.X, pady=2, padx=0)

            parts = move.split(" ", 2)  # Split into move number, white move, and black move
            move_number = parts[0] if len(parts) > 0 else ""
            white_move = parts[1] if len(parts) > 1 else ""
            black_move = parts[2] if len(parts) > 2 else ""

            move_number_label = ttk.Label(move_frame, text=move_number, font=("Courier", 12), anchor="center", width=5)
            move_number_label.pack(side=tk.LEFT, fill=tk.Y)

            white_move_label = ttk.Label(
                move_frame,
                text=white_move,
                font=("Courier", 12),
                anchor="center",
                background="#add8e6" if idx * 2 == self.current_move_index else "#ffffff",
                width=10
            )
            white_move_label.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 5))
            white_move_label.bind("<Button-1>", lambda e, move_idx=idx * 2: self.go_to_move(move_idx))

            black_move_label = ttk.Label(
                move_frame,
                text=black_move,
                font=("Courier", 12),
                anchor="center",
                background="#add8e6" if idx * 2 + 1 == self.current_move_index else "#ffffff",
                width=10
            )
            black_move_label.pack(side=tk.LEFT, fill=tk.Y)
            black_move_label.bind("<Button-1>", lambda e, move_idx=idx * 2 + 1: self.go_to_move(move_idx))

    def get_pgn(self):
        exporter = chess.pgn.StringExporter(headers=False, variations=False, comments=False)
        self.game.accept(exporter)
        pgn_str = str(exporter)
        moves = re.findall(r'\b(?:\d+\.+[^\s]*)|(\S+)', pgn_str)
        moves = [m for m in moves if m and not re.match(r'^\d+\.+$', m)]
        formatted = []
        move_number = 1
        for idx, move in enumerate(moves):
            if idx % 2 == 0:
                formatted.append(f"{move_number}. {move}")
            else:
                if formatted:
                    formatted[-1] += f" {move}"
                    move_number += 1
        if not self.game.end():
            if len(moves) % 2 == 0:
                formatted.append(f"{move_number}. *")
            else:
                if formatted:
                    formatted[-1] += " *"
        return "\n".join(formatted)

    def go_to_move(self, move_index):
        """
        Reverts the board to the position corresponding to the given move index.
        :param move_index: The index of the move to revert to.
        """
        self.board = chess.Board()  # Reset the board to the starting position
        self.node = self.game  # Reset the PGN node to the root
        for i, move in enumerate(self.game.mainline_moves()):
            if i > move_index:
                break
            self.board.push(move)
            self.node = self.node.variation(0) if self.node.variations else self.node
        self.selected_square = None
        self.hover_square = None
        self.current_move_index = move_index  # Update the current move index
        self.update_pgn_display()  # Refresh PGN display to highlight the current move
        self.draw_board()

    def on_square_clicked(self, event):
        col = event.x // self.square_size
        row = 7 - (event.y // self.square_size)
        # Ensure the click is within the board boundaries
        if not (0 <= col < 8 and 0 <= row < 8):
            return
        square = chess.square(col, row)
        if self.selected_square is not None:
            move = chess.Move(self.selected_square, square)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.node = self.node.add_variation(move)
                self.selected_square = None
                self.current_move_index += 1  # Update the current move index
                self.update_pgn_display()  # Update PGN only when a move is made
                # Print the FEN after a valid move
                print("Current FEN:", self.board.fen())
                self.analyze_position()  # Call engine analysis after the move
            else:
                self.selected_square = square
        else:
            self.selected_square = square
        self.draw_board()

    def analyze_position(self):
        """
        Analyzes the current board position using the chess engine.
        """
        with chess.engine.SimpleEngine.popen_uci(engine_path) as engine:
            info = engine.analyse(self.board, chess.engine.Limit(time=0.1))
            print("Engine Analysis:", info)

    def on_square_hover(self, event):
        col = event.x // self.square_size
        row = 7 - (event.y // self.square_size)
        # Ensure the hover is within the board boundaries
        if not (0 <= col < 8 and 0 <= row < 8):
            if self.hover_square is not None:  # Clear hover if outside the board
                self.hover_square = None
                self.draw_board()
            return
        square = chess.square(col, row)
        if self.hover_square != square:  # Only redraw if the hover square changes
            self.hover_square = square
            self.draw_board()

    def on_pgn_click(self, event):
        """
        Handles clicks on the PGN canvas.
        """
        widget = self.pgn_canvas.winfo_containing(event.x_root, event.y_root)
        if isinstance(widget, ttk.Label):
            widget.event_generate("<Button-1>")

