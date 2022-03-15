#!/usr/bin/env node
import { assert } from "@common/helpers";

const BOARDS = [
  'HIS THAT WORLD OF HE FEELS WAS ANY THAN CULTIVATION IS THE AGAINST I A CONSPIRACY BORN LESS WRITER THE SUPPOSE TALENT INTO WHICH',
  'THAT WITH AND A FURNITURE TO A SUCH STOCK BRAIN CHOOSE YOU YOU I MAN\u2019S IT LIKE LITTLE HAVE ATTIC AS IS CONSIDER ORIGINALLY',
  'IN NO OF PROBLEMS AND SMALL BETWEEN THE FOR THERE SAME AND THE OF IS JUSTICE TRUTH ALL LARGE TREATMENT ISSUES CONCERNING ARE DIFFERENCE PEOPLE',
  'PEOPLE WIDELY IN MOVE THE A THE VERY OF MADE AND A BEGINNING CREATED ANGRY WAS LOT HAS BAD BEEN AS THIS REGARDED',
  'OF IMAGINATION CAST DEATH DREAMS TO FED WE UPON BORN IN AWAY BY REALITY AND PUT PRICELESS ILLUSION',
  'THEIR THEM PEOPLE REASON EVEN OF LEFT WHEN AS AFRAID THEM A IF BECOME HAS MOMENTS FEW FOR WE LEFT HAD',
  'WISDOM WITHOUT SPEECH BE OF NO AND NO LIBERTY AS WITHOUT AS SUCH FREEDOM SUCH FREEDOM OF THING THERE CAN THING THOUGHT',
];
// prettier-ignore
export const LETTERS = [
  ['HIINO', 'EIOT', 'AEHIW', 'ACS', 'ALT', 'NPTWY', 'AOSS', 'BINTT', 'CLOS', 'AEWY', 'ANT', 'AHST', 'ADLLO', 'ILNNV', 'AEIS', 'CKMOT', 'AFU', 'BINN', 'HRRT', 'ALNNS', 'CITV', 'CEFIN', 'OTU', 'ESW', 'HOST'],
  ['EILNT', 'AHIKS', 'OST', 'BEINT', 'EOU', 'AIST', 'EHIOT', 'DEEUU', 'ADHS', 'EEHPT', 'CLOR', 'ENTU', 'AELT', 'ACLOR', 'CEEF', 'GGLM', 'AEIIO', 'ITU', 'AART', 'AIJN', 'EHIL', 'ATY', 'ARST', 'CEMR', 'CEL'],
  ['DISW', 'ABLNT', 'FMOS', 'EFRT', 'EILOS', 'EERT', 'NNUW', 'FNVW', 'CEHNR', 'ADDLN', 'HRY', 'COOP', 'BBHNO', 'EEOO', 'EIPR', 'FMR', 'EENS', 'EMRS', 'EN', 'AGRT', 'ADU', 'AAES', 'RRSTT', 'EHIM', 'AAE'],
  ['HPR', 'ADEI', 'ESU', 'EGIP', 'HLMR', 'ENOP', 'AGGT', 'AII', 'EINT', 'EGRY', 'EEST', 'BDFL', 'ORSY', 'AFS', 'AD', 'EINTW', 'AABL', 'DDL', 'EOTU', 'NSV', 'ENY', 'EGN', 'ADT', 'BTY', 'DET'],
  ['DEIOT', 'FHMNP', 'ER', 'IITT', 'ANT', 'AMO', 'MRS', 'FHIW', 'AACE', 'AEO', 'IL', 'EFIP', 'EEY', 'BDNW', 'PR', 'CCW', 'AEEO', 'LMS', 'AILU', 'EPT', 'DHIO', 'ANOS', 'ANS', 'NR', 'AHO'],
  ['CIOO', 'DHIV', 'AEEH', 'FNNO', 'HOOR', 'ESTT', 'EFT', 'ANW', 'EILNO', 'GMMW', 'FNS', 'FOTT', 'CFHO', 'HLORT', 'EHT', 'EFLS', 'EEHIN', 'ERT', 'EER', 'DES', 'AFT', 'AAT', 'BFO', 'HNS', 'AMW'],
  ['HPSW', 'CCFIT', 'RSS', 'ADNNS', 'CRSUU', 'EHMY', 'AAHHP', 'DEIOT', 'DSY', 'ERT', 'GHO', 'HOORU', 'AIU', 'DEO', 'ISU', 'BGHNS', 'FPRT', 'ELNW', 'EGITT', 'CEIIY', 'HOT', 'AHMO', 'EERS', 'EINR', 'EHLU'],
]
export const WIDTH = 25;
export const NUM_GRIDS = 7;
const SOLUTION_LETTERS_UP = [
  ['HNI', 'EI', 'WHI', 'AS', 'T', 'TP', 'A', 'BN', 'OS', 'AW', 'NT', 'AT', 'ALL', 'LNN', 'ES', 'COT', 'U', 'I', 'HR', 'AN', 'TV', 'CEF', 'OT', 'EW', 'OST'],
];
const SOLUTION_LETTERS_DOWN: string[][] = [];
export const SOLUTION_LETTERS_UP_INDICES: Set<number>[][] = [];

// Check data is consistent.
assert(BOARDS.length === NUM_GRIDS);
assert(LETTERS.length === NUM_GRIDS);

// Allocate letters to the dropquote.
type LetterBoardCell = { readonly type: 'letter', readonly value: string };
type BoardCell =
  | { readonly type: 'empty' }
  | { readonly type: 'fixed', readonly value: string }
  | LetterBoardCell;

const allocations: ReadonlyArray<ReadonlyArray<BoardCell>>[] = [];
const lettersByCol: Record<number, string> = {};
for (let col = 0; col < WIDTH; col++) {
  lettersByCol[col] = '';
}

for (let boardIndex = 0; boardIndex < NUM_GRIDS; boardIndex++) {
  const boardInfo: BoardCell[][]  = [];
  const state = {
    row: -1,
    col: WIDTH - 1,
    isFirstWord: true,
  };
  const incrementPointer = () => {
    if (state.col === WIDTH - 1) {
      boardInfo.push([]);
      state.row += 1;
      state.col = 0;
    } else {
      state.col += 1;
    }
  }
  for (const word of BOARDS[boardIndex].split(' ')) {
    if (!state.isFirstWord) {
      incrementPointer();
      boardInfo[state.row].push({ type: 'empty'});
    } else {
      state.isFirstWord = false;
    }

    for (const letter of word) {
      incrementPointer();
      assert(letter === letter.toUpperCase());
      if (/[A-Z]/.test(letter)) {
        boardInfo[state.row].push({ type: 'letter', value: letter });
        lettersByCol[state.col] += letter;
      } else if (letter === ' ') {
        boardInfo[state.row].push({ type: 'empty' });
      } else {
        boardInfo[state.row].push({ type: 'fixed', value: letter });
      }
    }
  }
  const lastRow = boardInfo[boardInfo.length - 1];
  while (lastRow.length < WIDTH) {
    lastRow.push({ type: 'empty' });
  }
  allocations.push(boardInfo);
}

for (let col = 0; col < WIDTH; col++) {
  let colLetters = '';
  for (let board = 0; board < NUM_GRIDS; board++) {
    const letters = LETTERS[board][col];
    colLetters += letters;

    assert(letters === sortedString(letters));
  }
  const sortedColLetters = sortedString(colLetters);
  const sortedExpectedColLetters = sortedString(lettersByCol[col]);
  assert(sortedColLetters === sortedExpectedColLetters);
}

export const ALLOCATIONS: ReadonlyArray<ReadonlyArray<ReadonlyArray<BoardCell>>> = allocations;

// Generate solution letter allocations.
for (let boardIndex = 0; boardIndex < NUM_GRIDS; boardIndex++) {
  const upLetters: string[] = [];
  const downLetters = [];
  for (let col = 0; col < WIDTH; col++) {
    const colDownLetters = difference([...LETTERS[boardIndex][col]], SOLUTION_LETTERS_UP[boardIndex][col]);
    downLetters.push(colDownLetters);

    const nextBoardLetters = getBoardCol((boardIndex + 1) % NUM_GRIDS, col, {keepEmpty: false});
    upLetters.push(difference(nextBoardLetters, downLetters[col]));
  }
  if (boardIndex < NUM_GRIDS - 1) {
    SOLUTION_LETTERS_UP.push(upLetters);
  } else {
    assert(SOLUTION_LETTERS_UP[0].every((cell, col) => {
      return sortedString(cell) === sortedString(upLetters[col]);
    }));
  }
  SOLUTION_LETTERS_DOWN.push(downLetters);
}
// And then allocate indices to each from within the board.
for (let boardIndex = 0; boardIndex < NUM_GRIDS; boardIndex++) {
  const colUpIndices = [];
  for (let col = 0; col < WIDTH; col++) {
    const indices = new Set<number>();
    const letters = getBoardCol(boardIndex, col, {keepEmpty: true});
    for (const letter of SOLUTION_LETTERS_UP[boardIndex][col]) {
      let fromIndex = 0;
      let index = letters.indexOf(letter, fromIndex);
      while (indices.has(index)) {
        fromIndex = index + 1;
        index = letters.indexOf(letter, fromIndex);
      }
      assert(index > -1, `Could not find ${SOLUTION_LETTERS_UP[boardIndex][col]} in ${letters}`);
      indices.add(index);
    }
    colUpIndices.push(indices);
  }
  SOLUTION_LETTERS_UP_INDICES.push(colUpIndices);
}

function difference(haystack: (string | null)[], needle: string) {
  const used = new Set<number>();
  for (const letter of needle) {
    let fromIndex = 0;
    let index = haystack.indexOf(letter, fromIndex);
    while (used.has(index)) {
      fromIndex = index + 1;
      index = haystack.indexOf(letter, fromIndex);
    }
    assert(index > -1, `Could not find ${needle} in ${haystack}`);
    used.add(index);
  }
  return [...haystack].filter((_, i) => !used.has(i)).join('');
}

function sortedString(a: string) {
  return a.split('').sort().join('').toUpperCase();
}

function getBoardCol(boardIndex: number, col: number, {keepEmpty}: {keepEmpty: boolean}) {
  return ALLOCATIONS[boardIndex]
      .map(row => row[col])
      .map(cell => cell.type === 'letter' ? cell.value : null)
      .filter(value => keepEmpty || !!value);
}
