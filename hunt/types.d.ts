interface Window {
  puzzleOnLoad?: () => void;
  puzzleOnCopy?: (copiedPuzzle: HTMLElement) => void;
  puzzleAuthToken?: string;
  puzzleStaticDirectory?: string;
  puzzleUrl?: string;
  isPublicAccess?: boolean;

  playSolveSound?: (url: string) => void;
}

declare module 'robust-websocket' {
  export = RobustWebSocket;
}

declare module RobustWebSocket {
  interface OpenEvent extends CustomEvent<undefined> {
    type: 'open';
  }
  interface MessageEvent extends CustomEvent<undefined> {
    type: 'message';
    data: globalThis.MessageEvent['data'];
  }
  interface EventMap {
    'open': OpenEvent;
    'message': MessageEvent;
    'close': CloseEvent;
  }
}

declare class RobustWebSocket extends WebSocket {
  constructor(url: string, protocols: string | string[] | null, options: { shouldReconnect: (event: CloseEvent, ws: {attempts: number}) => number | undefined});
  addEventListener<K extends keyof RobustWebSocket.EventMap>(
    type: K,
    listener: (this: RobustWebSocket, event: RobustWebSocket.EventMap[K]) => any,
    options?: boolean | AddEventListenerOptions,
  ): void;
  addEventListener(type: string, listener: EventListenerOrEventListenerObject, options?: boolean | AddEventListenerOptions): void;
  removeEventListener<K extends keyof RobustWebSocket.EventMap>(
    type: K,
    listener: (this: RobustWebSocket, event: RobustWebSocket.EventMap[K]) => any,
    options?: boolean | EventListenerOptions,
  ): void;
  removeEventListener(type: string, listener: EventListenerOrEventListenerObject, options?: boolean | EventListenerOptions): void;
}
