import {
  StateListPuzzleManager,
  StateListPuzzleManagerOpts,
} from "@common/state-list-puzzle-manager";
import { Cell, Updates, Refresh, Partial } from "./types";
import { initializeVirtualScrolling, restoreInitialGridOrder } from './common';
import { PUBLIC_STATE_MANAGER } from './public';

// Export globally so the auto onload handler can find this.
window.puzzleOnLoad = puzzleOnLoad;
window.puzzleOnCopy = puzzleOnCopy;

const NUM_BOARDS = 7;
const MAX_HEIGHT = 6;
const WIDTH = 25;

type DomUpdateDescriptor = Partial;

function puzzleOnLoad() {
  puzzleManager.markPuzzleLoaded();
}

function puzzleOnCopy(copiedPuzzle: HTMLElement) {
  const container =
    copiedPuzzle.querySelector<HTMLElement>(".scroll-container")!;
  restoreInitialGridOrder(container);

  // Make a copy of that .crossword at the other end of the container.
  container.appendChild(container.firstElementChild!.cloneNode(true));
}

const puzzleManager = new (class extends StateListPuzzleManager<
  Updates,
  Refresh,
  Partial,
  DomUpdateDescriptor
> {
  private readonly boards: (string | null)[][][] = [];
  private readonly letters: Set<number>[][] = [];

  constructor(opts: StateListPuzzleManagerOpts) {
    super(opts, PUBLIC_STATE_MANAGER);

    for (let board = 0; board < NUM_BOARDS; board++) {
      this.boards.push([]);
      for (let row = 0; row < MAX_HEIGHT; row++) {
        this.boards[board].push([]);
        for (let col = 0; col < WIDTH; col++) {
          this.boards[board][row].push(null);
        }
      }

      this.letters.push([]);
      for (let col = 0; col < WIDTH; col++) {
        this.letters[board].push(new Set<number>());
      }
    }
  }

  initializeDom() {
    for (const cell of document.querySelectorAll<HTMLElement>(
      "table.crossword td"
    )) {
      initializeDropquoteCellDom(cell);
    }
    for (const cell of document.querySelectorAll<HTMLElement>(
      "table.letters td.letter"
    )) {
      initializeLettersCellDom(cell);
    }
    for (const board of document.querySelectorAll<HTMLElement>(
      "table.crossword"
    )) {
      board.addEventListener("input", onDropquoteInputHandler(board));
      board.addEventListener("keydown", onDropquoteKeydownHandler(board));
      board.addEventListener("keydown", onArrowKeydownHandler(board, 'td', 'td.letter', 'input'));
      board.addEventListener("focusin", onFocusinHandler(board, 'input'));
    }
    for (const board of document.querySelectorAll<HTMLElement>("table.letters")) {
      board.addEventListener("click", onLettersClick);
      board.addEventListener("keydown", (event) => {
        // The other keydown handler breaks enter/space to click.
        if (event.key === 'Enter' || event.key === ' ') {
          onLettersClick(event);
          event.preventDefault();
        }
      });
      board.addEventListener("keydown", onArrowKeydownHandler(board, 'td', 'td.letter'));
      board.addEventListener("focusin", onFocusinHandler(board, 'td.letter'));
    }
    initializeVirtualScrolling();
  }

  handleRefresh(refresh: Refresh) {
    for (let board = 0; board < NUM_BOARDS; board++) {
      for (let row = 0; row < MAX_HEIGHT; row++) {
        for (let col = 0; col < WIDTH; col++) {
          this.boards[board][row][col] = null;
        }
      }
    }
    for (const { board, row, col, letter } of refresh.cells) {
      this.boards[board][row][col] = letter;
    }

    for (let board = 0; board < NUM_BOARDS; board++) {
      for (let col = 0; col < WIDTH; col++) {
        this.letters[board][col].clear();
      }
    }
    for (const { board, col, index } of refresh.usedIndices) {
      this.letters[board][col].add(index);
    }
  }

  handleUpdate(update: Partial) {
    if (update.action === "cell") {
      this.boards[update.board][update.row][update.col] = update.letter;
    } else {
      const set = this.letters[update.board][update.col];
      if (update.used) {
        set.add(update.index);
      } else {
        set.delete(update.index);
      }
    }
    return update;
  }

  handleRollback(rollback: Updates) {
    return rollback;
  }

  synchronizeToDom(descriptor?: DomUpdateDescriptor) {
    if (!descriptor || descriptor.action === "cell") {
      this.updateBoardDom(descriptor);
    }
    if (!descriptor || descriptor.action === "usedIndex") {
      this.updateLettersDom(descriptor);
    }
  }

  private updateBoardDom(ref?: { board: number; row: number; col: number }) {
    let query = "table.crossword td.letter";
    if (ref) {
      query += `[data-board="${ref.board}"][data-row="${ref.row}"][data-col="${ref.col}"]`;
    }

    for (const cell of document.querySelectorAll<HTMLElement>(query)) {
      if (!cell.dataset.board || !cell.dataset.row || !cell.dataset.col) {
        continue;
      }
      const board = parseInt(cell.dataset.board, 10);
      const row = parseInt(cell.dataset.row, 10);
      const col = parseInt(cell.dataset.col, 10);

      const input = cell.querySelector<HTMLInputElement>("input")!;
      input.value = this.boards[board][row][col] || "";

      if (input.value) {
        cell.classList.add("entered");
      } else {
        cell.classList.remove("entered");
      }
    }
  }

  private updateLettersDom(ref?: {
    board: number;
    col: number;
    index: number;
  }) {
    let query = "table.letters td.letter";
    if (ref) {
      query += `[data-board="${ref.board}"][data-col="${ref.col}"][data-index="${ref.index}"]`;
    }

    for (const cell of document.querySelectorAll<HTMLElement>(query)) {
      if (!cell.dataset.board || !cell.dataset.col || !cell.dataset.index) {
        continue;
      }
      const board = parseInt(cell.dataset.board, 10);
      const col = parseInt(cell.dataset.col, 10);
      const index = parseInt(cell.dataset.index, 10);

      if (this.letters[board][col].has(index)) {
        cell.classList.add("used");
      } else {
        cell.classList.remove("used");
      }
    }
  }
})({
  serverUrl: "/ws/puzzle/the-messy-room",
  puzzleUrl: "the-messy-room",
  defaultScope: "1",
  puzzleAuthToken: window.puzzleAuthToken,
  // The puzzle can't really be put into an invalid state, so no need for seq-based
  // locking. It also means we don't need to queue updates until the previous one
  // resolves.
  skipLock: true,
});

function initializeDropquoteCellDom(cell: HTMLElement) {
  if (cell.classList.contains("letter")) {
    const input = document.createElement("input");
    input.type = "text";
    input.maxLength = 1;
    input.pattern = "[a-zA-Z]";
    input.dataset.copyInputValue = "true";
    cell.appendChild(input);
  }

  // Don't include background colors when copying.
  if (!cell.classList.contains("filled")) {
    cell.dataset.copyOnlyStyles =
      (cell.dataset.copyOnlyStyle || "") + "background-color: transparent;";
  }
}

function initializeLettersCellDom(cell: HTMLElement) {
  // Don't include background colors when copying.
  cell.dataset.copyOnlyStyles =
    (cell.dataset.copyOnlyStyle || "") + "background-color: transparent;";
}

function onDropquoteInputHandler(board: HTMLElement) {
  const inputs = Array.from(board.querySelectorAll("input"));
  return (event: Event) => {
    if (
      !event.target ||
      (event.target as HTMLElement).tagName.toLowerCase() !== "input"
    )
      return;

    const target = event.target as HTMLInputElement;
    const parent = target.parentNode! as HTMLElement;
    if (!parent.dataset.board || !parent.dataset.row || !parent.dataset.col) {
      return;
    }
    const letter = target.value;
    puzzleManager.puzzleState.update({
      action: "cell",
      board: parseInt(parent.dataset.board, 10),
      row: parseInt(parent.dataset.row, 10),
      col: parseInt(parent.dataset.col, 10),
      letter: letter ? letter.toUpperCase() : null,
    });

    // If we've typed a letter, move focus to the next input, so we can make
    // entering words nice and easy.
    if (letter) {
      const currentIndex = inputs.indexOf(target);
      if (currentIndex > -1 && currentIndex < inputs.length - 1) {
        inputs[currentIndex + 1].focus();
        inputs[currentIndex + 1].select();
      }
    }

    // Optimistically toggle the class, although it will be set again when we
    // receive the update.
    if (letter) {
      parent.classList.add("entered");
    } else {
      parent.classList.remove("entered");
    }

    event.stopPropagation();
  };
}

function onLettersClick(event: Event) {
  if (!event.target) return;

  const target = event.target as HTMLElement;
  if (!target.dataset.board || !target.dataset.col || !target.dataset.index) {
    return;
  }
  const used = !target.classList.contains("used");
  puzzleManager.puzzleState.update({
    action: "usedIndex",
    board: parseInt(target.dataset.board, 10),
    col: parseInt(target.dataset.col, 10),
    index: parseInt(target.dataset.index, 10),
    used,
  });
  target.classList.toggle("used", used);
  event.stopPropagation();
}

function onDropquoteKeydownHandler(board: HTMLElement) {
  const inputs = Array.from(board.querySelectorAll<HTMLInputElement>("input"));

  return (event: KeyboardEvent) => {
    const target = event.target && (event.target as HTMLInputElement);
    if (!target || target.tagName.toLowerCase() !== "input") {
      return;
    }
    const key = event.key;
    if (key === "Backspace" && !target.value) {
      const currentIndex = inputs.indexOf(target);
      if (currentIndex > 0) {
        inputs[currentIndex - 1].focus();
        inputs[currentIndex - 1].select();
      }
    }
  };
}

function onArrowKeydownHandler(board: HTMLElement, cellSelector: string, focusableSelector: string, focusSelector?: string) {
  const rows = Array.from(board.querySelectorAll<HTMLTableRowElement>('tr'));
  const cellsByRow = rows.map(row => Array.from(row.querySelectorAll<HTMLElement>(cellSelector)));

  for (let i = 0; i < cellsByRow.length; i++) {
    for (let j = 0; j < cellsByRow[i].length; j++) {
      if (cellsByRow[i][j].matches(focusableSelector)) {
        const cell = cellsByRow[i][j];
        const focus = focusSelector ? cell.querySelector<HTMLElement>(focusSelector) : cell;
        cell.tabIndex = -1;
      }
    }
  }
  board.querySelector<HTMLElement>(focusSelector || focusableSelector)!.tabIndex = 0;

  return (event: KeyboardEvent) => {
    const target = event.target && (event.target as HTMLElement).closest<HTMLElement>(focusableSelector);
    if (!target) return;

    let targetPos;
    for (let i = 0; i < cellsByRow.length; i++) {
      for (let j = 0; j < cellsByRow[i].length; j++) {
        if (cellsByRow[i][j] === target) {
          targetPos = [i, j] as const;
          break;
        }
      }
      if (targetPos) break;
    }
    if (!targetPos) return;

    let newPos;
    switch (event.key) {
      case 'ArrowLeft':
        newPos = [targetPos[0], targetPos[1] - 1];
        while (newPos[1] > 0 && !cellsByRow[newPos[0]][newPos[1]].matches(focusableSelector)) {
          newPos[1] -= 1;
        }
        break;
      case 'ArrowRight':
        newPos = [targetPos[0], targetPos[1] + 1];
        while (newPos[1] < cellsByRow[newPos[0]].length && !cellsByRow[newPos[0]][newPos[1]].matches(focusableSelector)) {
          newPos[1] += 1;
        }
        break;
      case 'ArrowUp':
        newPos = [targetPos[0] - 1, targetPos[1]];
        while (newPos[0] > 0 && !cellsByRow[newPos[0]][newPos[1]].matches(focusableSelector)) {
          newPos[0] -= 1;
        }
        break;
      case 'ArrowDown':
        newPos = [targetPos[0] + 1, targetPos[1]];
        while (newPos[0] < cellsByRow.length && !cellsByRow[newPos[0]][newPos[1]].matches(focusableSelector)) {
          newPos[0] += 1;
        }
        break;
    }
    if (!newPos || !cellsByRow[newPos[0]] || !cellsByRow[newPos[0]][newPos[1]]) {
      return;
    }

    for (let i = 0; i < cellsByRow.length; i++) {
      for (let j = 0; j < cellsByRow[i].length; j++) {
        if (cellsByRow[i][j].matches(focusableSelector)) {
          const cell = cellsByRow[i][j];
          const focus = focusSelector ? cell.querySelector<HTMLElement>(focusSelector) : cell;
          focus!.tabIndex = -1;
        }
      }
    }

    const cell = cellsByRow[newPos[0]][newPos[1]];
    const focus = cell && focusSelector ? cell.querySelector<HTMLElement>(focusSelector) : cell;
    if (!focus) return;
    focus.focus();
    focus.tabIndex = 0;
    event.preventDefault();
    event.stopPropagation();
  };
}

function onFocusinHandler(board: HTMLElement, focusableSelector: string) {
  const focusables = Array.from(board.querySelectorAll<HTMLInputElement>(focusableSelector));
  return (event: FocusEvent) => {
    const target = event.target && (event.target as HTMLElement).closest<HTMLElement>(focusableSelector);
    if (!target) {
      return;
    }
    for (const focusable of focusables) {
      focusable.tabIndex = -1;
    }
    target.tabIndex = 0;
    event.stopPropagation();
  };
}
