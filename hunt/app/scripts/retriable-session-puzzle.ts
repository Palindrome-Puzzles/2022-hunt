import {
  SessionPuzzle,
  SessionPuzzleResponse,
  SessionPuzzleResponseSuccess,
} from "./session-puzzle";

type SetDisconnectedCallback = (disconnected: boolean) => void;
type RejectCallback = (error?: unknown) => void;
type Completable<Type> = {
  readonly response: Type;
  readonly complete: boolean;
};

function disconnectedRetrier<Response, Result>({
  initial,
  project,
  onDisconnected,
}: {
  initial: () => Promise<SessionPuzzleResponse<Response>>;
  project: (serverResponse: SessionPuzzleResponseSuccess<Response>) => Result;
  onDisconnected: (retryFn: () => void) => void;
}): Promise<Result> {
  let resolve: ((result: Result) => void) | null = null;
  let reject: RejectCallback | null = null;
  const promise = new Promise<Result>((innerResolve, innerReject) => {
    resolve = innerResolve;
    reject = innerReject;
  });

  const handleResponse = (response: SessionPuzzleResponse<Response>) => {
    switch (response.status) {
      case "success":
      case "complete":
        resolve!(project(response));
        break;

      case "error":
        reject!();
        break;

      case "disconnected":
        onDisconnected(() => {
          response.retry().then(handleResponse);
        });
        break;
    }
  };
  initial().then(handleResponse);
  return promise;
}

/** Helper that handles common UI logic for session puzzles for disconnection and retrying. */
export class RetriableSessionPuzzle<
  InitialResponse,
  SendRequest,
  SendResponse
> {
  private readonly session: SessionPuzzle<
    InitialResponse,
    SendRequest,
    SendResponse
  >;
  private readonly onDisconnected: (retryFn: () => void) => void;

  constructor(
    sessionPuzzle: SessionPuzzle<InitialResponse, SendRequest, SendResponse>,
    {
      setDisconnected,
      onRetry,
    }: {
      setDisconnected: SetDisconnectedCallback;
      onRetry: (cb: () => void) => void;
    }
  ) {
    this.session = sessionPuzzle;

    setDisconnected(false);

    this.onDisconnected = (retryFn: () => void) => {
      setDisconnected(true);
      onRetry(() => {
        setDisconnected(false);
        retryFn();
      });
    };
  }

  /**
   * Initializes the puzzle session and returns a promise with the initial session info.
   *
   * If `allowIncomplete` then this can be called before the session completed. Otherwise, this
   * throws if the session is incomplete, and has already been initialized.
   *
   * If successful, it will resolve with the response.
   *
   * If an error occurs, it will reject with no argument.
   *
   * If the user is disconnected, it will enable the retry button and show a
   * disconnected message. When reconnected and retried, it will resolve or reject
   * the originally returned promise.
   */
  initialize({
    allowIncomplete,
  }: { allowIncomplete?: boolean } = {}): Promise<InitialResponse> {
    return disconnectedRetrier<InitialResponse, InitialResponse>({
      initial: () => this.session.initialize({ allowIncomplete }),
      project: (serverResponse) => serverResponse.response,
      onDisconnected: this.onDisconnected,
    });
  }

  /**
   * Sends an update request for the puzzle session and returns a promise with the new puzzle
   * info.
   *
   * If successful, it will resolve with the response and whether it is complete.
   *
   * If an error occurs, it will reject with no argument.
   *
   * If the user is disconnected, it will enable the retry button and show a
   * disconnected message. When reconnected and retried, it will resolve or reject
   * the originally returned promise.
   */
  send(message: SendRequest): Promise<Completable<SendResponse>> {
    return disconnectedRetrier<SendResponse, Completable<SendResponse>>({
      initial: () => this.session.send(message),
      project: (serverResponse) => ({
        response: serverResponse.response,
        complete: serverResponse.status === "complete",
      }),
      onDisconnected: this.onDisconnected,
    });
  }
}
