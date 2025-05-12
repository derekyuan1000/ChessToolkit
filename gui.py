import chess
import chess.pgn
import chess.engine
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import re
from utils import get_piece_symbol

class ModernChessGUI:
    def __init__(self, root, position, engine_path="engines/Stockfish17.exe"):
        self.root = root
        self.engine_path = engine_path
        self.root.configure(bg="#2d2d2d")
        self.root.title("Chess Toolkit Pro")
        self.configure_styles()
        self.engines = {
            "Stockfish": "engines/Stockfish17.exe",
            "Komodo Dragon": "engines/KomodoDragon3.3.exe",
            "Houdini": "engines/Houdini.exe",
            "Obsidian": "engines/Obsidian.exe",
        }
        self.board = chess.Board(position)
        self.square_size = 60
        self.selected_square = None
        self.hover_square = None
        self.game = chess.pgn.Game()
        self.node = self.game
        self.current_move_index = -1
        self.THINK_TIME = 0.05
        self.create_header()
        self.create_main_panes()
        self.create_board_section()
        self.create_side_panel()
        self.draw_board()
        self.canvas.bind("<Button-1>", self.on_square_clicked)
        self.canvas.bind("<Motion>", self.on_square_hover)
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        self.pgn_tree.bind("<<TreeviewSelect>>", self.on_pgn_select)

    def configure_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Modern.TFrame", background="#2d2d2d")
        style.configure("Card.TFrame", background="#363636", borderwidth=2)
        style.configure("PanelTitle.TLabel", background="#363636", foreground="#ffffff", font=('Segoe UI', 10, 'bold'))
        style.configure("Modern.TCombobox", fieldbackground="#404040", foreground="#000000", selectbackground="#4a9bff")  # Changed foreground to black
        style.configure("Modern.Treeview", background="#363636", fieldbackground="#363636", foreground="#ffffff", borderwidth=0)
        style.map("Modern.Treeview", background=[('selected', '#4a9bff')])

    def create_header(self):
        self.header = ttk.Frame(self.root, style="Modern.TFrame")
        self.header.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(self.header, text="Chess Toolkit Pro", font=("Segoe UI", 14, "bold"), foreground="#ffffff", background="#2d2d2d").pack(side=tk.LEFT)
        self.engine_var = tk.StringVar(value="Stockfish")
        self.engine_menu = ttk.Combobox(self.header, textvariable=self.engine_var, values=list(self.engines.keys()), style="Modern.TCombobox", state="readonly")
        self.engine_menu.pack(side=tk.RIGHT, padx=10)
        self.engine_menu.bind("<<ComboboxSelected>>", self.on_engine_change)

    def create_main_panes(self):
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    def create_board_section(self):
        self.board_container = ttk.Frame(self.main_paned, style="Card.TFrame")
        self.board_frame = ttk.Frame(self.board_container)
        self.board_frame.pack(padx=20, pady=20)
        self.canvas = tk.Canvas(self.board_frame, bg="#363636", highlightthickness=0)
        self.canvas.pack()
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        self.main_paned.add(self.board_container, weight=3)

    def create_side_panel(self):
        self.side_panel = ttk.Frame(self.main_paned, style="Card.TFrame")
        ttk.Label(self.side_panel, text="GAME HISTORY", style="PanelTitle.TLabel").pack(pady=(10, 5), padx=10, anchor='w')
        self.pgn_tree = ttk.Treeview(self.side_panel, columns=('move', 'white', 'black'), show='headings', style="Modern.Treeview")
        self.pgn_tree.heading('move', text='Move', anchor='w')
        self.pgn_tree.heading('white', text='White', anchor='w')
        self.pgn_tree.heading('black', text='Black', anchor='w')
        self.pgn_tree.column('move', width=60)
        self.pgn_tree.column('white', width=100)
        self.pgn_tree.column('black', width=100)
        self.pgn_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        ttk.Label(self.side_panel, text="ENGINE ANALYSIS", style="PanelTitle.TLabel").pack(pady=(10, 5), padx=10, anchor='w')
        self.evaluation_bar = tk.Canvas(self.side_panel, height=20, bg="#404040", highlightthickness=0)
        self.evaluation_bar.pack(fill=tk.X, padx=10, pady=(0, 5))
        self.analysis_text = tk.Text(self.side_panel, height=8, wrap=tk.WORD, bg="#404040", fg="white", insertbackground="white", padx=10, pady=5, font=("Segoe UI", 10))
        self.analysis_text.pack(fill=tk.BOTH, padx=10, pady=(0, 10))
        self.main_paned.add(self.side_panel, weight=1)

    def draw_board(self):
        self.canvas.delete("all")
        board_size = 8 * self.square_size
        self.canvas.config(width=board_size, height=board_size)
        self.create_round_rect(0, 0, board_size, board_size, radius=15, fill="#1e1e1e")  # Darker background
        for row in range(8):
            for col in range(8):
                x = col * self.square_size
                y = row * self.square_size
                color = "#f0d9b5" if (row + col) % 2 == 0 else "#b58863"  # Light and dark brown squares
                square = chess.square(col, 7 - row)
                if self.selected_square == square:
                    color = "#ffcccb"  # Highlight selected square with light red
                elif self.hover_square == square:
                    color = "#add8e6"  # Highlight hover square with light blue
                # Removed unnecessary borders or outlines
                self.canvas.create_rectangle(x, y, x + self.square_size, y + self.square_size, fill=color, outline="")
                piece = self.board.piece_at(square)
                if piece:
                    text = get_piece_symbol(piece)
                    fill_color = "#ffffff" if piece.color == chess.WHITE else "#000000"
                    self.canvas.create_text(x + self.square_size // 2, y + self.square_size // 2, text=text, font=('Segoe UI', int(self.square_size * 0.6), 'bold'), fill=fill_color)
        self.update_status_labels()

    def create_round_rect(self, x1, y1, width, height, radius=25, **kwargs):
        x2 = x1 + width
        y2 = y1 + height
        points = [x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius, x2, y2 - radius, x2 - radius, y2, x1 + radius, y2, x1, y2, x1, y2 - radius, x1, y1 + radius, x1 + radius, y1]
        return self.canvas.create_polygon(points, **kwargs, smooth=True)

    def update_status_labels(self):
        status_text = ""
        if self.board.is_checkmate():
            status_text = f"Checkmate! {'White' if not self.board.turn else 'Black'} wins!"
        elif self.board.is_check():
            status_text = f"Check! {'White' if self.board.turn else 'Black'} to move."
        else:
            status_text = f"{'White' if self.board.turn else 'Black'} to move"
        self.header.children['!label'].configure(text=f"Chess Toolkit Pro • {status_text}")

    def on_engine_change(self, event):
        engine_name = self.engine_var.get()
        self.engine_path = self.engines[engine_name]
        self.analysis_text.config(state=tk.NORMAL)
        self.analysis_text.delete(1.0, tk.END)
        self.analysis_text.insert(tk.END, f"Engine changed to: {engine_name}\n")
        self.analysis_text.config(state=tk.DISABLED)
        self.analyze_position()

    def analyze_position(self):
        with chess.engine.SimpleEngine.popen_uci(self.engine_path) as engine:
            info = engine.analyse(self.board, chess.engine.Limit(time=self.THINK_TIME))
            self.display_analysis(info)
            self.update_evaluation_bar(info['score'].relative)

    def display_analysis(self, info):
        self.analysis_text.config(state=tk.NORMAL)
        self.analysis_text.delete(1.0, tk.END)
        analysis_lines = [
            f"{self.engine_var.get()} Analysis:",
            f"Evaluation: {self.format_score(info['score'].relative)}",
            f"Best line: {self.format_pv(info['pv'])}"
        ]
        self.analysis_text.insert(tk.END, "\n".join(analysis_lines))
        self.analysis_text.config(state=tk.DISABLED)

    def format_score(self, score):
        if score.is_mate():
            return f"M{abs(score.mate())}"
        return f"{score.score() / 100:.2f}"

    def format_pv(self, pv):
        board_copy = self.board.copy()
        moves = []
        for move in pv:
            moves.append(board_copy.san(move))
            board_copy.push(move)
        return " ".join(moves[:5]) + ("..." if len(moves) > 5 else "")

    def update_evaluation_bar(self, score):
        self.evaluation_bar.delete("all")
        bar_width = self.evaluation_bar.winfo_width()
        for i in range(bar_width):
            ratio = i / bar_width
            # White-to-black gradient
            color = "#%02x%02x%02x" % (int(255 * (1 - ratio)), int(255 * (1 - ratio)), int(255 * (1 - ratio)))
            self.evaluation_bar.create_line(i, 0, i, 20, fill=color)
        if score.is_mate():
            eval_value = 1.0 if score.mate() > 0 else 0.0
        else:
            eval_value = (score.score() / 100 + 10) / 20
        marker_x = eval_value * bar_width
        self.evaluation_bar.create_line(marker_x, 0, marker_x, 20, fill="#ff0000", width=2)  # Red marker for clarity

        # Determine text color and position
        if score.is_mate():
            text = f"M{abs(score.mate())}"
            text_color = "#000000" if score.mate() > 0 else "#ffffff"
            text_anchor = tk.W if score.mate() > 0 else tk.E
            text_x = 10 if score.mate() > 0 else bar_width - 10
        else:
            eval_value = score.score() / 100
            text = f"{eval_value:.2f}"
            if eval_value > 0:  # White is winning
                text_color = "#000000"
                text_anchor = tk.W
                text_x = 10
            else:  # Black is winning
                text_color = "#ffffff"
                text_anchor = tk.E
                text_x = bar_width - 10

        self.evaluation_bar.create_text(
            text_x, 10, text=text, anchor=text_anchor, fill=text_color, font=("Segoe UI", 9)
        )

    def on_square_clicked(self, event):
        col = (event.x) // self.square_size
        row = 7 - (event.y // self.square_size)
        if not (0 <= col < 8 and 0 <= row < 8):
            return
        square = chess.square(col, row)
        piece = self.board.piece_at(square)

        if self.selected_square is None:
            if piece and piece.color == self.board.turn:
                self.selected_square = square
        else:
            move = chess.Move(self.selected_square, square)
            if move in self.board.legal_moves:
                self.make_move(move)
            self.selected_square = None

        self.draw_board()

    def make_move(self, move):
        self.board.push(move)
        self.node = self.node.add_variation(move)
        self.selected_square = None
        self.current_move_index += 1
        self.update_pgn_display()
        self.analyze_position()


    def update_pgn_display(self):
        self.pgn_tree.delete(*self.pgn_tree.get_children())
        pgn_str = self.get_pgn()
        moves = re.findall(r'(\d+)\.\s+(\S+)(?:\s+(\S+))?', pgn_str)
        for move_num, white, black in moves:
            self.pgn_tree.insert("", "end", values=(move_num, white, black or ""))

    def get_pgn(self):
        exporter = chess.pgn.StringExporter(headers=False)
        return self.game.accept(exporter)

    def on_pgn_select(self, event):
        selected_item = self.pgn_tree.selection()
        if selected_item:
            move_num = int(self.pgn_tree.item(selected_item[0], 'values')[0])
            self.go_to_move((move_num - 1) * 2)

    def go_to_move(self, move_index):
        self.board = chess.Board()
        self.node = self.game
        for i, move in enumerate(self.game.mainline_moves()):
            if i > move_index:
                break
            self.board.push(move)
            self.node = self.node.variation(0)
        self.current_move_index = move_index
        self.draw_board()
        self.analyze_position()

    def on_canvas_resize(self, event):
        # Increase the scaling factor by using a larger portion of the canvas dimensions
        new_size = min(event.width, event.height) // 8
        self.square_size = new_size
        self.draw_board()

    def on_square_hover(self, event):
        col = event.x // self.square_size
        row = 7 - (event.y // self.square_size)
        square = chess.square(col, row) if (0 <= col < 8 and 0 <= row < 8) else None
        if self.hover_square != square:
            self.hover_square = square
            self.draw_board()
