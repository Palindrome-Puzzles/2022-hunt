import { ManagedWebSocket } from "@common/managed-web-socket";
import { Progress, MinipuzzleProgress } from "@common/helpers";

import { Game as Game6 } from './game6/game';
import { LevelInfo as Game6LevelInfo } from './game6/common';
import { Game as Game8 } from './game8/game';
import htm from 'htm';
import { h, render } from 'preact';

declare global {
  interface Window {
    onGame6Progress?: (cb: (progress: ProgressInfo['game6']) => void) => void;
  }
}


const html = htm.bind(h);

let answers: ReadonlyArray<string | null>;

interface ProgressInfo {
  readonly game6: {
    readonly levels: ReadonlyArray<Game6LevelInfo>;
  };
}


renderGame6({levels: []});
renderGame8();

if (window.onGame6Progress) {
  window.onGame6Progress(renderGame6);
} else {
  const socket = new ManagedWebSocket<
    void,
    Progress<ProgressInfo> | MinipuzzleProgress
  >("/ws/puzzle/strange-garnets", window.puzzleAuthToken);

  socket.addListener((message) => {
    if (message.type === "progress") {
      renderGame6(message.progress.game6);
    } else if (message.type === 'minipuzzle') {
      for (const update of message.updates) {
        const iframe = document.querySelector<HTMLIFrameElement>(`.${update.ref}-answers`);
        if (iframe) {
          iframe.src = iframe.src;
        }
      }
    }
  });
}

function renderGame6(progress: ProgressInfo['game6']) {
  render(
    html`<${Game6} levels="${progress.levels}"/>`,
    document.querySelector('.game6')!);
}

function renderGame8() {
  render(html`<${Game8}/>`, document.querySelector('.game8')!);
}
