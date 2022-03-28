window.puzzleOnLoad = () => {
  if (window.stubBooks) {
    handleMessage({
      type: 'progress',
      progress: window.stubBooks(),
    });
  }
  else {
    const socket = new RobustWebSocket(
      (location.protocol === "https:" ? "wss://" : "ws://") +
        `${window.location.host}/ws/puzzle/completing-the-story`
    );
    socket.addEventListener('open', (event) => {
      socket.send(
        JSON.stringify({
          type: "AUTH",
          data: window.puzzleAuthToken,
        })
      );
    });
    socket.addEventListener('message', (event) => {
      handleMessage(JSON.parse(event.data));
    });
  }
};

const found = document.querySelector('.found');
const solved = document.querySelector('.solved');
let foundBooks = [];
let solvedBooks = [];
function handleMessage(message) {
  if (message.type === "progress") {
    foundBooks = message.progress.unsolved;
    solvedBooks = message.progress.solved;
    updateBookLists();
  } else if (message.type === 'minipuzzle') {
    for (const update of message.updates) {
      const iframe = document.querySelector<HTMLIFrameElement>(`.book[data-book=${update.ref}] iframe`);
      if (iframe) {
        iframe.src = iframe.src;
      }
    }
  }
}

function updateBookLists() {
  const listInfos = [
    {list: foundBooks, parent: found},
    {list: solvedBooks, parent: solved},
  ];
  alphaSort(solvedBooks);
  for (const {list, parent} of listInfos) {
    const noneFound = parent.querySelector('.empty');
    if (list.length) {
      if (noneFound) noneFound.remove();

      const bookRefsToKeep = new Set(list.map(book => book.book));
      const existing = Array.from(parent.querySelectorAll('.book'));
      let i = 0;
      let j = 0;
      while (i < list.length || j < existing.length) {
        if (i < list.length && j < existing.length && list[i].book === existing[j].dataset.book) {
          i += 1;
          j += 1;
        } else if (i < list.length && (j === existing.length || bookRefsToKeep.has(existing[j].dataset.book))) {
          parent.insertBefore(createBook(list[i]), existing[j]);
          i += 1;
        } else {
          existing[j].remove();
          j += 1;
        }
      }
    } else {
      if (!noneFound) {
        const newNoneFound = document.createElement('div');
        newNoneFound.classList.add('empty');
        newNoneFound.innerText = 'Nothing here.'
        parent.appendChild(newNoneFound);
      }
      for (const book of parent.querySelectorAll('.book')) {
        book.remove();
      }
    }
  }
}

function alphaSort(bookList) {
  const normalize = (answer) => {
    answer = answer.toLowerCase();
    for (const articlePrefix of ['a ', 'an ', 'the ']) {
      if (answer.indexOf(articlePrefix) === 0) {
        return answer.slice(articlePrefix.length);
      }
    }
    return answer;
  };
  const compare = (book1, book2) => {
    let answer1 = normalize(book1.answer);
    let answer2 = normalize(book2.answer);
    if (answer1 > answer2) return 1;
    if (answer1 < answer2) return -1;
    return 0;
  };
  bookList.sort(compare);
}

function createBook(bookInfo) {
  const book = document.createElement('div');
  book.classList.add('book');
  book.dataset.book = bookInfo.book;

  if (window.isPublicAccess && bookInfo.type === 'solved') {
    book.classList.add('spoiler');
  }

  if (bookInfo.type === 'solved') {
    const pdf = document.createElement('a');
    pdf.href = window.puzzleStaticDirectory + "pages/" + bookInfo.pdf;
    pdf.innerText = bookInfo.answer;
    pdf.target = '_blank';

    book.appendChild(pdf);
  } else {
    const flavor = document.createElement('p');
    flavor.classList.add('clue');
    flavor.innerText = bookInfo.flavor;
    book.appendChild(flavor);

    const iframe = document.createElement('iframe');
    iframe.classList.add('minipuzzle-iframe');
    iframe.src = window.puzzleUrl + 'answer/?ref=' + bookInfo.book + '&guess=1';
    book.appendChild(iframe);
  }
  return book;
}
