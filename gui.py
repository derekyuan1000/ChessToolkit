import chess
import chess.pgn
import chess.engine
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import re
from utils import get_piece_symbol

engine_path = "engines/Stockfish17.exe"

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
        self.current_move_index = -1

        self.engines = {
            "Stockfish": "engines/Stockfish17.exe",
            "Komodo Dragon": "engines/KomodoDragon3.3.exe",
            "Houdini": "engines/Houdini.exe",
            "Obsidian": "engines/Obsidian.exe",
        }
        self.engine_path = engine_path

        self.main_frame = ttk.Frame(root, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.board_frame = ttk.Frame(self.main_frame)
        self.board_frame.pack(side=tk.LEFT, padx=10, pady=(0, 10), fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.board_frame, bg='white', highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0), pady=(20, 0))
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        self.canvas.bind("<Button-1>", self.on_square_clicked)
        self.canvas.bind("<Motion>", self.on_square_hover)

        self.pgn_frame = ttk.Frame(self.main_frame, padding=10)
        self.pgn_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)

        self.turn_label = ttk.Label(self.pgn_frame, font=("Arial", 12, "italic"))
        self.turn_label.pack(pady=(0, 10))

        self.pgn_label = ttk.Label(self.pgn_frame, text="PGN History", font=("Arial", 14, "bold"))
        self.pgn_label.pack(pady=(0, 10))

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
        self.pgn_canvas.bind("<Button-1>", self.on_pgn_click)

        self.analysis_frame = ttk.Frame(self.main_frame, padding=10)
        self.analysis_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 10))

        self.analysis_label = ttk.Label(self.analysis_frame, text="Engine Analysis", font=("Arial", 14, "bold"))
        self.analysis_label.pack(anchor="w", pady=(0, 5))

        self.analysis_text = tk.Text(self.analysis_frame, height=5, wrap=tk.WORD, state=tk.DISABLED, bg="#f9f9f9")
        self.analysis_text.pack(fill=tk.BOTH, expand=True)

        self.evaluation_bar = tk.Canvas(self.analysis_frame, height=20, bg="#d9d9d9", highlightthickness=0)
        self.evaluation_bar.pack(fill=tk.X, pady=(5, 0))

        self.engine_button = ttk.Button(self.analysis_frame, text="Select Engine", command=self.select_engine)
        self.engine_button.pack(side=tk.RIGHT, padx=(0, 10), pady=(5, 0))

        self.draw_board()

        self.THINK_TIME = 0.05

        self.highlighted_squares = set()
        self.arrows = []
        self.arrow_start_square = None

    def draw_board(self):
        self.canvas.delete("all")

        board_size = 8 * self.square_size
        total_size = board_size + 40
        self.canvas.config(width=total_size, height=total_size)

        self.draw_rounded_rectangle(20, 20, board_size + 20, board_size + 20, radius=20, fill="#d9d9d9")

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
                    self.canvas.create_text(x1 + self.square_size // 2, y1 + self.square_size // 2, text=text, font=("Arial", int(self.square_size * 0.5), "bold"), fill="black" if piece.color == chess.BLACK else "white")

        self.draw_coordinates()

        if self.board.is_checkmate():
            self.turn_label.config(text=f"Checkmate! {'White' if not self.board.turn else 'Black'} wins!", foreground="red")
        elif self.board.is_check():
            self.turn_label.config(text=f"Check! {'White' if self.board.turn else 'Black'} to move.", foreground="orange")
        else:
            self.turn_label.config(text=f"Turn: {'White' if self.board.turn else 'Black'}", foreground="black")

    def draw_rounded_rectangle(self, x1, y1, x2, y2, radius=20, **kwargs):
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
        for i in range(8):
            rank_label = 8 - i
            self.canvas.create_text(10, i * self.square_size + self.square_size // 2 + 20, text=str(rank_label), font=("Arial", int(self.square_size * 0.3), "bold"), anchor="w")
            file_label = chr(ord('a') + i)
            self.canvas.create_text(i * self.square_size + self.square_size // 2 + 20, 8 * self.square_size + 30, text=file_label, font=("Arial", int(self.square_size * 0.3), "bold"), anchor="s")

    def _resize_pgn_inner_frame(self, event):
        canvas_width = event.width
        self.pgn_canvas.itemconfig(self.pgn_window, width=canvas_width)

    def on_canvas_resize(self, event):
        new_size = min(event.width - 40, event.height - 40) // 8
        self.square_size = new_size
        self.draw_board()

    def update_pgn_display(self):
        for widget in self.pgn_inner_frame.winfo_children():
            widget.destroy()

        pgn_str = self.get_pgn()
        moves = pgn_str.split("\n")

        for idx, move in enumerate(moves):
            move_frame = ttk.Frame(self.pgn_inner_frame)
            move_frame.pack(fill=tk.X, pady=2, padx=0)

            parts = move.split(" ", 2)
            move_number = parts[0] if len(parts) > 0 else ""
            white_move = parts[1] if len(parts) > 1 else ""
            black_move = parts[2] if len(parts) > 2 else ""

            move_number_label = ttk.Label(move_frame, text=move_number, font=("Courier", 12), anchor="center", width=5)
            move_number_label.pack(side=tk.LEFT, fill=tk.Y)

            white_move_label = ttk.Label(move_frame, text=white_move, font=("Courier", 12), anchor="center", background="#add8e6" if idx * 2 == self.current_move_index else "#ffffff", width=10)
            white_move_label.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 5))
            white_move_label.bind("<Button-1>", lambda e, move_idx=idx * 2: self.go_to_move(move_idx))

            black_move_label = ttk.Label(move_frame, text=black_move, font=("Courier", 12), anchor="center", background="#add8e6" if idx * 2 + 1 == self.current_move_index else "#ffffff", width=10)
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
        self.board = chess.Board()
        self.node = self.game
        for i, move in enumerate(self.game.mainline_moves()):
            if i > move_index:
                break
            self.board.push(move)
            self.node = self.node.variation(0) if self.node.variations else self.node
        self.selected_square = None
        self.hover_square = None
        self.current_move_index = move_index
        self.update_pgn_display()
        self.draw_board()

    def on_square_clicked(self, event):
        col = (event.x - 20) // self.square_size
        row = 7 - ((event.y - 20) // self.square_size)
        if not (0 <= col < 8 and 0 <= row < 8):
            return
        square = chess.square(col, row)
        if self.selected_square is not None:
            move = chess.Move(self.selected_square, square)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.node = self.node.add_variation(move)
                self.selected_square = None
                self.current_move_index += 1
                self.update_pgn_display()
                print("Current FEN:", self.board.fen())
                self.analyze_position()
            else:
                self.selected_square = square
        else:
            self.selected_square = square
        self.draw_board()

    def select_engine(self):
        engine_window = tk.Toplevel(self.root)
        engine_window.title("Select Engine")
        engine_window.geometry("200x250")

        ttk.Label(engine_window, text="Select an Engine:", font=("Arial", 12, "bold")).pack(pady=10)

        for engine_name, engine_path in self.engines.items():
            ttk.Button(
                engine_window,
                text=engine_name,
                command=lambda path=engine_path: self.set_engine(path, engine_window)
            ).pack(pady=5)

    def set_engine(self, path, window):
        self.engine_path = path
        print(f"Engine selected: {self.engine_path}")
        window.destroy()

    def analyze_position(self):
        with chess.engine.SimpleEngine.popen_uci(self.engine_path) as engine:
            info = None
            while not info or "pv" not in info or not info["pv"]:
                info = engine.analyse(self.board, chess.engine.Limit(time=self.THINK_TIME))
            self.display_analysis(info)

    def update_evaluation_bar(self, score):
        self.evaluation_bar.delete("all")
        bar_width = self.evaluation_bar.winfo_width()
        bar_height = self.evaluation_bar.winfo_height()

        if score.is_mate():
            eval_value = 1.0 if score.mate() > 0 else -1.0
            eval_text = f"Mate in {abs(score.mate())}"
        else:
            eval_value = max(-10, min(10, score.score() / 100))
            eval_text = f"{eval_value:.2f}"
            eval_value = (eval_value + 10) / 20  # Normalize to range [0, 1]

        white_portion = eval_value * bar_width
        self.evaluation_bar.create_rectangle(0, 0, white_portion, bar_height, fill="white", outline="")
        self.evaluation_bar.create_rectangle(white_portion, 0, bar_width, bar_height, fill="black", outline="")

        if eval_value > 0.5:  # White is winning
            self.evaluation_bar.create_text(10, bar_height // 2, text=eval_text, font=("Arial", 10, "bold"),
                                            fill="black", anchor="w")
        else:  # Black is winning
            self.evaluation_bar.create_text(bar_width - 10, bar_height // 2, text=eval_text, font=("Arial", 10, "bold"),
                                            fill="white", anchor="e")

    def display_analysis(self, info):
        self.analysis_text.config(state=tk.NORMAL)
        self.analysis_text.delete(1.0, tk.END)

        if "score" in info:
            score = info["score"].relative
            self.update_evaluation_bar(score)
            if score.is_mate():
                analysis_text = f"Mate in {score.mate()}"
            else:
                analysis_text = f"Score: {score.score() / 100:.2f}"
        else:
            self.update_evaluation_bar(chess.engine.PovScore(chess.engine.Cp(0), chess.WHITE))
            analysis_text = "No score available."

        if "pv" in info and len(info["pv"]) > 0:
            analysis_board = self.board.copy()
            moves = []
            try:
                for move in info["pv"]:
                    moves.append(analysis_board.san(move))
                    analysis_board.push(move)
                analysis_text += f"\nBest Line: {' '.join(moves)}"
            except Exception as e:
                print(f"Error processing principal variation: {e}")
                analysis_text += "\nBest Line: Error processing moves."
        else:
            analysis_text += "\nBest Line: No moves provided by the engine."

        self.analysis_text.insert(tk.END, analysis_text)
        self.analysis_text.config(state=tk.DISABLED)

    def on_square_hover(self, event):
        col = (event.x - 20) // self.square_size
        row = 7 - ((event.y - 20) // self.square_size)
        if not (0 <= col < 8 and 0 <= row < 8):
            if self.hover_square is not None:
                self.hover_square = None
                self.draw_board()
            return
        square = chess.square(col, row)
        if self.hover_square != square:
            self.hover_square = square
            self.draw_board()

    def on_pgn_click(self, event):
        widget = self.pgn_canvas.winfo_containing(event.x_root, event.y_root)
        if isinstance(widget, ttk.Label):
            widget.event_generate("<Button-1>")

