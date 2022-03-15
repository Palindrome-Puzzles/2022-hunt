import { Component } from 'preact';
import { Card, html } from './common';
import {GameCard} from './game-card';

interface GameSelectCardsProps {
  readonly waiting: boolean;
  readonly hideStatus: boolean;

  readonly level: number;
  readonly deck: ReadonlyArray<Card>;
  readonly target: number;
  readonly allowOrientation: boolean;
  readonly onSelect: (deck: ReadonlyArray<Card>) => void;
  readonly onAbandon: () => void;
}
interface GameSelectCardsState {
  readonly selected: Set<number>;
  readonly flipped: Set<number>;
  readonly focusIndex: number;
}

export class GameSelectCards extends Component<GameSelectCardsProps, GameSelectCardsState> {
  private readonly localStorageKey = `hunt:puzzle:strange-garnets:level:${this.props.level}`;

  constructor(props: GameSelectCardsProps) {
    super(props);

    const fromStorage = localStorage.getItem(this.localStorageKey);
    const parsed = fromStorage
      ? JSON.parse(fromStorage)
      : { selected: [], flipped: [] };
    this.state = {
      selected: new Set(parsed.selected),
      flipped: new Set(parsed.flipped),
      focusIndex: 0,
    };
  }

  begin() {
    const collated: Card[] = [];
    for (const selectedIndex of this.state.selected) {
      collated.push({
        ...this.props.deck[selectedIndex],
        ...(this.props.allowOrientation
          ? { 'orientation': this.state.flipped.has(selectedIndex) ? 'down' : 'up' }
          : {})
      });
    }
    this.props.onSelect(collated);
  }

  toggle(event: Event, stateProp: 'flipped' | 'selected', index: number) {
    const copied = new Set(this.state[stateProp]);
    if (copied.has(index)) {
      copied.delete(index);
    } else {
      copied.add(index);
    }
    this.setState({ [stateProp]: copied });
    event.stopPropagation();
  }

  render() {
    const normalizedState = {
      selected: [...this.state.selected],
      flipped: [...this.state.flipped],
    };
    localStorage.setItem(this.localStorageKey, JSON.stringify(normalizedState));

    const remaining = 20 - this.state.selected.size;
    let status: string | undefined;
    let showBegin = false;
    if (this.props.hideStatus) {
      status = undefined;
    } else if (this.props.waiting) {
      status = '...';
    } else if (remaining > 0) {
      status = `Select ${remaining} more card${remaining > 1 ? 's' : ''}`;
    } else if (remaining < 0) {
      status = `Unselect ${-remaining} card${remaining < -1 ? 's' : ''}`;
    } else {
      status = 'Are you ready to play?';
      showBegin = true;
    }
    const statusBanner = status
      ? html`<div class="puzzle-status banner no-copy" role="status">
          ${status}
          <button type="button" onClick=${() => this.props.onAbandon()} disabled=${this.props.waiting}>
            Change level
          </button>
        </div>`
      : '';

    return html`
      ${statusBanner}
      <div
        class="select-cards"
        onKeydown="${(event: KeyboardEvent) => this.handleKeydown(event)}"
        onFocusCapture="${(event: FocusEvent) => this.handleFocus(event)}"
        tabindex="-1"
      >
        <div class="actions">
          <div class="level-target">Target: >${this.props.target}</div>
          <button type="button" onClick=${() => this.begin()} disabled=${this.props.waiting || !showBegin}>
            Begin
          </button>
        </div>
        <div class="cards">
          ${this.props.deck.map((card, index) => html`
            <${GameCard}
              value=${card.card}
              color=${card.color}
              allowOrientation=${this.props.allowOrientation}
              selected=${this.state.selected.has(index)}
              flipped=${this.state.flipped.has(index)}
              focusable=${index === this.state.focusIndex}
              disabled=${this.props.waiting}
              onToggle=${(event: Event) => this.toggle(event, 'selected', index)}
              onFlip=${this.props.allowOrientation ? (event: Event) => this.toggle(event, 'flipped', index) : null}
            />`
          )}
        </div>

      </div>`;
  }

  handleKeydown(event: KeyboardEvent) {
    const target = event.target && (event.target as HTMLElement);
    const card = target && target.closest<HTMLElement>('.card');
    if (!card) return;

    let handled = false;
    let newFocusCard: HTMLElement | null = null;
    switch (event.key) {
      case 'ArrowLeft':
        this.setState(state => ({
          focusIndex: Math.max(state.focusIndex - 1, 0),
        }));
        newFocusCard = card.previousElementSibling as HTMLElement;
        handled = true;
        break;

      case 'ArrowRight':
        this.setState(state => ({
          focusIndex: Math.min(state.focusIndex + 1, this.props.deck.length - 1),
        }));
        newFocusCard = card.nextElementSibling as HTMLElement;
        handled = true;
        break;
    }

    if (newFocusCard) {
      const button = target.closest('button');
      if (button && button.classList.contains('flip')) {
        newFocusCard.querySelector<HTMLElement>('button.flip')!.focus();
      } else {
        newFocusCard.querySelector<HTMLElement>('button')!.focus();
      }
    }

    if (handled) {
      event.preventDefault();
      event.stopPropagation();
    }
  }

  handleFocus(event: FocusEvent) {
    const card = event.target && (event.target as HTMLElement).closest<HTMLElement>('.card');
    if (!card) return;

    const index = Array.from(card.parentNode!.children).indexOf(card);
    this.setState(state => ({
      focusIndex: index,
    }));
    event.stopPropagation();
  }
}
