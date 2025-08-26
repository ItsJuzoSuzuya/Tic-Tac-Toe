#!/usr/bin/env python3
"""
Tic-Tac-Toe Main Entry Point
"""

from game import TicTacToeGame


def main():
    """Haupteinstiegspunkt für das Tic-Tac-Toe Spiel"""
    game = TicTacToeGame()
    game.start()


if __name__ == "__main__":
    main()
