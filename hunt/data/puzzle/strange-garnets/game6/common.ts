import htm from 'htm';
import { h, Component } from 'preact';

export const html = htm.bind(h);

export interface Card {
  readonly card: string;
  readonly color: string;
  readonly orientation: 'up' | 'down' | null;
  readonly chosen?: boolean;
  readonly used?: boolean;
}

export type CardAction = 'open' | 'pass';

export interface LevelInfo {
  readonly level: number;
  readonly target: number;
  readonly won: boolean;
}
