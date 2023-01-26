import math
import json
import random
import pandas as pd
import numpy as np
import tensorflow as tf
from pieces import *
from chess_1 import Board


class ArtificialChessOpponent():

    color: str
    piece_pos: pd.DataFrame
    piece_eval: pd.DataFrame

    def __init__(self, color) -> None:
        self.color = color

        # with open("./piece_tables.json", "r") as file:
            
        #     loaded = json.load(file)

            # self.piece_pos = pd.DataFrame(loaded["pieces"])
            # self.piece_eval = pd.DataFrame(loaded["pos"])
        
        # display(self.piece_pos)

    def get_all_pieces(self, board: Board):

        whites, blacks = board.get_board_pieces(board.board)

        pieces = whites if self.color == "white" else blacks
        return pieces

    def random_move(self, board: Board):

        pieces = self.get_all_pieces(board)

        piece = random.choice(pieces)
        options = board.get_all_legal_moves_for_pos(piece)

        while len(options) == 0:
            piece = random.choice(pieces)
            options = board.get_all_legal_moves_for_pos(piece)

        move = random.choice(options)

        board.make_move(piece, move, board.board)

        if isinstance(board.board[move], Pawn):
            pawn = board.board[move]
            if (pawn.color == "white" and 8 - math.floor(move / 8) == 8) or (pawn.color == "black" and 8 - math.floor(move / 8) == 1):
                board.promote_pawn(move, random.choice(["q", "r", "b", "n"]))

        return

    def evaluation(self, board: Board):

        # get evaulation for white

        # get evaluation for black

        # get score, white_eval - black_eval


        return

    def eval(self, color: str, board: np.array):
        if color == "white":
            pieces = board
        else:
            pieces = board.flip()



        
        return
