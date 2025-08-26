"""
Spielmodul für Tic-Tac-Toe
Hauptkoordinator-Klasse für das gesamte Spiel
"""

from typing import Optional
from time import sleep

from game_logic import GameLogic
from display import create_display, OLEDDisplay
from keypad_input import KeypadInput, InputAction


class TicTacToeGame:
    """Hauptspiel-Klasse die alle Komponenten koordiniert"""
    
    WELCOME_DELAY = 2.0
    MAIN_LOOP_DELAY = 0.1
    
    def __init__(self):
        """Initialisiert das Spiel mit allen Komponenten"""
        self.game_logic = GameLogic()
        self.display = create_display()
        self.keypad = KeypadInput()
        self.running = False  
    
    
    def _handle_game_move(self, row: int, col: int) -> None:
        """Behandelt normale Spielzüge"""
        if self.game_logic.game_over:
            return
        
        if self.game_logic.make_move(row, col):
            self._update_display()
    
    def _handle_reset_game(self) -> None:
        """Behandelt Spiel-Reset"""
        self.game_logic.reset_game()
        self._update_display()
    
    def _handle_random_move(self) -> None:
        """Behandelt zufällige Züge"""
        if self.game_logic.game_over:
            return

        if self.game_logic.make_random_move():
            self._update_display()
    
    def _handle_exit_program(self) -> None:
        """Behandelt Programm-Beendigung"""
        self.running = False
    
    def _update_display(self) -> None:
        """Aktualisiert die Anzeige basierend auf dem Spielzustand"""
        if not self.display:
            self._print_console_board()
            return
        
        status = self.game_logic.get_status_message()
        
        if self.game_logic.winner and self.game_logic.winning_line:
            self.display.show_game_with_animation(
                self.game_logic.board,
                status,
                self.game_logic.winning_line
            )
        else:
            self.display.show_game(
                self.game_logic.board,
                status
            )
    
    def _print_console_board(self) -> None:
        """Fallback: Ausgabe auf der Konsole"""
        print("\n" + "="*30)
        print(f"Status: {self.game_logic.get_status_message()}")
        print("Current board:")
        for row in self.game_logic.board:
            print(" | ".join(cell if cell != "*" else " " for cell in row))
            print("-" * 9)
        print("="*30)
    
    def _show_welcome_screen(self) -> None:
        """Zeigt den Willkommensbildschirm"""
        if self.display:
            self.display.show_welcome()
        else:
            print("="*40)
            print("      Welcome to Tic-Tac-Toe!")
            print("="*40)
            print("Spiel-Steuerung:")
            print("- Reihe 0-2, Spalte 0-2: Spielzug")
            print("- Reihe 3, Spalte 0: Reset")
            print("- Reihe 3, Spalte 2: Zufälliger Zug")
            print("- Reihe 3, Spalte 3: Beenden")
            print("="*40)
        
        sleep(self.WELCOME_DELAY)
        self._update_display()
    
    def start(self) -> None:
        """Startet das Hauptspiel"""
        self.running = True
        try:
            self._show_welcome_screen()
            self._run_main_loop()
        except KeyboardInterrupt:
            print("\nSpiel durch Benutzer beendet.")
        except Exception as e:
            print(f"Unerwarteter Fehler: {e}")
        finally:
            self.cleanup()
    
    def _run_main_loop(self) -> None:
        """Hauptspiel-Schleife"""
        while self.running:
            try:
                # Input verarbeiten
                key = self.keypad.get_input_with_debounce()
                if key:
                    action, data = self.keypad.map_key_to_action(key)
                    
                    # Event-Handler aufrufen
                    if action == InputAction.GAME_MOVE and data:
                        self._handle_game_move(data[0], data[1])
                    elif action == InputAction.RESET_GAME:
                        self._handle_reset_game()
                    elif action == InputAction.RANDOM_MOVE:
                        self._handle_random_move()
                    elif action == InputAction.EXIT_PROGRAM:
                        self._handle_exit_program()
                
                # Kurze Pause um CPU zu schonen
                sleep(self.MAIN_LOOP_DELAY)
                
            except Exception as e:
                print(f"Fehler in der Hauptschleife: {e}")
                break
    
    def cleanup(self) -> None:
        """Räumt Ressourcen auf"""
        if hasattr(self, 'keypad'):
            self.keypad.cleanup()
        print("Spiel beendet. Auf Wiedersehen!")


