import random

from chess import Board


class ArtificialChessOpponent():

    color: str

    def __init__(self, color) -> None:
        self.color = color
    

    def get_all_pieces(self, board: Board):
        pieces = board.whites if self.color == "white" else board.blacks
        return pieces


    def random_move(self, board: Board):
        
        pieces = self.get_all_pieces(board)

        piece = random.choice(pieces)
        options = board.get_all_legal_moves_for_pos(piece)

        while len(options) == 0:
            piece = random.choice(pieces)
            options = board.get_all_legal_moves_for_pos(piece)
        
        move = random.choice(options)

        board.make_move(piece, move)
        

        return

