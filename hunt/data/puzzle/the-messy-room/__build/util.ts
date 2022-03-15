import { ALLOCATIONS, SOLUTION_LETTERS_UP_INDICES, LETTERS, WIDTH, NUM_GRIDS } from './data';

export const tab = (count = 1) => ' '.repeat(count * 4);

export const outputBoard = (boardIndex: number) => {
  const board = ALLOCATIONS[boardIndex];
  console.log(`${tab(1)}<table class="grid crossword" data-board="${boardIndex}">`);
  for (let row = 0; row < board.length; row++) {
    console.log(`${tab(2)}<tr>`);

    const rowCells = [];
    for (let col = 0; col < WIDTH; col++) {
      const cell = board[row][col];
      if (cell.type === 'empty') {
        rowCells.push('<td class="filled"></td>');
      } else if (cell.type === 'letter') {
        rowCells.push(`<td class="letter" data-board='${boardIndex}' data-row='${row}' data-col='${col}'></td>`);
      } else {
        rowCells.push(`<td class="fixed">${cell.value}</td>`);
      }
    }
    console.log(`${tab(3)}${rowCells.join('')}`);
    console.log(`${tab(2)}</tr>`);
  }
  console.log(`${tab(1)}</table>`);
};

export const outputSolutionBoard = (boardIndex: number) => {
  const board = ALLOCATIONS[boardIndex];
  console.log(`${tab(1)}<table class="grid crossword" data-board="${boardIndex}">`);
  for (let row = 0; row < board.length; row++) {
    console.log(`${tab(2)}<tr>`);

    const rowCells = [];
    for (let col = 0; col < WIDTH; col++) {
      const cell = board[row][col];
      if (cell.type === 'empty') {
        rowCells.push('<td class="filled"></td>');
      } else if (cell.type === 'letter') {
        rowCells.push(`<td class="letter ${SOLUTION_LETTERS_UP_INDICES[boardIndex][col].has(row) ? 'up' : 'down'}">
          ${cell.value}
        </td>`);
      } else {
        rowCells.push(`<td class="fixed">${cell.value}</td>`);
      }
    }
    console.log(`${tab(3)}${rowCells.join('')}`);
    console.log(`${tab(2)}</tr>`);
  }
  console.log(`${tab(1)}</table>`);
};

export const outputLetters = (board: number) => {
  const letterSet = LETTERS[board];
  let height = 0;
  for (const colLetters of letterSet) {
    height = Math.max(height, colLetters.length);
  }

  console.log(`${tab(1)}<table class="letters custom" data-skip-inline-borders="true" data-board="${board}">`);
  for (let row = 0; row < height; row++) {
    console.log(`${tab(2)}<tr>`);
    const rowCells = [];
    for (let col = 0; col < WIDTH; col++) {
      const colLetters = letterSet[col];
      const padding = height - colLetters.length;
      const letter = row < padding ? null : colLetters[row - padding];
      if (letter) {
        rowCells.push(`<td class="letter" data-board='${board}' data-col='${col}' data-index='${row - padding}'>${letter}</td>`);
      } else {
        rowCells.push(`<td class="empty"></td>`);
      }
    }
    console.log(`${tab(3)}${rowCells.join('')}`);
    console.log(`${tab(2)}</tr>`);
  }
  console.log(`${tab(1)}</table>`);
};

