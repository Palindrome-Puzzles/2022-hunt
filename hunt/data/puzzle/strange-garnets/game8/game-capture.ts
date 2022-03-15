import htm from "htm";
import { h, Component } from "preact";
import {GamePieceCaptured, HasId} from './game-manager';
import {GamePieceDisplay} from './game-piece-display';

const html = htm.bind(h);

interface GameCaptureProps {
  readonly selected: boolean;
  readonly capture: GamePieceCaptured & HasId;
  readonly canMoveFrom: boolean;
  readonly focusable: boolean;
  readonly handleDragstart: (event: DragEvent) => void;
  readonly handleDragend: (event: DragEvent) => void;
}

export class GameCapture extends Component<GameCaptureProps> {
  render() {
    const classes = [
      "piece",
      "captured",
      this.props.capture.type,
      `p${this.props.capture.player}`,
    ];
    if (this.props.selected) {
      classes.push("selected");
    }
    if (this.props.canMoveFrom) {
      classes.push("move-from");
    }

    const clickable = this.props.canMoveFrom;
    return html`<div
      data-clickable="${clickable}"
      data-type="${this.props.capture.type}"
      data-id="${this.props.capture.id}"
      class="${classes.join(" ")}"
    >
      <${GamePieceDisplay}
        piece="${this.props.capture}"
        clickable="${clickable}"
        focusable="${this.props.focusable}"
        ariaLabel="Player ${this.props.capture.player} capture: ${this.props.capture.type}"
        handleDragstart="${this.props.handleDragstart}"
        handleDragend="${this.props.handleDragend}"
      />
    </div>`;
  }
}
