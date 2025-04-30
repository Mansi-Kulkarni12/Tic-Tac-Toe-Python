"""A modern Tic-Tac-Toe game using Python and Tkinter with enhanced UI and game feedback."""

import tkinter as tk
from itertools import cycle
from tkinter import font
from typing import NamedTuple

# === DATA STRUCTURES ===

class Player(NamedTuple):
    label: str
    color: str

class Move(NamedTuple):
    row: int
    col: int
    label: str = ""

# === GAME SETTINGS ===

BOARD_SIZE = 3
DEFAULT_PLAYERS = (
    Player(label="X", color="blue"),       # Player 1 color
    Player(label="O", color="green"),      # Player 2 color
)

# === GAME LOGIC ===

class TicTacToeGame:
    def __init__(self, players=DEFAULT_PLAYERS, board_size=BOARD_SIZE):
        self._players = cycle(players)
        self.board_size = board_size
        self.current_player = next(self._players)
        self.winner_combo = []
        self._current_moves = []
        self._has_winner = False
        self._winning_combos = []
        self.scores = {p.label: 0 for p in players}  # Score tracking
        self._setup_board()

    def _setup_board(self):
        self._current_moves = [
            [Move(row, col) for col in range(self.board_size)]
            for row in range(self.board_size)
        ]
        self._winning_combos = self._get_winning_combos()

    def _get_winning_combos(self):
        rows = [[(m.row, m.col) for m in row] for row in self._current_moves]
        cols = [list(col) for col in zip(*rows)]
        diag1 = [rows[i][i] for i in range(self.board_size)]
        diag2 = [rows[i][self.board_size - 1 - i] for i in range(self.board_size)]
        return rows + cols + [diag1, diag2]

    def toggle_player(self):
        self.current_player = next(self._players)

    def is_valid_move(self, move):
        return not self._has_winner and self._current_moves[move.row][move.col].label == ""

    def process_move(self, move):
        self._current_moves[move.row][move.col] = move
        for combo in self._winning_combos:
            values = {self._current_moves[r][c].label for r, c in combo}
            if len(values) == 1 and "" not in values:
                self._has_winner = True
                self.winner_combo = combo
                self.scores[move.label] += 1  # Update score
                break

    def has_winner(self):
        return self._has_winner

    def is_tied(self):
        return not self._has_winner and all(move.label for row in self._current_moves for move in row)

    def reset_game(self):
        for r in range(self.board_size):
            for c in range(self.board_size):
                self._current_moves[r][c] = Move(r, c)
        self._has_winner = False
        self.winner_combo = []

# === GUI LOGIC ===

class TicTacToeBoard(tk.Tk):
    def __init__(self, game: TicTacToeGame):
        super().__init__()
        self.title("Tic Tac Toe - Python Edition")
        self.configure(bg="white")
        self._cells = {}
        self._game = game

        self._create_menu()
        self._create_score_display()
        self._create_board_display()
        self._create_board_grid()

    def _create_menu(self):
        menu_bar = tk.Menu(master=self)
        self.config(menu=menu_bar)
        file_menu = tk.Menu(master=menu_bar, tearoff=0)
        file_menu.add_command(label="New Game", command=self.reset_board)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menu_bar.add_cascade(label="Menu", menu=file_menu)

    def _create_score_display(self):
        score_frame = tk.Frame(master=self, bg="white")
        score_frame.pack(fill=tk.X)
        self.score_label = tk.Label(
            master=score_frame,
            text=self._format_scores(),
            font=font.Font(size=14, weight="bold"),
            fg="dark gray",
            bg="white"
        )
        self.score_label.pack(pady=(5, 0))

    def _create_board_display(self):
        display_frame = tk.Frame(master=self, bg="white")
        display_frame.pack()
        self.display = tk.Label(
            master=display_frame,
            text="Let's Play!",
            font=font.Font(size=24, weight="bold"),
            fg="black",
            bg="white"
        )
        self.display.pack(pady=(0, 10))

    def _create_board_grid(self):
        grid_frame = tk.Frame(master=self)
        grid_frame.pack()
        for row in range(self._game.board_size):
            for col in range(self._game.board_size):
                button = tk.Button(
                    master=grid_frame,
                    text="",
                    font=font.Font(size=36, weight="bold"),
                    fg="black",
                    width=4,
                    height=2,
                    bg="white",
                    activebackground="light blue"
                )
                self._cells[button] = (row, col)
                button.bind("<Button-1>", self.play)
                button.grid(row=row, column=col, padx=5, pady=5)

    def play(self, event):
        clicked = event.widget
        row, col = self._cells[clicked]
        move = Move(row, col, self._game.current_player.label)
        if self._game.is_valid_move(move):
            self._update_button(clicked)
            self._game.process_move(move)
            if self._game.has_winner():
                self._highlight_cells()
                msg = f'{self._game.current_player.label} wins!'
                self._update_display(msg, self._game.current_player.color)
            elif self._game.is_tied():
                self._update_display("It's a tie!", "gray")
            else:
                self._game.toggle_player()
                msg = f"{self._game.current_player.label}'s turn"
                self._update_display(msg)
            self._update_scores()

    def _update_button(self, button):
        button.config(text=self._game.current_player.label, fg=self._game.current_player.color)

    def _update_display(self, msg, color="black"):
        self.display.config(text=msg, fg=color)

    def _highlight_cells(self):
        for button, (r, c) in self._cells.items():
            if (r, c) in self._game.winner_combo:
                button.config(bg="light coral")  # Highlight winning cells

    def _update_scores(self):
        self.score_label.config(text=self._format_scores())

    def _format_scores(self):
        return "   ".join([f"{p}: {s}" for p, s in self._game.scores.items()])

    def reset_board(self):
        self._game.reset_game()
        self._update_display("Let's Play!", "black")
        for button in self._cells:
            button.config(text="", fg="black", bg="white")
        self._update_scores()

# === RUNNING THE APP ===

def main():
    game = TicTacToeGame()
    board = TicTacToeBoard(game)
    board.mainloop()

if __name__ == "__main__":
    main()
