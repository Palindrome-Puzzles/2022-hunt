import htm from "htm";
import { h, Component } from "preact";
import { assert, fetchJson } from "@common/helpers";
import {GameManager, HasId, PieceType, GamePiece,GameStatus, GameSquare, GamePlayer, GameMove, CollatedCaptures, CollatedInPlays} from './game-manager';
import {GameBoard} from './game-board';

const html = htm.bind(h);

const MAX_MOVES = 4;

declare global {
  interface Window {
    game8Initial?: () => Promise<InitialResponse>;
    game8Check?: (request: CheckRequest) => Promise<CheckResponse>;
  }
}

interface GameProps {}
interface GameState {
  readonly playerTurn: GamePlayer | null;
  readonly moveNumber: number | null;
  readonly captures: CollatedCaptures | null;
  readonly pieces: CollatedInPlays | null;

  readonly waiting: boolean;
  readonly completeMessage: string | null;
  readonly retryHandler: (() => void) | null;
}

interface InitialResponse {
  readonly playerTurn: GamePlayer;
  readonly pieces: ReadonlyArray<GamePiece>;
  readonly moveNumber: number;
}
type CheckRequest = ReadonlyArray<GameMove>;
interface CheckResponse {
  readonly optimal: boolean;
}

export class Game extends Component<GameProps, GameState> {
  private static cachedInitialState?: InitialResponse;

  private gameManager?: GameManager;

  constructor(props: GameProps) {
    super(props);
    this.restart();
  }

  restart() {
    const state: GameState = {
      playerTurn: null,
      moveNumber: null,
      captures: null,
      pieces: null,

      waiting: true,
      completeMessage: null,
      retryHandler: null,
    };
    this.setState(state);

    const fetchInitialState = Game.cachedInitialState
      ? Promise.resolve(Game.cachedInitialState)
      : window.game8Initial
        ? window.game8Initial()
        : fetchJson<void, InitialResponse>(`${window.puzzleUrl}game8/board`);
    fetchInitialState
      .then(response => {
        Game.cachedInitialState = response;

        const { playerTurn, moveNumber, pieces } = response;
        this.gameManager = new GameManager(playerTurn, moveNumber, pieces);
        this.setState({
          ...this.gameManager.getCollated(),
          waiting: false,
        });
      })
      .catch(err => {
        this.setState({
          // restart() is idempotent, can blindly retry.
          retryHandler: () => this.restart(),
        });
      });
  }

  makeMove(piece: GamePiece & HasId, toSquare: GameSquare) {
    assert(this.gameManager);

    const [status, winner] = this.gameManager.move(piece.id, toSquare);
    let maybeWon = false;
    let completeMessage: string | null = null;
    if (status === GameStatus.Checkmate) {
      if (winner === 1 && piece.type === PieceType.General) {
        maybeWon = true;
      } else if (winner === 1) {
        completeMessage = 'Did not mate with General. Please retry!';
      } else {
        completeMessage = 'Player 1 lost instead. Please retry!';
      }
    } else if (status === GameStatus.FinalRank) {
      if (winner === 1) {
        completeMessage = 'Player 1 won, but not by mate. Please retry!';
      } else {
        completeMessage = 'Player 1 lost instead. Please retry!';
      }
    } else if (status === GameStatus.Stalemate) {
      completeMessage = 'Did not mate with General. Please retry!';
    } else if (this.state.moveNumber === MAX_MOVES) {
      completeMessage = 'Out of moves. Please retry!';
    }

    if (maybeWon) {
      const checkOptimal = () => {
        assert(this.gameManager);
        this.setState({
          ...this.gameManager.getCollated(),
          completeMessage,
          waiting: maybeWon,
          retryHandler: null,
        });

        const check = window.game8Check
          ? window.game8Check(this.gameManager.getMoves())
          : fetchJson<CheckRequest, CheckResponse>(`${window.puzzleUrl}game8/check`, this.gameManager.getMoves());

        check
          .then(({optimal}) => {
            this.setState({
              completeMessage: optimal
                ? 'Congratulations - Player 1 won!'
                : 'Player 2 did not defend optimally. Please retry!',
              waiting: false,
            });
          })
          .catch(err => {
            this.setState({
              retryHandler: checkOptimal,
            });
          });
      };
      checkOptimal();
    } else {
      this.setState({
        ...this.gameManager.getCollated(),
        completeMessage,
        waiting: false,
        retryHandler: null,
      });
    }
  }

  render() {
    const disconnectedBanner = this.state.retryHandler
      ? html`<div class="disconnected banner no-copy" role="alert">
          Connection lost.
          <button type="button" onClick=${() => this.state.retryHandler && this.state.retryHandler()}>
            Retry
          </button>
        </div>`
      : '';
    const getPossibleMoves =
      this.gameManager ? this.gameManager.getPossibleMoves.bind(this.gameManager) : () => [];
    return html`${disconnectedBanner}
      <${GameBoard}
        makeMove=${this.makeMove.bind(this)}
        restart=${this.restart.bind(this)}
        getPossibleMoves=${getPossibleMoves}
        waiting=${this.state.waiting}
        isDisconnected=${!!this.state.retryHandler}
        completeMessage=${this.state.completeMessage}
        playerTurn=${this.state.playerTurn}
        moveNumber=${this.state.moveNumber}
        pieces=${this.state.pieces}
        captures=${this.state.captures}
      />`;
  }
}
