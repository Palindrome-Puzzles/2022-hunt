import { SessionPuzzle } from '@common/session-puzzle';
import { RetriableSessionPuzzle } from '@common/retriable-session-puzzle';
import { Component } from 'preact';
import { assert, assertTruthy } from '@common/helpers';
import {LevelInfo, Card, CardAction, html } from './common';
import {GamePickLevel} from './game-pick-level';
import {GamePlay} from './game-play';
import {GameSelectCards} from './game-select-cards';

type State = 'pick-level' | 'select-cards' | 'play';

interface InitialResponse {}

interface GameRequestBegin {
  readonly action: 'begin';
  readonly level: number;
}
interface GameResponseBegin {
  readonly deck: ReadonlyArray<Card>;
  readonly allowOrientation: boolean;
}
interface GameRequestSelect {
  readonly action: 'select';
  readonly deck: ReadonlyArray<Card>;
}
interface GameResponseSelect {
  readonly deck: ReadonlyArray<Card>;
}
interface GameRequestPlay {
  readonly action: 'open' | 'pass';
}
interface GameResponsePlay {
  readonly deck: ReadonlyArray<Card>;
  readonly opened: number;
  readonly played: number;
  readonly score: number | null;
}
type GameRequest = GameRequestBegin | GameRequestSelect | GameRequestPlay;
type GameResponse = GameResponseBegin | GameResponseSelect | GameResponsePlay;

interface GameProps {
  readonly levels: ReadonlyArray<LevelInfo>;
}
interface GameState {
  readonly state: State;
  readonly waiting: boolean;

  readonly level: number | null;
  readonly deck: ReadonlyArray<Card>;
  readonly allowOrientation: boolean;

  readonly opened: number | null;
  readonly played: number | null;
  readonly score: number | null;

  readonly isError: boolean;
  readonly isDisconnected: boolean;
  readonly retryHandler: (() => void) | null;
}

export class Game extends Component<GameProps, GameState> {
  readonly retriableSession: RetriableSessionPuzzle<InitialResponse, GameRequest, GameResponse>;

  constructor(props: GameProps) {
    super(props);

    this.goToLevelChooser();

    const session = new SessionPuzzle<InitialResponse, GameRequest, GameResponse>(`${window.puzzleUrl}game6/play`);
    this.retriableSession = new RetriableSessionPuzzle(session, {
      setDisconnected: (isDisconnected: boolean) => {
        this.setState({ isDisconnected });
      },
      onRetry: (retryHandler: () => void) => {
        this.setState({ retryHandler });
      },
    });
  }

  goToLevelChooser() {
    const state: GameState = {
      state: 'pick-level',
      waiting: false,

      level: null,
      deck: [],
      allowOrientation: false,

      opened: null,
      played: null,
      score: null,

      isError: false,
      isDisconnected: false,
      retryHandler: null,
    };
    this.setState(state);
  }

  pickLevel(level: number) {
    this.setState({ waiting: true });
    this.retriableSession.initialize({ allowIncomplete: true })
      .then(() => this.update({ action: 'begin', level }))
      .catch(() => {
        this.setState({ isError: true });
      });
  }

  update(request: GameRequest) {
    this.setState({ waiting: true });

    this.retriableSession.send(request).then(
      ({response}) => {
        if (request['action'] === 'begin') {
          const typedResponse = response as GameResponseBegin;
          this.setState({
            state: 'select-cards',
            waiting: false,

            level: request.level,
            deck: typedResponse.deck,
            allowOrientation: typedResponse.allowOrientation,

            opened: null,
            played: null,
            score: null,
          });
        } else if (request['action'] === 'select') {
          const typedResponse = response as GameResponseSelect;
          this.setState({
            state: 'play',
            waiting: false,

            deck: typedResponse.deck,
            opened: 0,
            played: 0,
          });
        } else {
          const typedResponse = response as GameResponsePlay;
          this.setState({
            state: 'play',
            waiting: false,

            deck: typedResponse.deck,
            opened: typedResponse.opened,
            played: typedResponse.played,
            score: typedResponse.score,
          });
        }
      },
      () => {
        this.setState({ isError: true });
      });
  }

  render() {
    const errorBanner = this.state.isError ?
      html`<div class="error banner no-copy" role="alert">
        Something went wrong. Please contact the hunt team to fix this!
      </div>` :
      '';
    const disconnectedBanner = this.state.isDisconnected && !this.state.isError
      ? html`<div class="disconnected banner no-copy" role="alert">
          Connection lost.
          <button type="button" onClick=${() => this.state.retryHandler && this.state.retryHandler()}>
            Retry
          </button>
        </div>`
      : '';

    let board;
    const levelInfo = !!this.state.level && this.props.levels.find(levelInfo => levelInfo.level === this.state.level);
    switch (this.state.state) {
      case 'pick-level':
        board = html`<${GamePickLevel}
          waiting=${this.state.waiting || !this.props.levels.length}
          hideStatus=${this.state.isDisconnected || this.state.isError}
          levels=${this.props.levels}
          onPick=${(level: number) => this.pickLevel(level)}
        />`;
        break

      case 'select-cards':
        assert(levelInfo);
        board = html`<${GameSelectCards}
          waiting=${this.state.waiting}
          hideStatus=${this.state.isDisconnected || this.state.isError}
          level=${levelInfo.level}
          deck=${this.state.deck}
          target=${levelInfo.target}
          allowOrientation=${this.state.allowOrientation}
          onSelect=${(deck: ReadonlyArray<Card>) => {
            this.update({ action: 'select', deck });
          }}
          onAbandon=${() => this.goToLevelChooser()}
        />`;
        break;

      case 'play':
        assert(levelInfo);
        board = html`<${GamePlay}
          waiting=${this.state.waiting}
          hideStatus=${this.state.isDisconnected || this.state.isError}
          deck=${this.state.deck}
          target=${levelInfo.target}
          allowOrientation=${this.state.allowOrientation}
          opened=${this.state.opened}
          played=${this.state.played}
          score=${this.state.score}
          onAction=${(action: GameRequestPlay['action']) => this.update({ action })}
          onAbandon=${() => this.goToLevelChooser()}
          onRestart=${() => this.pickLevel(assertTruthy(this.state.level))}
        />`;
        break
    }

    return html`
      ${errorBanner}
      ${disconnectedBanner}
      ${board}`;
  }
}
