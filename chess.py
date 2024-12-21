import os

class ChessGame:
    def __init__(self):
        # Initialize the board with pieces
        self.board = [
            ['♜', '♞', '♝', '♛', '♚', '♝', '♞', '♜'],
            ['♟', '♟', '♟', '♟', '♟', '♟', '♟', '♟'],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            ['♙', '♙', '♙', '♙', '♙', '♙', '♙', '♙'],
            ['♖', '♘', '♗', '♕', '♔', '♗', '♘', '♖']
        ]
        self.current_player = 'white'
        self.white_pieces = {'♔', '♕', '♖', '♗', '♘', '♙'}
        self.black_pieces = {'♚', '♛', '♜', '♝', '♞', '♟'}

    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('clear' if os.name == 'posix' else 'cls')

    def display_board(self):
        """Display the chess board with coordinates."""
        self.clear_screen()
        print("\n  a b c d e f g h")
        print("  ---------------")
        for i in range(8):
            print(f"{8-i}|", end=" ")
            for j in range(8):
                print(self.board[i][j], end=" ")
            print(f"|{8-i}")
        print("  ---------------")
        print("  a b c d e f g h\n")
        print(f"{self.current_player.capitalize()}'s turn")

    def is_valid_position(self, pos):
        """Check if the given position is valid chess notation."""
        if len(pos) != 2:
            return False
        col, row = pos[0], pos[1]
        return (col in 'abcdefgh' and row in '12345678')

    def convert_position(self, pos):
        """Convert chess notation to board indices."""
        col = ord(pos[0]) - ord('a')
        row = 8 - int(pos[1])
        return row, col

    def is_valid_piece(self, row, col):
        """Check if the selected piece belongs to the current player."""
        piece = self.board[row][col]
        if self.current_player == 'white':
            return piece in self.white_pieces
        return piece in self.black_pieces

    def make_move(self, from_pos, to_pos):
        """Move a piece from one position to another."""
        from_row, from_col = self.convert_position(from_pos)
        to_row, to_col = self.convert_position(to_pos)

        # Basic movement validation (simplified)
        if abs(from_row - to_row) <= 1 and abs(from_col - to_col) <= 1:
            # Move the piece
            self.board[to_row][to_col] = self.board[from_row][from_col]
            self.board[from_row][from_col] = ' '
            return True
        return False

    def play(self):
        """Main game loop."""
        while True:
            self.display_board()
            
            # Get the piece to move
            while True:
                from_pos = input("Select piece to move (e.g. 'e2') or 'q' to quit: ").lower()
                if from_pos == 'q':
                    return
                if not self.is_valid_position(from_pos):
                    print("Invalid position! Use letters a-h and numbers 1-8.")
                    continue
                row, col = self.convert_position(from_pos)
                if not self.is_valid_piece(row, col):
                    print("Invalid piece! Select your own piece.")
                    continue
                break

            # Get the destination
            while True:
                to_pos = input("Enter destination (e.g. 'e4'): ").lower()
                if not self.is_valid_position(to_pos):
                    print("Invalid position! Use letters a-h and numbers 1-8.")
                    continue
                break

            # Try to make the move
            if self.make_move(from_pos, to_pos):
                # Switch players
                self.current_player = 'black' if self.current_player == 'white' else 'white'
            else:
                input("Invalid move! Press Enter to try again...")

if __name__ == "__main__":
    game = ChessGame()
    game.play()
