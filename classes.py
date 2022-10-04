

from decimal import DivisionByZero
import math


class Board():

# 
# ---FUNCTIONS---
# Function that returns all available pieces
# Function to get all available moves for a selected field
# Function to check the board for check and checkmate
# Function to load game using FEN notaion -- https://www.chess.com/terms/fen-chess -- ALL PIECES OF FEN NOT ONLY BOARD
# 
# 
# ---MISC---
# 
# 

    turn = 1
    whites = []
    blacks = []
    castle_white = True
    castle_black = True

    def __init__(self, fen):
        self.board_history = []
        self.load_fen_board(fen)
    

    def select_piece(self, pos):
        file = ord(pos[0]) - 97
        rank = 8 - int(pos[1])
        return (rank * 8) + file


    def int_to_pos(self, num):
        try:
            rank = 8 - math.floor(num / 8)
            file = chr(97 + (num % 8))
            return f"{file}{rank}"
        except DivisionByZero:
            return "a8"


    def get_all_piece_moves(self, pos):

        # Initializes a list for all available moves
        available_moves = []

        # Select numeric value for piece position
        piece_pos = self.select_piece(pos)

        # Select piece from numeric position
        piece = self.board[piece_pos]
        
        # Initialize a blank board
        board = [None for _ in range(64)]

        # Makes sure it's parsed by value and not reference
        pattern = piece.pattern.copy()

        # Checks if it's a pawn and if it has moved, if so gives it its start moves
        if isinstance(piece, Pawn) and not piece.haveMoved:
            pattern += piece.init_pattern

        # Iterate through every direction in patterns
        for dir in pattern:

            # Iterate through every move in direction
            for idx, move in enumerate(dir):
            
                num = -1

                # Calculates the new numeric position value
                total = piece_pos + move

                # Checks if new valuse is out of bounds in top or bottom
                if total < 0 or total > 63:
                    break

                # If piece is a Knight, make special check for out of bounds on sides
                if piece.symbol == "N" and abs(piece_pos % 8 - total % 8) > 2:
                    continue
                
                # Breaks if direction hits another piece, and marks enemy piece as 'X'
                if self.board[total] != None:
                    if self.board[total].color != piece.color:
                        board[total] = "X"
                    break

                
                # Makes sure offset num is not making it to be Out of Bounds
                if idx == 0:
                    num = 0

                # Checks if move is exceeding the side border, and breaks if so
                if ((total % 8 == 7 and (dir[idx+num]+piece_pos) % 8 == 0) or (total % 8 == 0 and (dir[idx+num]+piece_pos) % 8 == 7)) and piece.symbol != "N":
                    break
                    
                # Sets a '#' for every available move
                board[total] = "#"
                available_moves.append(total)
    
        # Sets selected piece into its position on the board
        board[piece_pos] = piece
        

        # Display all the current available moves
        self.display(board)

        return available_moves


    def move_piece(self, from_pos, to_pos):
        
        piece_pos = self.select_piece(from_pos)
        piece = self.board[piece_pos]

        target_pos = self.select_piece(to_pos)
        target = self.board[target_pos]

        self.board[piece_pos] = None

        if target is not None:
            print(f"{piece} killed {target} - {from_pos}-{to_pos}")

    
    def load_fen_board(self, fen_string: str):
        
        # Splits fen string into its different pieces
        fen_pieces = fen_string.split(" ")

        # Initiates a list for the whole board, and both black and white pieces
        board  = []
        blacks = []
        whites = []

        # Splits fen notation of the board into 8 ranks
        split_fen = fen_pieces[0].split("/")

        # Iterate through every rank
        for rank in split_fen:

            # Iterate thorugh every entry in rank
            for entry in rank:

                # Try to convert entry to int
                try: 
                    
                    # If entry is an int, fill board with n None
                    filler_cells = int(entry)
                    for _ in range(filler_cells):
                        board.append(None)
                
                # If entry is a char
                except:

                    # Create corresponding piece
                    match entry.lower():
                        case "k":
                            piece = King(entry)
                        case "q":
                            piece = Queen(entry)
                        case "r":
                            piece = Rook(entry)
                        case "b":
                            piece = Bishop(entry)
                        case "n":
                            piece = Knight(entry)
                        case "p":
                            piece = Pawn(entry)
                    
                    # Append the piece to its position on the board
                    board.append(piece)

                    # Checks the color of the piece by char-case, appends to correct list
                    if entry.islower():
                        blacks.append(piece)
                    else:
                        whites.append(piece)
        
        # If FEN notation is not correct, use default game
        if len(board) != 64:
            print("Invalid FEN notation - returns to default setting")
            return self.load_fen_board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
        

        self.board = board 
        self.blacks = blacks
        self.whites = whites

    def display(self, board = None):

        if board is None:
            board = self.board

        # Print top row of characters A-H underlined
        print(u"  \033[4m A B C D E F G H \033[0m")

        # Prints out every rank with rank number on both sides
        # pieces are represented as corresponding char and empty spaces as dots
        for i in range(8):
            rank = str([f"{piece}" if piece is not None else "." for piece in board[i * 8:i * 8 + 8]]).replace("'","").replace(",","")[1:-1]
            print(f'{8-i}| {rank} |{8-i}')

        # Prints out bottom row of characters A-H overlined
        print(u"  \u203EA\u0305\u203EB\u0305\u203EC\u0305\u203ED\u0305\u203EE\u0305\u203EF\u0305\u203EG\u0305\u203EH\u0305\u203E")


def max_move(num):
    return [num*(n+1) for n in range(7)]

class _Piece:
    symbol = None
    pattern = None
    haveMoved = False
    Color = None

    def __init__(self, symbol) -> None:
        self.symbol = symbol
        self.color = "white" if symbol.isupper() else "black"
        if symbol.lower() == "p":
            self.pattern = self.pattern[symbol]
            self.init_pattern = self.init_pattern[symbol]
            self.attack_pattern = self.attack_pattern[symbol]

    def __str__(self) -> str:
        return self.symbol


class King(_Piece):
    symbol = "K"
    pattern = [
        [-8], # Top
        [-7], # Top Right
        [-1], # Right
        [1],  # Down Right
        [7],  # Down 
        [8],  # Down Left
        [9],  # Left
        [-9], # Top Left
    ]


class Queen(_Piece):
    symbol = "Q"
    pattern = [
        max_move(-8), # Top
        max_move(-7), # Top Right
        max_move(-1), # Right
        max_move(1),  # Down Right
        max_move(7),  # Down
        max_move(8),  # Down Left
        max_move(9),  # Left
        max_move(-9)  # Top Left
    ]


class Bishop(_Piece):
    symbol = "B"
    pattern = [
        max_move(-9), # Top Left
        max_move(-7), # Top Right
        max_move(7),  # Down Left
        max_move(9)   # Down Right
    ]


class Knight(_Piece):
    symbol = "N"
    pattern = [
        [-17, -15], # Top
        [-6 , 10],  # Right
        [15, 17],   # Down
        [-10, 6],   # Left
    ]


class Rook(_Piece):
    symbol = "R"
    pattern = [
        max_move(-8), # Top
        max_move(1),  # Right
        max_move(8),  # Down
        max_move(-1), # Left
    ]


class Pawn(_Piece):
    symbol = "P"
    pattern = {
        "P": [[-8]],
        "p": [[8]]
    }

    init_pattern = {
        "P": [[-16]],
        "p": [[16]]
    }

    attack_pattern = {
        "P": [[-7, -9]],
        "p": [[7, 9]]
    }

