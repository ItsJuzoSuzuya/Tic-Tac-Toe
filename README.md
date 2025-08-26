# Tic-Tac-Toe Raspberry Pi Spiel

Ein vollständig funktionales Tic-Tac-Toe Spiel für Raspberry Pi mit OLED Display und Keypad-Steuerung.

## Features

- **Vollständige Spiellogik**: Klassisches 3x3 Tic-Tac-Toe mit Gewinn- und Unentschieden-Erkennung
- **OLED Display Support**: Grafische Darstellung auf 128x64 OLED Display (SSD1306)
- **Keypad-Eingabe**: 4x4 Matrix-Keypad für Spielsteuerung
- **Gewinner-Animation**: Blinkende Animation der Gewinnerlinie
- **Zufallszüge**: Computer kann zufällige Züge machen
- **Fallback-Modus**: Funktioniert auch ohne Hardware (Konsolen-Output)

## Hardware-Anforderungen

### OLED Display (SSD1306)
- **Auflösung**: 128x64 Pixel
- **Interface**: I2C
- **Standard-Adresse**: 0x3C
- **Port**: 1

### Matrix Keypad (4x4)
**Standard Pin-Belegung:**
- **Reihen**: GPIO 16, 20, 21, 5
- **Spalten**: GPIO 6, 13, 19, 26

**Keypad Layout:**
```
[1] [2] [3] [A]
[4] [5] [6] [B] 
[7] [8] [9] [C]
[*] [0] [#] [D]
```

## Installation

### System-Abhängigkeiten
```bash
sudo apt update
sudo apt install python3-pip python3-dev i2c-tools
sudo pip3 install pillow luma.oled gpiozero
```

### I2C aktivieren
```bash
sudo raspi-config
# Interface Options -> I2C -> Enable
```

### Repository klonen
```bash
git clone <repository-url>
cd tic-tac-toe
```

## Verwendung

### Spiel starten
```bash
python3 main.py
```

### Steuerung

**Spielzüge (Keypad-Positionen 1-9):**
```
[1] [2] [3]    entspricht    [0,0] [0,1] [0,2]
[4] [5] [6]        →          [1,0] [1,1] [1,2]
[7] [8] [9]                   [2,0] [2,1] [2,2]
```

**Spezialfunktionen:**
- **[*]**: Neues Spiel starten
- **[#]**: Zufälliger Zug
- **[D]**: Programm beenden

### Spielablauf
1. Spieler X beginnt
2. Wähle eine Position (1-9) auf dem Keypad
3. Spieler wechseln automatisch
4. Gewinner wird mit blinkender Animation angezeigt
5. Neues Spiel mit [*] starten

Optional: Zufälliger Computer Zug mit [#]-Taste

## Projektstruktur

```
tic-tac-toe/
├── main.py              # Haupteinstiegspunkt
├── game.py              # Spiel-Koordinator
├── game_logic.py        # Kernlogik und Regeln
├── display.py           # OLED Display-Verwaltung
├── keypad_input.py      # Keypad-Eingabe mit Entprellung
├── tests.py             # Umfassende Tests
└── README.md           # Diese Datei
```

### Module-Übersicht

#### `game_logic.py`
- **GameLogic**: Kernklasse für Spiellogik
- Methoden: `make_move()`, `make_random_move()`, `reset_game()`, `get_status_message()`
- Gewinn-Erkennung und Unentschieden-Prüfung
- Validierung von Spielzügen

#### `display.py`
- **OLEDDisplay**: OLED-Anzeige mit PIL/Luma
- Methoden: `show_welcome()`, `show_game()`, `show_game_with_animation()`
- Automatischer Fallback auf Konsolen-Ausgabe
- Gewinner-Animation mit blinkenden Symbolen

#### `keypad_input.py`
- **KeypadInput**: Matrix-Keypad mit GPIO
- Hardware-Entprellung und Action-Mapping
- Enum `InputAction` für Aktionstypen
- Konfigurierbare Pin-Belegung

#### `game.py`
- **TicTacToeGame**: Hauptkoordinator
- Event-Loop mit Input-Handling
- Integration aller Module
- Fehlerbehandlung und Cleanup

## Konfiguration

### Display-Einstellungen
```python
# In display.py anpassen
WIDTH = 128
HEIGHT = 64
GRID_SIZE = 45
ANIMATION_DELAY = 0.2
```

### Keypad-Pins anpassen
```python
# In keypad_input.py oder bei Initialisierung
keypad = KeypadInput(
    row_pins=[16, 20, 21, 5],
    col_pins=[6, 13, 19, 26]
)
```

## Tests

Umfassende Test-Suite mit allen wichtigen Funktionen:

```bash
python3 tests.py
```

**Test-Abdeckung:**
- Spiellogik-Tests (Züge, Gewinn-Szenarien, Validation)
- Display-Tests (Fallback-Verhalten)
- Input-Tests (Action-Mapping, Mock-Hardware)
- Integration-Tests

## Fehlerbehebung

### Häufige Probleme

**OLED Display wird nicht erkannt:**
```bash
sudo i2cdetect -y 1
# Sollte Adresse 0x3c zeigen
```

**Permission-Fehler bei GPIO:**
```bash
sudo usermod -a -G gpio $USER
# Neu anmelden erforderlich
```

**Import-Fehler:**
```bash
pip3 install --user pillow luma.oled gpiozero
```

### Hardware-unabhängiger Betrieb
Das Spiel funktioniert auch ohne Hardware:
- OLED → Konsolen-Ausgabe
- Keypad → (würde Hardware-Simulation benötigen)

## Entwicklung

### Code-Style
- Deutsche Kommentare und Variablennamen
- Type Hints für alle Funktionen
- Umfassende Dokumentation
- Modulare Architektur
