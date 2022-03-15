import RobustWebSocket from "robust-websocket";

export type SocketStatus = 'new' | 'open' | 'closed';
export type Listener<Data> = (event: Data) => void;

export class ManagedWebSocket<Send = any, Receive = any> {
  private readonly socket: RobustWebSocket;
  private readonly listeners = new Set<Listener<Receive>>();
  private readonly statusListeners = new Set<Listener<SocketStatus>>();
  private scope: string | null = null;
  private sendQueue: Send[] = [];
  private hasOpened = false;

  constructor(
    private readonly endpointPath: string,
    private readonly authToken?: string
  ) {
    this.socket = new RobustWebSocket(
      (location.protocol === "https:" ? "wss://" : "ws://") +
        `${window.location.host}${endpointPath}`,
        null,
        {
          shouldReconnect: (event, ws) => {
            if (event.code === 1008 || event.code === 1011) return
            return Math.pow(1.3, ws.attempts) * 2000;
          },
        }
    );
    this.socket.addEventListener('open', (event) => {
      this.hasOpened = true;
      this.handleOpen(event);
    });
    this.socket.addEventListener('message', (event) => {
      this.handleMessage(event);
    });
    this.socket.addEventListener('close', (event) => {
      // Ignore the connecting event if it's due to a "normal" (code 1000) close.
      // https://developer.mozilla.org/en-US/docs/Web/API/CloseEvent/code
      if (event.code !== 1000) {
        this.updateSocketStatus();
      }
    });
  }

  send(message: Send) {
    if (this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
    } else {
      this.sendQueue.push(message);
    }
  }

  addListener(listener: Listener<Receive>) {
    this.listeners.add(listener);
  }

  addStatusListener(listener: Listener<SocketStatus>) {
    this.statusListeners.add(listener);
    this.updateSocketStatus(listener);
  }

  setScope(scope: string | null = null) {
    this.scope = scope;
  }

  private handleOpen(event: RobustWebSocket.OpenEvent) {
    this.socket.send(
      JSON.stringify({
        type: "AUTH",
        data: this.authToken,
        scope: this.scope,
      })
    );
    // Can rely on websocket message ordering and just blast them.
    for (const queued of this.sendQueue) {
      this.socket.send(JSON.stringify(queued));
    }
    this.sendQueue = [];
    this.updateSocketStatus();
  }

  private handleMessage(event: RobustWebSocket.MessageEvent) {
    const data: Receive = JSON.parse(event.data);
    for (const listener of this.listeners) {
      listener(data);
    }
  }

  private updateSocketStatus(listener?: Listener<SocketStatus>) {
    const targets = listener ? [listener] : this.statusListeners;
    const status = this.socket.readyState === WebSocket.OPEN
      ? 'open'
      : this.hasOpened
        ? 'closed'
        : 'new';
    for (const listener of targets) {
      listener(status);
    }
  }
}
