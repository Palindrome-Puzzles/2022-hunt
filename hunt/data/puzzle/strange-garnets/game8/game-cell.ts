import htm from "htm";
import { h, Component } from "preact";
import {GamePieceInPlay, GameSquare, HasId} from './game-manager';
import {GamePieceDisplay} from './game-piece-display';

const html = htm.bind(h);

interface GameCellProps extends GameSquare {
  readonly selected: boolean;
  readonly canMoveFrom: boolean;
  readonly canMoveTo: boolean;
  readonly piece: GamePieceInPlay & HasId | null;
  readonly focusable: boolean;
  readonly handleDragstart: ((event: DragEvent) => void) | null;
  readonly handleDragend: ((event: DragEvent) => void) | null;
  readonly handleDragenter: ((event: DragEvent) => void) | null;
  readonly handleDrop: ((event: DragEvent) => void) | null;
}

export class GameCell extends Component<GameCellProps> {
  render() {
    const classes = ["piece", "in-play"];
    if (this.props.piece) {
      classes.push(this.props.piece.type, `p${this.props.piece.player}`);
    }
    if (this.props.selected) {
      classes.push("selected");
    }
    if (this.props.canMoveFrom) {
      classes.push("move-from");
    }
    if (this.props.canMoveTo) {
      classes.push("move-to");
    }
    const clickable = this.props.canMoveFrom || this.props.canMoveTo;
    const ariaLabel =
      'ABC'[this.props.file - 1]
      + this.props.rank.toString()
      + (this.props.piece
        ? ` (Player ${this.props.piece.player} ${this.props.piece.type})`
        : '');
    const onDragover =
      this.props.handleDragenter
        ? (event: DragEvent) => { event.preventDefault() }
        : null;

    return html`
      <td
        data-clickable="${clickable}"
        data-rank="${this.props.rank}"
        data-file="${this.props.file}"
        data-type="${this.props.piece ? this.props.piece.type : null}"
        data-id="${this.props.piece ? this.props.piece.id : null}"
        class="${classes.join(" ")}"
        onDragenter="${this.props.handleDragenter}"
        onDragover="${onDragover}"
        onDrop="${this.props.handleDrop}"
      >
        <${GamePieceDisplay}
          piece="${this.props.piece}"
          clickable="${clickable}"
          ariaLabel="${ariaLabel}"
          focusable="${this.props.focusable}"
          handleDragstart="${this.props.handleDragstart}"
          handleDragend="${this.props.handleDragend}"
        />
      </td>`;
  }
}
