import unittest

from chess import Board
from pieces import Pawn, Rook


class TestChessClass(unittest.TestCase):

# Init function
    def test_init_function(self):

        obj = Board()

        self.assertEqual(len(obj.board), 64)
        self.assertTrue(isinstance(obj.board[0], Rook))
        self.assertTrue(isinstance(obj.board[20], None))

    def test_incorrect_fen_notation(self):

        obj = Board("This is not valid")

        self.assertEqual(len(obj.board), 64)
        self.assertTrue(isinstance(obj.board[0], Rook))
        self.assertTrue(obj.board[20] is None)

    def test_correct_fen_notation(self):

        obj = Board("rnbqkbnr/8/pppppppp/8/8/PPPPPPPP/8/RNBQKBNR")

        self.assertEqual(len(obj.board), 64)
        self.assertTrue(obj.board[8] is None)
        self.assertTrue(isinstance(obj.board[16], Pawn))
        self.assertTrue(obj.board[48] is None)
        self.assertTrue(isinstance(obj.board[40], Pawn))

# Select piece
    def test_select_piece(self):

        obj = Board()

        self.assertEqual(obj.select_piece("a8"), 0)
        self.assertEqual(obj.select_piece("a1"), 56)
        self.assertEqual(obj.select_piece("d2"), 51)
        self.assertEqual(obj.select_piece("f5"), 29)
        self.assertEqual(obj.select_piece("g7"), 14)
        self.assertEqual(obj.select_piece("h1"), 63)
        self.assertEqual(obj.select_piece(None), -1)

# Int to pos 
    def test_int_to_pos(self):
        
        obj = Board()

        self.assertEqual(obj.int_to_pos(0), "a8")
        self.assertEqual(obj.int_to_pos(56), "a1")
        self.assertEqual(obj.int_to_pos(51), "d2")
        self.assertEqual(obj.int_to_pos(29), "f5")
        self.assertEqual(obj.int_to_pos(14), "g7")
        self.assertEqual(obj.int_to_pos(63), "h1")

        