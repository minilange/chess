import os
from time import sleep
from classes import Board




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


    board = Board("rnbqkbnr/ppppp2p/8/5ppQ/3PP3/8/PPP2PPP/RNB1KBNR")

    # board = Board()
    board.display()

    while not board.is_player_checkmate():
        print()
        test = input()
        print(test*2)
    
    winner = "White" if not board.turn else "Black"

    print(f"The winner is {winner}")


if __name__ == "__main__":
    main()