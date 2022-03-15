// TODO(sahil): Find some library to do drag-and-drop that supports touch too.

import htm from "htm";
import { h, Component } from "preact";
import { assertTruthy } from "@common/helpers";
import {GamePieceCaptured, FILES, GameRank, GameFile, RANKS, HasId, PieceType, Moves, GamePiece, GameSquare, GamePlayer, CollatedCaptures, CollatedInPlays} from './game-manager';
import {GameCell} from './game-cell';
import {GameCapture} from './game-capture';

const html = htm.bind(h);

const INVALID_MOVE_CLEAR_DELAY_MS = 2000;

interface GameBoardProps {
  readonly playerTurn: GamePlayer | null;
  readonly moveNumber: number | null;
  readonly captures: CollatedCaptures | null;
  readonly pieces: CollatedInPlays | null;
  readonly waiting: boolean;
  readonly isDisconnected: boolean;
  readonly completeMessage: string | null;

  readonly makeMove: (fromPiece: GamePiece & HasId, toSquare: GameSquare) => boolean;
  readonly restart: () => void;
  readonly getPossibleMoves: (id: string) => Moves;
}
interface GameBoardState {
  selectedPiece: GamePiece & HasId | null;
  invalidMove: boolean;
  invalidMoveTimer: number | null;
  captureFocus: [number, number];
  boardFocus: GameSquare;
}

export class GameBoard extends Component<GameBoardProps, GameBoardState> {
  constructor(props: GameBoardProps) {
    super(props);

    this.state = {
      selectedPiece: null,
      invalidMove: false,
      invalidMoveTimer: null,
      captureFocus: [-1, -1],
      boardFocus: {rank: 1, file: 1},
    };
  }

  restart() {
    this.setState({
      selectedPiece: null,
      invalidMove: false,
      invalidMoveTimer: null,
    });
    this.props.restart();
  }

  render() {
    const mode = this.getMode();
    const classes = ['puzzle-status', 'banner', 'no-copy'];
    if (this.props.completeMessage) {
      classes.push('complete');
    }
    if (this.state.invalidMove) {
      classes.push('invalid');
    }
    const statusBanner = this.props.isDisconnected
      ? ''
      : html`<div class="${classes.join(" ")}" role="${this.state.invalidMove ? 'alert' : 'status'}">
          ${this.getStatus()}
          <button type="button" onClick=${() => this.restart()} disabled="${this.props.waiting}">
            Restart
          </button>
        </div>`;

    const possibleMoves =
      this.state.selectedPiece ? this.props.getPossibleMoves(this.state.selectedPiece.id) : [];
    const getBoardCell = (rank: GameRank, file: GameFile) => {
      const piece = this.props.pieces ? this.props.pieces.get(rank)!.get(file) : null;
      const selected = piece && this.state.selectedPiece
        ? piece.id === this.state.selectedPiece.id
        : false;
      const canMoveFrom = mode === 'from' && piece && piece.player === this.props.playerTurn;
      const canMoveTo = mode === 'to' && possibleMoves.some(
        move => move.square.rank === rank && move.square.file === file);
      const focusable = this.state.boardFocus.rank === rank && this.state.boardFocus.file === file;
      return html`<${GameCell}
        selected=${selected}
        canMoveFrom=${canMoveFrom}
        canMoveTo=${canMoveTo}
        rank=${rank}
        file=${file}
        piece=${piece}
        focusable=${focusable}
        handleDragstart="${piece ? ((event: DragEvent) => this.handleDragstart(piece, event)) : null}"
        handleDragend="${piece ? ((event: DragEvent) => this.handleDragend(event)) : null}"
        handleDragenter="${canMoveTo ? ((event: DragEvent) => this.handleDragenter({rank, file}, event)) : null}"
        handleDrop="${canMoveTo ? ((event: DragEvent) => this.handleDrop({rank, file}, event)) : null}"
      />`;
    };

    const getCapture = (player: GamePlayer, capture: GamePieceCaptured & HasId, focusable: boolean) => {
      const selected = this.state.selectedPiece
        ? capture.id === this.state.selectedPiece.id
        : false;
      const canMoveFrom = mode === 'from' && capture.player === this.props.playerTurn;
      return html`<${GameCapture}
        selected=${selected}
        capture=${capture}
        canMoveFrom=${canMoveFrom}
        focusable=${focusable}
        handleDragstart="${(event: DragEvent) => this.handleDragstart(capture, event)}"
        handleDragend="${(event: DragEvent) => this.handleDragend(event)}"
      />`;
    };
    const getPlayerCaptures = (player: GamePlayer) => {
      const captures = this.props.captures ? this.props.captures.get(player)! : [];
      const emptyClass = captures.length ? '' : 'empty';
      const focusIndex = this.getCaptureFocusIndex(player);
      return html`
        <div class="p${player} captures">
          <div class="captures-wrapper ${emptyClass}">
            ${captures.map((capture, index) => getCapture(player, capture, index === focusIndex))}
          </div>
        </div>`;
    };

    return html`
      ${statusBanner}
      <div
        class="game-area ${mode}"
        onClick="${(event: Event) => this.handleClick(event)}"
        onKeydown="${(event: KeyboardEvent) => this.handleKeydown(event)}"
        onFocusCapture="${(event: FocusEvent) => this.handleFocus(event)}"
        tabindex="-1"
      >
        ${getPlayerCaptures(1)}
        <table class="board grid">
          ${FILES.map((file) =>
            html`<tr>
              ${RANKS.map((rank) => getBoardCell(rank, file))}
            </tr>`
          )}
        </table>
        ${getPlayerCaptures(2)}
      </div>`;
  }

  private getCaptureFocusIndex(player: GamePlayer) {
    const captures = this.props.captures ? this.props.captures.get(player)! : [];
    let index = this.state.captureFocus[player - 1] || -1;
    if (index >= captures.length) {
      return captures.length - 1;
    } else if (index === -1 && captures.length) {
      return 0;
    }
    return index;
  }

  handleClick(event: Event) {
    const target = assertTruthy(event.target) as HTMLElement;
    const clickableTarget = target.closest<HTMLElement>('[data-clickable]');
    if (!clickableTarget) {
      if (this.unselectPiece()) {
        event.stopPropagation();
        event.preventDefault();
      }
      return;
    }
    if (this.state.selectedPiece) {
      this.selectTo(clickableTarget.dataset);
    } else {
      this.selectFrom(clickableTarget.dataset);
    }
    event.stopPropagation();
    event.preventDefault();
  }

  private unselectPiece() {
    if (this.state.selectedPiece) {
      this.setState({ selectedPiece: null });
      return true;
    }
    return false;
  }

  private selectFrom(fromInfo: DOMStringMap) {
    this.clearInvalidMove();
    this.setState({
      selectedPiece: {
        id: fromInfo.id!,
        type: fromInfo.type as PieceType,
        player: this.props.playerTurn!,
        ...(fromInfo.rank && fromInfo.file
          ? {
              rank: parseInt(fromInfo.rank, 10) as GameRank,
              file: parseInt(fromInfo.file, 10) as GameFile,
            }
          : { rank: null, file: null }),
      }
    });
  }

  private selectTo(toInfo: DOMStringMap) {
    const toSquare = {
      rank: parseInt(toInfo.rank!, 10) as GameRank,
      file: parseInt(toInfo.file!, 10) as GameFile,
    };

    const selectedPiece = assertTruthy(this.state.selectedPiece);
    const possibleMoves = this.props.getPossibleMoves(selectedPiece.id);
    const {valid} = assertTruthy(possibleMoves.find(
      ({square}) => square.rank == toSquare.rank && square.file === toSquare.file));

    if (valid) {
      this.clearInvalidMove();
      this.setState({
        selectedPiece: null,
      });
      this.props.makeMove(selectedPiece, toSquare);
    } else {
      this.madeInvalidMove();
    }
  }

  private clearInvalidMove() {
    if (this.state.invalidMoveTimer) {
      clearTimeout(this.state.invalidMoveTimer);
      this.setState({
        invalidMove: false,
        invalidMoveTimer: null,
      });
    }
  }

  private madeInvalidMove() {
    if (this.state.invalidMoveTimer) {
      clearTimeout(this.state.invalidMoveTimer);
    }
    const invalidMoveTimer = window.setTimeout(() => {
      this.setState({
        invalidMove: false,
        invalidMoveTimer: null,
      });
    }, INVALID_MOVE_CLEAR_DELAY_MS);
    this.setState({
      selectedPiece: null,
      invalidMove: true,
      invalidMoveTimer,
    });
  }

  handleKeydown(event: KeyboardEvent) {
    const piece = event.target && (event.target as HTMLElement).closest<HTMLElement>('.piece');
    if (!piece) return;

    let handled = false;
    let newFocusPiece: HTMLElement | null = null;
    if (piece.classList.contains('captured')) {
      const player = piece.classList.contains('p1') ? 1 : 2;
      switch (event.key) {
        case 'ArrowLeft':
          this.updateCaptureFocus(player, (index) => index - 1);
          newFocusPiece = piece.previousElementSibling as HTMLElement;
          handled = true;
          break;

        case 'ArrowRight':
          this.updateCaptureFocus(player, (index) => index + 1);
          newFocusPiece = piece.nextElementSibling as HTMLElement;
          handled = true;
          break;
      }
    } else {
      const {rank, file, wasArrowKey} = this.updateBoardForKeydown(piece, event);
      if (wasArrowKey) {
        newFocusPiece = document.querySelector<HTMLElement>(`[data-rank="${rank}"][data-file="${file}"]`);
        handled = true;
      }
    }
    if (newFocusPiece) {
      newFocusPiece.querySelector('button')!.focus();
    }

    if (event.key === 'Escape' && this.state.selectedPiece) {
      this.unselectPiece();
      handled = true;
    } else if (event.key === 'Enter' || event.key === ' ') {
      this.handleClick(event);
    }

    if (handled) {
      event.preventDefault();
      event.stopPropagation();
    }
  }

  handleFocus(event: FocusEvent) {
    const piece = event.target && (event.target as HTMLElement).closest<HTMLElement>('.piece');
    if (!piece) return;

    if (piece.classList.contains('captured')) {
      const player = piece.classList.contains('p1') ? 1 : 2;
      const index = Array.from(piece.parentNode!.children).indexOf(piece);
      this.updateCaptureFocus(player, () => index);
    } else {
      const rank = parseInt(piece.dataset.rank!, 10) as GameRank;
      const file = parseInt(piece.dataset.file!, 10) as GameFile;
      this.setState({
        boardFocus: {rank, file},
      });
    }
    event.stopPropagation();
  }

  private updateCaptureFocus(player: GamePlayer, indexTransform: (oldIndex: number) => number) {
    this.setState(state => {
      const newIndex = indexTransform(state.captureFocus[player - 1]);
      if (this.props.captures && newIndex >= 0 && newIndex < this.props.captures.get(player)!.length) {
        const updated: [number, number] = [...state.captureFocus];
        updated[player - 1] = newIndex;
        return { captureFocus: updated };
      }
      return {};
    });
  }

  private updateBoardForKeydown(piece: HTMLElement, event: KeyboardEvent) {
    const rank = parseInt(piece.dataset.rank!, 10);
    const file = parseInt(piece.dataset.file!, 10);
    let newRank = rank;
    let newFile = file;
    let wasArrowKey = false;
    switch (event.key) {
      case 'ArrowUp':
        if (file > Math.min(...FILES)) {
          newFile = file - 1;
        }
        wasArrowKey = true;
        break;
      case 'ArrowDown':
        if (file < Math.max(...FILES)) {
          newFile = file + 1;
        }
        wasArrowKey = true;
        break;
      case 'ArrowLeft':
        if (rank > Math.min(...RANKS)) {
          newRank = rank - 1;
        }
        wasArrowKey = true;
        break;
      case 'ArrowRight':
        if (rank < Math.max(...RANKS)) {
          newRank = rank + 1;
        }
        wasArrowKey = true;
        break;
    }
    if (newRank !== rank || newFile !== file) {
      this.setState({
        boardFocus: {rank: newRank as GameRank, file: newFile as GameFile},
      });
    }
    return {rank: newRank, file: newFile, wasArrowKey };
  }

  handleDragstart(piece: GamePiece & HasId, event: DragEvent) {
    const pieceEl = event.target && (event.target as HTMLElement).closest<HTMLElement>('.piece');
    if (!pieceEl) return;

    this.selectFrom(pieceEl.dataset);
  }

  handleDragend(event: DragEvent) {
    this.unselectPiece();
  }

  handleDragenter(square: GameSquare, event: DragEvent) {
    if (event.dataTransfer) {
      event.dataTransfer.dropEffect = "move";
    }
    event.preventDefault();
  }

  handleDrop(square: GameSquare, event: DragEvent) {
    const pieceEl = event.target && (event.target as HTMLElement).closest<HTMLElement>('.piece');
    if (!pieceEl) return;

    this.selectTo(pieceEl.dataset);
    this.setState({
      boardFocus: square,
    });
    pieceEl.querySelector('button')!.focus();
    event.preventDefault();
  }

  private getMode() {
    if (!this.props.waiting && !this.props.completeMessage) {
      return this.state.selectedPiece ? "to" : "from";
    }
    return null;
  }

  private getStatus() {
    const movePrefix = `Player ${this.props.playerTurn} (move ${this.props.moveNumber}):`;
    if (this.props.completeMessage) {
      return this.props.completeMessage;
    } else if (this.props.waiting) {
      return "...";
    } else if (this.state.invalidMove) {
      return `Player ${this.props.playerTurn} would be in check`;
    } else if (this.state.selectedPiece) {
      return `${movePrefix} Select square to move piece to`;
    } else {
      return `${movePrefix} Select piece to move`;
    }
  }
}
