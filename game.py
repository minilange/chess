from time import sleep
from classes import Board

def main():
    print("Started script")
    
    board = Board("8")

    board.display()

    tmp = [
            "a1","b1","c1","d1","e1","f1","g1","h1",
            "a2","b2","c2","d2","e2","f2","g2","h2",
            "a7","b7","c7","d7","e7","f7","g7","h7",
            "a8","b8","c8","d8","e8","f8","g8","h8"
        ]

    # tmp = ["f7"]

    total_moves = 0

    for en in tmp:
        total_moves += len(board.get_piece_moves(en))


    print(total_moves)

if __name__ == "__main__":
    main()