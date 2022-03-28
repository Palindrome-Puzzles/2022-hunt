import { ManagedWebSocket } from "@common/managed-web-socket";
import { SessionPuzzle } from "@common/session-puzzle";
import { RetriableSessionPuzzle } from "@common/retriable-session-puzzle";
import { assert, assertTruthy, Progress, hasSpecialKey } from "@common/helpers";
import { pick } from "lodash-es";

declare global {
  interface Window {
    onWin?: (cb: (summary: ReadonlyArray<QuestionSummary>) => void) => void;
  }
}

interface HasQuestionResponse {
  readonly num: number;
  readonly q: string;
  readonly options: ReadonlyArray<string>;
  readonly image: string;
  readonly score: number;
}
interface NoQuestionResponse {
  readonly num: null;
  readonly score: number;
}
type QuestionResponse = HasQuestionResponse | NoQuestionResponse;

interface AnswerRequest {
  readonly answer: number;
}

interface QuestionSummary {
  readonly q: string;
  readonly options: ReadonlyArray<string>;
  readonly image: string;
  readonly score: number;
  readonly correct: number;
}

interface State {
  browsing: boolean;
  questionNumber: number | null;
  seenFirstQuestion: boolean;
  summary: ReadonlyArray<QuestionSummary>;
  retryHandler: (() => void) | null;
}
const state: State = {
  browsing: false,
  questionNumber: 1,
  seenFirstQuestion: false,
  summary: [],
  retryHandler: null,
};

const container = document.querySelector<HTMLElement>(".container")!;
const waiting = document.querySelector<HTMLElement>(".waiting")!;
const intro = document.querySelector<HTMLElement>(".intro")!;
const gameArea = document.querySelector<HTMLElement>(".game-area")!;
const correctArea = document.querySelector<HTMLElement>(".correct-area")!;
const incorrectArea = document.querySelector<HTMLElement>(".incorrect-area")!;
const winArea = document.querySelector<HTMLElement>(".win-area")!;
const optionButtons = Array.from(
  document.querySelectorAll<HTMLButtonElement>(".options button")
);
const browseToggleWrapper =
  document.querySelector<HTMLButtonElement>(".browse-toggle")!;
const browseToggleButton = document.querySelector<HTMLButtonElement>(
  ".browse-toggle button"
)!;
const browseButtons = document.querySelector<HTMLElement>(".browse-buttons")!;
const scoreDisplay = gameArea.querySelector<HTMLElement>(".score-display")!;
const nextButton = gameArea.querySelector<HTMLButtonElement>(".next")!;
const prevButton = gameArea.querySelector<HTMLButtonElement>(".prev")!;
const retryButton = document.querySelector<HTMLButtonElement>(
  ".disconnected.banner button"
)!;

showScreen(intro, {forceFocus: true});

const session = new SessionPuzzle<
  HasQuestionResponse,
  AnswerRequest,
  QuestionResponse
>(`${window.puzzleUrl}state`);
const retriableSession = new RetriableSessionPuzzle(session, {
  setDisconnected: (isDisconnected: boolean) => {
    document
      .querySelector(".disconnected.banner")!
      .classList.toggle("hidden", !isDisconnected);
    document.querySelector<HTMLButtonElement>(
      ".disconnected.banner button"
    )!.disabled = !isDisconnected;
  },
  onRetry: (retryHandler: () => void) => {
    state.retryHandler = retryHandler;
  },
});
retryButton.addEventListener("click", () => {
  if (state.retryHandler) {
    state.retryHandler();
    retryButton.disabled = true;
  }
});

intro.addEventListener("click", () => {
  intro.classList.toggle("hidden", true);
  waiting.classList.toggle("hidden", false);
  getInitialQuestion()
    .then((question) => displayReceivedQuestion(question))
    .catch(handleError);
});

correctArea.addEventListener("click", () => {
  correctArea.classList.toggle("hidden", true);
  if (state.questionNumber === null) {
    showScreen(winArea);
  } else {
    showScreen(gameArea);
  }
});

incorrectArea.addEventListener("click", () => {
  incorrectArea.classList.toggle("hidden", true);
  showScreen(gameArea);
});

winArea.addEventListener("click", () => {
  winArea.classList.toggle("hidden", true);
  showScreen(intro);
});

gameArea.addEventListener('keydown', handleKeydown);
browseToggleButton.addEventListener('keydown', handleKeydown);

for (const optionButton of optionButtons) {
  optionButton.addEventListener("click", () => {
    gameArea.classList.toggle("hidden", true);
    handleAnswer(parseInt(assertTruthy(optionButton.dataset.option), 10));
  });
}

browseToggleButton.addEventListener("click", () => {
  state.browsing = !state.browsing;
  state.seenFirstQuestion = false;

  browseButtons.classList.toggle("hidden", !state.browsing);
  browseToggleButton.innerText = state.browsing
    ? "Re-take test"
    : "Browse test";

  for (const optionButton of optionButtons) {
    optionButton.disabled = state.browsing;
    optionButton.classList.toggle("correct", false);
  }

  if (state.browsing) {
    assert(state.summary.length);
    state.questionNumber = 1;
    hideAllScreens();
    displayQuestionSummary(0);
    gameArea.classList.toggle("hidden", false);
    gameArea.setAttribute('tabindex', '-1');
  } else {
    hideAllScreens();
    state.questionNumber = null;
    showScreen(intro);
    gameArea.removeAttribute('tabindex');
  }
});

nextButton.addEventListener("click", () => {
  moveQuestionSummary(1);
});
prevButton.addEventListener("click", () => {
  moveQuestionSummary(-1);
});

function onWinCallback(progress: ReadonlyArray<QuestionSummary>) {
  state.summary = progress;
  browseToggleWrapper.classList.toggle("hidden", false);

  injectCopiableSummary(state.summary);
}

if (window.onWin) {
  window.onWin(onWinCallback);
} else {
  // Can ignore status - this can be best-effort if we get disconnected.
  const socket = new ManagedWebSocket<
    void,
    Progress<ReadonlyArray<QuestionSummary>>
  >("/ws/puzzle/trust-nobody", window.puzzleAuthToken);
  socket.addListener((summary) => {
    if (summary.type === "progress" && summary.progress.length) {
      onWinCallback(summary.progress);
    }
  });
}

function displayReceivedQuestion(question: QuestionResponse) {
  waiting.classList.toggle("hidden", true);

  // Show correct or incorrect interstital first.
  if (question.score > 0) {
    correctArea.querySelector<HTMLElement>(".score")!.innerText =
      normalizeScore(question.score);
    showScreen(correctArea);
  } else if (state.seenFirstQuestion) {
    showScreen(incorrectArea);
  } else {
    showScreen(gameArea);
  }

  // Load the question content into .game-area now, as correct/incorrect just
  // dumbly advance to the game area when dismissed.
  if (question.num) {
    state.seenFirstQuestion = true;
    state.questionNumber = question.num;

    gameArea.querySelector<HTMLElement>(
      ".question-number"
    )!.innerText = `Q${question.num}`;
    gameArea.querySelector<HTMLElement>(".question")!.innerHTML =
      normalizeQuestion(question.q);
    gameArea.querySelector<HTMLImageElement>("img")!.src = question.image;

    for (let i = 0; i < 5; i++) {
      optionButtons[i].querySelector<HTMLElement>(".option")!.innerText =
        question.options[i];
    }
  } else {
    state.seenFirstQuestion = false;
    state.questionNumber = null;
  }
}

function handleAnswer(answer: number) {
  gameArea.classList.toggle("hidden", true);
  waiting.classList.toggle("hidden", false);
  checkAnswer(answer)
    .then((response) => displayReceivedQuestion(response))
    .catch(handleError);
}

function displayQuestionSummary(index: number) {
  const question = state.summary[index];

  gameArea.querySelector<HTMLElement>(".question-number")!.innerText = `Q${
    index + 1
  }`;
  gameArea.querySelector<HTMLElement>(".question")!.innerHTML =
    normalizeQuestion(question.q);
  gameArea.querySelector<HTMLImageElement>("img")!.src = question.image;
  scoreDisplay.innerText = normalizeScore(question.score);

  for (let i = 0; i < 5; i++) {
    const option = optionButtons[i].querySelector<HTMLElement>(".option")!;
    option.innerText = question.options[i];
    optionButtons[i].classList.toggle("correct", question.correct === i);
  }

  optionButtons[0].focus();

  prevButton.style.visibility = index === 0 ? 'hidden' : 'visible';
  nextButton.style.visibility = index === state.summary.length - 1 ? 'hidden' : 'visible';
}

function moveQuestionSummary(delta: number) {
  assert(state.questionNumber);
  if (state.questionNumber + delta >= 1 && state.questionNumber + delta <= state.summary.length) {
    state.questionNumber += delta;
    displayQuestionSummary(state.questionNumber - 1);
    return true;
  }
  return false;
}

function hideAllScreens() {
  const screens = [
    waiting,
    intro,
    gameArea,
    correctArea,
    incorrectArea,
    winArea,
  ];
  for (const screen of screens) {
    screen.classList.toggle("hidden", true);
  }
}

function showScreen(screen: HTMLElement, {forceFocus}: {forceFocus?: boolean} = {}) {
  screen.classList.toggle("hidden", false);

  const firstButton = screen.querySelector('button');
  if (firstButton && (forceFocus || container.contains(document.activeElement))) {
    firstButton.focus();
  }
}

function handleError(error: unknown) {
  document.querySelector(".error.banner")!.classList.toggle("hidden", false);
}

function handleKeydown(event: KeyboardEvent) {
  if (hasSpecialKey(event)) {
    return;
  }
  if (state.browsing && (event.key === 'ArrowLeft' || event.key === 'ArrowRight')) {
    if (event.key === 'ArrowLeft' && moveQuestionSummary(-1)) {
      event.preventDefault();
    } else if (event.key === 'ArrowRight' && moveQuestionSummary(1)) {
      event.preventDefault();
    }
  } else if (!state.browsing && (event.key === 'ArrowUp' || event.key === 'ArrowDown')) {
    const focusedIndex = (optionButtons as Element[]).indexOf(document.activeElement!);
    if (focusedIndex > 0 && event.key === 'ArrowUp') {
      optionButtons[focusedIndex - 1].focus();
      event.preventDefault();
    } else if (focusedIndex > -1 && focusedIndex < optionButtons.length - 1 && event.key === 'ArrowDown') {
      optionButtons[focusedIndex + 1].focus();
      event.preventDefault();
    }
  }
}

async function getInitialQuestion(): Promise<HasQuestionResponse> {
  // If the team has won already, we can skip going to the server to check correctness.
  if (state.summary.length) {
    return {
      num: 1,
      score: 0,
      ...pick(state.summary[0], "q", "options", "image"),
    };
  } else {
    return retriableSession.initialize();
  }
}

async function checkAnswer(answer: number): Promise<QuestionResponse> {
  assert(state.questionNumber);

  // If the team has won already, we can skip going to the server to check correctness.
  if (state.summary.length) {
    const currentQuestion = state.summary[state.questionNumber - 1];
    const isCorrect = currentQuestion.correct === answer;
    const score = isCorrect ? currentQuestion.score : 0;
    const nextQuestionNumber = isCorrect
      ? state.questionNumber < state.summary.length
        ? state.questionNumber + 1
        : null
      : 1;
    return nextQuestionNumber
      ? {
          num: nextQuestionNumber,
          score,
          ...pick(state.summary[nextQuestionNumber - 1], "q", "options", "image"),
        }
      : { num: null, score };
  } else {
    return retriableSession.send({ answer }).then((result) => result.response);
  }
}

function normalizeQuestion(text: string) {
  const highlightedIndex = text.indexOf("[");
  return (
    text.slice(0, highlightedIndex) +
    `<span class="highlighted">${text[highlightedIndex + 1]}</span>` +
    text.slice(highlightedIndex + 3)
  );
}

function normalizeScore(score: number) {
  return score === 1 ? "1 euro" : `${score} euros`;
}

function injectCopiableSummary(summary: ReadonlyArray<QuestionSummary>) {
  const table = document.createElement('table');
  table.classList.toggle('copy-only', true);
  document.querySelector('.puzzle')!.appendChild(table);

  const headerRow = document.createElement('tr');
  table.appendChild(headerRow);

  const numTh = document.createElement('th');
  numTh.innerText = '#';
  headerRow.appendChild(numTh);

  const qTh = document.createElement('th');
  qTh.innerText = 'Question';
  headerRow.appendChild(qTh);

  const ansTh = document.createElement('th');
  ansTh.innerText = 'Answer';
  headerRow.appendChild(ansTh);

  const potTh = document.createElement('th');
  potTh.innerText = 'Added to Pot';
  headerRow.appendChild(potTh);

  const fingerprintTh = document.createElement('th');
  fingerprintTh.innerText = 'Fingerprint';
  headerRow.appendChild(fingerprintTh);

  for (let i = 0; i < summary.length; i++) {
    const tr = document.createElement('tr');
    table.appendChild(tr);

    const numTd = document.createElement('td');
    numTd.innerText = (i + 1).toString();
    tr.appendChild(numTd);

    const qTd = document.createElement('td');
    qTd.innerText = summary[i].q;
    tr.appendChild(qTd);

    const ansTd = document.createElement('td');
    const options = summary[i].options.map((option, j) => j === summary[i].correct ? option.toUpperCase() : option);
    ansTd.innerHTML = options.join('<br>\n');
    tr.appendChild(ansTd);

    const potTd = document.createElement('td');
    potTd.innerText = normalizeScore(summary[i].score);
    tr.appendChild(potTd);

    const fingerprintTd = document.createElement('td');
    const image = document.createElement('img');
    image.src = summary[i].image;
    image.alt = 'Colorful fingerprint';
    fingerprintTd.appendChild(image);
    tr.appendChild(fingerprintTd);
  }
}
