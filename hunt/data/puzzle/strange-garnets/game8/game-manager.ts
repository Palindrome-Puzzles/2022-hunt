import { assert, assertTruthy } from "@common/helpers";
import {pick} from 'lodash-es';

export class GameManager {
  private piecesList: ReadonlyArray<GamePiece & HasId>;
  private readonly moves: GameMove[] = [];

  constructor(
    private playerTurn: GamePlayer,
    private moveNumber: number,
    piecesList: ReadonlyArray<GamePiece>
  ) {
    this.piecesList = injectIds(piecesList);
  }

  getCollated() {
    return {
      playerTurn: this.playerTurn,
      moveNumber: this.moveNumber,
      ...collatePieces(this.piecesList),
    };
  }

  getMoves(): ReadonlyArray<GameMove> {
    return this.moves;
  }

  getPossibleMoves(id: string): Moves {
    return getPossibleMoves(this.piecesList, this.playerTurn, id);
  }

  move(id: string, square: GameSquare) {
    square = pick(square, 'rank', 'file');

    const piece = assertTruthy(findPiece(this.piecesList, {id}));
    assert(!inCheckAfterMove(this.piecesList, this.playerTurn, piece, square));

    const takenPiece = findPiece(this.piecesList, square);

    const originalPlayer = this.playerTurn;
    const finalRank = this.playerTurn === 1 ? 4 : 1;
    const shouldPromote = piece.type === PieceType.Man && square.rank === finalRank;
    const newPieces = [];
    newPieces.push({
      ...piece,
      ...square,
      type: shouldPromote ? PieceType.FeudalLord : piece.type,
    });
    if (takenPiece) {
      newPieces.push({
        ...takenPiece,
        rank: null,
        file: null,
        player: getOtherPlayer(takenPiece.player),
        type: takenPiece.type === PieceType.FeudalLord ? PieceType.Man : takenPiece.type,
      });
    }

    if (this.playerTurn === 2) {
      this.moveNumber++;
    }
    this.playerTurn = getOtherPlayer(this.playerTurn);

    this.piecesList = [
      ...this.piecesList.filter(
        existingPiece => existingPiece !== piece && existingPiece !== takenPiece),
      ...newPieces,
    ];

    this.moves.push({
      type: piece.type,
      fromRank: piece.rank,
      fromFile: piece.file,
      toRank: square.rank,
      toFile: square.file,
    });

    if (isCheckmate(this.piecesList, originalPlayer)) {
      return [GameStatus.Checkmate, originalPlayer] as const;
    } else if (piece.type === PieceType.King && square.rank === finalRank) {
      const isCheck = !getThreateners(this.piecesList, getOtherPlayer(originalPlayer), square);
      const winner: GamePlayer = isCheck ? getOtherPlayer(originalPlayer) : originalPlayer;
      return [GameStatus.FinalRank, winner];
    } else if (isStalemate(this.piecesList, this.playerTurn)) {
      return [GameStatus.Stalemate, null];
    } else {
      return [GameStatus.Unfinished, null] as const;
    }
  }
}

export const RANKS = [1, 2, 3, 4] as const;
export const FILES = [1, 2, 3] as const;
export const PLAYERS = [1, 2] as const;
export type GameRank = typeof RANKS[number];
export type GameFile = typeof FILES[number];
export type GamePlayer = typeof PLAYERS[number];

export const enum PieceType {
  King = "king",
  General = "general",
  Minister = "minister",
  Man = "man",
  FeudalLord = "feudal-lord",
}
export const enum GameStatus {
  Unfinished = 1,
  Checkmate,
  FinalRank,
  Stalemate,
}

// prettier-ignore
const ALLOWED_MOVES = {
  [PieceType.King]: [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]],
  [PieceType.General]: [[-1, 0], [0, -1], [0, 1], [1, 0]],
  [PieceType.Minister]: [[-1, -1], [-1, 1], [1, -1], [1, 1]],
  [PieceType.Man]: [[1, 0]],
  [PieceType.FeudalLord]: [[1, -1], [-1, 0], [1, 1], [0, -1], [0, 1], [1, 0]],
};

export interface HasId {
  readonly id: string;
}
export type Moves = ReadonlyArray<{
  readonly square: GameSquare;
  readonly valid: boolean;
}>;

export interface GameSquare {
  readonly rank: GameRank;
  readonly file: GameFile;
}

export interface GamePieceInPlay {
  readonly type: PieceType;
  readonly player: GamePlayer;
  readonly rank: GameRank;
  readonly file: GameFile;
}
export interface GamePieceCaptured {
  readonly type: PieceType;
  readonly player: GamePlayer;
  readonly rank: null;
  readonly file: null;
}
export type GamePiece = GamePieceInPlay | GamePieceCaptured;

export interface GameMove {
  readonly type: PieceType;
  readonly fromRank: GameRank | null;
  readonly fromFile: GameFile | null;
  readonly toRank: GameRank;
  readonly toFile: GameFile;
}

export type CollatedCaptures = ReadonlyMap<GamePlayer, ReadonlyArray<GamePieceCaptured & HasId>>;
export type CollatedInPlays = ReadonlyMap<GameRank, ReadonlyMap<GameFile, GamePieceInPlay & HasId>>;

function isReachable(piece: GamePieceInPlay, target: GameSquare) {
  const deltaFactor = piece.player === 1 ? 1 : -1;
  const deltaRank = (target.rank - piece.rank) * deltaFactor;
  const deltaFile = (target.file - piece.file) * deltaFactor;
  return ALLOWED_MOVES[piece.type].some(
    (move) => move[0] === deltaRank && move[1] === deltaFile
  );
}

function getThreateners(
  pieces: ReadonlyArray<GamePiece>,
  threatenerPlayer: GamePlayer,
  target: GameSquare
): ReadonlyArray<GamePieceInPlay> {
  const threateners = [];
  for (const piece of pieces) {
    if (piece.player !== threatenerPlayer) continue;
    if (!piece.rank) continue;
    if (isReachable(piece, target)) {
      threateners.push(piece);
    }
  }
  return threateners;
}

function findPiece<P extends GamePiece>(
  pieces: ReadonlyArray<P>,
  matcher: Partial<P>
) {
  return pieces.find((piece) =>
    (Object.keys(matcher) as ReadonlyArray<keyof GamePiece>).every(
      (key) => piece[key] === matcher[key]
    )
  );
}

function getOtherPlayer(player: GamePlayer): GamePlayer {
  return player === 1 ? 2 : 1;
}

function inCheckAfterMove(
  pieces: ReadonlyArray<GamePiece>,
  playerTurn: GamePlayer,
  fromPiece: GamePiece,
  toSquare: GameSquare
) {
  const kingLocation =
    fromPiece.type === PieceType.King
      ? toSquare
      : findPiece(pieces, { type: PieceType.King, player: playerTurn });
  assert(kingLocation, "king location");
  assert(kingLocation.rank, "king should be on board");

  const threateners = getThreateners(pieces, getOtherPlayer(playerTurn), kingLocation);
  for (const threatener of threateners) {
    // If threatening piece was just taken, ignore.
    if (
      threatener.rank === toSquare.rank &&
      threatener.file === toSquare.file
    ) {
      continue;
    }
    return true;
  }
  return false;
}

function isCheckmate(pieces: ReadonlyArray<GamePiece>, playerTurn: GamePlayer) {
  const otherKing = findPiece(pieces, {type: PieceType.King, player: getOtherPlayer(playerTurn)});
  assert(otherKing && otherKing.rank);
  const threateners = getThreateners(pieces, playerTurn, otherKing);

  // Is the king even in check?
  if (!threateners.length) {
    return false;
  }

  // Can the threatening piece be taken?
  if (threateners.length === 1) {
    const threatener = threateners[0];
    const canTakeThreatener = getThreateners(pieces, getOtherPlayer(playerTurn), threatener);
    // If there are multiple takers, the non-king one can take it.
    if (canTakeThreatener.length > 1) {
      return false;
    }
    // If the only piece that can take it isn't the king, all good.
    if (canTakeThreatener.length === 1 && canTakeThreatener[0].type !== PieceType.King) {
      return false;
    }
    // If the only piece that can take it is the king, check if the threatener isn't defended.
    else if (canTakeThreatener.length === 1) {
      const threatenerDefenders = getThreateners(pieces, playerTurn, threatener);
      if (!threatenerDefenders.length) {
        return false;
      }
    }
  }

  // Can the king escape elsewhere?
  for (const [rankDelta, fileDelta] of ALLOWED_MOVES[PieceType.King]) {
    // No need to normalize delta based on player - kings move symmetrically.
    const escapeRank = (otherKing.rank + rankDelta) as GameRank;
    const escapeFile = (otherKing.file + fileDelta) as GameFile;
    if (!RANKS.includes(escapeRank) || !FILES.includes(escapeFile)) {
      continue;
    }
    const escapeSquare = {rank: escapeRank, file: escapeFile};

    // Is the escape square blocked by their own piece?
    const pieceAtSquare = findPiece(pieces, escapeSquare);
    if (pieceAtSquare && pieceAtSquare.player === getOtherPlayer(playerTurn)) {
      continue;
    }
    // Is the escape square also threatened?
    const escapeThreateners = getThreateners(pieces, playerTurn, escapeSquare);
    if (escapeThreateners.length) {
      continue;
    }
    // We found an escape!
    return false;
  }

  return true;
}

function isStalemate(pieces: ReadonlyArray<GamePiece & HasId>, playerTurn: GamePlayer) {
  for (const piece of pieces) {
    if (piece.player !== playerTurn) continue;
    const validMoves = getPossibleMoves(pieces, playerTurn, piece.id).filter(move => move.valid);
    if (validMoves.length) {
      return false;
    }
  }
  return true;
}

function getPossibleMoves(pieces: ReadonlyArray<GamePiece & HasId>, playerTurn: GamePlayer, id: string): Moves {
  const piece = assertTruthy(findPiece(pieces, {id}));
  if (piece.player !== playerTurn) {
    return [];
  }

  const possibleSquares = [];
  for (const rank of RANKS) {
    for (const file of FILES) {
      const targetPiece = findPiece(pieces, {rank, file});
      const isEmpty = !targetPiece;
      let possible;
      if (piece.rank) {
        const isOtherPlayers = !!targetPiece && targetPiece.player !== playerTurn;
        const reachable = isReachable(piece, {rank, file});
        possible = (isEmpty || isOtherPlayers) && reachable;
      } else {
        const finalRank = playerTurn === 1 ? 4 : 1;
        const isFinalRank = rank === finalRank;
        possible = isEmpty && !isFinalRank;
      }

      if (possible) {
        possibleSquares.push({ rank, file });
      }
    }
  }

  return possibleSquares.map(square => ({
    square,
    valid: !inCheckAfterMove(pieces, playerTurn, piece, square),
  }));
}

function collatePieces(piecesList: ReadonlyArray<GamePiece & HasId>): {
  readonly captures: CollatedCaptures;
  readonly pieces: CollatedInPlays;
} {
  const captures = new Map<GamePlayer, Array<GamePieceCaptured & HasId>>();
  const pieces = new Map<GameRank, Map<GameFile, GamePieceInPlay & HasId>>();
  for (const player of PLAYERS) {
    captures.set(player, []);
  }
  for (const rank of RANKS) {
    pieces.set(rank, new Map<GameFile, GamePieceInPlay & HasId>());
  }
  for (const piece of piecesList) {
    if (piece.rank) {
      pieces.get(piece.rank)!.set(piece.file, piece);
    } else {
      captures.get(piece.player)!.push(piece);
    }
  }
  for (const player of PLAYERS) {
    captures.get(player)!.sort((a, b) => a["type"].localeCompare(b["type"]));
  }
  return { captures, pieces };
}

function injectIds(pieces: ReadonlyArray<GamePiece>): ReadonlyArray<GamePiece & HasId> {
  return pieces.map((piece, i) =>({
    ...piece,
    id: i.toString(),
  }));
}
