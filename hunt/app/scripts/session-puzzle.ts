import {fetchJson} from './helpers';

interface ServerRequest {
  readonly __sid: string | null;
  readonly __seq: number;
}
interface ServerResponse {
  readonly __status: 'success' | 'complete' | 'error';
  readonly __sid: string;
  readonly __seq: number;
}

export interface SessionPuzzleResponseSuccess<Type> {
  readonly status: 'success' | 'complete';
  readonly response: Type;
}
export interface SessionPuzzleResponseError {
  readonly status: 'error';
}
export interface SessionPuzzleResponseDisconnected<Type> {
  readonly status: 'disconnected';
  readonly retry: () => Promise<SessionPuzzleResponse<Type>>;
}
export type SessionPuzzleResponse<Type> = SessionPuzzleResponseSuccess<Type> | SessionPuzzleResponseError | SessionPuzzleResponseDisconnected<Type>;

/**
 * Helper to interact with a session puzzle. It takes care of initializing the
 * session, and sending updates to it. It also detects network outages, and
 * offers a retry helper.
 */
export class SessionPuzzle<InitialResponse, SendRequest, SendResponse> {
  private seq = 0;
  private sid: string | null = null;
  private pendingSend = false;

  constructor(private readonly url: string) {}

  /**
   * Initializes the puzzle session and returns a promise with the initial session info.
   *
   * If `allowIncomplete` then this can be called before the session completed. Otherwise, this
   * throws if the session is incomplete, and has already been initialized.
   *
   * The promise will return with a status and the response, or a retry function if disconnected.
   *
   * If the `status` is `error`, this is generally unrecoverable, and is probably an internal
   * error with the puzzle.
   *
   * No other calls may occur until the returned promise resolves. And if disconnected, no other
   * calls can occur until `retry()` is called and returns with a non-disconnected response. (This
   * is because the client only has partial state, so it needs to stay in sync with the server,
   * and know which of it's messages have been received.)
   */
  initialize({allowIncomplete}: { allowIncomplete?: boolean } = {}): Promise<SessionPuzzleResponse<InitialResponse>> {
    if (allowIncomplete) {
      this.seq = 0;
      this.sid = null
    }
    if (this.seq > 0) {
      throw new Error("The session puzzle has already been initialized.");
    }
    return this.performSend();
  }

  /**
   * Sends an update request for the puzzle session and returns a promise with the new puzzle
   * info.
   *
   * The promise will return with a status and the response, or a retry function if disconnected.
   *
   * If the `status` is `error`, this is generally unrecoverable, and is probably an internal
   * error with the puzzle.
   *
   * If the `status` is `complete`, you'll need to call `initialize` next to make a new session.
   *
   * No other calls may occur until the returned promise resolves. And if disconnected, no other
   * calls can occur until `retry()` is called and returns with a non-disconnected response. (This
   * is because the client only has partial state, so it needs to stay in sync with the server,
   * and know which of it's messages have been received.)
   */
  send(message: SendRequest): Promise<SessionPuzzleResponse<SendResponse>> {
    if (this.seq === 0) {
      throw new Error("The session puzzle has not been initialized.");
    }
    return this.performSend(message);
  }

  performSend<Request, Response>(opt_message?: Request): Promise<SessionPuzzleResponse<Response>> {
    if (this.pendingSend) {
      throw new Error("There is already an outstanding request.");
    }
    const body = {
      ...((opt_message || {}) as Request),
      __sid: this.sid,
      __seq: this.seq,
    };
    this.pendingSend = true;
    return fetchJson<ServerRequest & Request, ServerResponse & Response>(this.url, body)
      .then((response) => {
        const status = response["__status"];
        if (status === "complete") {
          this.seq = 0;
          this.sid = null;
        } else {
          this.seq += 1;
          this.sid = response["__sid"] || this.sid;
        }

        this.pendingSend = false;

        const responseEntries = Object.entries(response);
        const entriesForClient = responseEntries.filter(
          ([key, value]) => !key.startsWith("__")
        );
        return status === 'error' ? { status } : {
          status,
          response: Object.fromEntries(entriesForClient) as Response,
        };
      })
      .catch((err) => {
        let canRetry = true;
        return {
          status: "disconnected",
          retry: () => {
            if (canRetry) {
              canRetry = false;
              this.pendingSend = false;
              return this.performSend(opt_message);
            } else {
              throw Error(
                "You've already retried this request, wait for the retry response to come back and use that instead."
              );
            }
          },
        };
      });
  }
}
