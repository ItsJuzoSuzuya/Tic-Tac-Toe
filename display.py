"""
Display Modul für Tic-Tac-Toe
Unterstützt OLED und Konsole
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    from luma.core.interface.serial import i2c
    from luma.oled.device import ssd1306
    OLED_AVAILABLE = True
except ImportError:
    OLED_AVAILABLE = False

from typing import List

class OLEDDisplay:
    def __init__(self):
        self.serial = i2c(port=1, address=0x3c)
        self.device = ssd1306(self.serial, width=128, height=64)
        
        try:
            self.font_small = ImageFont.truetype("DejaVuSans.ttf", 10)
            self.font_medium = ImageFont.truetype("DejaVuSans-Bold.ttf", 12)
            self.font_large = ImageFont.truetype("DejaVuSans-Bold.ttf", 16)
        except:
            self.font_small = ImageFont.load_default()
            self.font_medium = ImageFont.load_default()
            self.font_large = ImageFont.load_default()
    
    def show_welcome(self):
        """Zeigt Willkommensnachricht"""
        with Image.new('1', (128, 64)) as img:
            draw = ImageDraw.Draw(img)
            draw.rectangle([(0, 0), (128, 16)], fill=1)
            draw.text((20, 2), "Tic-Tac-Toe", font=self.font_small, fill=0)
            
            instructions = ["1-9: Feld waehlen", "*: Neues Spiel", "#: Zufallszug"]
            for i, text in enumerate(instructions):
                draw.text((5, 25 + i * 12), text, font=self.font_small, fill=1)
                
            self.device.display(img)
    
    def show_game(self, board: List[List[str]], current_player: str, game_status: str):
        """Zeigt das Spiel"""
        with Image.new('1', (128, 64)) as img:
            draw = ImageDraw.Draw(img)
            
            # Header
            draw.rectangle([(0, 0), (128, 16)], fill=1)
            text_bbox = draw.textbbox((0, 0), game_status, font=self.font_small)
            text_width = text_bbox[2] - text_bbox[0]
            draw.text(((128 - text_width) // 2, 2), game_status, font=self.font_small, fill=0)
            
            # Grid
            grid_size = 45
            cell_size = 15
            start_x = (128 - grid_size) // 2
            start_y = 18
            
            # Grid-Linien
            for i in range(1, 3):
                x = start_x + i * cell_size
                draw.line([(x, start_y), (x, start_y + grid_size)], fill=1)
                y = start_y + i * cell_size
                draw.line([(start_x, y), (start_x + grid_size, y)], fill=1)
            
            # X und O
            for i, row in enumerate(board):
                for j, cell in enumerate(row):
                    if board[i][j] != '*':
                        cell_x = start_x + j * cell_size
                        cell_y = start_y + i * cell_size
                        
                        # Text-Bounding-Box für Zentrierung berechnen
                        text_bbox = draw.textbbox((0, 0), cell, font=self.font_medium)
                        text_width = text_bbox[2] - text_bbox[0] 
                        text_height = text_bbox[3] - text_bbox[1] 
                        
                        # Zentriert in der Zelle platzieren
                        x = cell_x + (cell_size - text_width) / 2
                        y = cell_y + (cell_size - text_height) / 2 - text_bbox[1]
                        draw.text((x, y), cell, font=self.font_medium, fill=1)
            
            self.device.display(img)
    
    def show_game_with_animation(self, board: List[List[str]], current_player: str, game_status: str, winning_line: List):
        """Zeigt das Spiel mit Gewinner-Animation"""
        # Erst das normale Spiel anzeigen
        self.show_game(board, current_player, game_status)
        
        if winning_line:
            # Animation: Linie durch die Gewinn-Symbole zeichnen
            for frame in range(5):  # 5 Frames Animation
                with Image.new('1', (128, 64)) as img:
                    draw = ImageDraw.Draw(img)
                    
                    # Header
                    draw.rectangle([(0, 0), (128, 16)], fill=1)
                    text_bbox = draw.textbbox((0, 0), game_status, font=self.font_small)
                    text_width = text_bbox[2] - text_bbox[0]
                    draw.text(((128 - text_width) // 2, 2), game_status, font=self.font_small, fill=0)
                    
                    # Grid
                    grid_size = 45
                    cell_size = 15
                    start_x = (128 - grid_size) // 2
                    start_y = 18
                    
                    # Grid-Linien
                    for i in range(1, 3):
                        x = start_x + i * cell_size
                        draw.line([(x, start_y), (x, start_y + grid_size)], fill=1)
                        y = start_y + i * cell_size
                        draw.line([(start_x, y), (start_x + grid_size, y)], fill=1)
                    
                    # X und O
                    for i, row in enumerate(board):
                        for j, cell in enumerate(row):
                            if board[i][j] != '*':
                                cell_x = start_x + j * cell_size
                                cell_y = start_y + i * cell_size
                                
                                text_bbox = draw.textbbox((0, 0), cell, font=self.font_medium)
                                text_width = text_bbox[2] - text_bbox[0] 
                                text_height = text_bbox[3] - text_bbox[1] 
                                
                                x = cell_x + (cell_size - text_width) / 2
                                y = cell_y + (cell_size - text_height) / 2 - text_bbox[1]
                                
                                # Blinken der Gewinn-Symbole
                                if (i, j) in winning_line and frame % 2 == 0:
                                    draw.text((x, y), cell, font=self.font_medium, fill=1)
                                elif (i, j) not in winning_line:
                                    draw.text((x, y), cell, font=self.font_medium, fill=1)
                    
                    # Linie durch die Gewinn-Symbole zeichnen
                    if len(winning_line) >= 2:
                        start_pos = winning_line[0]
                        end_pos = winning_line[-1]
                        
                        start_pixel_x = start_x + start_pos[1] * cell_size + cell_size // 2
                        start_pixel_y = start_y + start_pos[0] * cell_size + cell_size // 2
                        end_pixel_x = start_x + end_pos[1] * cell_size + cell_size // 2
                        end_pixel_y = start_y + end_pos[0] * cell_size + cell_size // 2
                        
                        draw.line([(start_pixel_x, start_pixel_y), (end_pixel_x, end_pixel_y)], fill=1, width=2)
                    
                    self.device.display(img)
                    
                from time import sleep
                sleep(0.3)


def create_display():
    """Factory-Funktion für Display"""
    if OLED_AVAILABLE:
        try:
            return OLEDDisplay()
        except Exception:
            return None

    return None
