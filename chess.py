import math
from decimal import DivisionByZero
from pieces import Bishop, King, Knight, Pawn, Queen, Rook
from copy import deepcopy


def outside_border(total, pos, offset):
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

        board = deepcopy(
            self.board) if examine_board is None else examine_board

        # Select piece from numeric position
        piece = board[piece_pos]
        # print(piece, piece_pos, self.board)

        # Makes sure it's parsed by value and not reference
        pattern = piece.pattern.copy()

        # Checks if piece is a pawn
        if isinstance(piece, Pawn):
        
            # Check if pawn is allowed to make double start
            if not piece.have_moved:
                new_pattern = (pattern[0] + piece.init_pattern[0]).copy()
                pattern = [new_pattern]
        
            available_moves += self.get_en_passant_moves(piece_pos, board)

        # Check if piece is the king and have not moved, for castling
        if isinstance(piece, King) and not piece.have_moved:
            available_moves += self.get_castle_moves(piece_pos, board)

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

                # Breaks if direction hits another piece, and appends move is it's an opponent
                if board[total] != None:
                    if board[total].color != piece.color and not isinstance(piece, Pawn):
                        available_moves.append(total)
                    break

                # Makes sure offset num is not making it to be Out of Bounds
                if idx == 0:
                    idx_offset = 0

                # Checks if move is exceeding the side border, and breaks if so
                if outside_border(total, piece_pos, dir[idx + idx_offset]) and not isinstance(piece, Knight):
                    break

                # Sets a '#' for every available move
                available_moves.append(total)

        return available_moves

    def get_castle_moves(self, piece_pos: int, board: list[int]):

        moves = []

        # Select the piece, if any, at king's side rook position
        r_ks = board[piece_pos + 3]

        # Check if selected piece is a rook, and have not moved
        if isinstance(r_ks, Rook) and not r_ks.have_moved:
            if self.castle_available(piece_pos, piece_pos + 3):
                moves.append(piece_pos + 2)

            # # Gets the pieces between king and rook on king side
            # empty_space_ks = [self.board[piece_pos + i + 1] for i in range(2)]

            # # Checks if all positions between king and rook are empty
            # if empty_space_ks.count(None) == 2:

        r_qs = board[piece_pos - 4]
        if isinstance(r_qs, Rook) and not r_qs.have_moved:
            if self.castle_available(piece_pos, piece_pos - 3):
                moves.append(piece_pos - 2)

        return moves

    def get_en_passant_moves(self, piece_pos: int, board: list[int]):

        moves = []

        piece = board[piece_pos]


        # Checks if Pawn can kill an opponant piece
        for move in piece.attack_pattern[0]:

            # Makes sure move is within the board
            if piece_pos + move < 0 or piece_pos + move > 63:
                break

            # Checks if there is an piece on attack spot
            if board[piece_pos + move] != None and board[piece_pos + move].color != piece.color:
                moves.append(piece_pos + move)

        # Checks if an opposing pawn is to the left of pawn, and if en passant is allowed
        if isinstance(board[piece_pos - 1], Pawn):
            if board[piece_pos - 1].en_passant:
                moves.append(
                    piece_pos + piece.attack_pattern[0][0])

        # # Checks if an opposing pawn is to the right of pawn, and if en passant is allowed
        if isinstance(board[piece_pos + 1], Pawn):
            if board[piece_pos + 1].en_passant:
                moves.append(
                    piece_pos + piece.attack_pattern[0][1])

        return moves

    def castle_available(self, king_pos: int, rook_pos: int):

        x = 1

        pos_delta = abs(king_pos - rook_pos)

        if (king_pos - rook_pos) > 0:
            x = -1

        between_space_pos = [i + 1 for i in range(pos_delta - 1)]
        between_spaces = [self.board[king_pos +
                                     (x * i)] for i in between_space_pos]

        # if king_pos == 60:
        # print(king_pos, between_space_pos, between_spaces)

        if between_spaces.count(None) != pos_delta - 1:
            return False

        for new_pos in between_space_pos:
            if not self.is_move_legal(king_pos, king_pos + (x * new_pos)):
                # print(new_pos)
                return False

        return True

    def is_move_legal(self, from_pos: int, to_pos: int):

        # Determine whos king to look for and choose enemy piece set
        symbol = "K" if self.turn else "k"

        # Create a copy of the board
        examine_board = deepcopy(self.board)

        # Makes the selected move to get analysis
        # print(enemy_pieces)
        self.make_move(from_pos, to_pos, examine_board)

        whites, blacks = self.get_board_pieces(examine_board)

        enemy_pieces = blacks if self.turn else whites

        # Retrieve the position of the king
        king_pos = [idx for idx, piece in enumerate(
            examine_board) if piece is not None and piece.symbol == symbol]

        if len(king_pos) == 0:
            return False

        king_pos = king_pos[0]

        # Iterate through every enemy move and if an enemy piece can kill king return 'illegal'
        for spot in enemy_pieces:
            if king_pos in self.get_all_legal_moves_for_pos(spot, examine_board):
                return False

        # If no move could kill the king, return 'legal'
        return True

    def get_all_legal_moves_for_pos(self, pos: int, board: list[int] = None):

        board = self.board if board == None else board
        # Initiate a list for all legal moves for piece
        legal_moves = []

        # Get all psuedo legal moves
        piece_moves = self.get_piece_moves(pos, board)

        # Iterate through every move and remove illegal moves
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

    def get_board_pieces(self, board: list[int] = None):

        if board is None:
            return self.whites, self.blacks
        else:
            whites = []
            blacks = []

            for idx, pos in enumerate(board):
                if pos != None:

                    if pos.color == "white":
                        whites.append(idx)
                    else:
                        blacks.append(idx)

            return whites, blacks

    def make_move(self, from_pos: int, to_pos: int, copy_board=None):

        board = self.board if copy_board is None else copy_board

        en_passant_move = 0
        castle = False

        # check if the position which the piece is moving to, is already occupied
        if board[to_pos] is not None:
            message = f" and killed {board[to_pos]}"

        # Checks if attacking piece is a Pawn and is trying to do en passant
        elif isinstance(board[from_pos], Pawn):

            # Check if white performed en passant
            if (to_pos - 8) >= 0 and isinstance(board[to_pos - 8], Pawn) and board[to_pos - 8].en_passant:
                message = f" and killed {board[to_pos - 8]}"
                en_passant_move = to_pos - 8

            # Check if black performed en passant
            elif (to_pos + 8) <= 63 and isinstance(board[to_pos + 8], Pawn) and board[to_pos + 8].en_passant:
                message = f" and killed {board[to_pos + 8]}"
                en_passant_move = to_pos + 8

            else:
                # No added message if not piece was killed
                message = ""

        else:
            # No added message if not piece was killed
            message = ""

        if isinstance(board[from_pos], King) and abs(from_pos - to_pos) > 1:
            x = 1 if (from_pos - to_pos) < 0 else -2

            if (to_pos + x) <= 63 and (to_pos + x) >= 0 and board[to_pos + x] is not None and isinstance(board[to_pos + x], Rook) and not board[to_pos + x].have_moved:
                castle = True

                # to_pos + x, to_pos + (-1 * x), board
                # from_pos, to_pos, board

                r_from = to_pos + x
                r_to = to_pos + 1 if x < 0 else to_pos - 1

                if copy_board == None:
                    self.make_move(r_from, r_to)
                    self.make_move(from_pos, to_pos)
                else:
                    self.make_move(r_from, r_to, board)
                    self.make_move(from_pos, to_pos, board)

        # Print message for the move
        if copy_board == None:
            if castle:
                side = 'kingsside' if x == 1 else 'queensside'
                print(f"Performed castle to {side}")
                return
            else:
                print(
                    f"Moved {self.int_to_pos(from_pos)} to {self.int_to_pos(to_pos)}{message}")

        # Marks pawn as able to be killed with 'en passant'
        # Handles all special cases there is for a pawn
        if isinstance(board[from_pos], Pawn):
            piece = board[from_pos]

            # Makes sure piece moved two files and have not moved before
            if (to_pos - from_pos) in piece.init_pattern[0] and not piece.have_moved:
                piece.en_passant = True

        whites, blacks = self.get_board_pieces(copy_board)

        # Makes sure player piece lists are up-to-date
        if self.turn:  # Whites turn
            player = whites
            opponent = blacks

        else:  # Blacks turn
            player = blacks
            opponent = whites

        # Updates players piece list if it's an actual move
        if copy_board == None:
            player.remove(from_pos)
            player.append(to_pos)

        # Updates opponents piece list if a piece was lost
        if board[to_pos] is not None and copy_board == None and not castle:
            opponent.remove(to_pos)

        # Updates opponents piece list if en passant was performed
        if en_passant_move != 0:
            opponent.remove(en_passant_move)

        # Pieces have been marked as moved and have been moved
        if not castle:

            # Makes sure piece is marked as moved
            board[from_pos].have_moved = True

            # Move piece from 'from_pos' to 'to_pos' and leave 'from_pos' with None
            board[to_pos] = board[from_pos]
            board[from_pos] = None

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
                        case _:
                            print(
                                "Invalid FEN notation - returns to default setting")
                            return self.load_fen_board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")

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
