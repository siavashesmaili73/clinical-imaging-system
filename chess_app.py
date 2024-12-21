import tkinter as tk
from tkinter import messagebox

class ChessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Game")
        
        # Game state
        self.current_player = 'white'
        self.selected_piece = None
        self.board = self.create_initial_board()
        
        # Create the board GUI
        self.squares = {}
        self.create_board()
        
        # Status label
        self.status = tk.Label(root, text="White's turn", font=('Arial', 14))
        self.status.pack(pady=10)

    def create_initial_board(self):
        board = {}
        # Set up black pieces
        board['a8'] = ('black', '♜')
        board['b8'] = ('black', '♞')
        board['c8'] = ('black', '♝')
        board['d8'] = ('black', '♛')
        board['e8'] = ('black', '♚')
        board['f8'] = ('black', '♝')
        board['g8'] = ('black', '♞')
        board['h8'] = ('black', '♜')
        
        # Set up black pawns
        for col in 'abcdefgh':
            board[f'{col}7'] = ('black', '♟')
            
        # Set up white pawns
        for col in 'abcdefgh':
            board[f'{col}2'] = ('white', '♙')
            
        # Set up white pieces
        board['a1'] = ('white', '♖')
        board['b1'] = ('white', '♘')
        board['c1'] = ('white', '♗')
        board['d1'] = ('white', '♕')
        board['e1'] = ('white', '♔')
        board['f1'] = ('white', '♗')
        board['g1'] = ('white', '♘')
        board['h1'] = ('white', '♖')
        
        return board

    def create_board(self):
        board_frame = tk.Frame(self.root)
        board_frame.pack(padx=20, pady=20)
        
        # Create column labels (a-h)
        for col in range(8):
            label = tk.Label(board_frame, text=chr(97 + col), font=('Arial', 12))
            label.grid(row=8, column=col)
            
        # Create row labels (1-8)
        for row in range(8):
            label = tk.Label(board_frame, text=str(8 - row), font=('Arial', 12))
            label.grid(row=row, column=8)
        
        # Create the chess board squares
        for row in range(8):
            for col in range(8):
                color = '#F0D9B5' if (row + col) % 2 == 0 else '#B58863'
                square = tk.Label(
                    board_frame,
                    width=4,
                    height=2,
                    bg=color,
                    font=('Arial', 24)
                )
                square.grid(row=row, column=col)
                
                # Bind click events
                square.bind('<Button-1>', lambda e, pos=f"{chr(97+col)}{8-row}": self.on_square_click(e, pos))
                
                # Store reference to square
                self.squares[f"{chr(97+col)}{8-row}"] = square
        
        # Place initial pieces
        self.update_board_display()

    def update_board_display(self):
        for pos, square in self.squares.items():
            if pos in self.board:
                color, piece = self.board[pos]
                square.config(text=piece, fg='black')
            else:
                square.config(text='')

    def on_square_click(self, event, pos):
        square = event.widget
        
        # If no piece is selected and clicked square has a piece of current player
        if self.selected_piece is None:
            if pos in self.board and self.board[pos][0] == self.current_player:
                self.selected_piece = pos
                square.config(bg='#7B61FF')  # Highlight selected square
            return
            
        # If a piece is already selected
        if self.selected_piece:
            old_square = self.squares[self.selected_piece]
            old_color = '#F0D9B5' if (int(self.selected_piece[1])+ord(self.selected_piece[0]))%2 == 0 else '#B58863'
            old_square.config(bg=old_color)
            
            # If clicking the same square, deselect it
            if pos == self.selected_piece:
                self.selected_piece = None
                return
                
            # Try to make the move
            if self.is_valid_move(self.selected_piece, pos):
                # Move the piece
                self.board[pos] = self.board[self.selected_piece]
                del self.board[self.selected_piece]
                
                # Update display
                self.update_board_display()
                
                # Switch players
                self.current_player = 'black' if self.current_player == 'white' else 'white'
                self.status.config(text=f"{self.current_player.capitalize()}'s turn")
            
            self.selected_piece = None

    def is_valid_move(self, from_pos, to_pos):
        # Basic validation - check if target square is empty or has opponent's piece
        if to_pos in self.board and self.board[to_pos][0] == self.current_player:
            return False
            
        # Convert chess notation to grid coordinates
        from_col, from_row = ord(from_pos[0]) - 97, int(from_pos[1]) - 1
        to_col, to_row = ord(to_pos[0]) - 97, int(to_pos[1]) - 1
        
        # Simplified movement - allow one square in any direction
        if abs(from_row - to_row) <= 1 and abs(from_col - to_col) <= 1:
            return True
            
        return False

if __name__ == "__main__":
    root = tk.Tk()
    app = ChessApp(root)
    root.mainloop()
