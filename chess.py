import math
from decimal import DivisionByZero
from turtle import pos

from pieces import Bishop, King, Knight, Pawn, Queen, Rook


def at_border(total, pos, offset):
    return ((total % 8 == 7 and ((pos % 8 == 0 and math.floor(total / 8) != math.floor(pos / 8)) or offset + pos % 8 == 0)) or
            (total % 8 == 0 and ((pos % 8 == 7 and math.floor(total / 8) != math.floor(pos / 8)) or offset + pos % 8 == 7)))


class Board():

    #
    # ---FUNCTIONS---
    # Function that returns all available pieces
    # Function to check the board if player is checked
    # Function to load game using FEN notaion -- https://www.chess.com/terms/fen-chess -- ALL PIECES OF FEN NOT ONLY BOARD
    #
    #
    # ---MISC---
    #
    #

    # False = blacks turn
    # True  = whites turn
    turn = True

    whites = []
    blacks = []
    castle_white = True
    castle_black = True

    def __init__(self, fen: str = ""):
        self.board_history = []
        self.load_fen_board(fen)

    def select_piece(self, pos: str):

        # returns -1 if no position was parsed
        if pos is None:
            return -1

        # Calculate the numerical value for string pos
        file = ord(pos[0]) - 97
        rank = 8 - int(pos[1])

        return (rank * 8) + file

    def int_to_pos(self, num: int):

        # returns the string position of a numerical position
        try:
            rank = 8 - math.floor(num / 8)
            file = chr(97 + (num % 8))
            return f"{file}{rank}"
        except DivisionByZero:
            return "a8"

    def get_piece_moves(self, piece_pos: int, examine_board: list[int] = None):

        # Initializes a list for all available moves
        available_moves = []

        # Select piece from numeric position
        piece = self.board[piece_pos]
        # print(piece, piece_pos, self.board)

        copy_board = self.board.copy() if examine_board is None else examine_board

        # Initialize a blank board
        board = [None for _ in range(64)]

        # Makes sure it's parsed by value and not reference
        pattern = piece.pattern.copy()

        # Checks if piece is a pawn
        if isinstance(piece, Pawn):

            # Check if pawn is allowed to make double start
            if not piece.haveMoved:
                new_pattern = (pattern[0] + piece.init_pattern[0]).copy()
                pattern = [new_pattern]

            # Checks if Pawn can kill an opponant piece
            for move in piece.attack_pattern[0]:

                # Makes sure move is within the board
                if piece_pos + move < 0 or piece_pos + move > 63:
                    break

                # Checks if there is an piece on attack spot
                if self.board[piece_pos + move] != None and self.board[piece_pos + move].color != piece.color:
                    available_moves.append(piece_pos + move)

            # Checks if an opposing pawn is to the left of pawn, and if en passant is allowed
            if isinstance(self.board[piece_pos - 1], Pawn):
                if self.board[piece_pos - 1].en_passant:
                    available_moves.append(
                        piece_pos + piece.attack_pattern[0][0])

            # # Checks if an opposing pawn is to the right of pawn, and if en passant is allowed
            if isinstance(self.board[piece_pos + 1], Pawn):
                if self.board[piece_pos + 1].en_passant:
                    available_moves.append(
                        piece_pos + piece.attack_pattern[0][1])

        # Iterate through every direction in patterns
        for dir in pattern:

            # Iterate through every move in direction
            for idx, move in enumerate(dir):

                # Set idx offset to
                idx_offset = -1

                # Calculates the new numeric position value
                total = piece_pos + move

                # Checks if new valuse is out of bounds in top or bottom
                if total < 0 or total > 63:
                    break

                # If piece is a Knight, make special check for out of bounds on sides
                if isinstance(piece, Knight) and abs(piece_pos % 8 - total % 8) > 2:
                    continue

                # Breaks if direction hits another piece, and marks enemy piece as 'X'
                if copy_board[total] != None:
                    if copy_board[total].color != piece.color and not isinstance(piece, Pawn):
                        # board[total] = "X"
                        available_moves.append(total)
                    break

                # Makes sure offset num is not making it to be Out of Bounds
                if idx == 0:
                    idx_offset = 0

                # Checks if move is exceeding the side border, and breaks if so
                if at_border(total, piece_pos, dir[idx + idx_offset]) and not isinstance(piece, Knight):
                    break

                # Sets a '#' for every available move
                # board[total] = "#"
                available_moves.append(total)

        # Sets selected piece into its position on the board
        # board[piece_pos] = piece

        # Display all the current available moves
        # self.display(board)

        return available_moves

    def is_move_legal(self, from_pos: int, to_pos: int):

        # Determine whos king to look for and choose enemy piece set
        symbol = "K" if self.turn else "k"
        enemy_pieces = self.blacks if self.turn else self.whites

        # Create a copy of the board
        examine_board = self.board.copy()

        # Move piece to specified spot and leave origin as None
        examine_board[to_pos] = examine_board[from_pos]
        examine_board[from_pos] = None

        # Retrieve the position of the king
        king_pos = [idx for idx, piece in enumerate(
            examine_board) if piece is not None and piece.symbol == symbol]

        if len(king_pos) == 0:
            return False

        king_pos = king_pos[0]

        # Iterate through every enemy move and if an enemy piece can kill king return 'illegal'
        for spot in enemy_pieces:
            if king_pos in self.get_piece_moves(spot, examine_board):
                return False

        # If no move could kill the king, return 'legal'
        return True

    def get_all_legal_moves_for_pos(self, pos: int):

        # Initiate a list for all legal moves for piece
        legal_moves = []

        # Get all psuedo legal moves
        piece_moves = self.get_piece_moves(pos)

        # Iterate through every move and remove illegal mvoes
        for move in piece_moves:
            if self.is_move_legal(pos, move):
                legal_moves.append(move)

        return legal_moves

    def is_player_checkmate(self):

        # Select current player piece set
        player_pieces = self.whites if self.turn else self.blacks

        # Iterate through evert piece and see if they have any legal moves
        for piece in player_pieces:
            moves = self.get_all_legal_moves_for_pos(piece)

            # If a legal move was found, return 'not checkmate'
            if len(moves) > 0:
                return False

        # If there were found no legal moves in piece set reutrn 'checkmate'
        return True

    def make_move(self, from_pos: int, to_pos: int):

        en_passant_move = 0

        # check if the position which the piece is moving to, is already occupied
        if self.board[to_pos] is not None:
            message = f" and killed {self.board[to_pos]}"

        # Checks if attacking piece is a Pawn and is trying to do en passant
        elif isinstance(self.board[from_pos], Pawn):

            # Check if white performed en passant
            if isinstance(self.board[to_pos - 8], Pawn) and self.board[to_pos - 8].en_passant:
                message = f" and killed {self.board[to_pos - 8]}"
                en_passant_move = to_pos - 8

            # Check if black performed en passant
            elif isinstance(self.board[to_pos + 8], Pawn) and self.board[to_pos + 8].en_passant:
                message = f" and killed {self.board[to_pos + 8]}"
                en_passant_move = to_pos + 8

            else:
                # No added message if not piece was killed
                message = f""

        else:
            # No added message if not piece was killed
            message = ""

        # Print message for the move
        print(
            f"Moved {self.int_to_pos(from_pos)} to {self.int_to_pos(to_pos)}{message}")

        # Marks pawn as able to be killed with 'en passant'
        # Handles all special cases there is for a pawn
        if isinstance(self.board[from_pos], Pawn):
            piece = self.board[from_pos]

            # Makes sure piece moved two files and have not moved before
            if (to_pos - from_pos) in piece.init_pattern[0] and not piece.haveMoved:
                piece.en_passant = True

        # Makes sure player piece lists are up-to-date
        if self.turn:  # Whites turn
            player = self.whites
            opponent = self.blacks

        else:  # Blacks turn
            player = self.blacks
            opponent = self.whites

        # Updates players piece list
        player.remove(from_pos)
        player.append(to_pos)

        # Updates opponents piece list if a piece was lost
        if self.board[to_pos] is not None:
            opponent.remove(to_pos)

        # Updates opponents piece list if en passant was performed
        if en_passant_move != 0:
            opponent.remove(en_passant_move)

        # Makes sure piece is marked as moved
        self.board[from_pos].haveMoved = True

        # Move piece from 'from_pos' to 'to_pos' and leave 'from_pos' with None
        self.board[to_pos] = self.board[from_pos]
        self.board[from_pos] = None

        # Removes piece if piece was killed with en passant
        if en_passant_move != 0:
            self.board[en_passant_move] = None

    def end_turn(self):
        self.turn = not self.turn

        pieces = self.whites if self.turn else self.blacks

        for piece_pos in pieces:
            if isinstance(self.board[piece_pos], Pawn):
                self.board[piece_pos].en_passant = False

    def load_fen_board(self, fen_string: str):

        # Splits fen string into its different pieces
        fen_pieces = fen_string.split(" ")

        # Initiates a list for the whole board, and both black and white pieces
        board = []
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
                        blacks.append(len(board) - 1)
                    else:
                        whites.append(len(board) - 1)

        # If FEN notation is not correct, use default game
        if len(board) != 64:
            print("Invalid FEN notation - returns to default setting")
            return self.load_fen_board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")

        self.board = board
        self.blacks = blacks
        self.whites = whites

    def display(self, board=None):

        if board is None:
            board = self.board

        # Print top row of characters A-H underlined
        print(u"  \033[4m A B C D E F G H \033[0m")

        # Prints out every rank with rank number on both sides
        # pieces are represented as corresponding char and empty spaces as dots
        for i in range(8):
            rank = str([f"{piece}" if piece is not None else "." for piece in board[i * 8:i * 8 + 8]]
                       ).replace("'", "").replace(",", "")[1:-1]
            print(f'{8-i}| {rank} |{8-i}')

        # Prints out bottom row of characters A-H overlined
        print(u"  \u203EA\u0305\u203EB\u0305\u203EC\u0305\u203ED\u0305\u203EE\u0305\u203EF\u0305\u203EG\u0305\u203EH\u0305\u203E")
