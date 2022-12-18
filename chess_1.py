
from copy import deepcopy
import math
from decimal import DivisionByZero
from pieces import Bishop, King, Knight, Pawn, Piece, Queen, Rook


def outside_border(total, pos, offset):
    # Boolean expression of hell - DO NOT TOUCH
    outside = (
        (total % 8 == 7 and ((pos % 8 == 0 and math.floor(total / 8) != math.floor(pos / 8)) or offset + pos % 8 == 0)) or
        (total % 8 == 0 and ((pos % 8 == 7 and math.floor(total / 8) != math.floor(pos / 8)) or offset + pos % 8 == 7)) or
        (math.floor(total / 8) == math.floor((offset + pos) / 8) and abs(total - (offset + pos)) > 1) or
        (math.floor(total / 8) == math.floor((offset + pos) / 8) + 2 or math.floor(total / 8) == math.floor((offset + pos) / 8) - 2) or
        ((abs(offset + pos - total) > 1 or (abs(offset + pos - total) ==
         0 and abs(offset) != 1)) and math.floor(total / 8) == math.floor(pos / 8))
    )
    return outside


class Board():

    turn = True
    threefold_history = []
    end_game_reason = None
    current_en_passant = None
    half_clock = 0
    full_move_num = 0

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

    def sort_piece_func(self, p):
        p = self.board[p]

        score = {
            "k": 0,
            "q": 1,
            "b": 2,
            "n": 3,
            "r": 4,
            "p": 5
        }
        return score[p.symbol.lower()]

    def get_all_piece_moves(self, piece_pos: int, board: list[Piece | None], mask: bool = False):

        possible_moves = []

        piece = board[piece_pos]

        pattern = piece.pattern

        # Checks if piece is a pawn
        if isinstance(piece, Pawn):

            # Check if pawn is allowed to make double start
            if not piece.have_moved:
                new_pattern = (pattern[0] + piece.init_pattern[0]).copy()
                pattern = [new_pattern]

            possible_moves += self.get_special_pawn_moves(
                piece_pos, board, mask)

            if mask:
                return possible_moves

        # Check if piece is the king and have not moved, for castling
        if isinstance(piece, King) and not piece.have_moved and not mask:
            possible_moves += self.get_castle_moves(piece_pos, board)

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
                    if isinstance(piece, Knight):
                        continue
                    else:
                        break

                if idx == 0:
                    idx_offset = 0

                # Checks if move is exceeding the side border, and breaks if so
                # print(total, piece_pos, dir[idx + idx_offset])
                if not isinstance(piece, Knight) and outside_border(total, piece_pos, dir[idx + idx_offset]):
                    break

                # If piece is a Knight, make special check for out of bounds on sides
                if isinstance(piece, Knight) and abs(piece_pos % 8 - total % 8) > 2:
                    continue

                # Breaks if direction hits another piece, and appends move is it's an opponent
                if board[total] != None:
                    if board[total].color != piece.color and not isinstance(piece, Pawn):
                        possible_moves.append(total)

                    if isinstance(piece, Knight):
                        continue
                    else:
                        break

                # Makes sure offset num is not making it to be Out of Bounds
                if idx == 0:
                    idx_offset = 0

                # Adds the me as a possible move
                possible_moves.append(total)

        return possible_moves

    def get_opponent_move_mask(self, boad: list[Piece | None]):

        player, _ = self.get_colors()

        king_pos = self.get_king_pos(self.board, player)

        copy_board = deepcopy(boad)

        copy_board[king_pos] = None

        whites, blacks = self.get_board_pieces(copy_board)

        enemy_pieces = blacks if player == "white" else whites

        all_moves = []
        for piece in enemy_pieces:
            moves = self.get_all_piece_moves(piece, copy_board, True)
            all_moves += moves

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

        pins, _ = self.num_king_pinned(self.board)

        if isinstance(self.board[piece_pos], King):

            king_moves = self.get_king_moves(piece_pos)

            return king_moves

        if pins == 2:
            return []

        # elif pins == 1:

            # moves = self.get_all_piece_moves(piece_pos, self.board)
            # moves = []

            # mask = self.get_opponent_move_mask(self.board)
            # for move in piece_moves:
            #     if move in mask:
            #         moves.append(move)
#
        # else:
        moves = self.get_all_piece_moves(piece_pos, self.board)

        # removes any move that leaves the king pinned
        for move in deepcopy(moves):
            copy_board = deepcopy(self.board)

            copy_board[move] = self.board[piece_pos]
            copy_board[piece_pos] = None

            pins, _ = self.num_king_pinned(copy_board)

            if pins > 0:
                moves.remove(move)

        return moves

    def get_king_pos(self, board: list[Piece | None], color: str):

        for idx, spot in enumerate(board):
            if spot is not None and isinstance(spot, King) and spot.color == color:
                return idx

    def get_king_moves(self, piece_pos: int):

        psudeo_moves = self.get_all_piece_moves(piece_pos, self.board)

        for move in deepcopy(psudeo_moves):
            copy_board = deepcopy(self.board)
            copy_board[move] = None
            if move in self.get_opponent_move_mask(copy_board):
                psudeo_moves.remove(move)

        return psudeo_moves

    def num_king_pinned(self, board: list[Piece | None]):

        board = deepcopy(board)

        color = "white" if self.turn else "black"

        king = self.get_king_pos(self.board, color)

        pin_checks = [
            Bishop(symbol="B" if self.turn else "b"),
            Knight(symbol="N" if self.turn else "n"),
            Rook(symbol="R" if self.turn else "r"),
            Pawn(symbol="P" if self.turn else "p")
        ]

        num_pinned = 0
        pin_pos = []

        for piece in pin_checks:
            board[king] = piece
            moves = self.get_all_piece_moves(king, board)

            for move in moves:
                if board[move] is not None and board[move].color != color:

                    if type(board[move]) == type(piece) or (type(board[move]) == Queen and type(piece) != Knight):
                        num_pinned += 1
                        pin_pos.append(move)

        return num_pinned, pin_pos

    def get_special_pawn_moves(self, piece_pos: int, board: list[Piece | None], mask: bool = False):

        moves = []

        piece = board[piece_pos]

        # Checks if Pawn can kill an opponant piece
        for move in piece.attack_pattern[0]:

            # Makes sure move is within the board and does not escape sides
            if piece_pos + move <= 0 or piece_pos + move >= 63 or (piece_pos % 8 == 0 and (piece_pos + move) % 8 == 7) or (piece_pos % 8 == 7 and (piece_pos + move) % 8 == 0):
                continue

            # Checks if there is an piece on attack spot
            if (board[piece_pos + move] != None and board[piece_pos + move].color != piece.color) or mask:
                moves.append(piece_pos + move)

        sides = [1, -1]

        # Checks if an opposing pawn is to the left or right of the pawn, and if en passant is allowed
        for side in sides:
            if piece_pos + side <= 0 and piece_pos + side >= 63 and isinstance(board[piece_pos + side], Pawn):
                if board[piece_pos + side].en_passant:

                    copy_board = deepcopy(board)
                    copy_board[piece_pos] = None
                    copy_board[piece_pos + side] = None

                    pins, _ = self.num_king_pinned(copy_board)
                    if pins == 0:
                        index = 0 if side == -1 else 1
                        moves.append(
                            piece_pos + piece.attack_pattern[0][index])

        # # # Checks if an opposing pawn is to the right of pawn, and if en passant is allowed

        return moves

    def promote_pawn(self, piece_pos, upgrade_piece):

        symbol = upgrade_piece.upper(
        ) if self.board[piece_pos].color == "white" else upgrade_piece.lower()

        match symbol.lower():
            case "q":
                new_piece = Queen(symbol)
            case "r":
                new_piece = Rook(symbol)
            case "b":
                new_piece = Bishop(symbol)
            case "n":
                new_piece = Knight(symbol)
            case _:
                new_piece = Queen("q" if symbol.islower() else "Q")

        new_piece.have_moved = False

        self.board[piece_pos] = new_piece

        return

    def get_castle_moves(self, king_pos: int, board: list[Piece | None]):

        moves = []

        # Select the piece, if any, at king's side rook position
        if king_pos + 3 < 64:
            r_ks = board[king_pos + 3]

            # Check if selected piece is a rook, and have not moved
            if isinstance(r_ks, Rook) and not r_ks.have_moved:
                if self.castle_available(king_pos, king_pos + 3, board):
                    board[king_pos].castle = True
                    moves.append(king_pos + 2)

        if king_pos - 4 > -1:
            r_qs = board[king_pos - 4]

            if isinstance(r_qs, Rook) and not r_qs.have_moved:
                if self.castle_available(king_pos, king_pos - 4, board):
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

        enemy_mask = self.get_opponent_move_mask(board)

        for new_pos in between_space_pos:
            if king_pos + (new_pos * x) in enemy_mask:
                return False

        return True

    def is_game_over(self):

        if self.is_player_checkmate():
            reason = "Checkmate"

        elif self.is_stalemate():
            reason = "Stalemate"

        elif self.is_dead_pos():
            reason = "Deadpos"

        elif self.fifty_move_draw():
            reason = "Fifty-move-rule"

        elif self.threefold_repetition():
            reason = "Threefold repetition"

        else:
            reason = None

        if reason is not None:
            self.end_game_reason = reason
            return True

        else:
            return False

    def is_stalemate(self):
        whites, blacks = self.get_board_pieces(self.board)

        pieces = whites if self.turn else blacks

        for piece in pieces:
            legal_moves = self.get_all_legal_moves_for_pos(piece)

            if len(legal_moves) > 0:
                return False

        return True

    def is_player_checkmate(self):
        pins, _ = self.num_king_pinned(self.board)

        if pins == 0:
            return False

        no_moves = self.is_stalemate()

        return no_moves

    def threefold_repetition(self):
        boards = {}

        for board in self.threefold_history:

            if board in boards:
                boards[board] += 1
            else:
                boards[board] = 1

            if boards[board] == 3:
                return True

        return False

    def is_dead_pos(self):
        whites, blacks = self.get_board_pieces(self.board)

        if len(whites) == 1 and len(blacks) == 1:
            if isinstance(self.board[whites[0]], King) and isinstance(self.board[blacks[0]], King):
                return True

        elif (len(whites) == 2 and len(blacks) == 1) or (len(whites) == 1 and len(blacks) == 2):
            big, small = (blacks, whites) if len(
                whites) == 1 else (whites, blacks)
            big.sort(key=self.sort_piece_func)
            small.sort(key=self.sort_piece_func)

            if (isinstance(self.board[big[1]], Bishop) or isinstance(self.board[big[1]], Knight)) and \
                    isinstance(self.board[big[0]], King) and isinstance(self.board[small[0]], King):
                return True

        elif len(whites) == 2 and len(blacks) == 2:
            whites.sort(key=self.sort_piece_func)
            blacks.sort(key=self.sort_piece_func)

            if isinstance(whites[0], King) and isinstance(whites[1], Bishop) and isinstance(blacks[0], King) and isinstance(blacks[1], Bishop):
                if whites[1] % 2 == blacks[1] % 2:
                    return True

        return False

    def fifty_move_draw(self):

        if self.half_clock >= 100:
            return True

        return False

    def end_turn(self):

        splits = self.export_fen_notation().split(" ")
        new_board = f"{splits[0]} {splits[1]} {splits[2]} {splits[3]}"

        self.threefold_history.append(new_board)
        self.turn = not self.turn

        if self.current_en_passant is not None:
            self.board[self.current_en_passant].en_passant = False
            self.current_en_passant = None

        # whites, blacks = self.get_board_pieces(self.board)

        # pieces = whites if self.turn else blacks

        # for piece_pos in pieces:
        #     if isinstance(self.board[piece_pos], Pawn):
        #         self.board[piece_pos].en_passant = False
        #         self.current_en_passant = "-"

            # if isinstance(self.board[piece_pos], King):
            #     self.board[piece_pos].castle = False

    def make_move(self, from_pos: int, to_pos: int, board: list[Piece | None]):

        en_passant_move = 0
        reset_fifty_move = False

        if board[to_pos] is not None:
            message = f" and killed {board[to_pos]}"
            reset_fifty_move = True
            self.threefold_history = []

        # Checks if attacking piece is a Pawn and is trying to do en passant
        elif isinstance(board[from_pos], Pawn):

            color_moves = board[from_pos].pattern * -1

            # Check if white or black performed en passant
            for move in color_moves:
                if (to_pos + move) >= 0 and isinstance(board[to_pos + move], Pawn) and board[to_pos + move].en_passant:
                    message = f" and killed {board[to_pos + move]}"
                en_passant_move = to_pos + move

            else:
                # No added message if not piece was killed
                message = ""

            reset_fifty_move = True
            self.threefold_history = []

        else:
            # No added message if not piece was killed
            message = ""

        if isinstance(board[from_pos], King) and board[from_pos].castle and abs(from_pos - to_pos) == 2:
            self.make_move_castle(from_pos, to_pos, board)
            return

        # print(
        #     f"Moved {self.int_to_pos(from_pos)} to {self.int_to_pos(to_pos)}{message}")

        # Marks pawn as able to be killed with 'en passant'
        # Handles all special cases there is for a pawn
        if isinstance(board[from_pos], Pawn):
            piece = board[from_pos]

            # Makes sure piece moved two files and have not moved before
            if (to_pos - from_pos) in piece.init_pattern[0] and not piece.have_moved:
                self.current_en_passant = to_pos
                piece.en_passant = True

        # Makes sure piece is marked as moved
        board[from_pos].have_moved = True

        # Move piece from 'from_pos' to 'to_pos' and leave 'from_pos' with None
        board[to_pos] = board[from_pos]
        board[from_pos] = None

        # Increment fifty_consecutive_moves_ rule
        self.half_clock += 1

        if reset_fifty_move:
            self.half_clock = 0

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
                            return self.invalid_fen_notation()

                    # Append the piece to its position on the board
                    board.append(piece)

                    # Check if piece is at the original starting spot
                    board[-1].have_moved = self.piece_have_moved(
                        board[-1].symbol, len(board) - 1)

        # If FEN notation is not correct, use default game
        if len(board) != 64:
            return self.invalid_fen_notation()

        # Set whos turn it is
        try:
            self.turn = True if fen_pieces[1] == "w" else False
        except IndexError:
            return self.invalid_fen_notation()

        # Set correct castling options
        char_pos = {"Q": 56, "K": 63, "q": 0, "k": 7}
        try:
            for opt in ["Q", "K", "q", "k"]:
                if opt in fen_pieces[2] and isinstance(board[char_pos[opt]], Rook):
                    board[char_pos[opt]].have_moved = False
        except IndexError:
            return self.invalid_fen_notation()

        # Set active en passant
        try:
            if fen_pieces[3] != "-":
                en_passant_pos = fen_pieces[3]

                if self.select_piece(en_passant_pos) in [40, 41, 42, 43, 44, 45, 46, 47]:
                    pos = self.select_piece(en_passant_pos) - 8

                elif self.select_piece(en_passant_pos) in [16, 17, 18, 19, 20, 21, 22, 23]:
                    pos = self.select_piece(en_passant_pos) + 8

                print(pos)

                if pos is not None:
                    board[pos].en_passant = True
                    self.current_en_passant = pos

        except IndexError:
            return self.invalid_fen_notation()

        # Sets halfclock
        try:
            self.half_clock = int(fen_pieces[4])
        except IndexError:
            return self.invalid_fen_notation()

        # Set full move number
        try:
            self.full_move_num = int(fen_pieces[5])
        except IndexError:
            return self.invalid_fen_notation()

        self.board = board

    def invalid_fen_notation(self):
        # print("Invalid FEN notation - returns to default setting")
        return self.load_fen_board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

    def piece_have_moved(self, symbol, pos):
        values = {
            "r": [0, 7],
            "n": [1, 6],
            "b": [2, 5],
            "q": [3],
            "k": [4],
            "p": [8, 9, 10, 11, 12, 13, 14, 15],

            "R": [56, 63],
            "N": [57, 62],
            "B": [58, 61],
            "Q": [59],
            "K": [60],
            "P": [48, 49, 50, 51, 52, 53, 54, 55],
        }

        return pos not in values[symbol]

    def export_fen_notation(self):

        fen = ""
        empty_fields = 0

        # Set board string
        for idx, pos in enumerate(self.board):

            if idx % 8 == 0 and idx != 0:
                if empty_fields != 0:
                    fen += str(empty_fields)
                empty_fields = 0

                fen += "/"

            if pos is None:
                empty_fields += 1
            else:
                if empty_fields != 0:
                    fen += str(empty_fields)

                fen += pos.symbol
                empty_fields = 0
        if empty_fields != 0:
            fen += f"{empty_fields}"

        # Set turn
        fen += f" {'w' if self.turn else 'b'}"

        # Find castling options
        castling = ""
        if isinstance(self.board[60], King) and not self.board[60].have_moved:

            if isinstance(self.board[63], Rook) and not self.board[63].have_moved:
                castling += "K"
            if isinstance(self.board[56], Rook) and not self.board[56].have_moved:
                castling += "Q"

        if isinstance(self.board[4], King) and not self.board[4].have_moved:

            if isinstance(self.board[7], Rook) and not self.board[7].have_moved:
                castling += "k"
            if isinstance(self.board[0], Rook) and not self.board[0].have_moved:
                castling += "q"

        # Set castling options
        fen += f" {castling if len(castling) != 0 else '-'}"

        # Set en passant options
        if self.current_en_passant is None:
            fen += "-"

        elif self.board[self.current_en_passant].color == "white":
            fen += f" {self.int_to_pos(self.current_en_passant + 8)}"
        else:
            fen += f" {self.int_to_pos(self.current_en_passant - 8)}"
        

        # Set half moves clock
        fen += f" {self.half_clock}"

        # Set full move clock
        fen += f" {self.full_move_num}"

        return fen

    def display(self, board=None):

        # return

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
