class Board():
    def __init__(self) -> None:
        self.name = "Board"
        print(self.name)

class Piece():
    def __init__(self) -> None:
        self.name = "Piece"
        print(self.name)

class King(Piece):
    def __init__(self) -> None:
        self.name = "King"
        print(self.name)


class Queen(Piece):
    def __init__(self) -> None:
        self.name = "Queen"
        print(self.name)


class Bishop(Piece):
    def __init__(self) -> None:
        self.name = "Bishop"
        print(self.name)


class Knight(Piece):
    def __init__(self) -> None:
        self.name = "Knight"
        print(self.name)


class Rook(Piece):
    def __init__(self) -> None:
        self.name = "Rook"
        print(self.name)


class Pawn(Piece):
    def __init__(self) -> None:
        self.name = "Pawn"
        print(self.name)
