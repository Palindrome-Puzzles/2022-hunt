import htm from "htm";
import { h, Component } from "preact";
import {GamePiece, PieceType} from './game-manager';
import {assertTruthy} from '@common/helpers';

const html = htm.bind(h);

interface GamePieceDisplayProps {
  readonly piece?: GamePiece;
  readonly clickable: boolean;
  readonly ariaLabel: string;
  readonly focusable: boolean;
  readonly handleDragstart: ((event: DragEvent) => void) | null;
  readonly handleDragend: ((event: DragEvent) => void) | null;
}

export class GamePieceDisplay extends Component<GamePieceDisplayProps> {
  render() {
    const staticDirectory = assertTruthy(window.puzzleStaticDirectory)
    let pieceDisplay = html``;
    if (this.props.piece) {
      switch (this.props.piece.type) {
        case PieceType.FeudalLord:
        case PieceType.General:
        case PieceType.Man:
        case PieceType.Minister:
          pieceDisplay = html`
            <img
              src="${staticDirectory}game8/images/${this.props.piece.type}.png"
              alt="${this.props.piece.type}"
            />`;
          break;

        case PieceType.King:
          const color = this.props.piece.player === 1 ? 'red' : 'blue';
          pieceDisplay = html`
            <img
              src="${staticDirectory}game8/images/${color}-${this.props.piece.type}.png"
              alt="${this.props.piece.type}"
            />`;
          break;
      }
    }
    return html`<button
          type="button"
          aria-disabled="${!this.props.clickable}"
          draggable="${this.props.clickable}"
          onDragstart="${this.props.handleDragstart}"
          onDragend="${this.props.handleDragend}"
          tabindex="${this.props.focusable ? 0 : -1}"
          class="unstyled ${this.props.piece ? 'piece-wrapper' : ''}"
          aria-label="${this.props.ariaLabel}${this.props.clickable ? '' : ' (invalid)'}"
        >${pieceDisplay}</button>`;
  }
}
