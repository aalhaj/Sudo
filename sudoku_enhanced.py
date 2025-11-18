import pygame
import random
import math
import time
from enum import Enum
from typing import List, Tuple, Optional
import json
import os

class Difficulty(Enum):
    EASY = 0.3
    MEDIUM = 0.5
    HARD = 0.7
    EXPERT = 0.8

class Theme(Enum):
    LIGHT = "light"
    DARK = "dark"
    BLUE = "blue"

class SudokuGame:
    def __init__(self):
        pygame.init()
        self.WINDOW_WIDTH = 800  # Increased width for sidebar
        self.WINDOW_HEIGHT = 700
        self.GRID_SIZE = 9
        self.CELL_SIZE = 60
        self.MARGIN = 30
        
        # Initialize display
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("سودوكو الاحترافية - Professional Sudoku")
        
        # Color themes
        self.themes = {
            Theme.LIGHT: {
                'bg': (240, 240, 240),
                'grid': (0, 0, 0),
                'text': (0, 0, 0),
                'initial': (0, 0, 0),
                'player': (52, 152, 219),
                'selected': (243, 156, 18),
                'error': (231, 76, 60),
                'success': (46, 204, 113),
                'notes': (128, 128, 128),
                'button': (52, 152, 219),
                'button_hover': (41, 128, 185)
            },
            Theme.DARK: {
                'bg': (40, 40, 40),
                'grid': (255, 255, 255),
                'text': (255, 255, 255),
                'initial': (255, 255, 255),
                'player': (52, 152, 219),
                'selected': (243, 156, 18),
                'error': (231, 76, 60),
                'success': (46, 204, 113),
                'notes': (170, 170, 170),
                'button': (52, 152, 219),
                'button_hover': (41, 128, 185)
            },
            Theme.BLUE: {
                'bg': (230, 240, 250),
                'grid': (25, 25, 112),
                'text': (25, 25, 112),
                'initial': (25, 25, 112),
                'player': (30, 144, 255),
                'selected': (255, 165, 0),
                'error': (220, 20, 60),
                'success': (34, 139, 34),
                'notes': (100, 100, 150),
                'button': (30, 144, 255),
                'button_hover': (0, 100, 200)
            }
        }
        
        self.current_theme = Theme.LIGHT
        self.colors = self.themes[self.current_theme]
        
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
        
        # Statistics
        self.stats = self.load_stats()
        self.current_session_stats = {
            'games_played': 0,
            'games_won': 0,
            'total_time': 0,
            'total_errors': 0
        }
        
        # Animation
        self.animation_time = 0
        self.win_animation = False
        
        # Generate initial puzzle
        self.generate_new_puzzle()
        
    def load_stats(self):
        """Load game statistics"""
        try:
            if os.path.exists('sudoku_stats.json'):
                with open('sudoku_stats.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {
            'games_played': 0,
            'games_won': 0,
            'total_time': 0,
            'total_errors': 0,
            'best_times': {
                'easy': float('inf'),
                'medium': float('inf'),
                'hard': float('inf'),
                'expert': float('inf')
            }
        }
    
    def save_stats(self):
        """Save game statistics"""
        try:
            with open('sudoku_stats.json', 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
        except:
            pass
    
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
                    nums = list(range(1, 10))
                    random.shuffle(nums)
                    for num in nums:
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
        
        # Fill the diagonal 3x3 boxes first
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
        
        cells_to_remove = int(81 * difficulty.value)
        cells = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(cells)
        
        removed_count = 0
        for row, col in cells:
            if removed_count >= cells_to_remove:
                break
            
            # Remove the cell
            temp = puzzle[row][col]
            puzzle[row][col] = 0
            
            # Check if puzzle still has unique solution
            test_board = [row[:] for row in puzzle]
            solutions = self.count_solutions(test_board)
            
            if solutions == 1:
                removed_count += 1
            else:
                # Put the number back if multiple solutions
                puzzle[row][col] = temp
        
        return puzzle, complete_board
    
    def count_solutions(self, board):
        """Count number of solutions for a puzzle"""
        count = [0]
        
        def solve_count(board, count):
            if count[0] > 1:  # Early termination if multiple solutions found
                return
                
            for i in range(9):
                for j in range(9):
                    if board[i][j] == 0:
                        for num in range(1, 10):
                            if self.is_valid_move(board, i, j, num):
                                board[i][j] = num
                                solve_count(board, count)
                                board[i][j] = 0
                        return
            count[0] += 1
        
        solve_count(board, count)
        return count[0]
    
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
        self.win_animation = False
        self.current_session_stats['games_played'] += 1
    
    def get_hint(self):
        """Get a hint for the selected cell"""
        if self.hints > 0 and self.selected_cell:
            row, col = self.selected_cell
            if self.board[row][col] == 0:
                self.board[row][col] = self.solution[row][col]
                self.hints -= 1
                # Clear notes for this cell
                self.notes[row][col] = [False] * 9
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
            if self.initial_board[row][col] == 0:
                if self.notes_mode:
                    self.toggle_note(num)
                else:
                    if self.solution[row][col] == num:
                        self.board[row][col] = num
                        self.notes[row][col] = [False] * 9
                        # Check for win
                        if self.is_game_won():
                            self.win_animation = True
                            self.is_game_active = False
                            self.current_session_stats['games_won'] += 1
                            self.update_best_time()
                    else:
                        self.error_count += 1
                        self.current_session_stats['total_errors'] += 1
        
        # Delete/Backspace
        elif key in (pygame.K_DELETE, pygame.K_BACKSPACE):
            if self.initial_board[row][col] == 0:
                self.board[row][col] = 0
                self.notes[row][col] = [False] * 9
        
        # Toggle notes mode
        elif key == pygame.K_n:
            self.notes_mode = not self.notes_mode
        
        # Theme switching
        elif key == pygame.K_t:
            self.switch_theme()
    
    def switch_theme(self):
        """Switch between themes"""
        themes = list(Theme)
        current_index = themes.index(self.current_theme)
        next_index = (current_index + 1) % len(themes)
        self.current_theme = themes[next_index]
        self.colors = self.themes[self.current_theme]
    
    def update_best_time(self):
        """Update best time for current difficulty"""
        if self.is_game_won():
            difficulty_name = self.difficulty.name.lower()
            current_time = self.game_time
            if current_time < self.stats['best_times'][difficulty_name]:
                self.stats['best_times'][difficulty_name] = current_time

    def draw_grid(self):
        """Draw the sudoku grid"""
        for i in range(10):
            thickness = 3 if i % 3 == 0 else 1
            # Vertical lines
            x = self.MARGIN + i * self.CELL_SIZE
            pygame.draw.line(self.screen, self.colors['grid'], 
                           (x, self.MARGIN), 
                           (x, self.MARGIN + 9 * self.CELL_SIZE), thickness)
            
            # Horizontal lines
            y = self.MARGIN + i * self.CELL_SIZE
            pygame.draw.line(self.screen, self.colors['grid'], 
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
                        color = self.colors['initial']
                    else:
                        color = self.colors['player']
                    
                    text = self.font_large.render(str(self.board[row][col]), True, color)
                    text_rect = text.get_rect(center=(x, y))
                    self.screen.blit(text, text_rect)
                
                # Draw notes
                elif any(self.notes[row][col]):
                    for num in range(9):
                        if self.notes[row][col][num]:
                            note_x = self.MARGIN + col * self.CELL_SIZE + (num % 3) * 20 + 6
                            note_y = self.MARGIN + row * self.CELL_SIZE + (num // 3) * 20 + 6
                            note_text = self.font_tiny.render(str(num + 1), True, self.colors['notes'])
                            self.screen.blit(note_text, (note_x, note_y))
    
    def draw_selection(self):
        """Draw selection highlight"""
        if self.selected_cell:
            row, col = self.selected_cell
            x = self.MARGIN + col * self.CELL_SIZE
            y = self.MARGIN + row * self.CELL_SIZE
            
            # Draw selection rectangle
            pygame.draw.rect(self.screen, self.colors['selected'], 
                           (x, y, self.CELL_SIZE, self.CELL_SIZE), 3)
            
            # Highlight same numbers
            if self.board[row][col] != 0:
                num = self.board[row][col]
                for r in range(9):
                    for c in range(9):
                        if self.board[r][c] == num and (r != row or c != col):
                            highlight_x = self.MARGIN + c * self.CELL_SIZE
                            highlight_y = self.MARGIN + r * self.CELL_SIZE
                            pygame.draw.rect(self.screen, (255, 255, 0, 50), 
                                           (highlight_x, highlight_y, self.CELL_SIZE, self.CELL_SIZE))
    
    def draw_ui(self):
        """Draw UI elements"""
        # Draw title
        title = self.font_medium.render("سودوكو", True, self.colors['text'])
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
        
        timer_surface = self.font_small.render(timer_text, True, self.colors['text'])
        self.screen.blit(timer_surface, (self.MARGIN, self.MARGIN + 9 * self.CELL_SIZE + 10))
        
        # Draw error count
        error_text = f"الأخطاء: {self.error_count}"
        error_surface = self.font_small.render(error_text, True, self.colors['error'])
        self.screen.blit(error_surface, (self.MARGIN + 150, self.MARGIN + 9 * self.CELL_SIZE + 10))
        
        # Draw hints
        hints_text = f"تلميحات: {self.hints}"
        hints_surface = self.font_small.render(hints_text, True, self.colors['selected'])
        self.screen.blit(hints_surface, (self.MARGIN + 300, self.MARGIN + 9 * self.CELL_SIZE + 10))
        
        # Draw progress
        remaining = self.check_progress()
        progress_text = f"متبقي: {remaining} خلية"
        progress_surface = self.font_small.render(progress_text, True, self.colors['success'])
        self.screen.blit(progress_surface, (self.MARGIN + 450, self.MARGIN + 9 * self.CELL_SIZE + 10))
        
        # Draw notes mode indicator
        if self.notes_mode:
            notes_text = "وضع الملاحظات: مفعّل"
            notes_color = self.colors['selected']
        else:
            notes_text = "وضع الملاحظات: معطل"
            notes_color = self.colors['notes']
        
        notes_surface = self.font_small.render(notes_text, True, notes_color)
        self.screen.blit(notes_surface, (self.MARGIN, self.MARGIN + 9 * self.CELL_SIZE + 40))
        
        # Draw difficulty
        difficulty_text = f"الصعوبة: {self.difficulty.name}"
        difficulty_surface = self.font_small.render(difficulty_text, True, self.colors['text'])
        self.screen.blit(difficulty_surface, (self.MARGIN + 300, self.MARGIN + 9 * self.CELL_SIZE + 40))
        
        # Draw buttons
        self.draw_buttons()
        
        # Draw sidebar
        self.draw_sidebar()
    
    def draw_buttons(self):
        """Draw control buttons"""
        buttons = {}
        
        # Button definitions
        button_defs = [
            ('new_game', "لعبة جديدة", 50, self.GREEN),
            ('solve', "حل تلقائي", 170, self.colors['button']),
            ('reset', "إعادة تعيين", 290, self.colors['selected']),
            ('hint', "تلميح", 410, self.colors['button']),
        ]
        
        for action, text, x, color in button_defs:
            rect = pygame.Rect(x, 620, 100, 40)
            pygame.draw.rect(self.screen, color, rect)
            button_text = self.font_small.render(text, True, (255, 255, 255))
            text_rect = button_text.get_rect(center=rect.center)
            self.screen.blit(button_text, text_rect)
            buttons[action] = rect
        
        return buttons
    
    def draw_sidebar(self):
        """Draw sidebar with statistics and controls"""
        sidebar_x = 600
        sidebar_width = 200
        
        # Draw sidebar background
        sidebar_rect = pygame.Rect(sidebar_x, 0, sidebar_width, self.WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, (200, 200, 200), sidebar_rect)
        
        # Statistics title
        stats_title = self.font_medium.render("الإحصائيات", True, self.colors['text'])
        self.screen.blit(stats_title, (sidebar_x + 20, 50))
        
        # Game statistics
        y_offset = 100
        stats_texts = [
            f"الألعاب: {self.stats['games_played']}",
            f"الفوز: {self.stats['games_won']}",
            f"نسبة الفوز: {self.stats['games_won']/max(self.stats['games_played'], 1) * 100:.1f}%",
            "",
            "أفضل الأوقات:",
            f"سهل: {self.format_time(self.stats['best_times']['easy'])}",
            f"متوسط: {self.format_time(self.stats['best_times']['medium'])}",
            f"صعب: {self.format_time(self.stats['best_times']['hard'])}",
            f"خبير: {self.format_time(self.stats['best_times']['expert'])}"
        ]
        
        for text in stats_texts:
            if text == "":
                y_offset += 20
                continue
            text_surface = self.font_small.render(text, True, self.colors['text'])
            self.screen.blit(text_surface, (sidebar_x + 20, y_offset))
            y_offset += 30
        
        # Difficulty selection
        y_offset = 400
        difficulty_title = self.font_medium.render("الصعوبة", True, self.colors['text'])
        self.screen.blit(difficulty_title, (sidebar_x + 20, y_offset))
        y_offset += 50
        
        difficulties = [
            ("سهل", Difficulty.EASY, self.GREEN),
            ("متوسط", Difficulty.MEDIUM, self.colors['button']),
            ("صعب", Difficulty.HARD, self.colors['selected']),
            ("خبير", Difficulty.EXPERT, self.colors['error'])
        ]
        
        for text, diff, color in difficulties:
            rect = pygame.Rect(sidebar_x + 20, y_offset, 120, 35)
            
            # Highlight current difficulty
            if diff == self.difficulty:
                pygame.draw.rect(self.screen, color, rect)
                text_color = (255, 255, 255)
            else:
                pygame.draw.rect(self.screen, color, rect, 2)
                text_color = self.colors['text']
            
            text_surface = self.font_small.render(text, True, text_color)
            text_rect = text_surface.get_rect(center=rect.center)
            self.screen.blit(text_surface, text_rect)
            
            y_offset += 45
    
    def format_time(self, seconds):
        """Format time in seconds to readable string"""
        if seconds == float('inf'):
            return "--:--"
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    def handle_button_click(self, pos, buttons):
        """Handle button clicks"""
        for action, rect in buttons.items():
            if rect.collidepoint(pos):
                if action == 'new_game':
                    self.generate_new_puzzle()
                elif action == 'solve':
                    self.board = [row[:] for row in self.solution]
                    self.is_game_active = False
                    self.current_session_stats['games_won'] += 1
                elif action == 'reset':
                    self.board = [row[:] for row in self.initial_board]
                    self.error_count = 0
                    self.start_time = time.time()
                    self.is_game_active = True
                    self.hints = 3
                    self.notes = [[[False for _ in range(9)] for _ in range(9)] for _ in range(9)]
                elif action == 'hint':
                    self.get_hint()
    
    def handle_sidebar_click(self, pos):
        """Handle clicks on sidebar"""
        sidebar_x = 600
        if pos[0] >= sidebar_x:
            y_offset = 450
            difficulties = [
                ("سهل", Difficulty.EASY),
                ("متوسط", Difficulty.MEDIUM),
                ("صعب", Difficulty.HARD),
                ("خبير", Difficulty.EXPERT)
            ]
            
            for text, diff in difficulties:
                rect = pygame.Rect(sidebar_x + 20, y_offset, 120, 35)
                if rect.collidepoint(pos):
                    self.difficulty = diff
                    self.generate_new_puzzle()
                    break
                y_offset += 45
    
    def draw_win_animation(self):
        """Draw win celebration animation"""
        if self.win_animation:
            # Create celebration effect
            center_x = self.MARGIN + 9 * self.CELL_SIZE // 2
            center_y = self.MARGIN + 9 * self.CELL_SIZE // 2
            
            # Draw celebration message
            win_text = self.font_medium.render("تهانينا! لقد فزت! 🎉", True, self.colors['success'])
            win_rect = win_text.get_rect(center=(center_x, center_y - 50))
            self.screen.blit(win_text, win_rect)
            
            # Draw time and score
            minutes = int(self.game_time // 60)
            seconds = int(self.game_time % 60)
            time_text = f"الوقت: {minutes:02d}:{seconds:02d} - الأخطاء: {self.error_count}"
            time_surface = self.font_small.render(time_text, True, self.colors['text'])
            time_rect = time_surface.get_rect(center=(center_x, center_y))
            self.screen.blit(time_surface, time_rect)
    
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
                        self.handle_sidebar_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    self.handle_key(event.key)
            
            # Clear screen
            self.screen.fill(self.colors['bg'])
            
            # Draw everything
            self.draw_grid()
            self.draw_numbers()
            self.draw_selection()
            self.draw_ui()
            
            # Draw win animation
            if self.win_animation:
                self.draw_win_animation()
            
            # Update display
            pygame.display.flip()
            clock.tick(60)
        
        # Save stats before quitting
        self.stats['games_played'] += self.current_session_stats['games_played']
        self.stats['games_won'] += self.current_session_stats['games_won']
        self.stats['total_time'] += self.current_session_stats['total_time']
        self.stats['total_errors'] += self.current_session_stats['total_errors']
        self.save_stats()
        
        pygame.quit()

def main():
    game = SudokuGame()
    game.run()

if __name__ == "__main__":
    main()