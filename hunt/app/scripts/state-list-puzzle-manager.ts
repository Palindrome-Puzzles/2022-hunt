import { ManagedWebSocket, SocketStatus } from "@common/managed-web-socket";
import { TeamPuzzleState, StateRx, PublicStateManager } from "@common/team-puzzle-state";
import { TeamPuzzleStateList, HasScope } from "@common/team-puzzle-state-list";

export interface StateListPuzzleManagerOpts {
  readonly serverUrl: string;
  readonly puzzleUrl: string;
  readonly defaultScope: string;
  readonly puzzleAuthToken?: string;
  readonly skipLock: boolean;
}

export abstract class StateListPuzzleManager<Updates, Refresh, Partial, DomUpdateDescriptor = void> {
  private puzzleLoaded = false;
  private domInitialized = false;
  private hasInitialState = false;
  private socketStatus: SocketStatus = 'closed';
  private stateList: ReadonlyArray<HasScope> = [];
  private scope: string | null = null;

  private readonly socket?: ManagedWebSocket;
  readonly puzzleState: TeamPuzzleState<Updates, Refresh, Partial>;
  protected readonly puzzleStateList?: TeamPuzzleStateList;

  constructor(
    opts: StateListPuzzleManagerOpts,
    private readonly publicStateManager?: PublicStateManager<Updates, Refresh>
  ) {
    if (window.isPublicAccess && this.publicStateManager) {
      this.puzzleState = new TeamPuzzleState<Updates, Refresh, Partial>(
        { stateManager: this.publicStateManager },
        { skipLock: opts.skipLock });
      this.socketStatus = 'open';

      this.checkedInitializeDom();
    } else {
      const localStorageKey = `hunt:puzzle:${opts.puzzleUrl}:scope`;

      this.socket = new ManagedWebSocket(opts.serverUrl, opts.puzzleAuthToken);
      this.puzzleState = new TeamPuzzleState<Updates, Refresh, Partial>(
        { socket: this.socket },
        { skipLock: opts.skipLock });
      this.puzzleStateList = new TeamPuzzleStateList(this.socket);

      const initialScope = localStorage.getItem(localStorageKey) || opts.defaultScope;
      if (initialScope) {
        this.puzzleStateList.selectScope(initialScope);
      }

      this.socket.addStatusListener(status => {
        this.socketStatus = status;
        this.checkedUpdateStatusDom();
      })

      this.puzzleStateList.setListener((message) => {
        this.stateList = [...message.stateList];
        this.scope = message.scope;

        if (this.scope) {
          localStorage.setItem(localStorageKey, this.scope);
        } else {
          localStorage.removeItem(localStorageKey);
        }
        this.checkedInitializeDom();
        this.checkedUpdateStateListDom();
      });
    }

    this.puzzleState.setListener((message) => {
      switch (message.type) {
        case "state":
          if (message.refresh) {
            this.handleRefresh(message.state);
            this.hasInitialState = true;

            this.checkedInitializeDom();
            this.checkedSynchronizeToDom();
          } else {
            const descriptor = this.handleUpdate(message.state);
            this.checkedSynchronizeToDom(descriptor);
          }
          break;

        case "state.update.rollback":
          const descriptor = this.handleRollback(message.updates);
          this.checkedSynchronizeToDom(descriptor);
          break;
      }
    });
  }

  markPuzzleLoaded() {
    this.puzzleLoaded = true;
    this.checkedInitializeDom();
  }

  private checkedInitializeDom() {
    if (!this.puzzleLoaded || !this.hasInitialState || (this.puzzleStateList && !this.stateList.length)) {
      return;
    }
    if (this.domInitialized) {
      return;
    }

    document.querySelector('.puzzle')!.classList.add("interactive");

    this.maybeInitializeStateListDom();
    this.initializeDom();

    this.checkedSynchronizeToDom();
    this.checkedUpdateStateListDom();
    this.checkedUpdateStatusDom();
    this.domInitialized = true;
  }

  private checkedSynchronizeToDom(descriptor?: DomUpdateDescriptor) {
    if (!this.puzzleLoaded || !this.hasInitialState) {
      return;
    }
    this.synchronizeToDom(descriptor);
  }

  private checkedUpdateStateListDom() {
    if (!this.puzzleStateList) return;
    if (!this.puzzleLoaded || !this.stateList.length) return;

    const keepFocus = document.activeElement && document.querySelector<HTMLElement>(".state-list")!.contains(document.activeElement);
    for (const stateListButton of document.querySelectorAll<HTMLButtonElement>(
      ".state-list button"
    )) {
      if (stateListButton.innerText === this.scope) {
        stateListButton.classList.add("active");
        if (!keepFocus) stateListButton.tabIndex = 0;
      } else {
        stateListButton.classList.remove("active");
        if (!keepFocus) stateListButton.tabIndex = -1;
      }
    }
  }

  private checkedUpdateStatusDom() {
    if (this.socketStatus === 'closed') {
      document.querySelector('.disconnected.banner')!.classList.remove('hidden');
    } else {
      document.querySelector('.disconnected.banner')!.classList.add('hidden');
    }
  }

  private maybeInitializeStateListDom() {
    const stateListContainer = document.querySelector(".state-list-container")!;
    if (!this.puzzleStateList) {
      stateListContainer.classList.add('hidden');
      return;
    }

    const stateList = document.querySelector<HTMLElement>(".state-list")!;
    let first = true;
    for (const state of this.stateList) {
      const button = document.createElement("button");
      button.innerText = state.scope;
      button.type = "button";
      button.tabIndex = first ? 0 : -1;
      stateList.appendChild(button);

      button.addEventListener("click", () => {
        this.puzzleStateList!.selectScope(state.scope);
      });
      first = false;
    }

    const buttons = Array.from(stateList.querySelectorAll<HTMLElement>('button'));
    stateList.addEventListener('keydown', (event: KeyboardEvent) => {
      handleKeydown(buttons, event);
    });
    stateList.addEventListener('focusin', event => {
      const button = event.target && (event.target as HTMLElement).closest<HTMLElement>('button');
      if (!button) return;

      const oldFocus = stateList.querySelector<HTMLElement>('button[tabIndex="0"]');
      if (oldFocus) {
        oldFocus.tabIndex = -1;
      }
      button.tabIndex = 0;
    });
  }

  protected abstract initializeDom(): void;
  protected abstract handleRefresh(refresh: Refresh): void;
  protected abstract handleUpdate(update: Partial): DomUpdateDescriptor;
  protected abstract handleRollback(rollback: Updates): DomUpdateDescriptor;
  protected abstract synchronizeToDom(descriptor?: DomUpdateDescriptor): void;
}

function handleKeydown(buttons: ReadonlyArray<HTMLElement>, event: KeyboardEvent) {
  const button = event.target && (event.target as HTMLElement).closest<HTMLElement>('button');
  if (!button) return;

  let index = buttons.indexOf(button);
  if (index === -1) return;

  let newFocus;
  switch (event.key) {
    case 'ArrowLeft':
      newFocus = buttons[index - 1];
      break;
    case 'ArrowRight':
      newFocus = buttons[index + 1];
      break;
  }
  if (!newFocus) return;

  button.tabIndex = -1;
  newFocus.tabIndex = 0;
  newFocus.focus();
  event.preventDefault();
  event.stopPropagation();
}
