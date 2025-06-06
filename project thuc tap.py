import tkinter as tk
from tkinter import messagebox
import random
import os

SCORE_FILE = "score.txt"

class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe - Nâng cấp toàn diện")

        self.mode = None
        self.player_symbol = "X"
        self.ai_symbol = "O"
        self.current_turn = "X"

        self.board = []
        self.buttons = []
        self.winning_cells = []

        self.label_turn = None
        self.label_score = None

        self.score = {"X": 0, "O": 0}
        self.load_score()

        self.setup_menu()

    def load_score(self):
        if os.path.exists(SCORE_FILE):
            with open(SCORE_FILE, "r") as f:
                try:
                    x, o = f.read().split(",")
                    self.score["X"] = int(x)
                    self.score["O"] = int(o)
                except:
                    pass

    def save_score(self):
        with open(SCORE_FILE, "w") as f:
            f.write(f"{self.score['X']},{self.score['O']}")

    def setup_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="🎮 Chọn chế độ chơi:", font=("Arial", 16)).pack(pady=10)
        tk.Button(self.root, text="👫 Người vs Người (PvP)", width=30, command=self.start_pvp, bg="#E0F7FA").pack(pady=5)
        tk.Button(self.root, text="🤖 Máy - Dễ", width=30, command=lambda: self.setup_ai_options("easy"), bg="#E8F5E9").pack(pady=5)
        tk.Button(self.root, text="🧠 Máy - Khó (AI)", width=30, command=lambda: self.setup_ai_options("hard"), bg="#FFF3E0").pack(pady=5)

    def setup_ai_options(self, difficulty):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.mode = "ai_" + difficulty
        tk.Label(self.root, text="🤔 Chọn ký hiệu của bạn:", font=("Arial", 16)).pack(pady=10)
        tk.Button(self.root, text="X (Bạn đi trước)", width=20, command=lambda: self.start_ai("X")).pack(pady=5)
        tk.Button(self.root, text="O (Máy đi trước)", width=20, command=lambda: self.start_ai("O")).pack(pady=5)

    def start_pvp(self):
        self.mode = "pvp"
        self.player_symbol = "X"
        self.ai_symbol = None
        self.current_turn = "X"
        self.create_board()

    def start_ai(self, player_choice):
        self.player_symbol = player_choice
        self.ai_symbol = "O" if player_choice == "X" else "X"
        self.current_turn = "X"
        self.create_board()
        if self.current_turn == self.ai_symbol:
            self.root.after(500, self.computer_move)

    def create_board(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        self.winning_cells = []

        self.label_turn = tk.Label(self.root, text=f"🔄 Lượt: {self.current_turn}", font=("Arial", 14))
        self.label_turn.grid(row=0, column=0, columnspan=3, pady=(5, 0))

        self.label_score = tk.Label(self.root, text=self.get_score_text(), font=("Arial", 12))
        self.label_score.grid(row=1, column=0, columnspan=3)

        reset_btn = tk.Button(self.root, text="🔁 Reset điểm", command=self.reset_score, bg="#FFCDD2")
        reset_btn.grid(row=2, column=0, columnspan=3, pady=5)

        for i in range(3):
            for j in range(3):
                btn = tk.Button(self.root, text="", font=('Arial', 40), width=5, height=2,
                                bg="#F5F5F5", command=lambda r=i, c=j: self.on_click(r, c))
                btn.grid(row=i+3, column=j, padx=3, pady=3)
                self.buttons[i][j] = btn

    def reset_score(self):
        self.score = {"X": 0, "O": 0}
        self.save_score()
        self.label_score.config(text=self.get_score_text())

    def on_click(self, row, col):
        if self.board[row][col] == "":
            self.board[row][col] = self.current_turn
            self.buttons[row][col].config(text=self.current_turn, state="disabled")

            if self.check_winner(self.current_turn):
                self.mark_winner()
                self.score[self.current_turn] += 1
                self.save_score()
                messagebox.showinfo("🎉 Chiến thắng", f"{self.current_turn} thắng!")
                self.ask_restart()
                return
            elif self.is_full():
                messagebox.showinfo("🤝 Hòa", "Không ai thắng cả.")
                self.ask_restart()
                return

            self.current_turn = "O" if self.current_turn == "X" else "X"
            self.label_turn.config(text=f"🔄 Lượt: {self.current_turn}")

            if self.mode.startswith("ai") and self.current_turn == self.ai_symbol:
                self.root.after(500, self.computer_move)

    def computer_move(self):
        if self.mode == "ai_easy":
            empty = [(i, j) for i in range(3) for j in range(3) if self.board[i][j] == ""]
            if empty:
                i, j = random.choice(empty)
                self.on_click(i, j)
        elif self.mode == "ai_hard":
            best_score = -float('inf')
            move = None
            for i in range(3):
                for j in range(3):
                    if self.board[i][j] == "":
                        self.board[i][j] = self.ai_symbol
                        score = self.minimax(self.board, 0, False)
                        self.board[i][j] = ""
                        if score > best_score:
                            best_score = score
                            move = (i, j)
            if move:
                self.on_click(*move)

    def minimax(self, board, depth, is_max):
        if self.check_winner_static(board, self.ai_symbol):
            return 1
        elif self.check_winner_static(board, self.player_symbol):
            return -1
        elif self.is_full_static(board):
            return 0

        if is_max:
            best = -float('inf')
            for i in range(3):
                for j in range(3):
                    if board[i][j] == "":
                        board[i][j] = self.ai_symbol
                        best = max(best, self.minimax(board, depth + 1, False))
                        board[i][j] = ""
            return best
        else:
            best = float('inf')
            for i in range(3):
                for j in range(3):
                    if board[i][j] == "":
                        board[i][j] = self.player_symbol
                        best = min(best, self.minimax(board, depth + 1, True))
                        board[i][j] = ""
            return best

    def check_winner(self, mark):
        # Rows, Columns, Diagonals
        for i in range(3):
            if all(self.board[i][j] == mark for j in range(3)):
                self.winning_cells = [(i, j) for j in range(3)]
                return True
            if all(self.board[j][i] == mark for j in range(3)):
                self.winning_cells = [(j, i) for j in range(3)]
                return True
        if all(self.board[i][i] == mark for i in range(3)):
            self.winning_cells = [(i, i) for i in range(3)]
            return True
        if all(self.board[i][2-i] == mark for i in range(3)):
            self.winning_cells = [(i, 2-i) for i in range(3)]
            return True
        return False

    def check_winner_static(self, board, mark):
        for i in range(3):
            if all(board[i][j] == mark for j in range(3)) or all(board[j][i] == mark for j in range(3)):
                return True
        if all(board[i][i] == mark for i in range(3)) or all(board[i][2-i] == mark for i in range(3)):
            return True
        return False

    def mark_winner(self):
        for r, c in self.winning_cells:
            self.buttons[r][c].config(bg="#A5D6A7")  # màu xanh lá nhạt

    def is_full(self):
        return all(self.board[i][j] != "" for i in range(3) for j in range(3))

    def is_full_static(self, board):
        return all(board[i][j] != "" for i in range(3) for j in range(3))

    def ask_restart(self):
        if messagebox.askyesno("Chơi tiếp?", "Bạn có muốn chơi ván khác?"):
            self.create_board()
        else:
            self.root.quit()

    def get_score_text(self):
        return f"📊 Tỉ số - X: {self.score['X']} | O: {self.score['O']}"

# Khởi chạy chương trình
if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToe(root)
    root.mainloop()
