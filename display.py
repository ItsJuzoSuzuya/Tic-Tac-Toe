"""
Display Module für Tic-Tac-Toe
OLED Display Verwaltung
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    from luma.core.interface.serial import i2c
    from luma.oled.device import ssd1306
    OLED_AVAILABLE = True
except ImportError:
    OLED_AVAILABLE = False

from typing import List, Optional, Tuple
from time import sleep

class OLEDDisplay:
    """OLED Display Klasse für Tic-Tac-Toe"""
    
    # Display Konstanten
    WIDTH = 128
    HEIGHT = 64
    GRID_SIZE = 45
    CELL_SIZE = 15
    ANIMATION_FRAMES = 6
    ANIMATION_DELAY = 0.2
    
    def __init__(self, port: int = 1, address: int = 0x3c):
        """Initialisiert das OLED Display"""
        self.serial = i2c(port=port, address=address)
        self.device = ssd1306(self.serial, width=self.WIDTH, height=self.HEIGHT)
        self._load_fonts()
        
    def _load_fonts(self) -> None:
        """Lädt die Schriftarten"""
        try:
            self.font_small = ImageFont.truetype("DejaVuSans.ttf", 10)
            self.font_medium = ImageFont.truetype("DejaVuSans-Bold.ttf", 12)
            self.font_large = ImageFont.truetype("DejaVuSans-Bold.ttf", 16)
        except (OSError, IOError):
            self.font_small = ImageFont.load_default()
            self.font_medium = ImageFont.load_default()
            self.font_large = ImageFont.load_default()
    
    def show_welcome(self) -> None:
        """Zeigt Willkommensnachricht"""
        with Image.new('1', (self.WIDTH, self.HEIGHT)) as img:
            draw = ImageDraw.Draw(img)
            
            # Header mit Titel
            draw.rectangle([(0, 0), (self.WIDTH, 16)], fill=1)
            self._draw_centered_text(draw, "Tic-Tac-Toe", 2, self.font_small, fill=0)
            
            # Anweisungen
            instructions = [
                "[1-9]: Feld wählen",
                "[*]: Neues Spiel", 
                "[#]: Zufallszug",
                "[D]: Programm beenden"
            ]
            
            for i, text in enumerate(instructions):
                draw.text((5, 20 + i * 10), text, font=self.font_small, fill=1)
                
            self.device.display(img)
    
    def show_game(self, board: List[List[str]], game_status: str) -> None:
        """Zeigt das aktuelle Spiel"""
        with Image.new('1', (self.WIDTH, self.HEIGHT)) as img:
            draw = ImageDraw.Draw(img)
            
            # Header mit Status
            self._draw_header(draw, game_status)
            
            # Spiel-Grid zeichnen
            self._draw_game_grid(draw, board)
            
            self.device.display(img)
    
    def show_game_with_animation(self, board: List[List[str]], 
                               game_status: str, winning_line: List[Tuple[int, int]]) -> None:
        """Zeigt das Spiel mit Gewinner-Animation"""
        # Erst das normale Spiel anzeigen
        self.show_game(board, game_status)
        
        if winning_line:
            self._animate_winning_line(board, game_status, winning_line)
    
    def _animate_winning_line(self, board: List[List[str]], game_status: str, 
                            winning_line: List[Tuple[int, int]]) -> None:
        """Animiert die Gewinnerlinie"""
        for frame in range(self.ANIMATION_FRAMES):
            with Image.new('1', (self.WIDTH, self.HEIGHT)) as img:
                draw = ImageDraw.Draw(img)
                
                # Header zeichnen
                self._draw_header(draw, game_status)
                
                # Grid mit blinkenden Gewinnersymbolen
                self._draw_animated_grid(draw, board, winning_line, frame)
                
                # Gewinnerlinie zeichnen
                self._draw_winning_line(draw, winning_line)
                
                self.device.display(img)
                sleep(self.ANIMATION_DELAY)
    
    def _draw_header(self, draw: ImageDraw.Draw, status: str) -> None:
        """Zeichnet den Header mit Status"""
        draw.rectangle([(0, 0), (self.WIDTH, 16)], fill=1)
        self._draw_centered_text(draw, status, 2, self.font_small, fill=0)
    
    def _draw_centered_text(self, draw: ImageDraw.Draw, text: str, y: int, 
                          font: ImageFont.ImageFont, fill: int = 1) -> None:
        """Zeichnet zentrierten Text"""
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        x = (self.WIDTH - text_width) // 2
        draw.text((x, y), text, font=font, fill=fill)
    
    def _draw_game_grid(self, draw: ImageDraw.Draw, board: List[List[str]]) -> None:
        """Zeichnet das Spielfeld"""
        start_x = (self.WIDTH - self.GRID_SIZE) // 2
        start_y = 18
        
        # Grid-Linien zeichnen
        self._draw_grid_lines(draw, start_x, start_y)
        
        # X und O zeichnen
        self._draw_game_symbols(draw, board, start_x, start_y)
    
    def _draw_animated_grid(self, draw: ImageDraw.Draw, board: List[List[str]], 
                          winning_line: List[Tuple[int, int]], frame: int) -> None:
        """Zeichnet das Spielfeld mit Animation"""
        start_x = (self.WIDTH - self.GRID_SIZE) // 2
        start_y = 18
        
        # Grid-Linien zeichnen
        self._draw_grid_lines(draw, start_x, start_y)
        
        # Symbole mit Blinken für Gewinner zeichnen
        for i, row in enumerate(board):
            for j, cell in enumerate(row):
                if cell != '*':
                    # Blinken der Gewinn-Symbole
                    if (i, j) in winning_line and frame % 2 == 0:
                        continue  # Symbol nicht zeichnen (blinkt)
                    
                    self._draw_symbol_at_position(draw, cell, i, j, start_x, start_y)
    
    def _draw_grid_lines(self, draw: ImageDraw.Draw, start_x: int, start_y: int) -> None:
        """Zeichnet die Gitterlinien"""
        for i in range(1, 3):
            # Vertikale Linien
            x = start_x + i * self.CELL_SIZE
            draw.line([(x, start_y), (x, start_y + self.GRID_SIZE)], fill=1)
            
            # Horizontale Linien
            y = start_y + i * self.CELL_SIZE
            draw.line([(start_x, y), (start_x + self.GRID_SIZE, y)], fill=1)
    
    def _draw_game_symbols(self, draw: ImageDraw.Draw, board: List[List[str]], 
                         start_x: int, start_y: int) -> None:
        """Zeichnet alle Spielsymbole"""
        for i, row in enumerate(board):
            for j, cell in enumerate(row):
                if cell != '*':
                    self._draw_symbol_at_position(draw, cell, i, j, start_x, start_y)
    
    def _draw_symbol_at_position(self, draw: ImageDraw.Draw, symbol: str, 
                               row: int, col: int, start_x: int, start_y: int) -> None:
        """Zeichnet ein Symbol an der angegebenen Position"""
        cell_x = start_x + col * self.CELL_SIZE
        cell_y = start_y + row * self.CELL_SIZE
        
        # Text-Bounding-Box für Zentrierung berechnen
        text_bbox = draw.textbbox((0, 0), symbol, font=self.font_medium)
        text_width = text_bbox[2] - text_bbox[0] 
        text_height = text_bbox[3] - text_bbox[1] 
        
        # Zentriert in der Zelle platzieren
        x = cell_x + (self.CELL_SIZE - text_width) // 2
        y = cell_y + (self.CELL_SIZE - text_height) // 2 - text_bbox[1]
        draw.text((x, y), symbol, font=self.font_medium, fill=1)
    
    def _draw_winning_line(self, draw: ImageDraw.Draw, winning_line: List[Tuple[int, int]]) -> None:
        """Zeichnet die Gewinnerlinie"""
        if len(winning_line) < 2:
            return
            
        start_x = (self.WIDTH - self.GRID_SIZE) // 2
        start_y = 18
        
        start_pos = winning_line[0]
        end_pos = winning_line[-1]
        
        start_pixel_x = start_x + start_pos[1] * self.CELL_SIZE + self.CELL_SIZE // 2
        start_pixel_y = start_y + start_pos[0] * self.CELL_SIZE + self.CELL_SIZE // 2
        end_pixel_x = start_x + end_pos[1] * self.CELL_SIZE + self.CELL_SIZE // 2
        end_pixel_y = start_y + end_pos[0] * self.CELL_SIZE + self.CELL_SIZE // 2
        
        draw.line([(start_pixel_x, start_pixel_y), (end_pixel_x, end_pixel_y)], 
                 fill=1, width=2)


def create_display() -> Optional[OLEDDisplay]:
    """Factory-Funktion für Display-Erstellung"""
    if not OLED_AVAILABLE:
        return None
        
    try:
        return OLEDDisplay()
    except Exception as e:
        print(f"Fehler beim Erstellen des OLED Displays: {e}")
        return None
