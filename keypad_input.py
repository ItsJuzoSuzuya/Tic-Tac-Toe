"""
Keypad Input Module für Tic-Tac-Toe
"""

from typing import Optional, Tuple
from time import sleep
from enum import Enum
from gpiozero import DigitalOutputDevice, Button


class InputAction(Enum):
    """Definiert verfügbare Eingabe-Aktionen"""
    GAME_MOVE = "game_move"
    RESET_GAME = "reset"
    RANDOM_MOVE = "random"
    EXIT_PROGRAM = "exit"


class KeypadInput:
    """Keypad-Eingabe-Klasse mit Entprellung und Mapping"""
    
    # Hardware-Konfiguration
    DEFAULT_ROW_PINS = [16, 20, 21, 5]
    DEFAULT_COL_PINS = [6, 13, 19, 26]
    
    # Timing-Konstanten
    DEBOUNCE_DELAY = 0.1
    SCAN_DELAY = 0.01
    
    def __init__(self, row_pins: Optional[list] = None, col_pins: Optional[list] = None):
        """Initialisiert das Keypad mit konfigurierbaren Pins"""
        self.row_pins = row_pins or self.DEFAULT_ROW_PINS
        self.col_pins = col_pins or self.DEFAULT_COL_PINS
        
        # Hardware initialisieren
        self.rows = [DigitalOutputDevice(pin) for pin in self.row_pins]
        self.cols = [Button(pin, pull_up=False) for pin in self.col_pins]
        
        # Entprellung
        self.last_key_pressed = None
        
    
    def cleanup(self) -> None:
        """Räumt Hardware-Ressourcen auf"""
        for row in self.rows:
            row.close()
        for col in self.cols:
            col.close()
    
    def read_keypad(self) -> Optional[Tuple[int, int]]:
        """Liest das Keypad und gibt die gedrückte Taste zurück"""
        for i, row in enumerate(self.rows):
            row.on()
            sleep(self.SCAN_DELAY)  # Kleine Verzögerung für Hardware
            
            for j, col in enumerate(self.cols):
                if col.is_pressed:
                    row.off()
                    return (i, j)
            
            row.off()
        
        return None
    
    def get_input_with_debounce(self) -> Optional[Tuple[int, int]]:
        """Liest Eingabe mit Entprellung"""
        current_key = self.read_keypad()
        
        if current_key and current_key != self.last_key_pressed:
            self.last_key_pressed = current_key
            return current_key
        
        return None
    
    def map_key_to_action(self, key: Tuple[int, int]) -> Tuple[InputAction, Optional[Tuple[int, int]]]:
        """Mapped eine Tasteneingabe zu einer Aktion"""
        row, col = key
        
        # Spezielle Tasten in Reihe 3
        if row == 3:
            if col == 0:
                return (InputAction.RESET_GAME, None)
            elif col == 2:
                return (InputAction.RANDOM_MOVE, None)
            elif col == 3:
                return (InputAction.EXIT_PROGRAM, None)
        
        # Normale Spielzüge (3x3 Grid)
        elif 0 <= row < 3 and 0 <= col < 3:
            return (InputAction.GAME_MOVE, (row, col))
        
        # Unbekannte Eingabe
        return (InputAction.GAME_MOVE, None)
    
