board = [["*" for _ in range(3)] for _ in range(3)]
current_player = 0 # Player 0 : X - Player 1 : O

from gpiozero import DigitalOutputDevice, Button
from time import sleep
from display import create_display
import random
import sys

row_pins = [16, 20, 21, 5]
col_pins = [6, 13, 19, 26]

rows = [DigitalOutputDevice(pin) for pin in row_pins]
cols = [Button(pin, pull_up=False) for pin in col_pins]

display = create_display()
display.show_welcome()
sleep(2)
if display:
    display.show_game(board, "X", "Spieler X ist dran")

def read_keypad():
    for i, row in enumerate(rows):
        row.on()
        for j, col in enumerate(cols):
            if col.is_pressed:
                row.off()
                return (i,j)

        row.off()
    return None

def check_winner(board):
    global winning_line
    
    # Check rows
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != "*":
            winning_line = [(i, 0), (i, 1), (i, 2)]
            return board[i][0]
    
    # Check columns
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != "*":
            winning_line = [(0, col), (1, col), (2, col)]
            return board[0][col]
    
    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] != "*":
        winning_line = [(0, 0), (1, 1), (2, 2)]
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != "*":
        winning_line = [(0, 2), (1, 1), (2, 0)]
        return board[0][2]
    
    return None

def is_board_full(board):
    for row in board:
        if "*" in row:
            return False
    return True

def print_board(board):
    print("\nCurrent board:")
    for row in board:
        print(" ".join(row))
    print()

def reset_game():
    global board, current_player, game_over, winner, winning_line
    board = [["*" for _ in range(3)] for _ in range(3)]
    current_player = 0
    game_over = False
    winner = None
    winning_line = []

def make_random_move():
    global board, current_player
    if game_over:
        return False
    
    empty_positions = []
    for i in range(3):
        for j in range(3):
            if board[i][j] == "*":
                empty_positions.append((i, j))
    
    if empty_positions:
        row, col = random.choice(empty_positions)
        board[row][col] = "X" if current_player == 0 else "O"
        return True
    return False

last_key_pressed = None

game_over = False
winner = None
winning_line = []

while True:
    key = read_keypad()
    if key and key != last_key_pressed:
        last_key_pressed = key
        
        # Special buttons in row 3
        if key[0] == 3:
            if key[1] == 0:  # Column 0 Row 3: Reset game
                reset_game()
                status = f"Spieler {'X' if current_player == 0 else 'O'} ist dran"
                if display:
                    display.show_game(board, "X" if current_player == 0 else "O", status)
            elif key[1] == 2:  # Column 2 Row 3: Random move
                if make_random_move():
                    winner = check_winner(board)
                    if winner:
                        game_over = True
                        status = f"Spieler {winner} gewinnt!"
                        if display:
                            display.show_game_with_animation(board, "X" if current_player == 0 else "O", status, winning_line)
                    elif is_board_full(board):
                        game_over = True
                        status = "Unentschieden!"
                    else:
                        current_player = 1 - current_player
                        status = f"Spieler {'X' if current_player == 0 else 'O'} ist dran"
                    
                    if display and not winner:
                        display.show_game(board, "X" if current_player == 0 else "O", status)
            elif key[1] == 3:  # Column 3 Row 3: Exit program
                sys.exit()
        
        # Normal game moves
        elif key and not game_over and key[0] < 3 and key[1] < 3:
            row, col = key
            
            # Check if position is empty
            if board[row][col] == "*":
                # Place X or O
                board[row][col] = "X" if current_player == 0 else "O"
                
                # Check for winner
                winner = check_winner(board)
                if winner:
                    game_over = True
                    status = f"Spieler {winner} gewinnt!"
                    if display:
                        display.show_game_with_animation(board, "X" if current_player == 0 else "O", status, winning_line)
                elif is_board_full(board):
                    game_over = True
                    status = "Unentschieden!"
                    if display:
                        display.show_game(board, "X" if current_player == 0 else "O", status)
                else:
                    # Switch player
                    current_player = 1 - current_player
                    status = f"Spieler {'X' if current_player == 0 else 'O'} ist dran"
                    if display:
                        display.show_game(board, "X" if current_player == 0 else "O", status)
                    
    sleep(0.1)
        

