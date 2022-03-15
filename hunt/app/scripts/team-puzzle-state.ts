import { ManagedWebSocket, Listener } from './managed-web-socket';

export interface StateTx<Updates> {
  readonly type: 'state.update';
  readonly expectedSeq: number | null;
  readonly scope: string | null;
  readonly updates: Updates;
}

export interface StateTxRollback<Updates> {
  readonly type: 'state.update.rollback';
  readonly expectedSeq: number | null;
  readonly scope: string | null;
  readonly updates: Updates;
}

export type StateTxActions =
  | { readonly type: 'state.refresh', readonly scope: string | null }
  | { readonly type: 'state.abandon', readonly scope: string | null, readonly force?: boolean };

export interface StateRx<State, Refresh extends boolean> {
  readonly type: 'state';
  readonly refresh: Refresh;
  readonly seq: number;
  readonly scope: string | null;
  readonly state: State;
}

export interface PublicStateManager<Updates, Refresh> {
  readonly initial: () => Refresh;
  readonly onMessage: (message: StateTx<Updates> | StateTxActions) => Refresh | null;
}

export class TeamPuzzleState<Updates, Refresh, Partial = Refresh> {
  private replayMessages: (StateRx<Refresh, true> | StateRx<Partial, false>)[] = [];
  private lastScope: string | null = null;
  private lastSeq: number | null = null;
  private listener: Listener<StateRx<Refresh, true> | StateRx<Partial, false> | StateTxRollback<Updates>> | null = null;

  constructor(
    private readonly channel:
      | {readonly socket: ManagedWebSocket, readonly stateManager?: undefined}
      | {readonly socket?: undefined, readonly stateManager: PublicStateManager<Updates, Refresh>},
    private readonly opts: { skipLock: boolean }
  ) {
    if (this.channel.socket) {
      this.channel.socket.addListener(message => this.handleMessage(message));
    } else {
      setTimeout(() => {
        this.handleMessage(stubRxMessage(this.channel.stateManager!.initial()));
      }, 0);
    }
  }

  update(updates: Updates) {
    this.sendMessage({
      type: 'state.update',
      expectedSeq: this.opts.skipLock ? null : this.lastSeq,
      scope: this.lastScope,
      updates,
    });
  }

  setListener(listener: Listener<StateRx<Refresh, true> | StateRx<Partial, false> | StateTxRollback<Updates>>) {
    if (this.listener) {
      throw Error('Listener already set');
    }
    this.listener = listener;

    for (const replayMessage of this.replayMessages) {
      listener(replayMessage);
    }
    this.replayMessages = [];
  }

  refresh() {
    this.sendMessage({
      type: 'state.refresh',
      scope: this.lastScope,
    });
  }

  abandon(force = false) {
    this.sendMessage({
      type: 'state.abandon',
      scope: this.lastScope,
      force,
    });
  }

  private sendMessage(message: StateTx<Updates> | StateTxActions) {
    if (this.channel.socket) {
      this.channel.socket.send(message);
    } else {
      const result = this.channel.stateManager.onMessage(message);
      if (result) {
        setTimeout(() => {
          this.handleMessage(stubRxMessage(result));
        }, 0);
      }
    }
  }

  private handleMessage(event: StateRx<Refresh, true> | StateRx<Partial, false> | StateTxRollback<Updates>) {
    if (event.type === 'state') {
      this.lastScope = event.scope;
      this.lastSeq = event.seq;

      if (this.listener) {
        this.listener(event);
      } else {
        if (event.refresh) {
          this.replayMessages = [event];
        } else {
          this.replayMessages.push(event);
        }
      }
    } else if (event.type === 'state.update.rollback') {
      if (this.listener) {
        this.listener(event);
      }
    }
  }
}

function stubRxMessage<State>(state: State): StateRx<State, true> {
  return {
    type: 'state',
    refresh: true,
    seq: 1,
    scope: null,
    state,
  };
}
