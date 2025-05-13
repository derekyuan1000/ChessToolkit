import os
import time
import chess
import chess.engine
import chess.pgn
import customtkinter as ctk
from datetime import datetime
import threading
import queue


class BattleArena:
    def __init__(self, root):
        self.root = root
        self.engines = {
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

        # Match settings
        self.num_games = 10
        self.time_per_move = 1.0  # seconds
        self.current_game_num = 0
        self.score = {"engine1": 0, "engine2": 0, "draws": 0}

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
            width=200
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
            width=200
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

        back_button = ctk.CTkButton(
            self.main_container,
            text="Back",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            height=40,
            width=150,
            corner_radius=10,
            command=self.confirm_back
        )
        back_button.pack(side="bottom", pady=10)

        self.start_display_updates()

    def confirm_back(self):
        confirm_window = ctk.CTkToplevel(self.root)
        confirm_window.title("Confirm")
        confirm_window.geometry("300x150")

        label = ctk.CTkLabel(confirm_window, text="Are you sure you want to go back?", font=("Segoe UI", 14))
        label.pack(pady=20)

        def go_back():
            confirm_window.destroy()
            self.root.destroy()
            from Code.main_menu import main_menu
            main_menu()

        yes_button = ctk.CTkButton(confirm_window, text="Yes", command=go_back)
        yes_button.pack(side="left", padx=20, pady=10)

        no_button = ctk.CTkButton(confirm_window, text="No", command=confirm_window.destroy)
        no_button.pack(side="right", padx=20, pady=10)

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
            # Format the moves in a readable way
            moves = []
            board = chess.Board()
            i = 0

            for move in self.current_game.mainline_moves():
                if i % 2 == 0:
                    move_num = (i // 2) + 1
                    moves.append(f"{move_num}. {board.san(move)}")
                else:
                    moves[-1] += f" {board.san(move)}"
                board.push(move)
                i += 1

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

                # Light or dark square
                color = "#e9edcc" if (row + col) % 2 == 0 else "#779556"

                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color,
                    outline=""
                )

                # Draw piece if present
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

    def get_piece_symbol(self, piece):
        symbols = {
            'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
            'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'
        }
        return symbols.get(piece.symbol(), '')

    def update_board(self):
        self.draw_board()
        self.update_move_history()

    def run_match(self):
        engine1_name = self.engine1_var.get()
        engine2_name = self.engine2_var.get()
        engine1_path = self.engines[engine1_name]
        engine2_path = self.engines[engine2_name]

        try:
            for game_num in range(1, self.num_games + 1):
                if not self.is_match_running:
                    break

                self.current_game_num = game_num
                self.board = chess.Board()
                self.current_game = chess.pgn.Game()

                # Set up game headers
                self.current_game.headers["Event"] = "Engine Battle"
                self.current_game.headers["Date"] = datetime.now().strftime("%Y.%m.%d")
                self.current_game.headers["White"] = engine1_name if game_num % 2 == 1 else engine2_name
                self.current_game.headers["Black"] = engine2_name if game_num % 2 == 1 else engine1_name
                self.current_game.headers["Round"] = str(game_num)

                engine1 = chess.engine.SimpleEngine.popen_uci(
                    engine1_path if game_num % 2 == 1 else engine2_path
                )
                engine2 = chess.engine.SimpleEngine.popen_uci(
                    engine2_path if game_num % 2 == 1 else engine1_path
                )

                try:
                    node = self.current_game

                    # Initial board update
                    self.move_queue.put("board")

                    while not self.board.is_game_over() and self.is_match_running:
                        engine = engine1 if self.board.turn == chess.WHITE else engine2
                        result = engine.play(
                            self.board,
                            chess.engine.Limit(time=self.time_per_move)
                        )
                        self.board.push(result.move)
                        node = node.add_variation(result.move)
                        self.move_queue.put("board")

                        # Small delay to allow GUI updates
                        time.sleep(0.1)

                finally:
                    engine1.quit()
                    engine2.quit()

                # Update score after game ends
                if self.board.is_checkmate():
                    winner = "engine1" if (self.board.turn == chess.BLACK) == (game_num % 2 == 1) else "engine2"
                    self.score[winner] += 1
                else:
                    self.score["draws"] += 1

                self.move_queue.put("board")  # Final position update
                self.update_score_display()

        except Exception as e:
            self.update_status(f"Error: {str(e)}")
        finally:
            self.is_match_running = False
            self.stop_button.configure(state="disabled")
            self.start_button.configure(state="normal")
            self.update_status("Match completed.")

    def start_match(self):
        if self.is_match_running:
            return

        self.is_match_running = True
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.update_status("Match in progress...")

        self.start_display_updates()  # Ensure display updates are running
        self.match_thread = threading.Thread(target=self.run_match)
        self.match_thread.start()

    def stop_match(self):
        self.is_match_running = False
        self.stop_button.configure(state="disabled")
        self.start_button.configure(state="normal")
        self.update_status("Match stopped.")

    def return_to_main_menu(self):
        self.is_match_running = False
        self.root.destroy()


def start_battle_arena(fullscreen=False):  # Add fullscreen parameter
    root = ctk.CTk()
    root.title("Chess Engine Battle Arena")
    root.geometry("1200x900")
    if fullscreen:
        root.attributes("-fullscreen", True)  # Set fullscreen if requested

    arena = BattleArena(root)
    root.mainloop()


if __name__ == "__main__":
    start_battle_arena()

