import tkinter as tk
import chess
from Code.analysis import display_chess_board

def main_menu():
    def start_engine_analysis():
        root.destroy()
        starting_position = chess.STARTING_FEN
        display_chess_board(starting_position)

    root = tk.Tk()
    root.title("Chess Toolkit Main Menu")
    root.geometry("400x300")
    root.configure(bg="#2d2d2d")

    title_label = tk.Label(root, text="Chess Toolkit", font=("Segoe UI", 24, "bold"), bg="#2d2d2d", fg="white")
    title_label.pack(pady=50)

    engine_analysis_button = tk.Button(
        root, text="Engine Analysis", font=("Segoe UI", 16), bg="#4a9bff", fg="white", command=start_engine_analysis
    )
    engine_analysis_button.pack(pady=20)

    root.mainloop()

main_menu()
