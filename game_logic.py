"""
Game Logic Module für Tic-Tac-Toe
Handhabt Spielzustand, Regeln und Gewinnprüfung
"""

from typing import List, Optional, Tuple
import random


class GameLogic:
    def __init__(self):
        self.reset_game()
    
    def reset_game(self) -> None:
        """Setzt das Spiel zurück"""
        self.board = [["*" for _ in range(3)] for _ in range(3)]
        self.current_player = 0  # 0 = X, 1 = O
        self.game_over = False
        self.winner = None
        self.winning_line = []
    
    @property
    def current_player_symbol(self) -> str:
        """Gibt das Symbol des aktuellen Spielers zurück"""
        return "X" if self.current_player == 0 else "O"
    
    def is_valid_move(self, row: int, col: int) -> bool:
        """Prüft ob ein Zug gültig ist"""
        if self.game_over:
            return False
        if row < 0 or row >= 3 or col < 0 or col >= 3:
            return False
        return self.board[row][col] == "*"
    
    def make_move(self, row: int, col: int) -> bool :
        """Führt einen Zug aus und prüft auf Gewinn"""
        if not self.is_valid_move(row, col):
            return False 
        
        self.board[row][col] = self.current_player_symbol
        
        # Prüfe auf Gewinn
        self.winner = self._check_winner()
        if self.winner:
            self.game_over = True
            return True 
        
        # Prüfe auf Unentschieden
        if self._is_board_full():
            self.game_over = True
            return True 
        
        # Wechsel Spieler
        self.current_player = 1 - self.current_player
        return True
    
    def make_random_move(self) -> bool :
        """Macht einen zufälligen Zug für den aktuellen Spieler"""
        if self.game_over:
            return False
        
        empty_positions = self._get_empty_positions()
        if not empty_positions:
            return False
        
        row, col = random.choice(empty_positions)
        return self.make_move(row, col)
    
    def _get_empty_positions(self) -> List[Tuple[int, int]]:
        """Gibt alle leeren Positionen zurück"""
        empty_positions = []
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == "*":
                    empty_positions.append((i, j))
        return empty_positions
    
    def _check_winner(self) -> Optional[str]:
        """Prüft auf Gewinner und setzt winning_line"""
        # Prüfe Reihen
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != "*":
                self.winning_line = [(i, 0), (i, 1), (i, 2)]
                return self.board[i][0]
        
        # Prüfe Spalten
        for j in range(3):
            if self.board[0][j] == self.board[1][j] == self.board[2][j] != "*":
                self.winning_line = [(0, j), (1, j), (2, j)]
                return self.board[0][j]
        
        # Prüfe Diagonalen
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != "*":
            self.winning_line = [(0, 0), (1, 1), (2, 2)]
            return self.board[0][0]
        
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != "*":
            self.winning_line = [(0, 2), (1, 1), (2, 0)]
            return self.board[0][2]
        
        return None
    
    def _is_board_full(self) -> bool:
        """Prüft ob das Board voll ist"""
        for row in self.board:
            if "*" in row:
                return False
        return True
    
    def get_status_message(self) -> str:
        """Gibt die aktuelle Statusnachricht zurück"""
        if self.winner:
            return f"Spieler {self.winner} gewinnt!"
        elif self.game_over:
            return "Unentschieden!"
        else:
            return f"Spieler {self.current_player_symbol} ist dran"
