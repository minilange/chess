
def max_move(num):
    return [num*(n+1) for n in range(7)]


class _Piece:
    symbol = None
    pattern = None
    have_moved = False
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
        [-8],  # Top
        [-7],  # Top Right
        [-1],  # Right
        [1],   # Bottom Right
        [7],   # Bottom
        [8],   # Bottom Left
        [9],   # Left
        [-9],  # Top Left
    ]


class Queen(_Piece):
    symbol = "Q"
    pattern = [
        max_move(-8),  # Top
        max_move(-7),  # Top Right
        max_move(-1),  # Right
        max_move(1),   # Bottom Right
        max_move(7),   # Bottom
        max_move(8),   # Bottom Left
        max_move(9),   # Left
        max_move(-9)   # Top Left
    ]


class Bishop(_Piece):
    symbol = "B"
    pattern = [
        max_move(-9),  # Top Left
        max_move(-7),  # Top Right
        max_move(7),   # Bottom Left
        max_move(9)    # Bottom Right
    ]


class Knight(_Piece):
    symbol = "N"
    pattern = [
        [-17, -15],  # Top
        [-6, 10],    # Right
        [15, 17],    # Down
        [-10, 6],    # Left
    ]


class Rook(_Piece):
    symbol = "R"
    pattern = [
        max_move(-8),  # Top
        max_move(1),   # Right
        max_move(8),   # Bottom
        max_move(-1),  # Left
    ]


class Pawn(_Piece):
    symbol = "P"
    en_passant = False

    pattern = {
        "P": [[-8]],
        "p": [[8]]
    }

    init_pattern = {
        "P": [[-16]],
        "p": [[16]]
    }

    attack_pattern = {
        "P": [[-9, -7]],
        "p": [[7, 9]]
    }
