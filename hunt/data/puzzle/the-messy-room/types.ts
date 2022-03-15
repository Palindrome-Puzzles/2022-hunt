export interface Cell {
  readonly board: number;
  readonly row: number;
  readonly col: number;
  readonly letter: string | null;
}
export interface CellUpdates extends Cell {
  readonly action: "cell";
}
export interface UsedIndex {
  readonly board: number;
  readonly col: number;
  readonly index: number;
}
export interface UsedIndexUpdates extends UsedIndex {
  readonly action: "usedIndex";
  readonly used: boolean;
}
export type Updates = CellUpdates | UsedIndexUpdates;

export interface Refresh {
  readonly cells: ReadonlyArray<Cell>;
  readonly usedIndices: ReadonlyArray<UsedIndex>;
}
export type Partial = Updates;
