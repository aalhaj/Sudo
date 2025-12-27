document.addEventListener('DOMContentLoaded', () => {
    // Game State
    let solution = [];
    let initialBoard = [];
    let currentBoard = [];
    let notes = [];
    let history = [];
    let mistakes = 0;
    let timerSeconds = 0;
    let timerInterval = null;
    let selectedCell = null;
    let isNoteMode = false;
    let difficulty = 'medium';

    // DOM Elements
    const boardElement = document.getElementById('game-board');
    const mistakesElement = document.getElementById('mistakes');
    const timerElement = document.getElementById('timer');
    const difficultySelect = document.getElementById('difficulty-select');
    const difficultyDisplay = document.getElementById('difficulty-display');
    const themeToggle = document.getElementById('theme-toggle');
    const btnUndo = document.getElementById('btn-undo');
    const btnErase = document.getElementById('btn-erase');
    const btnNote = document.getElementById('btn-note');
    const btnHint = document.getElementById('btn-hint');
    const btnNewGame = document.getElementById('btn-new-game');
    const numButtons = document.querySelectorAll('.num-btn');
    const gameOverModal = document.getElementById('game-over-modal');
    const winModal = document.getElementById('win-modal');
    const btnRestart = document.getElementById('btn-restart');
    const btnNewGameWin = document.getElementById('btn-new-game-win');

    // Constants
    const MAX_MISTAKES = 3;
    const DIFFICULTY_HOLES = {
        'easy': 30,
        'medium': 40,
        'hard': 50,
        'expert': 60
    };

    // Initialization
    initGame();

    // Event Listeners
    difficultySelect.addEventListener('change', (e) => {
        difficulty = e.target.value;
        difficultyDisplay.textContent = difficulty.charAt(0).toUpperCase() + difficulty.slice(1);
        newGame();
    });

    themeToggle.addEventListener('click', toggleTheme);

    btnNewGame.addEventListener('click', newGame);
    btnRestart.addEventListener('click', newGame);
    btnNewGameWin.addEventListener('click', newGame);

    btnUndo.addEventListener('click', undo);
    btnErase.addEventListener('click', eraseCell);
    btnNote.addEventListener('click', toggleNoteMode);
    btnHint.addEventListener('click', useHint);

    numButtons.forEach(btn => {
        btn.addEventListener('click', () => handleInput(parseInt(btn.dataset.num)));
    });

    document.addEventListener('keydown', (e) => {
        if (gameOverModal.classList.contains('hidden') && winModal.classList.contains('hidden')) {
            if (e.key >= '1' && e.key <= '9') {
                handleInput(parseInt(e.key));
            } else if (e.key === 'Backspace' || e.key === 'Delete') {
                eraseCell();
            } else if (e.key === 'ArrowUp') moveSelection(-1, 0);
            else if (e.key === 'ArrowDown') moveSelection(1, 0);
            else if (e.key === 'ArrowLeft') moveSelection(0, -1);
            else if (e.key === 'ArrowRight') moveSelection(0, 1);
        }
    });

    // Game Logic Functions

    function initGame() {
        // Check for saved theme
        if (localStorage.getItem('theme') === 'dark') {
            document.body.classList.add('dark-mode');
        }
        newGame();
    }

    function newGame() {
        clearInterval(timerInterval);
        timerSeconds = 0;
        mistakes = 0;
        history = [];
        selectedCell = null;
        isNoteMode = false;

        updateTimerDisplay();
        updateMistakesDisplay();
        btnNote.classList.remove('active');
        gameOverModal.classList.add('hidden');
        winModal.classList.add('hidden');

        generateSudoku();
        renderBoard();
        startTimer();
    }

    function generateSudoku() {
        // Initialize empty 9x9 grid
        solution = Array.from({ length: 9 }, () => Array(9).fill(0));

        // Fill diagonal 3x3 boxes (independent)
        fillDiagonal();

        // Solve the rest
        solveSudoku(solution);

        // Create puzzle by removing numbers
        initialBoard = JSON.parse(JSON.stringify(solution));
        currentBoard = JSON.parse(JSON.stringify(solution));
        notes = Array.from({ length: 9 }, () => Array.from({ length: 9 }, () => new Set()));

        removeDigits();
    }

    function fillDiagonal() {
        for (let i = 0; i < 9; i += 3) {
            fillBox(i, i);
        }
    }

    function fillBox(row, col) {
        let num;
        for (let i = 0; i < 3; i++) {
            for (let j = 0; j < 3; j++) {
                do {
                    num = Math.floor(Math.random() * 9) + 1;
                } while (!isSafeInBox(row, col, num));
                solution[row + i][col + j] = num;
            }
        }
    }

    function isSafeInBox(rowStart, colStart, num) {
        for (let i = 0; i < 3; i++) {
            for (let j = 0; j < 3; j++) {
                if (solution[rowStart + i][colStart + j] === num) {
                    return false;
                }
            }
        }
        return true;
    }

    function isSafe(board, row, col, num) {
        // Check row
        for (let x = 0; x < 9; x++) {
            if (board[row][x] === num) return false;
        }
        // Check col
        for (let x = 0; x < 9; x++) {
            if (board[x][col] === num) return false;
        }
        // Check box
        let startRow = row - row % 3;
        let startCol = col - col % 3;
        for (let i = 0; i < 3; i++) {
            for (let j = 0; j < 3; j++) {
                if (board[startRow + i][startCol + j] === num) return false;
            }
        }
        return true;
    }

    function solveSudoku(board) {
        let row = -1;
        let col = -1;
        let isEmpty = false;
        for (let i = 0; i < 9; i++) {
            for (let j = 0; j < 9; j++) {
                if (board[i][j] === 0) {
                    row = i;
                    col = j;
                    isEmpty = true;
                    break;
                }
            }
            if (isEmpty) break;
        }

        if (!isEmpty) return true;

        for (let num = 1; num <= 9; num++) {
            if (isSafe(board, row, col, num)) {
                board[row][col] = num;
                if (solveSudoku(board)) return true;
                board[row][col] = 0;
            }
        }
        return false;
    }

    function removeDigits() {
        let attempts = DIFFICULTY_HOLES[difficulty];
        while (attempts > 0) {
            let row = Math.floor(Math.random() * 9);
            let col = Math.floor(Math.random() * 9);
            if (initialBoard[row][col] !== 0) {
                initialBoard[row][col] = 0;
                currentBoard[row][col] = 0;
                attempts--;
            }
        }
    }

    function renderBoard() {
        boardElement.innerHTML = '';
        for (let i = 0; i < 9; i++) {
            for (let j = 0; j < 9; j++) {
                const cell = document.createElement('div');
                cell.classList.add('cell');
                cell.dataset.row = i;
                cell.dataset.col = j;

                if (initialBoard[i][j] !== 0) {
                    cell.textContent = initialBoard[i][j];
                    cell.classList.add('fixed');
                } else {
                    cell.classList.add('user-input');
                    if (currentBoard[i][j] !== 0) {
                        cell.textContent = currentBoard[i][j];
                    } else {
                        // Render notes
                        const notesGrid = document.createElement('div');
                        notesGrid.classList.add('notes-grid');
                        for (let k = 1; k <= 9; k++) {
                            const note = document.createElement('div');
                            note.classList.add('note');
                            note.textContent = k;
                            if (notes[i][j].has(k)) {
                                note.classList.add('active');
                            }
                            notesGrid.appendChild(note);
                        }
                        cell.appendChild(notesGrid);
                    }
                }

                cell.addEventListener('click', () => selectCell(i, j));
                boardElement.appendChild(cell);
            }
        }
    }

    function selectCell(row, col) {
        selectedCell = { row, col };
        updateBoardHighlights();
    }

    function updateBoardHighlights() {
        if (!selectedCell) return;

        const cells = document.querySelectorAll('.cell');
        const selectedValue = currentBoard[selectedCell.row][selectedCell.col];

        cells.forEach(cell => {
            const r = parseInt(cell.dataset.row);
            const c = parseInt(cell.dataset.col);

            cell.classList.remove('selected', 'related', 'same-num');

            if (r === selectedCell.row && c === selectedCell.col) {
                cell.classList.add('selected');
            } else if (r === selectedCell.row || c === selectedCell.col ||
                (Math.floor(r / 3) === Math.floor(selectedCell.row / 3) &&
                    Math.floor(c / 3) === Math.floor(selectedCell.col / 3))) {
                cell.classList.add('related');
            }

            if (selectedValue !== 0 && currentBoard[r][c] === selectedValue) {
                cell.classList.add('same-num');
            }
        });
    }

    function handleInput(num) {
        if (!selectedCell) return;
        const { row, col } = selectedCell;

        // Cannot edit fixed cells
        if (initialBoard[row][col] !== 0) return;

        if (isNoteMode) {
            toggleNote(row, col, num);
        } else {
            enterNumber(row, col, num);
        }
    }

    function enterNumber(row, col, num) {
        if (currentBoard[row][col] === num) return; // No change

        // Save to history
        addToHistory();

        if (num === solution[row][col]) {
            // Correct
            currentBoard[row][col] = num;
            notes[row][col].clear(); // Clear notes in this cell
            updateRelatedNotes(row, col, num); // Clear this number from related notes
            renderBoard();
            selectCell(row, col);
            checkCompletion(row, col);
            checkWin();
        } else {
            // Incorrect
            mistakes++;
            updateMistakesDisplay();

            // Show error animation/style
            const cellIndex = row * 9 + col;
            const cell = boardElement.children[cellIndex];
            cell.classList.add('error');
            cell.textContent = num;

            setTimeout(() => {
                cell.classList.remove('error');
                // Re-render to restore state (remove the wrong number visually)
                renderBoard();
                selectCell(row, col);
            }, 500);

            if (mistakes >= MAX_MISTAKES) {
                gameOver();
            }
        }
    }

    function toggleNote(row, col, num) {
        if (currentBoard[row][col] !== 0) return; // Cannot add notes to filled cell

        addToHistory();

        if (notes[row][col].has(num)) {
            notes[row][col].delete(num);
        } else {
            notes[row][col].add(num);
        }
        renderBoard();
        selectCell(row, col);
    }

    function updateRelatedNotes(row, col, num) {
        // Remove 'num' from notes in same row, col, box
        for (let i = 0; i < 9; i++) {
            notes[row][i].delete(num);
            notes[i][col].delete(num);
        }
        let startRow = row - row % 3;
        let startCol = col - col % 3;
        for (let i = 0; i < 3; i++) {
            for (let j = 0; j < 3; j++) {
                notes[startRow + i][startCol + j].delete(num);
            }
        }
    }

    function eraseCell() {
        if (!selectedCell) return;
        const { row, col } = selectedCell;

        if (initialBoard[row][col] !== 0) return;

        addToHistory();

        if (currentBoard[row][col] !== 0) {
            currentBoard[row][col] = 0;
        } else {
            // Clear notes if cell is empty
            notes[row][col].clear();
        }
        renderBoard();
        selectCell(row, col);
    }

    function undo() {
        if (history.length === 0) return;
        const lastState = history.pop();

        currentBoard = JSON.parse(lastState.board);
        // Restore notes (convert arrays back to Sets)
        const savedNotes = JSON.parse(lastState.notes);
        notes = savedNotes.map(row => row.map(n => new Set(n)));

        renderBoard();
        if (selectedCell) selectCell(selectedCell.row, selectedCell.col);
    }

    function addToHistory() {
        // Deep copy notes (convert Sets to arrays for JSON)
        const notesArray = notes.map(row => row.map(set => Array.from(set)));

        history.push({
            board: JSON.stringify(currentBoard),
            notes: JSON.stringify(notesArray)
        });

        if (history.length > 20) history.shift(); // Limit history size
    }

    function toggleNoteMode() {
        isNoteMode = !isNoteMode;
        btnNote.classList.toggle('active', isNoteMode);
    }

    function useHint() {
        if (!selectedCell) return;
        const { row, col } = selectedCell;

        if (currentBoard[row][col] !== 0) return;

        addToHistory();

        const correctNum = solution[row][col];
        currentBoard[row][col] = correctNum;
        notes[row][col].clear();
        updateRelatedNotes(row, col, correctNum);

        renderBoard();
        selectCell(row, col);
        checkCompletion(row, col);
        checkWin();
    }

    function checkWin() {
        for (let i = 0; i < 9; i++) {
            for (let j = 0; j < 9; j++) {
                if (currentBoard[i][j] !== solution[i][j]) return;
            }
        }
        gameWin();
    }

    function gameWin() {
        clearInterval(timerInterval);
        document.getElementById('final-time').textContent = formatTime(timerSeconds);
        document.getElementById('final-difficulty').textContent = difficultyDisplay.textContent;
        winModal.classList.remove('hidden');
    }

    function gameOver() {
        clearInterval(timerInterval);
        gameOverModal.classList.remove('hidden');
    }

    function updateMistakesDisplay() {
        mistakesElement.textContent = `${mistakes}/${MAX_MISTAKES}`;
    }

    function startTimer() {
        timerInterval = setInterval(() => {
            timerSeconds++;
            updateTimerDisplay();
        }, 1000);
    }

    function updateTimerDisplay() {
        timerElement.textContent = formatTime(timerSeconds);
    }

    function formatTime(seconds) {
        const min = Math.floor(seconds / 60);
        const sec = seconds % 60;
        return `${min.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`;
    }

    function toggleTheme() {
        document.body.classList.toggle('dark-mode');
        const isDark = document.body.classList.contains('dark-mode');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    }

    function moveSelection(dRow, dCol) {
        if (!selectedCell) {
            selectCell(0, 0);
            return;
        }
        let newRow = selectedCell.row + dRow;
        let newCol = selectedCell.col + dCol;

        if (newRow >= 0 && newRow < 9 && newCol >= 0 && newCol < 9) {
            selectCell(newRow, newCol);
        }
    }

    function checkCompletion(row, col) {
        // Check Row
        let rowComplete = true;
        for (let j = 0; j < 9; j++) {
            if (currentBoard[row][j] !== solution[row][j]) {
                rowComplete = false;
                break;
            }
        }
        if (rowComplete) animateCompletion('row', row);

        // Check Column
        let colComplete = true;
        for (let i = 0; i < 9; i++) {
            if (currentBoard[i][col] !== solution[i][col]) {
                colComplete = false;
                break;
            }
        }
        if (colComplete) animateCompletion('col', col);

        // Check Box
        let boxComplete = true;
        let startRow = row - row % 3;
        let startCol = col - col % 3;
        for (let i = 0; i < 3; i++) {
            for (let j = 0; j < 3; j++) {
                if (currentBoard[startRow + i][startCol + j] !== solution[startRow + i][startCol + j]) {
                    boxComplete = false;
                    break;
                }
            }
        }
        if (boxComplete) animateCompletion('box', startRow, startCol);
    }

    function animateCompletion(type, index1, index2) {
        const cells = document.querySelectorAll('.cell');
        cells.forEach(cell => {
            const r = parseInt(cell.dataset.row);
            const c = parseInt(cell.dataset.col);
            let shouldAnimate = false;

            if (type === 'row' && r === index1) shouldAnimate = true;
            if (type === 'col' && c === index1) shouldAnimate = true;
            if (type === 'box') {
                if (r >= index1 && r < index1 + 3 && c >= index2 && c < index2 + 3) shouldAnimate = true;
            }

            if (shouldAnimate) {
                // Remove class first to reset animation if triggered rapidly
                cell.classList.remove('completed-animation');
                void cell.offsetWidth; // Trigger reflow
                cell.classList.add('completed-animation');

                setTimeout(() => {
                    cell.classList.remove('completed-animation');
                }, 600);
            }
        });
    }
});
