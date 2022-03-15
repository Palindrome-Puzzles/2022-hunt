import { Updates, Refresh } from './types';
import { PublicStateManager } from "@common/team-puzzle-state";
import { cloneDeep } from 'lodash-es';

const INITIAL: Refresh = {
  cells: [],
  usedIndices: [],
};

const LOCAL_STORAGE_KEY = 'hunt:the-messy-room:public';
const fromStorage = localStorage.getItem(LOCAL_STORAGE_KEY);
const parsedFromStorage: Refresh | null = fromStorage ? JSON.parse(fromStorage) : null;
let state = parsedFromStorage || INITIAL;

// In the live hunt, this was done by the server so the state could be synced
// across teams.
export const PUBLIC_STATE_MANAGER: PublicStateManager<Updates, Refresh> = {
  initial: () => {
    return cloneDeep(state);
  },
  onMessage: (message) => {
    // No need to handle refresh/abandon for this puzzle.
    if (message.type !== 'state.update') return null;

    const update = message.updates;
    if (update.action === 'cell') {
      state = {
        ...state,
        cells: [
          ...state.cells.filter(cell => cell.board !== update.board || cell.row !== update.row || cell.col !== update.col),
          ...(update.letter ? [{board: update.board, row: update.row, col: update.col, letter: update.letter}] : []),
        ],
      }
    } else if (update.action === 'usedIndex') {
      state = {
        ...state,
        usedIndices: [
          ...state.usedIndices.filter(cell => cell.board !== update.board || cell.col !== update.col || cell.index !== update.index),
          ...(update.used ? [{board: update.board, col: update.col, index: update.index}] : []),
        ],
      }
    }
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(state));
    return cloneDeep(state);
  },
}

