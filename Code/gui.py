import chess
import chess.pgn
import chess.engine
import customtkinter as ctk
from PIL import Image, ImageTk
import re
import os
from utils import get_piece_symbol

class ModernChessGUI:
    def __init__(self, root, position, engine_path="../engines/Stockfish17.exe"):
        # Initialize customtkinter settings
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Initialize properties
        self.root = root
        self.engine_path = engine_path
        self.engines = {
            "Stockfish": "../engines/Stockfish17.exe",
            "Komodo Dragon": "../engines/KomodoDragon3.3.exe",
            "Houdini": "../engines/Houdini.exe",
            "Obsidian": "../engines/Obsidian.exe",
        }
        self.board = chess.Board(position)
        self.square_size = 60
        self.selected_square = None
        self.hover_square = None
        self.game = chess.pgn.Game()
        self.node = self.game
        self.current_move_index = -1
        self.THINK_TIME = 0.05

        # Create the main window as a frame inside root
        self.main_container = ctk.CTkFrame(self.root)
        self.main_container.pack(fill="both", expand=True)

        # Create main layout
        self.create_header()
        self.create_main_layout()
        self.create_board_section()
        self.create_side_panel()
        self.draw_board()

        # Bind events
        self.canvas.bind("<Button-1>", self.on_square_clicked)
        self.canvas.bind("<Motion>", self.on_square_hover)
        self.canvas.bind("<Configure>", self.on_canvas_resize)

    def create_header(self):
        self.header = ctk.CTkFrame(self.main_container, corner_radius=0, fg_color="transparent")
        self.header.pack(fill="x", padx=20, pady=10)

        # App title
        self.title_label = ctk.CTkLabel(
            self.header,
            text="Chess Toolkit Pro",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold")
        )
        self.title_label.pack(side="left")

        # Engine selection
        self.engine_var = ctk.StringVar(value="Stockfish")
        
        self.engine_menu = ctk.CTkOptionMenu(
            self.header,
            values=list(self.engines.keys()),
            variable=self.engine_var,
            width=150,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            command=self.on_engine_change
        )
        self.engine_menu.pack(side="right")

        engine_label = ctk.CTkLabel(
            self.header,
            text="Engine:",
            font=ctk.CTkFont(family="Segoe UI", size=14)
        )
        engine_label.pack(side="right", padx=(0, 10))

    def create_main_layout(self):
        self.main_frame = ctk.CTkFrame(self.main_container, corner_radius=0, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)

    def create_board_section(self):
        self.board_frame = ctk.CTkFrame(self.main_frame, corner_radius=15)
        self.board_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.canvas_frame = ctk.CTkFrame(self.board_frame, corner_radius=0, fg_color="transparent")
        self.canvas_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Create canvas for the chessboard
        self.canvas = ctk.CTkCanvas(
            self.canvas_frame,
            bg="#2b2b2b",
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        # Turn indicator
        self.turn_frame = ctk.CTkFrame(self.board_frame, corner_radius=10, height=40, fg_color="#1f538d")
        self.turn_frame.pack(fill="x", padx=20, pady=(0, 20))

        self.turn_label = ctk.CTkLabel(
            self.turn_frame,
            text="White to move",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        )
        self.turn_label.pack(pady=10)

    def create_side_panel(self):
        self.side_panel = ctk.CTkFrame(self.main_frame, corner_radius=15, width=350)
        self.side_panel.pack(side="right", fill="y", padx=(10, 0))
        self.side_panel.pack_propagate(False)

        # Game history section
        history_label = ctk.CTkLabel(
            self.side_panel,
            text="GAME HISTORY",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        )
        history_label.pack(pady=(20, 10), padx=20, anchor="w")

        # Game history display
        self.pgn_frame = ctk.CTkFrame(self.side_panel, corner_radius=10, fg_color="#2b2b2b")
        self.pgn_frame.pack(fill="x", padx=20, pady=(0, 20))

        self.pgn_tree = ctk.CTkTextbox(
            self.pgn_frame,
            height=200,
            font=ctk.CTkFont(family="Segoe UI", size=14)
        )
        self.pgn_tree.pack(fill="both", padx=10, pady=10)
        self.pgn_tree.bind("<Button-1>", self.on_pgn_select)

        # Engine analysis section
        analysis_label = ctk.CTkLabel(
            self.side_panel,
            text="ENGINE ANALYSIS",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        )
        analysis_label.pack(pady=(20, 10), padx=20, anchor="w")

        # Evaluation bar
        self.eval_frame = ctk.CTkFrame(self.side_panel, corner_radius=10, fg_color="#2b2b2b")
        self.eval_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.evaluation_bar = ctk.CTkCanvas(
            self.eval_frame,
            height=30,
            bg="#2b2b2b",
            highlightthickness=0
        )
        self.evaluation_bar.pack(fill="x", padx=10, pady=10)

        # Analysis text
        self.analysis_frame = ctk.CTkFrame(self.side_panel, corner_radius=10, fg_color="#2b2b2b")
        self.analysis_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.analysis_text = ctk.CTkTextbox(
            self.analysis_frame,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            wrap="word"
        )
        self.analysis_text.pack(fill="both", expand=True, padx=10, pady=10)

    def draw_board(self):
        self.canvas.delete("all")
        board_size = 8 * self.square_size
        self.canvas.config(width=board_size, height=board_size)

        # Draw board background
        self.canvas.create_rectangle(0, 0, board_size, board_size, fill="#2b2b2b", outline="")

        # Draw squares
        for row in range(8):
            for col in range(8):
                x = col * self.square_size
                y = row * self.square_size
                color = "#e9edcc" if (row + col) % 2 == 0 else "#779556"  # Chess.com colors
                square = chess.square(col, 7 - row)

                # Highlight selected and hover squares
                if self.selected_square == square:
                    color = "#f7f769"  # Bright yellow for selected
                elif self.hover_square == square and self.board.piece_at(square):
                    if self.board.piece_at(square).color == self.board.turn:
                        color = "#baca44" if (row + col) % 2 == 0 else "#8fb344"

                self.canvas.create_rectangle(
                    x, y,
                    x + self.square_size,
                    y + self.square_size,
                    fill=color,
                    outline=""
                )

                # Draw pieces
                piece = self.board.piece_at(square)
                if piece:
                    text = get_piece_symbol(piece)
                    fill_color = "#ffffff" if piece.color == chess.WHITE else "#000000"
                    self.canvas.create_text(
                        x + self.square_size // 2,
                        y + self.square_size // 2,
                        text=text,
                        font=('Segoe UI', int(self.square_size * 0.6), 'bold'),
                        fill=fill_color
                    )

        # Draw coordinates
        for i in range(8):
            # File labels (a-h)
            file_label = chr(97 + i)
            x = i * self.square_size + self.square_size // 2
            y = board_size - 12
            self.canvas.create_text(
                x, y,
                text=file_label,
                font=('Segoe UI', 12),
                fill="#cccccc"
            )

            # Rank labels (1-8)
            rank_label = str(8 - i)
            x = 12
            y = i * self.square_size + self.square_size // 2
            self.canvas.create_text(
                x, y,
                text=rank_label,
                font=('Segoe UI', 12),
                fill="#cccccc"
            )

        # Update status
        self.update_status_labels()

    def update_status_labels(self):
        status_text = ""
        if self.board.is_checkmate():
            status_text = f"Checkmate! {'White' if not self.board.turn else 'Black'} wins!"
            bg_color = "#d64045"  # Red for checkmate
        elif self.board.is_stalemate():
            status_text = "Stalemate! Game is drawn."
            bg_color = "#777777"  # Gray for draw
        elif self.board.is_check():
            status_text = f"Check! {'White' if self.board.turn else 'Black'} to move."
            bg_color = "#e69a00"  # Orange for check
        else:
            status_text = f"{'White' if self.board.turn else 'Black'} to move"
            bg_color = "#1f538d" if self.board.turn else "#333333"  # Blue for white, dark for black

        self.turn_label.configure(text=status_text)
        self.turn_frame.configure(fg_color=bg_color)

    def on_engine_change(self, engine_name):
        self.engine_path = self.engines[engine_name]
        self.analysis_text.delete("1.0", "end")
        self.analysis_text.insert("1.0", f"Engine changed to: {engine_name}\n")
        self.analyze_position()

    def analyze_position(self):
        try:
            with chess.engine.SimpleEngine.popen_uci(self.engine_path) as engine:
                info = engine.analyse(self.board, chess.engine.Limit(time=self.THINK_TIME))
                self.display_analysis(info)
                self.update_evaluation_bar(info['score'].relative)
        except Exception as e:
            self.analysis_text.delete("1.0", "end")
            self.analysis_text.insert("1.0", f"Error analyzing position: {str(e)}")

    def display_analysis(self, info):
        self.analysis_text.delete("1.0", "end")
        analysis_lines = [
            f"{self.engine_var.get()} Analysis:",
            f"Evaluation: {self.format_score(info['score'].relative)}",
            f"Best line: {self.format_pv(info['pv'])}"
        ]
        self.analysis_text.insert("1.0", "\n".join(analysis_lines))

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
        self.evaluation_bar.delete("all")  # Clear previous drawings
        bar_width = self.evaluation_bar.winfo_width()
        bar_height = self.evaluation_bar.winfo_height()

        TEXT_PADDING = 20
        FONT_SIZE = 12

        # Calculate evaluation value (0 to 1)
        if score.is_mate():
            eval_value = 1.0 if score.mate() > 0 else 0.0
        else:
            eval_value = 1 / (1 + 10 ** (-score.score() / 400))

        # Calculate divider position
        divider_x = int(eval_value * bar_width)

        # Draw white and black sections
        self.evaluation_bar.create_rectangle(
            0, 0,
            divider_x, bar_height,
            fill="#ffffff",
            outline=""
        )
        self.evaluation_bar.create_rectangle(
            divider_x, 0,
            bar_width, bar_height,
            fill="#000000",
            outline=""
        )

        # Format score text
        if score.is_mate():
            text = f"M{abs(score.mate())}"
        else:
            eval_score = score.score() / 100
            text = f"{eval_score:+.2f}"

        # Position and style text based on winning side
        text_y = bar_height // 2
        if eval_value > 0.5:  # White advantage
            text_x = TEXT_PADDING
            text_color = "#000000"
            text_anchor = "w"
        else:  # Black advantage
            text_x = bar_width - TEXT_PADDING
            text_color = "#ffffff"
            text_anchor = "e"

        # Draw score text
        self.evaluation_bar.create_text(
            text_x, text_y,
            text=text,
            fill=text_color,
            font=("Segoe UI", FONT_SIZE, "bold"),
            anchor=text_anchor
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
        self.pgn_tree.delete("1.0", "end")
        pgn_str = self.get_pgn()

        # Format the moves nicely
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
        return self.game.accept(exporter)

    def on_pgn_select(self, event):
        # Get the line clicked on
        index = self.pgn_tree.index("@%d,%d" % (event.x, event.y))
        line = int(float(index)) - 1

        if 0 <= line < len(re.findall(r'\d+\.', self.get_pgn())):
            move_num = line + 1
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
