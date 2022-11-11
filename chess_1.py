
from copy import deepcopy
import math
from decimal import DivisionByZero
from pieces import Bishop, King, Knight, Pawn, Piece, Queen, Rook


def outside_border(total, pos, offset):
    return ((total % 8 == 7 and ((pos % 8 == 0 and math.floor(total / 8) != math.floor(pos / 8)) or offset + pos % 8 == 0)) or
            (total % 8 == 0 and ((pos % 8 == 7 and math.floor(total / 8) != math.floor(pos / 8)) or offset + pos % 8 == 7)))


class Board():

    turn = True

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

    def get_all_piece_moves(self, piece_pos: int, board: list[Piece | None]):

        possible_moves = []

        piece = board[piece_pos]

        pattern = piece.pattern

        # Checks if piece is a pawn
        # if isinstance(piece, Pawn):

        #     # Check if pawn is allowed to make double start
        #     if not piece.have_moved:
        #         new_pattern = (pattern[0] + piece.init_pattern[0]).copy()
        #         pattern = [new_pattern]

        #     possible_moves += self.get_en_passant_moves(piece_pos, board)

        # Check if piece is the king and have not moved, for castling
        # if isinstance(piece, King) and not piece.have_moved:
        #     possible_moves += self.get_castle_moves(piece_pos, board)

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
                        possible_moves.append(total)
                    break

                # Makes sure offset num is not making it to be Out of Bounds
                if idx == 0:
                    idx_offset = 0

                # Checks if move is exceeding the side border, and breaks if so
                if outside_border(total, piece_pos, dir[idx + idx_offset]) and not isinstance(piece, Knight):
                    break

                # Adds the me as a possible move
                possible_moves.append(total)

        return possible_moves

    def get_opponent_move_mask(self):

        player, oppo = self.get_colors()

        king_pos = self.get_king_pos(self.board, player)

        copy_board = deepcopy(self.board)

        copy_board[king_pos] = None

        whites, blacks = self.get_board_pieces(copy_board)

        enemy_pieces = blacks if player == "white" else whites

        all_moves = []
        for piece in enemy_pieces:
            print(piece)
            all_moves += self.get_all_piece_moves(piece, copy_board)

        all_moves = list(set(all_moves))

        return all_moves

    def get_board_pieces(self, board: list[int]):
        whites = []
        blacks = []

        for idx, pos in enumerate(board):
            if pos != None:

                if pos.color == "white":
                    whites.append(idx)
                else:
                    blacks.append(idx)

        return whites, blacks

    def get_colors(self):

        if self.turn:
            return "white", "black"
        else:
            return "black", "white"

    def get_all_legal_moves_for_pos(self, piece_pos: int):

        pins, pin_pos = self.num_king_pinned(self.board)

        if pins == 2:
            if not isinstance(self.board[piece_pos], King):
                return []
            else:
                # TODO
                psudeo_moves = self.get_all_piece_moves(piece_pos, self.board)

                for move in pin_pos:
                    if move in psudeo_moves:
                        psudeo_moves.remove(move)

                return psudeo_moves

        elif pins == 1:
            # TODO

            return

        else:
            # TODO
            return

        return

    def get_king_pos(self, board: list[Piece | None], color: str):

        for idx, spot in enumerate(board):
            if spot is not None and isinstance(spot, King) and spot.color == color:
                return idx

    def num_king_pinned(self):

        board = deepcopy(self.board)

        color = "white" if self.turn else "black"

        king = self.get_king_pos(self.board, color)

        pin_pieces = [
            # Queen(symbol="Q" if self.turn else "q"),
            Bishop(symbol="B" if self.turn else "b"),
            Knight(symbol="N" if self.turn else "n"),
            Rook(symbol="R" if self.turn else "r")
        ]

        num_pinned = 0
        pin_pos = []

        for piece in pin_pieces:
            board[king] = piece
            moves = self.get_all_piece_moves(king, board)

            for move in moves:
                if board[move] is not None and board[move].color != color:

                    if type(board[move]) == type(piece) or type(board[move]) == Queen:
                        num_pinned += 1
                        pin_pos.append(move)

        return num_pinned, pin_pos

    def get_en_passant_moves(self, piece_pos: int, board: list[Piece | None]):

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

    def get_castle_moves(self, king_pos: int, board: list[Piece | None]):

        moves = []

        # Select the piece, if any, at king's side rook position
        r_ks = board[king_pos + 3]

        # Check if selected piece is a rook, and have not moved
        if isinstance(r_ks, Rook) and not r_ks.have_moved:
            if self.castle_available(king_pos, king_pos + 3):
                board[king_pos].castle = True
                moves.append(king_pos + 2)

        r_qs = board[king_pos - 4]

        if isinstance(r_qs, Rook) and not r_qs.have_moved:
            if self.castle_available(king_pos, king_pos - 4):
                board[king_pos].castle = True
                moves.append(king_pos - 2)

        return moves

    def castle_available(self, king_pos: int, rook_pos: int, board: list[Piece | None]):

        x = 1

        pos_delta = abs(king_pos - rook_pos)

        if (king_pos - rook_pos) > 0:
            x = -1

        between_space_pos = [i + 1 for i in range(pos_delta - 1)]
        between_spaces = [board[king_pos + (x * i)] for i in between_space_pos]

        if between_spaces.count(None) != pos_delta - 1:
            return False

        # for new_pos in between_space_pos:
            # if not self.is_move_legal(king_pos, king_pos + (x * new_pos)):
            # return False

        return True

    # def is_move_legal(self, from_pos: int, to_pos: int, board: list[Piece | None], turn: bool):

    #     symbol = "K" if turn else "k"

    #     examine_board = deepcopy(board)

    #     # self.

    def make_move(self, from_pos: int, to_pos: int, board: list[Piece | None]):

        en_passant_move = 0

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

        if isinstance(board[from_pos], King) and board[from_pos].castle:
            self.make_move_castle(from_pos, to_pos, board)
            return

        print(
            f"Moved {self.int_to_pos(from_pos)} to {self.int_to_pos(to_pos)}{message}")

        # Marks pawn as able to be killed with 'en passant'
        # Handles all special cases there is for a pawn
        if isinstance(board[from_pos], Pawn):
            piece = board[from_pos]

            # Makes sure piece moved two files and have not moved before
            if (to_pos - from_pos) in piece.init_pattern[0] and not piece.have_moved:
                piece.en_passant = True

        # Makes sure piece is marked as moved
        board[from_pos].have_moved = True

        # Move piece from 'from_pos' to 'to_pos' and leave 'from_pos' with None
        board[to_pos] = board[from_pos]
        board[from_pos] = None

        # Removes piece if piece was killed with en passant
        if en_passant_move != 0:
            self.board[en_passant_move] = None

    def make_move_castle(self, from_king_pos: int, to_king_pos: int, board: list[Piece | None]):

        board[to_king_pos] = board[from_king_pos]
        board[from_king_pos] = None

        # Kingsside castle
        if from_king_pos - to_king_pos < 0:
            rook_from_pos = to_king_pos + 1
            rook_to_pos = to_king_pos - 1

        # Queensside castle
        else:
            rook_from_pos = to_king_pos - 2
            rook_to_pos = to_king_pos + 1

        board[rook_to_pos] = board[rook_from_pos]
        board[rook_from_pos] = None

        board[to_king_pos].castle = False
        board[rook_to_pos].have_moved = True
        board[to_king_pos].have_moved = True

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
