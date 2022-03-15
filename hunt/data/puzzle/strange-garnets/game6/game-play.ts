import { Component } from 'preact';
import {GameCard} from './game-card';
import { Card, CardAction, html } from './common';
import {range} from 'lodash-es';

interface GamePlayProps {
  readonly waiting: boolean;
  readonly hideStatus: boolean;

  readonly deck: ReadonlyArray<Card>;
  readonly target: number;
  readonly allowOrientation: boolean;

  readonly opened: number;
  readonly played: number;
  readonly score: number | null;
  readonly onAction: (action: CardAction) => void;
  readonly onAbandon: () => void;
  readonly onRestart: () => void;
}

export class GamePlay extends Component<GamePlayProps> {
  render() {
    let status: string | undefined;
    let showPickLevel = false;
    if (this.props.hideStatus) {
      status = undefined;
    } else if (this.props.waiting) {
      status = '...';
    } else if (this.props.score !== null && this.props.score >= this.props.target) {
      status = `Congratulations! You scored ${this.props.score}.`;
    } else if (this.props.score !== null) {
      status = `Too bad! You scored ${this.props.score}.`;
    } else {
      status = `Open ${10 - this.props.opened} of the remaining ${20 - this.props.played} cards`;
    }
    const statusBanner = status
      ? html`
        <div class="puzzle-status banner no-copy" role="status">
          ${status}
          <button type="button" onClick=${() => this.props.onAbandon()} disabled=${this.props.waiting}>
            Change level
          </button>
        </div>`
      : '';

    const opened = this.props.deck.filter(card => card.chosen);
    const passed = this.props.deck.filter((card, index) => !card.chosen && index < this.props.played).reverse();
    const current = this.props.deck[this.props.played] || null;
    const future = this.props.deck.filter((card, index) => index > this.props.played).reverse();

    return html`
      ${statusBanner}
      <div class="play-cards" tabindex="-1">
        <div class="actions">
          <div class="level-target">Target: >${this.props.target}</div>
          <div>
            <button type="button" onClick=${() => this.props.onAction('open')} disabled=${this.props.waiting || this.props.score !== null}>
              Open
            </button>
            <button type="button" onClick=${() => this.props.onAction('pass')} disabled=${this.props.waiting || this.props.score !== null}>
              Pass
            </button>
            <button type="button" onClick=${() => this.props.onRestart()} disabled=${this.props.waiting}>
              Restart
            </button>
          </div>
        </div>

        <div class="cards">
          <div class="future">
            ${future.map(card => html`
              <${GameCard}
                color=${card.color}
                allowOrientation=${this.props.allowOrientation}
                flipped=${card.orientation === 'down'}
              />`
            )}
          </div>

          ${current
            ? html`
              <${GameCard}
                color=${current.color}
                allowOrientation=${this.props.allowOrientation}
                flipped=${current.orientation === 'down'}
                focused=${true}
              />`
            : ''}

          <div class="passed">
            ${passed.map(card => html`
              <${GameCard}
                color=${card.color}
                allowOrientation=${this.props.allowOrientation}
                flipped=${card.orientation === 'down'}
              />`
            )}
          </div>
        </div>

        <div class="opened">
          ${range(10).map(i => opened[9 - i] || null).map((card) =>
            card
              ? html`
                <${GameCard}
                  value=${card.card}
                  color=${card.color}
                  allowOrientation=${this.props.allowOrientation}
                  selected=${card.chosen}
                  flipped=${card.orientation === 'down'}
                  ignored=${this.props.score !== null && !card.used}
                />`
              : html`<div aria-label="not opened yet" class="empty"></div>`
          )}
          <div class="equals">=</div>
        </div>
      </div>`;
  }
}
