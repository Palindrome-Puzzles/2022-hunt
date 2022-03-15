import { Component } from 'preact';
import { Card, html } from './common';
import { assertTruthy } from '@common/helpers';

interface GameCardProps {
  readonly value: string;
  readonly color: string;
  readonly allowOrientation: boolean;
  readonly selected: boolean;
  readonly flipped: boolean;
  readonly focused?: boolean;
  readonly disabled?: boolean;
  readonly focusable?: boolean;
  readonly ignored?: boolean;
  readonly onToggle?: (event: Event) => void;
  readonly onFlip?: (event: Event) => void;
}

export class GameCard extends Component<GameCardProps> {
  render() {
    const valueLabel = this.props.value === '*'
      ? 'times'
      : this.props.value === '+'
        ? 'plus'
        : this.props.value || 'reversed';

    const classes = ['card', this.props.color, valueLabel];
    if (this.props.selected) {
      classes.push('selected');
    }
    if (this.props.flipped) {
      classes.push('flipped');
    }
    if (this.props.focused) {
      classes.push('focused');
    }
    if (this.props.ignored) {
      classes.push('ignored');
    }

    const tabIndex = this.props.focusable === true
      ? 0
      : this.props.focusable === false
        ? -1
        : null;

    const flipControl = this.props.onFlip
      ? html`
        <button
          class="flip unstyled"
          type="button"
          aria-label="Flip"
          tabIndex="${tabIndex}"
          onClick=${(event: Event) => this.props.onFlip!(event)}
          disabled=${this.props.disabled}
        ><span aria-hidden="true">⟳</span></button>`
      : '';

    const staticDirectory = assertTruthy(window.puzzleStaticDirectory)
    const altText = this.props.value === '*' ? '×' : this.props.value;
    const backAltText = 'back of a ' + this.props.color + ' card'
    const valueDisplay = this.props.value
      ? html`<span class="value" aria-hidden="true">
          <img
              src="${staticDirectory}game6/images/card-${valueLabel}.png"
              alt="${altText}"
            />
        </span>`
      : this.props.color
      ? html`<span class="value" aria-hidden="true">
          <img
              src="${staticDirectory}game6/images/cardback-${this.props.color}.jpg"
              alt="${backAltText}"
            />
        </span>`
      : '';

    const ariaLabel = [
      this.props.color,
      ...[this.props.value ? [valueLabel || '(unknown)'] : []],
      ...[this.props.allowOrientation ? [this.props.flipped ? '(flipped)' : '(not flipped)'] : []],
      ...[this.props.selected ? ['(selected)'] : []],
      ...[this.props.focused ? ['(next to be dealt)'] : []],
    ].join(' ');

    if (this.props.onToggle) {
      return html`
        <div class="${classes.join(' ')}">
          <button
            class="unstyled"
            tabIndex="${tabIndex}"
            onClick=${(event: Event) => this.props.onToggle!(event)}
            disabled=${this.props.disabled}
            aria-label="${ariaLabel}"
          >
            ${valueDisplay}
          </button>
          ${flipControl}
        </div>`;
    } else {
      return html`
        <div class="${classes.join(' ')}" aria-label="${ariaLabel}">
          ${valueDisplay}
          ${flipControl}
        </div>
      `;
    }
  }
}
