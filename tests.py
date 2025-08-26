#!/usr/bin/env python3
"""
Umfassende Test-Suite für Tic-Tac-Toe Spiel
Testet alle wichtigen Funktionen der Module
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import io
from typing import List, Optional

# Module importieren
from game_logic import GameLogic
from keypad_input import KeypadInput, InputAction

# Mock für Hardware-abhängige Module
sys.modules['gpiozero'] = Mock()
sys.modules['PIL'] = Mock()
sys.modules['luma.core.interface.serial'] = Mock()
sys.modules['luma.oled.device'] = Mock()

from display import create_display, OLEDDisplay
from game import TicTacToeGame


class TestGameLogic(unittest.TestCase):
    """Tests für die GameLogic Klasse"""
    
    def setUp(self):
        """Setup vor jedem Test"""
        self.game = GameLogic()
    
    def test_initial_state(self):
        """Test des initialen Spielzustands"""
        # Board sollte leer sein
        expected_board = [["*" for _ in range(3)] for _ in range(3)]
        self.assertEqual(self.game.board, expected_board)
        
        # Spieler X sollte anfangen
        self.assertEqual(self.game.current_player, 0)
        self.assertEqual(self.game.current_player_symbol, "X")
        
        # Spiel sollte nicht beendet sein
        self.assertFalse(self.game.game_over)
        self.assertIsNone(self.game.winner)
        self.assertEqual(self.game.winning_line, [])
    
    def test_valid_moves(self):
        """Test für gültige Züge"""
        # Gültiger Zug
        self.assertTrue(self.game.is_valid_move(0, 0))
        self.assertTrue(self.game.is_valid_move(1, 1))
        self.assertTrue(self.game.is_valid_move(2, 2))
        
        # Nach einem Zug sollte die Position nicht mehr gültig sein
        self.assertTrue(self.game.make_move(0, 0))
        self.assertFalse(self.game.is_valid_move(0, 0))
    
    def test_invalid_moves(self):
        """Test für ungültige Züge"""
        # Außerhalb des Boards
        self.assertFalse(self.game.is_valid_move(-1, 0))
        self.assertFalse(self.game.is_valid_move(0, -1))
        self.assertFalse(self.game.is_valid_move(3, 0))
        self.assertFalse(self.game.is_valid_move(0, 3))
        
        # Bereits belegte Position
        self.game.make_move(1, 1)
        self.assertFalse(self.game.is_valid_move(1, 1))
    
    def test_player_switching(self):
        """Test des Spielerwechsels"""
        # Spieler X beginnt
        self.assertEqual(self.game.current_player_symbol, "X")
        
        # Nach einem Zug wechselt zu O
        self.game.make_move(0, 0)
        self.assertEqual(self.game.current_player_symbol, "O")
        
        # Nach weiterem Zug zurück zu X
        self.game.make_move(0, 1)
        self.assertEqual(self.game.current_player_symbol, "X")
    
    def test_win_conditions_rows(self):
        """Test für Gewinn in Reihen"""
        # X gewinnt in oberer Reihe
        self.game.make_move(0, 0)  # X
        self.game.make_move(1, 0)  # O
        self.game.make_move(0, 1)  # X
        self.game.make_move(1, 1)  # O
        self.game.make_move(0, 2)  # X
        
        self.assertTrue(self.game.game_over)
        self.assertEqual(self.game.winner, "X")
        self.assertEqual(self.game.winning_line, [(0, 0), (0, 1), (0, 2)])
    
    def test_win_conditions_columns(self):
        """Test für Gewinn in Spalten"""
        # O gewinnt in linker Spalte
        self.game.make_move(0, 1)  # X
        self.game.make_move(0, 0)  # O
        self.game.make_move(0, 2)  # X
        self.game.make_move(1, 0)  # O
        self.game.make_move(1, 1)  # X
        self.game.make_move(2, 0)  # O
        
        self.assertTrue(self.game.game_over)
        self.assertEqual(self.game.winner, "O")
        self.assertEqual(self.game.winning_line, [(0, 0), (1, 0), (2, 0)])
    
    def test_win_conditions_diagonal_main(self):
        """Test für Gewinn in Hauptdiagonale"""
        # X gewinnt diagonal von oben-links zu unten-rechts
        self.game.make_move(0, 0)  # X
        self.game.make_move(0, 1)  # O
        self.game.make_move(1, 1)  # X
        self.game.make_move(0, 2)  # O
        self.game.make_move(2, 2)  # X
        
        self.assertTrue(self.game.game_over)
        self.assertEqual(self.game.winner, "X")
        self.assertEqual(self.game.winning_line, [(0, 0), (1, 1), (2, 2)])
    
    def test_win_conditions_diagonal_anti(self):
        """Test für Gewinn in Anti-Diagonale"""
        # O gewinnt diagonal von oben-rechts zu unten-links
        self.game.make_move(0, 0)  # X
        self.game.make_move(0, 2)  # O
        self.game.make_move(0, 1)  # X
        self.game.make_move(1, 1)  # O
        self.game.make_move(1, 0)  # X
        self.game.make_move(2, 0)  # O
        
        self.assertTrue(self.game.game_over)
        self.assertEqual(self.game.winner, "O")
        self.assertEqual(self.game.winning_line, [(0, 2), (1, 1), (2, 0)])
    
    def test_draw_game(self):
        """Test für Unentschieden"""
        # Spielen bis Unentschieden
        moves = [
            (0, 0),  # X
            (0, 1),  # O
            (0, 2),  # X
            (1, 1),  # O
            (1, 0),  # X
            (1, 2),  # O
            (2, 1),  # X
            (2, 0),  # O
            (2, 2)   # X
        ]
        
        for row, col in moves:
            self.game.make_move(row, col)
        
        self.assertTrue(self.game.game_over)
        self.assertIsNone(self.game.winner)
        self.assertEqual(self.game.get_status_message(), "Unentschieden!")
    
    def test_random_move(self):
        """Test für zufällige Züge"""
        # Board halb füllen
        self.game.make_move(0, 0)
        self.game.make_move(0, 1)
        self.game.make_move(1, 1)
        
        # Zufälliger Zug sollte funktionieren
        result = self.game.make_random_move()
        self.assertTrue(result)
        
        # Nach dem Zug sollte ein neues Feld belegt sein
        filled_count = sum(1 for row in self.game.board for cell in row if cell != "*")
        self.assertEqual(filled_count, 4)
    
    def test_random_move_full_board(self):
        """Test für zufälligen Zug bei vollem Board"""
        # Board komplett füllen
        for i in range(3):
            for j in range(3):
                self.game.board[i][j] = "X"
        
        # Zufälliger Zug sollte fehlschlagen
        result = self.game.make_random_move()
        self.assertFalse(result)
    
    def test_reset_game(self):
        """Test für Spiel-Reset"""
        # Spiel ein bisschen spielen
        self.game.make_move(0, 0)
        self.game.make_move(1, 1)
        
        # Reset
        self.game.reset_game()
        
        # Sollte wieder im Anfangszustand sein
        expected_board = [["*" for _ in range(3)] for _ in range(3)]
        self.assertEqual(self.game.board, expected_board)
        self.assertEqual(self.game.current_player, 0)
        self.assertFalse(self.game.game_over)
        self.assertIsNone(self.game.winner)
        self.assertEqual(self.game.winning_line, [])
    
    def test_status_messages(self):
        """Test für Statusnachrichten"""
        # Anfangszustand
        self.assertEqual(self.game.get_status_message(), "Spieler X ist dran")
        
        # Nach einem Zug
        self.game.make_move(0, 0)
        self.assertEqual(self.game.get_status_message(), "Spieler O ist dran")
        
        # Gewinner-Szenario simulieren
        self.game.board = [["X", "X", "X"], ["*", "*", "*"], ["*", "*", "*"]]
        self.game.winner = "X"
        self.game.game_over = True
        self.assertEqual(self.game.get_status_message(), "Spieler X gewinnt!")


class TestKeypadInput(unittest.TestCase):
    """Tests für KeypadInput Klasse"""
    
    @patch('keypad_input.DigitalOutputDevice')
    @patch('keypad_input.Button')
    def setUp(self, mock_button, mock_output):
        """Setup mit gemockter Hardware"""
        self.mock_rows = [Mock() for _ in range(4)]
        self.mock_cols = [Mock() for _ in range(4)]
        
        mock_output.side_effect = self.mock_rows
        mock_button.side_effect = self.mock_cols
        
        self.keypad = KeypadInput()
    
    def test_action_mapping_game_moves(self):
        """Test für Spielzug-Mapping"""
        # Test aller gültigen Spielzüge
        for row in range(3):
            for col in range(3):
                action, data = self.keypad.map_key_to_action((row, col))
                self.assertEqual(action, InputAction.GAME_MOVE)
                self.assertEqual(data, (row, col))
    
    def test_action_mapping_special_functions(self):
        """Test für Spezialfunktionen-Mapping"""
        # Reset-Taste
        action, data = self.keypad.map_key_to_action((3, 0))
        self.assertEqual(action, InputAction.RESET_GAME)
        self.assertIsNone(data)
        
        # Zufälliger Zug
        action, data = self.keypad.map_key_to_action((3, 2))
        self.assertEqual(action, InputAction.RANDOM_MOVE)
        self.assertIsNone(data)
        
        # Programm beenden
        action, data = self.keypad.map_key_to_action((3, 3))
        self.assertEqual(action, InputAction.EXIT_PROGRAM)
        self.assertIsNone(data)
    
    def test_cleanup(self):
        """Test für Hardware-Cleanup"""
        # Cleanup sollte alle Hardware-Objekte schließen
        self.keypad.cleanup()
        
        for mock_row in self.mock_rows:
            mock_row.close.assert_called_once()
        
        for mock_col in self.mock_cols:
            mock_col.close.assert_called_once()


class TestDisplay(unittest.TestCase):
    """Tests für Display-Funktionalität"""
    
    def test_create_display_no_hardware(self):
        """Test für Display-Erstellung ohne Hardware"""
        with patch('display.OLED_AVAILABLE', False):
            display = create_display()
            self.assertIsNone(display)
    
    @patch('display.OLED_AVAILABLE', True)
    @patch('display.i2c')
    @patch('display.ssd1306')
    @patch('display.ImageFont')
    def test_create_display_with_hardware(self, mock_font, mock_ssd1306, mock_i2c):
        """Test für Display-Erstellung mit Hardware"""
        mock_font.truetype.side_effect = OSError("Font not found")
        mock_font.load_default.return_value = Mock()
        
        display = create_display()
        self.assertIsNotNone(display)
        
        # Font fallback sollte funktioniert haben
        self.assertEqual(mock_font.load_default.call_count, 3)


class TestTicTacToeGame(unittest.TestCase):
    """Tests für die Hauptspiel-Klasse"""
    
    @patch('game.create_display')
    @patch('game.KeypadInput')
    def setUp(self, mock_keypad_class, mock_create_display):
        """Setup mit gemockten Abhängigkeiten"""
        self.mock_display = Mock()
        self.mock_keypad = Mock()
        
        mock_create_display.return_value = self.mock_display
        mock_keypad_class.return_value = self.mock_keypad
        
        self.game = TicTacToeGame()
    
    def test_game_initialization(self):
        """Test der Spiel-Initialisierung"""
        self.assertIsNotNone(self.game.game_logic)
        self.assertIsNotNone(self.game.display)
        self.assertIsNotNone(self.game.keypad)
        self.assertFalse(self.game.running)
    
    def test_handle_game_move(self):
        """Test für Spielzug-Behandlung"""
        # Gültiger Zug
        self.game._handle_game_move(0, 0)
        
        # Board sollte aktualisiert sein
        self.assertEqual(self.game.game_logic.board[0][0], "X")
        
        # Display sollte aktualisiert worden sein
        self.mock_display.show_game.assert_called()
    
    def test_handle_reset_game(self):
        """Test für Spiel-Reset-Behandlung"""
        # Erst ein Zug
        self.game.game_logic.make_move(0, 0)
        
        # Dann Reset
        self.game._handle_reset_game()
        
        # Board sollte zurückgesetzt sein
        expected_board = [["*" for _ in range(3)] for _ in range(3)]
        self.assertEqual(self.game.game_logic.board, expected_board)
    
    def test_handle_random_move(self):
        """Test für zufälligen Zug"""
        initial_filled = sum(1 for row in self.game.game_logic.board for cell in row if cell != "*")
        
        self.game._handle_random_move()
        
        final_filled = sum(1 for row in self.game.game_logic.board for cell in row if cell != "*")
        self.assertEqual(final_filled, initial_filled + 1)
    
    def test_handle_exit_program(self):
        """Test für Programm-Beendigung"""
        self.game.running = True
        self.game._handle_exit_program()
        self.assertFalse(self.game.running)
    
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_console_fallback(self, mock_stdout):
        """Test für Konsolen-Fallback ohne Display"""
        self.game.display = None
        self.game._update_display()
        
        output = mock_stdout.getvalue()
        self.assertIn("Status:", output)
        self.assertIn("Current board:", output)
    
    def test_cleanup(self):
        """Test für Ressourcen-Aufräumung"""
        self.game.cleanup()
        self.mock_keypad.cleanup.assert_called_once()


class TestIntegration(unittest.TestCase):
    """Integrations-Tests"""
    
    @patch('game.create_display')
    @patch('game.KeypadInput')
    def test_complete_game_flow(self, mock_keypad_class, mock_create_display):
        """Test eines kompletten Spielablaufs"""
        # Setup
        mock_display = Mock()
        mock_keypad = Mock()
        mock_create_display.return_value = mock_display
        mock_keypad_class.return_value = mock_keypad
        
        game = TicTacToeGame()
        
        # Simuliere Spielzüge bis Gewinn
        game._handle_game_move(0, 0)  # X
        game._handle_game_move(1, 0)  # O
        game._handle_game_move(0, 1)  # X
        game._handle_game_move(1, 1)  # O
        game._handle_game_move(0, 2)  # X gewinnt
        
        # Überprüfe Endzustand
        self.assertTrue(game.game_logic.game_over)
        self.assertEqual(game.game_logic.winner, "X")
        
        # Display sollte mit Animation aufgerufen worden sein
        mock_display.show_game_with_animation.assert_called()
    
    def test_game_logic_and_display_integration(self):
        """Test der Integration zwischen GameLogic und Display"""
        game_logic = GameLogic()
        
        # Simuliere verschiedene Spielzustände
        test_cases = [
            ("Anfangszustand", "Spieler X ist dran"),
            ("Nach einem Zug", None),  # Wird dynamisch gesetzt
            ("Gewinner", None),        # Wird dynamisch gesetzt
            ("Unentschieden", None)    # Wird dynamisch gesetzt
        ]
        
        # Anfangszustand
        status = game_logic.get_status_message()
        self.assertEqual(status, "Spieler X ist dran")
        
        # Nach einem Zug
        game_logic.make_move(0, 0)
        status = game_logic.get_status_message()
        self.assertEqual(status, "Spieler O ist dran")
        
        # Gewinn simulieren
        game_logic.board = [["X", "X", "X"], ["*", "*", "*"], ["*", "*", "*"]]
        game_logic.winner = "X"
        game_logic.game_over = True
        game_logic.winning_line = [(0, 0), (0, 1), (0, 2)]
        status = game_logic.get_status_message()
        self.assertEqual(status, "Spieler X gewinnt!")


def run_tests():
    """Führt alle Tests aus und gibt Ergebnisse formatiert aus"""
    print("=" * 80)
    print("🎮 TIC-TAC-TOE TEST SUITE")
    print("=" * 80)
    
    # Test-Suite zusammenstellen
    test_classes = [
        TestGameLogic,
        TestKeypadInput,
        TestDisplay,
        TestTicTacToeGame,
        TestIntegration
    ]
    
    total_tests = 0
    total_failures = 0
    total_errors = 0
    
    for test_class in test_classes:
        print(f"\n📋 {test_class.__name__}")
        print("-" * 50)
        
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(
            verbosity=2,
            stream=sys.stdout,
            buffer=True
        )
        result = runner.run(suite)
        
        total_tests += result.testsRun
        total_failures += len(result.failures)
        total_errors += len(result.errors)
        
        # Ergebnis-Summary für diese Klasse
        if result.wasSuccessful():
            print(f"✅ Alle {result.testsRun} Tests bestanden!")
        else:
            print(f"❌ {len(result.failures)} Fehler, {len(result.errors)} Exceptions")
            
            # Details zu Fehlern ausgeben
            if result.failures:
                print("\n🔴 FEHLER:")
                for test, traceback in result.failures:
                    print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
            
            if result.errors:
                print("\n💥 EXCEPTIONS:")
                for test, traceback in result.errors:
                    print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    # Gesamt-Summary
    print("\n" + "=" * 80)
    print("📊 GESAMT-ERGEBNIS")
    print("=" * 80)
    
    if total_failures == 0 and total_errors == 0:
        print(f"🎉 ALLE {total_tests} TESTS ERFOLGREICH!")
        print("\n✨ Das Tic-Tac-Toe Spiel ist vollständig getestet und funktional!")
        print("\n🚀 Bereit für den Einsatz auf Raspberry Pi!")
    else:
        print(f"📈 Tests durchgeführt: {total_tests}")
        print(f"❌ Fehlgeschlagen: {total_failures}")
        print(f"💥 Exceptions: {total_errors}")
        print(f"✅ Erfolgreich: {total_tests - total_failures - total_errors}")
    
    print("\n📝 TEST-ABDECKUNG:")
    print("  ✅ Spiellogik (Züge, Gewinn-Erkennung, Validation)")
    print("  ✅ Display-Funktionen (OLED + Konsolen-Fallback)")
    print("  ✅ Keypad-Eingabe (Action-Mapping, Hardware-Mock)")
    print("  ✅ Spiel-Koordination (Event-Handling, Integration)")
    print("  ✅ Error-Handling und Edge-Cases")
    
    print("\n" + "=" * 80)
    
    return total_failures == 0 and total_errors == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
