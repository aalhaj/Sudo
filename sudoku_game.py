import pygame
import random
import math
import time
from enum import Enum
from typing import List, Tuple, Optional

class Difficulty(Enum):
    EASY = 0.3
    MEDIUM = 0.5
    HARD = 0.7
    EXPERT = 0.8

class SudokuGame:
    def __init__(self):
        pygame.init()
        self.WINDOW_WIDTH = 600
        self.WINDOW_HEIGHT = 700
        self.GRID_SIZE = 9
        self.CELL_SIZE = 60
        self.MARGIN = 30
        
        # Initialize display
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("سودوكو - لعبة الأرقام الذكية")
        
        # Colors (Professional color scheme)
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (128, 128, 128)
        self.LIGHT_GRAY = (240, 240, 240)
        self.BLUE = (52, 152, 219)
        self.DARK_BLUE = (41, 128, 185)
        self.GREEN = (46, 204, 113)
        self.RED = (231, 76, 60)
        self.ORANGE = (243, 156, 18)
        self.PURPLE = (155, 89, 182)
        
        # Fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        self.font_tiny = pygame.font.Font(None, 16)
        
        # Game state
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.solution = [[0 for _ in range(9)] for _ in range(9)]
        self.initial_board = [[0 for _ in range(9)] for _ in range(9)]
        self.selected_cell = None
        self.error_count = 0
        self.start_time = 0
        self.game_time = 0
        self.is_game_active = False
        self.difficulty = Difficulty.MEDIUM
        self.hints = 3
        self.notes_mode = False
        self.notes = [[[False for _ in range(9)] for _ in range(9)] for _ in range(9)]
        
        # Generate initial puzzle
        self.generate_new_puzzle()
        
    def is_valid_move(self, board, row, col, num):
        """Check if placing num at (row, col) is valid"""
        # Check row
        for x in range(9):
            if board[row][x] == num:
                return False
        
        # Check column
        for x in range(9):
            if board[x][col] == num:
                return False
        
        # Check 3x3 box
        start_row = row - row % 3
        start_col = col - col % 3
        for i in range(3):
            for j in range(3):
                if board[i + start_row][j + start_col] == num:
                    return False
        
        return True
    
    def solve_sudoku(self, board):
        """Solve sudoku using backtracking algorithm"""
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    for num in range(1, 10):
                        if self.is_valid_move(board, i, j, num):
                            board[i][j] = num
                            if self.solve_sudoku(board):
                                return True
                            board[i][j] = 0
                    return False
        return True
    
    def generate_complete_board(self):
        """Generate a complete valid sudoku board"""
        board = [[0 for _ in range(9)] for _ in range(9)]
        
        # Fill the diagonal 3x3 boxes first (they are independent)
        for box in range(0, 9, 3):
            nums = list(range(1, 10))
            random.shuffle(nums)
            for i in range(3):
                for j in range(3):
                    board[box + i][box + j] = nums.pop()
        
        # Solve the rest of the board
        self.solve_sudoku(board)
        return board
    
    def create_puzzle(self, difficulty):
        """Create a puzzle by removing cells from a complete board"""
        complete_board = self.generate_complete_board()
        puzzle = [row[:] for row in complete_board]
        
        # Calculate number of cells to remove based on difficulty
        cells_to_remove = int(81 * difficulty.value)
        
        # Remove cells randomly
        cells = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(cells)
        
        for i in range(cells_to_remove):
            row, col = cells[i]
            puzzle[row][col] = 0
        
        return puzzle, complete_board
    
    def generate_new_puzzle(self):
        """Generate a new puzzle and reset game state"""
        self.board, self.solution = self.create_puzzle(self.difficulty)
        self.initial_board = [row[:] for row in self.board]
        self.selected_cell = None
        self.error_count = 0
        self.start_time = time.time()
        self.is_game_active = True
        self.hints = 3
        self.notes = [[[False for _ in range(9)] for _ in range(9)] for _ in range(9)]
    
    def get_hint(self):
        """Get a hint for the selected cell"""
        if self.hints > 0 and self.selected_cell:
            row, col = self.selected_cell
            if self.board[row][col] == 0:
                self.board[row][col] = self.solution[row][col]
                self.hints -= 1
                return True
        return False
    
    def toggle_note(self, num):
        """Toggle note mode for a number"""
        if self.selected_cell and self.notes_mode:
            row, col = self.selected_cell
            if self.board[row][col] == 0:
                self.notes[row][col][num-1] = not self.notes[row][col][num-1]
    
    def check_progress(self):
        """Check game progress"""
        empty_cells = sum(row.count(0) for row in self.board)
        return empty_cells
    
    def is_game_won(self):
        """Check if the game is won"""
        return self.check_progress() == 0
    
    def handle_click(self, pos):
        """Handle mouse click events"""
        x, y = pos
        
        # Check if click is on the grid
        if self.MARGIN <= x < self.MARGIN + 9 * self.CELL_SIZE and \
           self.MARGIN <= y < self.MARGIN + 9 * self.CELL_SIZE:
            
            col = (x - self.MARGIN) // self.CELL_SIZE
            row = (y - self.MARGIN) // self.CELL_SIZE
            
            # Check if cell is not initial
            if self.initial_board[row][col] == 0:
                self.selected_cell = (row, col)
            else:
                self.selected_cell = None
        else:
            self.selected_cell = None
    
    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.selected_cell:
            return
        
        row, col = self.selected_cell
        
        # Number input (1-9)
        if pygame.K_1 <= key <= pygame.K_9:
            num = key - pygame.K_1 + 1
            if self.initial_board[row][col] == 0:  # Can only modify non-initial cells
                if self.notes_mode:
                    self.toggle_note(num)
                else:
                    # Check if move is valid
                    if self.solution[row][col] == num:
                        self.board[row][col] = num
                        # Clear notes for this cell
                        self.notes[row][col] = [False] * 9
                    else:
                        self.error_count += 1
        
        # Delete/Backspace
        elif key in (pygame.K_DELETE, pygame.K_BACKSPACE):
            if self.initial_board[row][col] == 0:
                self.board[row][col] = 0
                # Clear notes for this cell
                self.notes[row][col] = [False] * 9
        
        # Toggle notes mode
        elif key == pygame.K_n:
            self.notes_mode = not self.notes_mode
    
    def draw_grid(self):
        """Draw the sudoku grid"""
        # Draw grid lines
        for i in range(10):
            thickness = 3 if i % 3 == 0 else 1
            # Vertical lines
            x = self.MARGIN + i * self.CELL_SIZE
            pygame.draw.line(self.screen, self.BLACK, 
                           (x, self.MARGIN), 
                           (x, self.MARGIN + 9 * self.CELL_SIZE), thickness)
            
            # Horizontal lines
            y = self.MARGIN + i * self.CELL_SIZE
            pygame.draw.line(self.screen, self.BLACK, 
                           (self.MARGIN, y), 
                           (self.MARGIN + 9 * self.CELL_SIZE, y), thickness)
    
    def draw_numbers(self):
        """Draw numbers on the grid"""
        for row in range(9):
            for col in range(9):
                x = self.MARGIN + col * self.CELL_SIZE + self.CELL_SIZE // 2
                y = self.MARGIN + row * self.CELL_SIZE + self.CELL_SIZE // 2
                
                if self.board[row][col] != 0:
                    # Determine color based on cell type
                    if self.initial_board[row][col] != 0:
                        color = self.BLACK  # Initial numbers
                    else:
                        color = self.BLUE  # Player numbers
                    
                    text = self.font_large.render(str(self.board[row][col]), True, color)
                    text_rect = text.get_rect(center=(x, y))
                    self.screen.blit(text, text_rect)
                
                # Draw notes
                elif self.notes_mode or any(self.notes[row][col]):
                    for num in range(9):
                        if self.notes[row][col][num]:
                            note_x = self.MARGIN + col * self.CELL_SIZE + (num % 3) * 20 + 6
                            note_y = self.MARGIN + row * self.CELL_SIZE + (num // 3) * 20 + 6
                            note_text = self.font_tiny.render(str(num + 1), True, self.GRAY)
                            self.screen.blit(note_text, (note_x, note_y))
    
    def draw_selection(self):
        """Draw selection highlight"""
        if self.selected_cell:
            row, col = self.selected_cell
            x = self.MARGIN + col * self.CELL_SIZE
            y = self.MARGIN + row * self.CELL_SIZE
            
            # Draw selection rectangle
            pygame.draw.rect(self.screen, self.ORANGE, 
                           (x, y, self.CELL_SIZE, self.CELL_SIZE), 3)
    
    def draw_ui(self):
        """Draw UI elements"""
        # Draw title
        title = self.font_medium.render("سودوكو", True, self.DARK_BLUE)
        title_rect = title.get_rect(center=(self.WINDOW_WIDTH // 2, 25))
        self.screen.blit(title, title_rect)
        
        # Draw timer
        if self.is_game_active:
            self.game_time = time.time() - self.start_time
            minutes = int(self.game_time // 60)
            seconds = int(self.game_time % 60)
            timer_text = f"الوقت: {minutes:02d}:{seconds:02d}"
        else:
            timer_text = "الوقت: 00:00"
        
        timer_surface = self.font_small.render(timer_text, True, self.BLACK)
        self.screen.blit(timer_surface, (self.MARGIN, self.MARGIN + 9 * self.CELL_SIZE + 10))
        
        # Draw error count
        error_text = f"الأخطاء: {self.error_count}"
        error_surface = self.font_small.render(error_text, True, self.RED)
        self.screen.blit(error_surface, (self.MARGIN + 150, self.MARGIN + 9 * self.CELL_SIZE + 10))
        
        # Draw hints
        hints_text = f"تلميحات: {self.hints}"
        hints_surface = self.font_small.render(hints_text, True, self.ORANGE)
        self.screen.blit(hints_surface, (self.MARGIN + 300, self.MARGIN + 9 * self.CELL_SIZE + 10))
        
        # Draw progress
        remaining = self.check_progress()
        progress_text = f"متبقي: {remaining} خلية"
        progress_surface = self.font_small.render(progress_text, True, self.GREEN)
        self.screen.blit(progress_surface, (self.MARGIN + 450, self.MARGIN + 9 * self.CELL_SIZE + 10))
        
        # Draw notes mode indicator
        if self.notes_mode:
            notes_text = "وضع الملاحظات: مفعّل"
            notes_color = self.PURPLE
        else:
            notes_text = "وضع الملاحظات: معطل"
            notes_color = self.GRAY
        
        notes_surface = self.font_small.render(notes_text, True, notes_color)
        self.screen.blit(notes_surface, (self.MARGIN, self.MARGIN + 9 * self.CELL_SIZE + 40))
        
        # Draw buttons
        self.draw_buttons()
    
    def draw_buttons(self):
        """Draw control buttons"""
        # New Game button
        new_game_rect = pygame.Rect(50, 620, 100, 40)
        pygame.draw.rect(self.screen, self.GREEN, new_game_rect)
        new_game_text = self.font_small.render("لعبة جديدة", True, self.WHITE)
        text_rect = new_game_text.get_rect(center=new_game_rect.center)
        self.screen.blit(new_game_text, text_rect)
        
        # Solve button
        solve_rect = pygame.Rect(170, 620, 100, 40)
        pygame.draw.rect(self.screen, self.BLUE, solve_rect)
        solve_text = self.font_small.render("حل تلقائي", True, self.WHITE)
        text_rect = solve_text.get_rect(center=solve_rect.center)
        self.screen.blit(solve_text, text_rect)
        
        # Reset button
        reset_rect = pygame.Rect(290, 620, 100, 40)
        pygame.draw.rect(self.screen, self.ORANGE, reset_rect)
        reset_text = self.font_small.render("إعادة تعيين", True, self.WHITE)
        text_rect = reset_text.get_rect(center=reset_rect.center)
        self.screen.blit(reset_text, text_rect)
        
        # Hint button
        hint_rect = pygame.Rect(410, 620, 100, 40)
        pygame.draw.rect(self.screen, self.PURPLE, hint_rect)
        hint_text = self.font_small.render("تلميح", True, self.WHITE)
        text_rect = hint_text.get_rect(center=hint_rect.center)
        self.screen.blit(hint_text, text_rect)
        
        return {
            'new_game': new_game_rect,
            'solve': solve_rect,
            'reset': reset_rect,
            'hint': hint_rect
        }
    
    def handle_button_click(self, pos, buttons):
        """Handle button clicks"""
        for action, rect in buttons.items():
            if rect.collidepoint(pos):
                if action == 'new_game':
                    self.generate_new_puzzle()
                elif action == 'solve':
                    self.board = [row[:] for row in self.solution]
                    self.is_game_active = False
                elif action == 'reset':
                    self.board = [row[:] for row in self.initial_board]
                    self.error_count = 0
                    self.start_time = time.time()
                    self.is_game_active = True
                    self.hints = 3
                    self.notes = [[[False for _ in range(9)] for _ in range(9)] for _ in range(9)]
                elif action == 'hint':
                    self.get_hint()
    
    def run(self):
        """Main game loop"""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)
                        buttons = self.draw_buttons()
                        self.handle_button_click(event.pos, buttons)
                elif event.type == pygame.KEYDOWN:
                    self.handle_key(event.key)
            
            # Clear screen
            self.screen.fill(self.LIGHT_GRAY)
            
            # Draw everything
            self.draw_grid()
            self.draw_numbers()
            self.draw_selection()
            self.draw_ui()
            
            # Check for win
            if self.is_game_won() and self.is_game_active:
                self.is_game_active = False
                win_text = self.font_medium.render("تهانينا! لقد فزت!", True, self.GREEN)
                win_rect = win_text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2))
                self.screen.blit(win_text, win_rect)
            
            # Update display
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    game = SudokuGame()
    game.run()