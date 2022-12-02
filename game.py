import sys
import math
from time import sleep, time
from ai import ArtificialChessOpponent as ACO
from chess_1 import Board
from pieces import Pawn


def main():
    # print("Started script")

    # board = Board("8/8/8/8/2rPK3/8/8/8")

    # board.display()

    # tmp = [
    #         "a1","b1","c1","d1","e1","f1","g1","h1",
    #         "a2","b2","c2","d2","e2","f2","g2","h2",
    #         "a7","b7","c7","d7","e7","f7","g7","h7",
    #         "a8","b8","c8","d8","e8","f8","g8","h8"
    #     ]

    # # tmp = ["f7"]

    # total_moves = 0

    # # for en in tmp:
    # #     total_moves += len(board.get_piece_moves(en))

    # legal = board.get_all_legal_moves_for_pos(34)

    # print(legal)
    # print(total_moves)

    # board = Board("rnbqkbnr/ppppp2p/PPP2PPP/RNB1KBNR")
    # board = Board("rnbqkbnr/ppppp2p/8/5ppQ/3PP3/8/PPP2PPP/RNB1KBNR")

    player_color = True
    while player_color is None:
        player_color = input("Choose a color, white or black: ")

        if player_color.lower() != "white" and player_color.lower() != "black":
            player_color = None
        else:
            player_color = True if player_color == "white" else False

    opponent = ACO(color="black" if player_color else "white")
    player = ACO(color="white" if player_color else "black")

    board = Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
    # board = Board()

    while not board.is_game_over():

        board.display()

        if board.turn == player_color:
            # piece, moves = select_a_piece(board)

            # while not select_move(board, piece, moves):
            #     piece, moves = select_a_piece(board)

            player.random_move(board)

        else:
            opponent.random_move(board)

            # piece, moves = select_a_piece(board)

            # while not select_move(board, piece, moves):
            #     piece, moves = select_a_piece(board)

        # sleep(0.1)
        board.end_turn()

    # Print out the winner
    board.display()

    if board.end_game_reason == "Checkmate":
        winner = "Blacks" if board.turn else "Whites"
        print(f"The winner is {winner}")
        
    else:
        print(f"Game ended in a draw by {board.end_game_reason}")






def print_turn(board: Board):

    # Decide wether its whites or blacks turn
    turn = "White" if board.turn else "Black"

    # Print whose turn it is
    print(f"{turn} turn to make a move")


def select_a_piece(board: Board):

    # Initiate move as None
    move = None

    # Select a valid move, and ask for a new until a valid is parsed
    while move is None:

        # Retrieve userinput move
        move = input(
            "Select a piece to display it's possible movements: ").lower()

        # Checks if selected position is a valid position
        if len(move) != 2:
            print(f"'{move}' is not a valid arguemnt, try again!")
            move = None

        # Select current players piece set
        whites, blacks = board.get_board_pieces(board.board)
        piece_set = whites if board.turn else blacks

        # Retrieve selected postion as a numerical position
        num_move = board.select_piece(move)

        # Checks if selected numerical move is in the piece set
        if num_move not in piece_set:
            print(f"'{move}' is not one of your pieces, try again!")
            move = None

    # Display all options for moves and retrieves all legal moves
    legal_moves = display_options(board, move)

    # Return numerical position for piece, and all legal moves
    return num_move, legal_moves


def display_options(board: Board, selected: str):

    # Retrieve the numerical position for selected piece
    numerical_pos = board.select_piece(selected)

    # Deciedes whether to check for en passant move or not
    check_en_passant = isinstance(board.board[numerical_pos], Pawn)

    # Get all legal moves for selected piece
    moves = board.get_all_legal_moves_for_pos(numerical_pos)

    # Create a copy of the board
    copy = board.board.copy()

    # Change copy board with all legal moves with '#' if space is not occupied and 'X' if possibility to kill an enemy
    for move in moves:

        if check_en_passant:
            if isinstance(copy[numerical_pos - 1], Pawn) or isinstance(copy[numerical_pos + 1], Pawn):
                if (move - numerical_pos) in copy[numerical_pos].attack_pattern[0]:

                    side = 1 if (move - numerical_pos) > 0 else -1
                    if copy[numerical_pos + side].en_passant and copy[numerical_pos + side].color != copy[numerical_pos].color:
                        copy[side + numerical_pos] = "!"

        if copy[move] is None:
            copy[move] = "#"
        else:
            copy[move] = "X"

    # Display copy board with move options
    board.display(copy)

    # Return all legal moves
    return moves


def select_move(board: Board, piece: int, moves: list[int]):

    # Initiate move as None
    move = None

    # Checks if there are any moves available for selected piece
    if len(moves) == 0:
        print(
            f"{board.board[piece]} at {board.int_to_pos(piece)} does not have any available moves")
        return False

    # Select a valid move, and detects if operation is canceled
    while board.select_piece(move) not in moves:

        # Retrieve userinput move
        move = input("Select one of the highlighted moves, or cancel: ")

        # Check if no move is desired
        if move.lower() == "cancel":
            board.display()
            return False

        # Check if move is valid format
        if len(move) != 2:
            print(f"'{move}' is not a valid arguemnt, try again!")
            move = None

    # Retrieves the numerical position for selected move
    num_move = board.select_piece(move)

    # Make the selected move on the board
    board.make_move(piece, num_move, board.board)

    if isinstance(board.board[num_move], Pawn):
        pawn = board.board[num_move]

        if (pawn.color == "white" and 8 - math.floor(num_move / 8) == 8) or (pawn.color == "black" and 8 - math.floor(num_move / 8) == 0):
            choose_promotion(num_move, board)

    return True


def choose_promotion(piece_pos: int, board: Board):

    board.display()
    new_piece = input("Please select promition: ")

    while new_piece.lower() not in ["q", "r", "b", "n"]:
        print("Select either q, r, b or n")
        new_piece = input("Please select promition: ")

    board.promote_pawn(piece_pos, new_piece)

    return


if __name__ == "__main__":
    # sys.setrecursionlimit(20)


    init_time = time()
    for i in range(100):
        main()
    
    print(time() - init_time)
