import { SessionPuzzle } from "@common/session-puzzle";
import { RetriableSessionPuzzle } from "@common/retriable-session-puzzle";
import { assert, assertTruthy } from "@common/helpers";
import { debounce } from "lodash-es";

interface BuildComponentRequest {
  readonly action: 'component';
  readonly cards: readonly [string, string];
}

interface BuildDeviceRequest {
  readonly action: 'device';
  readonly recipe: number;
}

interface Response {
  readonly cards: ReadonlyArray<string>;
  readonly components: ReadonlyArray<string>;
  readonly recipes: ReadonlyArray<number>;
  readonly message: string | null;
}

interface State {
  selectedCard: string | null;
  availableRecipes: Set<number>;
  retryHandler: (() => void) | null;
}
const state: State = {
  selectedCard: null,
  availableRecipes: new Set(),
  retryHandler: null,
};

const container = document.querySelector<HTMLElement>('.container')!;
const log = document.querySelector<HTMLElement>('.log')!;
const game = document.querySelector<HTMLElement>('.game')!;
const recipes = Array.from(document.querySelectorAll<HTMLButtonElement>('.recipe'));
const cards = Array.from(document.querySelectorAll<HTMLButtonElement>('.card'));
const components = document.querySelector<HTMLElement>('.components')!;
const statusBanner = document.querySelector<HTMLButtonElement>('.status.banner')!;
const restartButton = document.querySelector<HTMLButtonElement>('.status.banner button')!;
const retryButton = document.querySelector<HTMLButtonElement>(
  ".disconnected.banner button"
)!;

const session = new SessionPuzzle<
  Response,
  BuildComponentRequest | BuildDeviceRequest,
  Response
>(`${window.puzzleUrl}build`);
const retriableSession = new RetriableSessionPuzzle(session, {
  setDisconnected: (isDisconnected: boolean) => {
    statusBanner.classList.toggle('hidden', isDisconnected);

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
restartButton.addEventListener('click', restart);
for (const recipe of recipes) {
  recipe.addEventListener('click', () => {
    buildRecipe(parseInt(recipe.dataset.recipe!, 10));
  });
}
for (const card of cards) {
  card.addEventListener('click', () => {
    toggleCard(card.dataset.color!);
  });
}
restart();

function restart() {
  state.selectedCard = null;
  state.availableRecipes = new Set();

  restartButton.disabled = true;
  for (const recipe of recipes) {
    recipe.disabled = true;
  }
  for (const card of cards) {
    card.disabled = true;
    card.classList.toggle('selected', false);
  }
  for (const message of document.querySelectorAll('.message:not(.initial)')) {
    message.remove();
  }
  retriableSession.initialize({ allowIncomplete: true })
    .then(updateState)
    .catch(handleError);
}

function buildRecipe(recipe: number) {
  disableAll();
  retriableSession.send({ action: 'device', recipe })
    .then(({response}) => updateState(response))
    .catch(handleError);
}

function toggleCard(card: string) {
  const cardEl = document.querySelector(`.card[data-color=${card}]`)!;
  if (state.selectedCard && state.selectedCard === card) {
    state.selectedCard = null;
    cardEl.classList.remove('selected');
    cardEl.querySelector<HTMLElement>('.status')!.innerText = '';

    for (const recipe of recipes) {
      recipe.disabled = !state.availableRecipes.has(parseInt(recipe.dataset.recipe!, 10));
    }
  } else if (state.selectedCard) {
    retriableSession.send({ action: 'component', cards: [state.selectedCard, card] })
      .then(({response}) => updateState(response))
      .catch(handleError);

    state.selectedCard = null;
    cardEl.classList.add('selected');
    cardEl.querySelector<HTMLElement>('.status')!.innerText = 'Selected';

    disableAll();
  } else {
    state.selectedCard = card;
    cardEl.classList.add('selected');
    cardEl.querySelector<HTMLElement>('.status')!.innerText = 'Selected';

    for (const recipe of recipes) {
      recipe.disabled = true;
    }
  }
}

function disableAll() {
  restartButton.disabled = true;
  for (const card of cards) {
    card.disabled = true;
  }
  for (const recipe of recipes) {
    recipe.disabled = true;
  }
}

function updateState(response: Response) {
  restartButton.disabled = false;
  const availableCardsSet = new Set(response.cards);
  for (const card of cards) {
    card.disabled = !availableCardsSet.has(card.dataset.color!);
    card.classList.toggle('used', card.disabled);
    card.classList.remove('selected');
    card.querySelector<HTMLElement>('.status')!.innerText = card.disabled ? 'Used': '';
  }
  state.availableRecipes = new Set(response.recipes);
  for (const recipe of recipes) {
    recipe.disabled = !state.availableRecipes.has(parseInt(recipe.dataset.recipe!, 10));
    recipe.querySelector<HTMLElement>('.status')!.innerText = recipe.disabled ? 'Unavailable': 'Available';
  }

  while (components.firstChild) {
    components.firstChild.remove();
  }
  for (const component of response.components) {
    const componentEl = document.createElement('div');
    componentEl.classList.add('component');
    componentEl.dataset.color = component;

    const componentTextEl = document.createElement('span');
    componentTextEl.innerText = component;
    componentTextEl.classList.add('sr-only');
    componentEl.appendChild(componentTextEl);

    components.appendChild(componentEl);
  }

  if (response.message) {
    const messageEl = document.createElement('div');
    messageEl.innerHTML = response.message;
    messageEl.classList.add('message');
    log.appendChild(messageEl);

    log.scrollTop = log.scrollHeight;
  }
}

function handleError(error: unknown) {
  statusBanner.classList.toggle('hidden', true);
  document.querySelector('.error.banner')!.classList.toggle('hidden', false);
}
