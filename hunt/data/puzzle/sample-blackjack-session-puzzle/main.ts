import { SessionPuzzle } from '@common/session-puzzle';
import { RetriableSessionPuzzle } from '@common/retriable-session-puzzle';
import { assertTruthy } from '@common/helpers';

// Export globally so the auto onload handler can find this.
window.puzzleOnLoad = puzzleOnLoad;

type InitialResponse = void;
type SendRequest = void;
interface SendResponse {
  readonly suit: string;
  readonly rank: string;
  readonly answer?: string;
}

function puzzleOnLoad() {
  const noCardsMessage = assertTruthy(document.querySelector<HTMLElement>(".no-cards"), '.no-cards');
  const cardsContainer = assertTruthy(document.querySelector<HTMLElement>(".cards"), ".cards");
  const drawCardButton = assertTruthy(document.querySelector<HTMLButtonElement>(".draw-card"), ".draw-card");
  const restartButton = assertTruthy(document.querySelector<HTMLButtonElement>(".restart"), ".restart");

  const resultMessage = assertTruthy(document.querySelector<HTMLElement>(".result"), ".result");
  const errorMessage = assertTruthy(document.querySelector<HTMLElement>(".error-message"), ".error-message");
  const disconnectedMessage = assertTruthy(document.querySelector<HTMLElement>(".disconnected-message"), ".disconnected-message");
  const retryButton = assertTruthy(document.querySelector<HTMLButtonElement>(".retry"), ".retry");

  const session = new SessionPuzzle<InitialResponse, SendRequest, SendResponse>(`${window.puzzleUrl}state`);
  const retriableSession = new RetriableSessionPuzzle(session, {
    setDisconnected: (disconnected: boolean) => {
      if (disconnected) {
        retryButton.classList.remove("hidden");
        disconnectedMessage.classList.remove("hidden");
      } else {
        retryButton.classList.add("hidden");
        disconnectedMessage.classList.add("hidden");
      }
    },
    onRetry: (cb: () => void) => retryButton.addEventListener('click', cb),
  });

  drawCardButton.addEventListener("click", drawCard);
  restartButton.addEventListener("click", restart);

  retriableSession.initialize().then(handleInitializeResult, handleError);

  function drawCard() {
    drawCardButton.disabled = true;
    retriableSession.send().then(handleDrawCardResult, handleError);
  }

  function handleInitializeResult() {
    drawCardButton.disabled = false;
  }

  function handleDrawCardResult({ complete, response }: { complete: boolean, response: SendResponse}) {
    handleCard(response);
    if (complete) {
      handleComplete(response.answer);
    } else {
      drawCardButton.disabled = false;
    }
  }

  function handleError() {
    errorMessage.classList.remove("hidden");
  }

  function handleCard({ suit, rank }: SendResponse) {
    noCardsMessage.classList.add("hidden");
    cardsContainer.classList.remove("hidden");

    const card = document.createElement("div");
    card.classList.add("card");
    card.classList.add(suit);

    const span1 = document.createElement("span");
    span1.classList.add("rank");
    span1.innerText = rank;
    card.appendChild(span1);

    const span2 = document.createElement("span");
    span2.innerText = " of ";
    card.appendChild(span2);

    const span3 = document.createElement("span");
    span3.classList.add("suit");
    span3.innerText = suit;
    card.appendChild(span3);

    cardsContainer.appendChild(card);
  }

  function handleComplete(maybeAnswer?: string) {
    resultMessage.classList.remove("hidden");
    restartButton.classList.remove("hidden");
    if (maybeAnswer) {
      resultMessage.classList.add("win");
      resultMessage.innerHTML = `Nice work - the answer is <span class="answer">${maybeAnswer}</span>`;
    } else {
      resultMessage.classList.remove("win");
      resultMessage.innerText = `Bad luck - you lost :(`;
    }
  }

  function restart() {
    while (cardsContainer.firstChild) {
      cardsContainer.removeChild(cardsContainer.firstChild);
    }

    noCardsMessage.classList.remove("hidden");
    cardsContainer.classList.add("hidden");

    resultMessage.classList.add("hidden");

    drawCardButton.classList.remove("hidden");
    restartButton.classList.add("hidden");

    retriableSession.initialize().then(handleInitializeResult, handleError);
  }
}
