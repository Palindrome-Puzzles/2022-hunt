import { Component } from 'preact';
import { Card, LevelInfo, html } from './common';

interface GamePickLevelProps {
  readonly waiting: boolean;
  readonly hideStatus: boolean;
  readonly levels: ReadonlyArray<LevelInfo>;
  readonly onPick: (level: number) => void;
}

export class GamePickLevel extends Component<GamePickLevelProps> {
  render() {
    const statusBanner = this.props.hideStatus
      ? ''
      : html`<div class="puzzle-status banner no-copy" role="status">
        Pick a level
      </div>`;

    const content = this.props.levels.length
      ? this.props.levels.map(
          levelInfo => html`
            <button
              type="button"
              onClick=${() => this.props.onPick(levelInfo.level)}
              disabled=${this.props.waiting}
            >
              <div class="level-name">
                Level ${levelInfo.level}
              </div>
              <div class="level-target">
                Target: >${levelInfo.target}
              </div>
              ${levelInfo.won ? html`<div class="complete">Complete</div>` : ''}
            </button>`
        )
      : html`<span class="waiting">⋯</span>`;

    return html`
      ${statusBanner}
      <div class="pick-level" tabindex="-1">
        ${content}
      </div>`;
  }
}
