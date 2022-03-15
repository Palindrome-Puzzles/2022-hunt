import { ManagedWebSocket, Listener } from "./managed-web-socket";
import { isArray } from "./helpers";

export interface HasScope {
  readonly scope: string;
}

interface StateList<StateInfo> {
  readonly type: "state.scopes";
  readonly state: ReadonlyArray<StateInfo> | StateInfo;
}

interface ScopeSelection {
  readonly type: "state.scope";
  readonly scope: string | null;
}

interface StateListInfo<StateInfo> {
  readonly stateList: ReadonlyArray<StateInfo>;
  readonly scope: string | null;
}

export class TeamPuzzleStateList<StateInfo extends HasScope = HasScope> {
  private stateList: ReadonlyArray<StateInfo> = [];
  private scope: string | null = null;
  private listener: Listener<StateListInfo<StateInfo>> | null = null;

  constructor(private readonly socket: ManagedWebSocket) {
    this.socket.addListener((message) => this.handleMessage(message));
  }

  setListener(listener: Listener<StateListInfo<StateInfo>>) {
    this.listener = listener;
    if (this.stateList.length) {
      listener(this.getStateListInfo());
    }
  }

  selectScope(scope: string) {
    this.socket.send({
      type: "state.scope.select",
      scope: scope,
    });
  }

  private handleMessage(event: StateList<StateInfo> | ScopeSelection) {
    if (event.type === "state.scopes") {
      const stateOrList = event.state;
      if (isArray(stateOrList)) {
        this.stateList = stateOrList;
      } else {
        this.stateList = this.stateList.map((state) =>
          state.scope === stateOrList.scope ? stateOrList : state
        );
      }

      if (this.listener) {
        this.listener(this.getStateListInfo());
      }
    } else if (event.type === "state.scope") {
      this.scope = event.scope;
      // Let the auth flow in the socket know, so that we stay within the same
      // scope if we reconnect.
      this.socket.setScope(this.scope);

      if (this.listener) {
        this.listener(this.getStateListInfo());
      }
    }
  }

  private getStateListInfo() {
    return {
      stateList: this.stateList,
      scope: this.scope,
    };
  }
}
