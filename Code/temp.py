import os
import time
import chess
import chess.engine
import chess.pgn
import customtkinter as ctk
from datetime import datetime
import threading
import queue
import re  # Import regex for PGN formatting


class BattleArena:
    def __init__(self, root):
        self.root = root
        self.engines = {
            "Human": "Human",
            "Stockfish": "../engines/Stockfish17.exe",
            "Komodo Dragon": "../engines/KomodoDragon3.3.exe",
            "Houdini": "../engines/Houdini.exe",
            "Obsidian": "../engines/Obsidian.exe",
        }
        self.engine1 = None
        self.engine2 = None
        self.board = chess.Board()
        self.game_history = []
        self.current_game = None
        self.is_match_running = False
        self.match_thread = None
        self.move_queue = queue.Queue()
        self.selected_square = None
        self.display_update_timer = None
        self.waiting_for_human = False

        # Match settings
        self.num_games = 10
        self.time_per_move = 1.0  # seconds
        self.current_game_num = 0
        self.score = {"engine1": 0, "engine2": 0, "draws": 0}
        self.node = None  # Initialize node
        self.current_move_index = -1  # Initialize move index

        self.create_gui()
        self.update_board()

    def create_gui(self):
        # Set up the main container
        self.main_container = ctk.CTkFrame(self.root)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_label = ctk.CTkLabel(
            self.main_container,
            text="Chess Engine Battle Arena",
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold")
        )
        title_label.pack(pady=(0, 20))

        # Engine selection panel
        self.setup_frame = ctk.CTkFrame(self.main_container, corner_radius=10)
        self.setup_frame.pack(fill="x", pady=10)

        # Engine 1 selection
        engine1_frame = ctk.CTkFrame(self.setup_frame, fg_color="transparent")
        engine1_frame.pack(side="left", fill="x", expand=True, padx=20, pady=10)

        ctk.CTkLabel(
            engine1_frame,
            text="Engine 1 (White):",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        ).pack(pady=(0, 5))

        self.engine1_var = ctk.StringVar(value="Stockfish")
        self.engine1_menu = ctk.CTkOptionMenu(
            engine1_frame,
            values=list(self.engines.keys()),
            variable=self.engine1_var,
            width=200,
            command=self.on_engine_selection_change
        )
        self.engine1_menu.pack()

        # Engine 2 selection
        engine2_frame = ctk.CTkFrame(self.setup_frame, fg_color="transparent")
        engine2_frame.pack(side="right", fill="x", expand=True, padx=20, pady=10)

        ctk.CTkLabel(
            engine2_frame,
            text="Engine 2 (Black):",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        ).pack(pady=(0, 5))

        self.engine2_var = ctk.StringVar(value="Komodo Dragon")
        self.engine2_menu = ctk.CTkOptionMenu(
            engine2_frame,
            values=list(self.engines.keys()),
            variable=self.engine2_var,
            width=200,
            command=self.on_engine_selection_change
        )
        self.engine2_menu.pack()

        # Match settings
        settings_frame = ctk.CTkFrame(self.main_container, corner_radius=10)
        settings_frame.pack(fill="x", pady=10)

        # Number of games
        games_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        games_frame.pack(side="left", fill="x", expand=True, padx=20, pady=10)

        ctk.CTkLabel(
            games_frame,
            text="Number of Games:",
            font=ctk.CTkFont(family="Segoe UI", size=14)
        ).pack(side="left", padx=(0, 10))

        self.games_var = ctk.StringVar(value="10")
        games_entry = ctk.CTkEntry(
            games_frame,
            width=60,
            textvariable=self.games_var
        )
        games_entry.pack(side="left")

        # Time per move
        time_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        time_frame.pack(side="right", fill="x", expand=True, padx=20, pady=10)

        ctk.CTkLabel(
            time_frame,
            text="Time per Move (seconds):",
            font=ctk.CTkFont(family="Segoe UI", size=14)
        ).pack(side="left", padx=(0, 10))

        self.time_var = ctk.StringVar(value="1.0")
        time_entry = ctk.CTkEntry(
            time_frame,
            width=60,
            textvariable=self.time_var
        )
        time_entry.pack(side="left")

        # Game display - split into board and info sections
        display_frame = ctk.CTkFrame(self.main_container, corner_radius=10)
        display_frame.pack(fill="both", expand=True, pady=10)

        # Chess board canvas
        board_frame = ctk.CTkFrame(display_frame, corner_radius=0)
        board_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.canvas = ctk.CTkCanvas(
            board_frame,
            width=400,
            height=400,
            bg="#2b2b2b",
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)

        # Add click handler for human moves
        self.canvas.bind("<Button-1>", self.on_square_clicked)

        # Game info and history
        info_frame = ctk.CTkFrame(display_frame, corner_radius=0, width=300)
        info_frame.pack(side="right", fill="both", padx=10, pady=10)
        info_frame.pack_propagate(False)

        # Current status
        status_label = ctk.CTkLabel(
            info_frame,
            text="Match Status",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        )
        status_label.pack(anchor="w", padx=10, pady=(10, 5))

        self.status_text = ctk.CTkTextbox(
            info_frame,
            height=80,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            wrap="word"
        )
        self.status_text.pack(fill="x", padx=10, pady=(0, 10))
        self.status_text.insert("1.0", "Ready to start match")
        self.status_text.configure(state="disabled")

        # Score display
        score_label = ctk.CTkLabel(
            info_frame,
            text="Match Score",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        )
        score_label.pack(anchor="w", padx=10, pady=(10, 5))

        self.score_text = ctk.CTkTextbox(
            info_frame,
            height=60,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            wrap="word"
        )
        self.score_text.pack(fill="x", padx=10, pady=(0, 10))
        self.update_score_display()
        self.score_text.configure(state="disabled")

        # Move history
        history_label = ctk.CTkLabel(
            info_frame,
            text="Current Game",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        )
        history_label.pack(anchor="w", padx=10, pady=(10, 5))

        self.move_text = ctk.CTkTextbox(
            info_frame,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            wrap="word"
        )
        self.move_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Control buttons
        control_frame = ctk.CTkFrame(self.main_container, corner_radius=10, height=60)
        control_frame.pack(fill="x", pady=10)

        self.start_button = ctk.CTkButton(
            control_frame,
            text="Start Match",
            font=ctk.CTkFont(family="Segoe UI", size=16),
            height=40,
            width=150,
            command=self.start_match
        )
        self.start_button.pack(side="left", padx=20, pady=10)

        self.stop_button = ctk.CTkButton(
            control_frame,
            text="Stop Match",
            font=ctk.CTkFont(family="Segoe UI", size=16),
            height=40,
            width=150,
            command=self.stop_match,
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=20, pady=10)

        self.return_button = ctk.CTkButton(
            control_frame,
            text="Return to Main Menu",
            font=ctk.CTkFont(family="Segoe UI", size=16),
            height=40,
            width=200,
            command=self.return_to_main_menu
        )
        self.return_button.pack(side="right", padx=20, pady=10)

        self.start_display_updates()

    def start_display_updates(self):
        def update_handler():
            if self.is_match_running:
                try:
                    while not self.move_queue.empty():
                        update = self.move_queue.get_nowait()
                        if update == "board":
                            self.update_board()
                except queue.Empty:
                    pass
                self.root.after(100, update_handler)

        self.root.after(100, update_handler)

    def update_score_display(self):
        engine1_name = self.engine1_var.get()
        engine2_name = self.engine2_var.get()

        self.score_text.configure(state="normal")
        self.score_text.delete("1.0", "end")
        score_info = f"{engine1_name}: {self.score['engine1']}\n"
        score_info += f"{engine2_name}: {self.score['engine2']}\n"
        score_info += f"Draws: {self.score['draws']}"
        self.score_text.insert("1.0", score_info)
        self.score_text.configure(state="disabled")

    def update_status(self, message):
        self.status_text.configure(state="normal")
        self.status_text.delete("1.0", "end")
        self.status_text.insert("1.0", message)
        self.status_text.configure(state="disabled")

    def update_move_history(self):
        self.move_text.delete("1.0", "end")

        if self.current_game:
            moves = []
            board = chess.Board()
            for i, move in enumerate(self.current_game.mainline_moves()):
                move_num = (i // 2) + 1
                if i % 2 == 0:
                    moves.append(f"{move_num}. {board.san(move)}")
                else:
                    moves[-1] += f" {board.san(move)}"
                board.push(move)

            self.move_text.insert("1.0", "\n".join(moves))

    def draw_board(self):
        self.canvas.delete("all")

        # Get canvas dimensions
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        # Ensure minimum size
        width = max(width, 400)
        height = max(height, 400)

        # Calculate square size
        square_size = min(width, height) // 8

        # Draw squares
        for row in range(8):
            for col in range(8):
                x1 = col * square_size
                y1 = row * square_size
                x2 = x1 + square_size
                y2 = y1 + square_size

                color = "#e9edcc" if (row + col) % 2 == 0 else "#779556"

                if self.selected_square is not None and self.waiting_for_human:
                    selected_col = chess.square_file(self.selected_square)
                    selected_row = 7 - chess.square_rank(self.selected_square)
                    if row == selected_row and col == selected_col:
                        color = "#f7f769"

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

                square = chess.square(col, 7 - row)
                piece = self.board.piece_at(square)

                if piece:
                    piece_symbol = self.get_piece_symbol(piece)
                    text_color = "#ffffff" if piece.color == chess.WHITE else "#000000"

                    self.canvas.create_text(
                        x1 + square_size // 2,
                        y1 + square_size // 2,
                        text=piece_symbol,
                        font=('Segoe UI', int(square_size * 0.6), 'bold'),
                        fill=text_color
                    )

        if self.selected_square is not None and self.waiting_for_human:
            for move in self.board.legal_moves:
                if move.from_square == self.selected_square:
                    target_col = chess.square_file(move.to_square)
                    target_row = 7 - chess.square_rank(move.to_square)
                    x1 = target_col * square_size
                    y1 = target_row * square_size

                    if self.board.piece_at(move.to_square):
                        self.canvas.create_rectangle(
                            x1, y1, x1 + square_size, y1 + square_size,
                            outline="#f7f769", width=3
                        )
                    else:
                        self.canvas.create_oval(
                            x1 + square_size * 0.4, y1 + square_size * 0.4,
                            x1 + square_size * 0.6, y1 + square_size * 0.6,
                            fill="#f7f769", outline=""
                        )

    def get_piece_symbol(self, piece):
        symbols = {
            'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
            'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'
        }
        return symbols.get(piece.symbol(), '')

    def update_board(self):
        self.draw_board()
        self.update_move_history()

    def on_engine_selection_change(self, *args):
        if self.engine1_var.get() == "Human" or self.engine2_var.get() == "Human":
            self.games_var.set("1")
            self.time_var.set("0.1")
            self.update_status("Human player selected. Number of games set to 1.")

    def on_square_clicked(self, event):
        if not self.waiting_for_human:
            return

        width = self.canvas.winfo_width()
        square_size = min(width, self.canvas.winfo_height()) // 8
        col = event.x // square_size
        row = 7 - (event.y // square_size)

        if not (0 <= col < 8 and 0 <= row < 8):
            return

        square = chess.square(col, row)
        piece = self.board.piece_at(square)

        if self.selected_square is None:
            if piece and piece.color == self.board.turn:
                self.selected_square = square
                self.draw_board()
        else:
            move = chess.Move(self.selected_square, square)
            if (piece and piece.piece_type == chess.PAWN and
                    ((self.board.turn == chess.WHITE and chess.square_rank(square) == 7) or
                     (self.board.turn == chess.BLACK and chess.square_rank(square) == 0))):
                move = chess.Move(self.selected_square, square, promotion=chess.QUEEN)

            if move in self.board.legal_moves:
                self.make_move(move)

            self.selected_square = None

        self.draw_board()

    def make_move(self, move):
        self.board.push(move)
        self.node = self.node.add_variation(move)
        self.update_move_history()
        self.update_pgn_display()
        self.analyze_position()

    def update_pgn_display(self):
        self.pgn_tree.delete("1.0", "end")
        pgn_str = self.get_pgn()
        formatted_moves = []
        moves = re.findall(r'(\d+)\.\s+(\S+)(?:\s+(\S+))?', pgn_str)
        for move_num, white, black in moves:
            move_str = f"{move_num}. {white} "
            if black:
                move_str += black
            formatted_moves.append(move_str)
        self.pgn_tree.insert("1.0", "\n".join(formatted_moves))

    def get_pgn(self):
        exporter = chess.pgn.StringExporter(headers=False)
        return self.current_game.accept(exporter)

    def on_pgn_select(self, event):
        index = self.pgn_tree.index("@%d,%d" % (event.x, event.y))
        line = int(float(index)) - 1

        if 0 <= line < len(re.findall(r'\d+\.', self.get_pgn())):
            move_num = line + 1
            self.go_to_move((move_num - 1) * 2)

    def go_to_move(self, move_index):
        self.board = chess.Board()
        self.node = self.current_game
        for i, move in enumerate(self.current_game.mainline_moves()):
            if i > move_index:
                break
            self.board.push(move)
            self.node = self.node.variation(0)
        self.current_move_index = move_index
        self.draw_board()
        self.analyze_position()

    def on_canvas_resize(self, event):
        new_size = min(event.width, event.height) // 8
        if new_size != self.square_size:
            self.square_size = new_size
            self.draw_board()

    def on_square_hover(self, event):
        col = event.x // self.square_size
        row = 7 - (event.y // self.square_size)
        square = chess.square(col, row) if (0 <= col < 8 and 0 <= row < 8) else None
        if self.hover_square != square:
            self.hover_square = square
            self.draw_board()

    def export_pgn(self):
        from export_dialog import ExportDialog
        game = self.current_game
        game.headers["Event"] = "Chess Analysis"
        game.headers["Date"] = datetime.now().strftime("%Y.%m.%d")
        game.headers["White"] = "?"
        game.headers["Black"] = "?"
        game.headers["Result"] = self.board.result()
        ExportDialog(self.root, str(game))

    def import_pgn(self):
        from import_dialog import ImportDialog
        ImportDialog(self.root, self.load_pgn)

    def load_pgn(self, pgn_text):
        try:
            import io
            pgn_io = io.StringIO(pgn_text)
            new_game = chess.pgn.read_game(pgn_io)
            if new_game is None:
                return

            self.current_game = new_game
            self.board = chess.Board()
            self.node = self.current_game
            self.current_move_index = -1

            for move in self.current_game.mainline_moves():
                self.board.push(move)
                self.node = self.node.variation(0)
                self.current_move_index += 1

            self.draw_board()
            self.update_pgn_display()
            self.analyze_position()

        except Exception as e:
            print(f"Error importing PGN: {str(e)}")