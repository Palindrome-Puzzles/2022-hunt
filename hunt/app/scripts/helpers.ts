import Cookies from "js-cookie";

export function assertTruthy<T>(
  value: T | undefined | null,
  context?: string
): T {
  if (value == null) {
    throw Error(`value is not truthy: ${value} ${context}`);
  }
  return value;
}

export function assert(value: unknown, context?: string): asserts value {
  if (!value) {
    throw Error(`assertion failed: ${value} ${context}`);
  }
}

export function isArray<T>(
  value: T | ReadonlyArray<T>
): value is ReadonlyArray<T> {
  return Array.isArray(value);
}

export interface Progress<Data> {
  readonly type: "progress";
  readonly progress: Data;
}

export interface MinipuzzleProgress {
  readonly type: "minipuzzle";
  readonly updates: ReadonlyArray<{
    readonly ref: string;
    readonly solved: boolean;
    readonly answer: string | null;
    readonly submissions: ReadonlyArray<{
      readonly update_time: string;
      readonly answer: string;
      readonly correct: boolean;
    }>;
  }>;
}

export function hasSpecialKey(event: KeyboardEvent) {
  return event.altKey || event.ctrlKey || event.metaKey || event.isComposing;
}

export function fetchJson<Body = unknown, Response = unknown>(
  url: string,
  ...bodyArgs: void extends Body ? [Body?] : [Body]
): Promise<Response> {
  const body: Body = bodyArgs[0] as Body;
  const csrfToken = assertTruthy(
    Cookies.get("csrftoken"),
    "csrf token should exist"
  );
  return fetch(url, {
    method: "POST",
    mode: "same-origin",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
    body: JSON.stringify(body),
  }).then((response) => response.json());
}

export function positiveMod(n: number, m: number) {
  const initial = n % m;
  return initial >= 0 ? initial : initial + m;
}
