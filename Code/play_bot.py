import chess
import chess.engine
import customtkinter as ctk
from utils import get_piece_symbol
from Code.analysis import display_chess_board  # Import the analysis function
import io
from tkinter import Listbox  # Add Listbox for move selection


def play_bot_game():
    """Start a game against a bot."""
    root = ctk.CTk()
    root.title("Play Against Bot")
    root.geometry("1000x800")

    board = chess.Board()
    engines = {
        "Stockfish": "../engines/Stockfish17.exe",
        "Komodo Dragon": "../engines/KomodoDragon3.3.exe",
        "Houdini": "../engines/Houdini.exe",
        "Obsidian": "../engines/Obsidian.exe",
    }
    engine_path = engines["Stockfish"]
    game_started = False
    selected_square = None
    hover_square = None

    def draw_board():
        canvas.delete("all")
        square_size = 80
        for row in range(8):
            for col in range(8):
                x1, y1 = col * square_size, row * square_size
                x2, y2 = x1 + square_size, y1 + square_size
                square = chess.square(col, 7 - row)

                # Determine square color
                color = "#e9edcc" if (row + col) % 2 == 0 else "#779556"
                if square == selected_square:
                    color = "#f7f769"  # Bright yellow for selected square
                elif square == hover_square:
                    color = "#baca44" if (row + col) % 2 == 0 else "#8fb344"  # Green for hover

                canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

                # Draw piece if present
                piece = board.piece_at(square)
                if piece:
                    piece_symbol = get_piece_symbol(piece)
                    text_color = "#ffffff" if piece.color == chess.WHITE else "#000000"
                    canvas.create_text(
                        x1 + square_size // 2,
                        y1 + square_size // 2,
                        text=piece_symbol,
                        font=("Segoe UI", int(square_size * 0.6), "bold"),
                        fill=text_color
                    )
        update_turn_indicator()

    def update_turn_indicator():
        if board.is_checkmate():
            turn_label.configure(text=f"Checkmate! {'White' if not board.turn else 'Black'} wins!")
            turn_frame.configure(fg_color="#d64045")  # Red for checkmate
        elif board.is_stalemate():
            turn_label.configure(text="Stalemate! Game is drawn.")
            turn_frame.configure(fg_color="#777777")  # Gray for stalemate
        elif board.is_check():
            turn_label.configure(text=f"Check! {'White' if board.turn else 'Black'} to move.")
            turn_frame.configure(fg_color="#e69a00")  # Orange for check
        else:
            turn_label.configure(text=f"{'White' if board.turn else 'Black'} to move")
            turn_frame.configure(fg_color="#1f538d" if board.turn else "#333333")  # Blue for white, dark for black

    def on_square_click(event):
        nonlocal selected_square
        if not game_started:
            update_status("Press 'Start Game' to begin.")
            return

        square_size = 80
        col, row = event.x // square_size, 7 - (event.y // square_size)
        square = chess.square(col, row)
        if selected_square is None:
            if board.piece_at(square) and board.piece_at(square).color == chess.WHITE:
                selected_square = square
        else:
            move = chess.Move(selected_square, square)
            if move in board.legal_moves:
                board.push(move)
                draw_board()
                update_pgn()
                selected_square = None
                root.after(500, bot_move)
            else:
                selected_square = None
        draw_board()

    def on_square_hover(event):
        nonlocal hover_square
        square_size = 80
        col, row = event.x // square_size, 7 - (event.y // square_size)
        square = chess.square(col, row)
        if hover_square != square:
            hover_square = square
            draw_board()

    def bot_move():
        with chess.engine.SimpleEngine.popen_uci(engine_path) as engine:
            result = engine.play(board, chess.engine.Limit(time=1.0))
            board.push(result.move)
            draw_board()
            update_pgn()

    def update_pgn():
        white_moves_listbox.delete(0, "end")
        black_moves_listbox.delete(0, "end")
        game = chess.pgn.Game()
        node = game
        board_copy = chess.Board()
        for i, move in enumerate(board.move_stack):
            node = node.add_variation(move)
            move_text = board_copy.san(move)
            if i % 2 == 0:
                white_moves_listbox.insert("end", f"{(i // 2) + 1}. {move_text}")
            else:
                black_moves_listbox.insert("end", move_text)
            board_copy.push(move)
        if white_moves_listbox.size() > 0 or black_moves_listbox.size() > 0:
            highlight_selected_move(len(board.move_stack) - 1)
        return str(game)

    def on_pgn_select(event):
        selected_index = (
            white_moves_listbox.curselection() or black_moves_listbox.curselection()
        )
        if selected_index:
            move_index = selected_index[0] * 2
            if event.widget == black_moves_listbox:
                move_index += 1
            go_to_move(move_index)

    def highlight_selected_move(move_index):
        white_moves_listbox.selection_clear(0, "end")
        black_moves_listbox.selection_clear(0, "end")
        if move_index % 2 == 0:
            white_moves_listbox.selection_set(move_index // 2)
        else:
            black_moves_listbox.selection_set(move_index // 2)

    def go_to_move(move_index):
        nonlocal board
        board = chess.Board()
        for i, move in enumerate(board.move_stack[:move_index + 1]):
            board.push(move)
        draw_board()
        highlight_selected_move(move_index)

    def start_game():
        nonlocal game_started
        game_started = True
        bot_menu.configure(state="disabled")
        start_button.configure(text="Resign", command=resign_game)
        analysis_button.pack_forget()  # Hide the analysis button during the game
        draw_board()

    def resign_game():
        nonlocal game_started
        game_started = False
        bot_menu.configure(state="normal")
        start_button.configure(text="Start Game", command=start_game)
        update_status("You resigned. Game over.")
        analysis_button.pack(pady=(10, 10))  # Show the analysis button after the game ends

    def reset_game():
        nonlocal game_started, board, selected_square, hover_square
        game_started = False
        board = chess.Board()
        selected_square = None
        hover_square = None
        bot_menu.configure(state="normal")
        start_button.configure(text="Start Game", command=start_game)
        analysis_button.pack_forget()  # Hide the analysis button during reset
        draw_board()
        update_pgn()

    def on_bot_selection(bot_name):
        nonlocal engine_path
        engine_path = engines[bot_name]
        bot_label.configure(text=f"Current Bot: {bot_name}")

    def update_status(message):
        status_label.configure(text=message)

    def go_to_analysis():
        """Open the analysis board with the current game's PGN."""
        pgn = update_pgn()  # Get the PGN of the current game
        try:
            import io
            pgn_io = io.StringIO(pgn)
            game = chess.pgn.read_game(pgn_io)  # Parse the PGN
            if game is None:
                raise ValueError("Invalid PGN format")
            root.destroy()  # Close the current window
            from Code.gui import ModernChessGUI
            root_analysis = ctk.CTk()
            root_analysis.title("Chess Analysis")
            gui = ModernChessGUI(root_analysis, position=chess.STARTING_FEN)
            gui.load_pgn(pgn)  # Load the PGN into the analysis board
            root_analysis.mainloop()
        except Exception as e:
            update_status(f"Error: {str(e)}")  # Display error message in the status label

    def confirm_back():
        confirm_window = ctk.CTkToplevel(root)
        confirm_window.title("Confirm")
        confirm_window.geometry("300x150")

        # Center the dialog over the main tab
        confirm_window.transient(root)
        confirm_window.grab_set()

        label = ctk.CTkLabel(confirm_window, text="Are you sure you want to go back?", font=("Segoe UI", 14))
        label.pack(pady=20)

        def go_back():
            confirm_window.destroy()
            root.destroy()
            from Code.main_menu import main_menu
            main_menu()

        yes_button = ctk.CTkButton(confirm_window, text="Yes", command=go_back)
        yes_button.pack(side="left", padx=20, pady=10)

        no_button = ctk.CTkButton(confirm_window, text="No", command=confirm_window.destroy)
        no_button.pack(side="right", padx=20, pady=10)

    # Main layout
    main_frame = ctk.CTkFrame(root)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Board section
    board_frame = ctk.CTkFrame(main_frame, width=640, height=640)
    board_frame.pack(side="left", padx=10, pady=10)
    canvas = ctk.CTkCanvas(board_frame, width=640, height=640, bg="#2b2b2b", highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    canvas.bind("<Button-1>", on_square_click)
    canvas.bind("<Motion>", on_square_hover)

    # Turn indicator
    turn_frame = ctk.CTkFrame(board_frame, height=40, fg_color="#1f538d")
    turn_frame.pack(fill="x", padx=10, pady=(0, 10))
    turn_label = ctk.CTkLabel(turn_frame, text="White to move", font=("Segoe UI", 16, "bold"))
    turn_label.pack(pady=10)

    # PGN and controls section
    side_frame = ctk.CTkFrame(main_frame, width=300)
    side_frame.pack(side="right", fill="y", padx=10, pady=10)

    bot_label = ctk.CTkLabel(side_frame, text="Current Bot: Stockfish", font=("Segoe UI", 16, "bold"))
    bot_label.pack(pady=(10, 20))

    bot_menu = ctk.CTkOptionMenu(
        side_frame,
        values=list(engines.keys()),
        command=on_bot_selection,
        width=200
    )
    bot_menu.set("Stockfish")
    bot_menu.pack(pady=(0, 20))

    start_button = ctk.CTkButton(side_frame, text="Start Game", command=start_game)
    start_button.pack(pady=(10, 10))

    reset_button = ctk.CTkButton(side_frame, text="Reset Game", command=reset_game)
    reset_button.pack(pady=(0, 20))

    analysis_button = ctk.CTkButton(
        side_frame,
        text="Go to Analysis",
        command=go_to_analysis,
        font=("Segoe UI", 16, "bold"),
        height=60,  # Increase button height
        width=250,  # Increase button width
        corner_radius=10  # Round the corners
    )
    analysis_button.pack(pady=(20, 20))  # Add more padding
    analysis_button.pack_forget()  # Hide the button initially

    status_label = ctk.CTkLabel(side_frame, text="", font=("Segoe UI", 14))
    status_label.pack(pady=(10, 10))

    pgn_label = ctk.CTkLabel(side_frame, text="PGN:", font=("Segoe UI", 16, "bold"))
    pgn_label.pack(anchor="w", padx=10, pady=(10, 5))

    history_frame = ctk.CTkFrame(side_frame, fg_color="#2b2b2b")  # Match usual background
    history_frame.pack(fill="x", padx=10, pady=(0, 10))
    
    # Container frame to force equal width
    move_container = ctk.CTkFrame(history_frame, fg_color="transparent")
    move_container.pack(fill="both", expand=True, padx=10, pady=10)
    move_container.grid_columnconfigure(0, weight=1, uniform="move_cols")
    move_container.grid_columnconfigure(1, weight=1, uniform="move_cols")

    white_moves_listbox = Listbox(
        move_container,
        font=("Segoe UI", 12),
        height=10,
        selectmode="single",
        exportselection=False,
        bg="#2b2b2b",
        fg="white"
    )
    white_moves_listbox.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

    black_moves_listbox = Listbox(
        move_container,
        font=("Segoe UI", 12),
        height=10,
        selectmode="single",
        exportselection=False,
        bg="#2b2b2b",
        fg="white"
    )
    black_moves_listbox.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

    white_moves_listbox.bind("<<ListboxSelect>>", on_pgn_select)
    black_moves_listbox.bind("<<ListboxSelect>>", on_pgn_select)

    back_button = ctk.CTkButton(
        main_frame,
        text="Back",
        command=confirm_back,
        corner_radius=10,
        font=("Segoe UI", 16, "bold"),
        height=40,
        width=150
    )
    back_button.pack(side="bottom", pady=10)

    draw_board()
    root.mainloop()

