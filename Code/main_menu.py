import chess
import customtkinter as ctk

from Code.analysis import display_chess_board


def main_menu():
    def start_engine_analysis():
        root.destroy()
        starting_position = chess.STARTING_FEN
        display_chess_board(starting_position)

    # Set appearance mode and default color theme
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Create the root window
    root = ctk.CTk()
    root.title("Chess Toolkit")
    root.geometry("800x600")

    # Create a frame for the content
    content_frame = ctk.CTkFrame(root, corner_radius=15)
    content_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # App logo/title
    title_label = ctk.CTkLabel(
        content_frame,
        text="Chess Toolkit",
        font=ctk.CTkFont(family="Segoe UI", size=36, weight="bold")
    )
    title_label.pack(pady=(50, 30))

    # Engine analysis button
    engine_analysis_button = ctk.CTkButton(
        content_frame,
        text="Engine Analysis",
        font=ctk.CTkFont(family="Segoe UI", size=18),
        height=50,
        width=250,
        corner_radius=10,
        command=start_engine_analysis
    )
    engine_analysis_button.pack(pady=20)

    # Credits text
    credits_label = ctk.CTkLabel(
        content_frame,
        text="Chess Toolkit v1.0",
        font=ctk.CTkFont(family="Segoe UI", size=12),
        text_color="gray70"
    )
    credits_label.pack(side="bottom", pady=10)

    root.mainloop()


main_menu()
