// For Game 6.
const OPEN_PASS_TARGETS = {
  1: 3000,
  2: 7500,
  3: 24500,
};

const GameState = {
    NEW: 'new',
    // The solver is selecting which cards to play with.
    SELECTING: 'selecting',
    // The solver is playing through their selected cards.
    PLAYING: 'playing',
};
const GameAction = {
    BEGIN: 'begin',
    SELECT: 'select',
    OPEN: 'open',
    PASS: 'pass',
};
const CardAction = {
    OPEN: 'open',
    PASS: 'pass',
};
const CardColor = {
    BLACK: 'black',
    BLUE: 'blue',
    RED: 'red',
};
const CardOrientation = {
    UP: 'up',
    DOWN: 'down',
};
const ALLOWED_CARDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, '+', '*']
const DECKS = {
    1: [
        ...[4, 4, 6, 6, 6, 7, 7, 8, 8, 9, 9, 10].map(card => ({'card': card, 'color': CardColor.BLACK})),
        ...[7, 7, 7, 7, 7, 8, 8, 8, 8, 10, '+', '+'].map(card => ({'card': card, 'color': CardColor.BLUE})),
        ...[5, 9, 10, '*', '*', '*'].map(card => ({'card': card, 'color': CardColor.RED}))
    ],
    2: [
        ...[5, 5, 6, 6, 6, 7, 7, 9, 9, '+', '+', '+', '+', '+'].map(card => ({'card': card, 'color': CardColor.BLACK})),
        ...[6, 7, 8, '*', '*', '*', '*', '*'].map(card => ({'card': card, 'color': CardColor.BLUE})),
        ...[4, 4, 5, 5, 6, 6, 6, 9].map(card => ({'card': card, 'color': CardColor.RED}))
    ],
    3: [
        ...[6, 6, 6, 7, 7, 7, 8, 8, 9, '*', '*', '*'].map(card => ({'card': card, 'color': CardColor.BLACK})),
        ...[6, 7, 7, 8, 8, 8, 9, 9, 9, 10, '+', '+', '*', '*'].map(card => ({'card': card, 'color': CardColor.BLUE})),
        ...[6, 6, 7, 7].map(card => ({'card': card, 'color': CardColor.RED}))
    ],
}
const ORIENTATION_ALLOWED = new Set([3])
const MAX_LEVEL = 3

const DECK_SIZE = 30
const SELECTED_DECK_SIZE = 20
const OPEN_COUNT = 10

// Show decks to users sorted by number instead of color.
for (const deck of Object.values(DECKS)) {
  deck.sort(function(a, b) {
    const aVal = a.card === '+' ? 11 : a.card === '*' ? 12 : a.card;
    const bVal = b.card === '+' ? 11 : b.card === '*' ? 12 : b.card;
    return aVal - bVal;
  });
}

let state = null;
// Give access to all levels in posthunt version.
let progress = {
  'levels': [1, 2, 3].map(level => ({
    'level': level,
    'target': OPEN_PASS_TARGETS[level],
    'won': false,
  })),
};
let game6ProgressHandler = () => {};

window.onGame6Progress = (handler) => {
  game6ProgressHandler = handler;
  game6ProgressHandler(progress);
};

window.stubSend = async (body) => {
  if (body.__seq === 0) {
    state = game6InitialState();
    return {...game6ProjectState(state), __sid: 'abc', __status: 'success'};
  } else {
    game6TransformState(state, body);
    return {
      ...game6ProjectState(state),
      __sid: 'abc',
      __status: state.completed ? 'complete' : 'success',
    };
  }
};

function game6InitialState() {
  return {
    state: GameState.NEW,
  };
}

function game6ProjectState(state) {
  switch (state.state) {
    case GameState.NEW:
      return state;

    case GameState.SELECTING:
      return {
        'deck': DECKS[state.level],
        'allowOrientation': ORIENTATION_ALLOWED.has(state.level),
      };

    case GameState.PLAYING:
      const deck = state.deck.map(card => ({
        'card': card['action'] === CardAction.OPEN ? card['card'] : null,
        'color': card['color'],
        'orientation': card['orientation'],
        'chosen': card['action'] === CardAction.OPEN,
        'used': !!card.used,
      }));
      return { 'score': state.score, 'deck': deck, 'opened': state.opened, 'played': state.played };
  }
}

function game6TransformState(state, body) {
  // Skip a bunch of assertions as posthunt.
  if (body.action === GameAction.BEGIN) {
    state.state = GameState.SELECTING;
    state.level = body.level;
  } else if (body.action === GameAction.SELECT) {
    const full_deck = DECKS[state.level];
    const deck = [];
    const used = new Set();
    for (const card of body.deck) {
        for (let i = 0; i < full_deck.length; i++) {
            if (used.has(i)) continue;
            if (full_deck[i]['card'] == card['card'] && full_deck[i]['color'] == card['color']) {
              used.add(i);
              deck.push({
                  'card': card['card'],
                  'color': card['color'],
                  'orientation': card.orientation || CardOrientation.UP,
                  'action': null,
              });
              break;
            }
        }
    }

    const shuffled = rigged_shuffle(deck);
    state.state = GameState.PLAYING;
    state.deck = shuffled;
    state.score = 0;
    state.opened = 0;
    state.played = 0;
  } else {
    let [played, opened] = get_counts(state.deck);

    // Play the next card.
    // Don't do anything if we're trying to open/pass an 11th card (due to
    // frontend spamming).
    if (played - opened < OPEN_COUNT && opened < OPEN_COUNT) {
      const current = state.deck[played];
      played += 1;
      if (body.action == GameAction.OPEN) {
        current['action'] = CardAction.OPEN;
        opened += 1;
      } else {
        current['action'] = CardAction.PASS;
      }
    }

    // Make rest of the moves if forced.
    let complete = false
    if (opened == OPEN_COUNT) {
      complete = true
      for (let i = played; i < SELECTED_DECK_SIZE; i++) {
        state.deck[i]['action'] = CardAction.PASS;
        played += 1;
      }
    } else if (opened + SELECTED_DECK_SIZE - played == OPEN_COUNT) {
      complete = true;
      for (let i = played; i < SELECTED_DECK_SIZE; i++) {
        state.deck[i]['action'] = CardAction.OPEN;
        opened += 1;
        played += 1;
      }
    }

    // Generate response.
    let score = null;
    if (complete) {
        state.completed = true;
        const used = get_used_cards(state.deck);
        for (const card of used) {
          card['used'] = true;
        }
        score = get_score(used);
    }

    // Update team progress if they won!
    if (complete && score >= OPEN_PASS_TARGETS[state.level]) {
      const levelProgress = progress.levels.find(levelInfo => levelInfo.level === state.level);
      levelProgress.won = true;
      game6ProgressHandler(progress);
    }

    state.score = score;
    state.opened = opened;
    state.played = played;
  }
}

function get_counts(deck) {
  let played = 0;
  let opened = 0;
  for (const card of deck) {
    if (!card['action']) break
    played += 1;
    if (card['action'] == CardAction.OPEN)
        opened += 1;
  }
  return [played, opened]
}

function is_operator(card) {
  return card == '+' || card == '*';
}

function get_used_cards(deck) {
  let effective = []
  let last_type = null
  for (let i = deck.length - 1; i >= 0; i--) {
    const card = deck[i];
    if (card['action'] != CardAction.OPEN)
      continue;
    const curr_type = is_operator(card['card']) ? 'op' : 'num';
    if (last_type != curr_type)
        effective.push(card);
    last_type = curr_type;
  }

  if (is_operator(effective[effective.length - 1]['card']))
      effective = effective.slice(0, effective.length - 1);

  return effective;
}

function get_score(used_cards) {
  let effective = used_cards.map(card => card.card);
  if (is_operator(effective[0]))
      effective = [0, ...effective];

  // Super-inefficient BODMAS impl.
  while (effective.length > 1) {
    let done = false;
    for (let i = 0; i < effective.length; i++) {
      if (effective[i] === '*') {
        effective = [
          ...effective.slice(0, i-1),
          effective[i-1] * effective[i+1],
          ...effective.slice(i+2)
        ];
        done = true;
        break;
      }
    }
    if (done) continue;

    for (let i = 0; i < effective.length; i++) {
      if (effective[i] == '+') {
        effective = [
          ...effective.slice(0, i-1),
          effective[i-1] + effective[i+1],
          ...effective.slice(i+2)
        ];
        break;
      }
    }
  }

  return effective[0];
}

function rigged_shuffle(deck) {
    // To make games winnable, have the following constraints:
    //  - no "*" next to each other
    //
    // We implement this by first placing "*" in positions, then shuffle the rest.
    let times_cards = [];
    let other_cards = [];
    for (const card of deck) {
        if (card['card'] == '*')
            times_cards.push(card);
        else
            other_cards.push(card);
    }

    // If there are K "*", and N cards, then we can treat it as if each of the K
    // cards has a blank card on the right. The "*" can also be in the final position
    // with the blank card hanging over the edge.
    const N = deck.length;
    const K = times_cards.length;
    const times_pos_domain = [];
    for (let i = 0; i < (N+1) - K; i++) {
      times_pos_domain.push(i);
    }
    const times_pos = randomSample(times_pos_domain, K);
    times_pos.sort();

    for (let i = 0; i < times_pos.length; i++) {
      times_pos[i] += i;
    }

    const times_pos_set = new Set(times_pos);
    const other_pos = [];
    for (let i = 0; i < N; i++) {
      if (!times_pos_set.has(i))
        other_pos.push(i);
    }

    // Our positions are ordered, so shuffle the partitioned cards instead.
    randomShuffle(times_cards)
    randomShuffle(other_cards)

    // And finally collate.
    const shuffled = new Array(N);
    for (let i = 0; i < K; i++)
        shuffled[times_pos[i]] = times_cards[i];
    for (let i = 0; i < N - K; i++)
        shuffled[other_pos[i]] = other_cards[i]
    return shuffled;
}

// For Game 8.
const Piece = {
  KING: 'king',
  GENERAL: 'general',
  MINISTER: 'minister',
  MAN: 'man',
  FEUDAL_LORD: 'feudal-lord',
};
// Moves are (type, from_rank, from_file, to_rank, to_file) tuples.
const OPTIMAL_MOVES = [
    [
        [Piece.GENERAL, null, null, 3, 2],
        [Piece.MINISTER, null, null, 4, 2],
        [Piece.GENERAL, null, null, 2, 1],
        [Piece.MAN, 4, 3, 3, 3],
        [Piece.MAN, null, null, 3, 1],
        [Piece.MINISTER, 4, 2, 3, 1],
        [Piece.GENERAL, 2, 1, 3, 1],
    ],
    [
        [Piece.GENERAL, null, null, 3, 2],
        [Piece.MINISTER, null, null, 3, 1],
        [Piece.GENERAL, null, null, 2, 1],
        [Piece.MINISTER, 3, 1, 2, 2],
        [Piece.KING, 1, 3, 2, 2],
        [Piece.MAN, 4, 3, 3, 3],
        [Piece.GENERAL, 2, 1, 3, 1],
    ],
    [
        [Piece.GENERAL, null, null, 3, 2],
        [Piece.MINISTER, null, null, 3, 1],
        [Piece.GENERAL, null, null, 2, 1],
        [Piece.MINISTER, 3, 1, 4, 2],
        [Piece.MAN, null, null, 3, 1],
        [Piece.MINISTER, 4, 2, 3, 1],
        [Piece.GENERAL, 2, 1, 3, 1],
    ],
];
const INITIAL_PIECES = [
    // Player 1's initial pieces.
    { 'type': Piece.KING, 'player': 1, 'rank': 1, 'file': 3},
    { 'type': Piece.MINISTER, 'player': 1, 'rank': 2, 'file': 3},
    { 'type': Piece.MAN, 'player': 1, 'rank': null, 'file': null},
    { 'type': Piece.GENERAL, 'player': 1, 'rank': null, 'file': null},
    { 'type': Piece.GENERAL, 'player': 1, 'rank': null, 'file': null},
    // Player 2's initial pieces.
    { 'type': Piece.KING, 'player': 2, 'rank': 4, 'file': 1},
    { 'type': Piece.MAN, 'player': 2, 'rank': 4, 'file': 3},
    { 'type': Piece.MINISTER, 'player': 2, 'rank': null, 'file': null},
];

window.game8Initial = async () => {
  return {
      'playerTurn': 1,
      'moveNumber': 1,
      'pieces': INITIAL_PIECES,
  };
};

window.game8Check = async (moves) => {
  for (const optimalMoves of OPTIMAL_MOVES) {
    if (optimalMoves.length !== moves.length) continue;
    for (let i = 0; i < optimalMoves.length; i++) {
      let matches = true;
      const move = [moves[i]['type'], moves[i]['fromRank'], moves[i]['fromFile'], moves[i]['toRank'], moves[i]['toFile']]
      for (let j = 0; j < 5; j++) {
        if (optimalMoves[i][j] !== move[j]) {
          matches = false;
          break;
        }
      }
      if (matches) {
        return {'optimal': true};
      }
    }
  }
  return {'optimal': false};
};


/// utility
function randomSample(arr, n) {
  if (n > arr.length) throw new Error('invalid n');
  const outputIndices = new Set();
  while (outputIndices.size < n) {
    const newIndex = randomInt(0, arr.length - 1);
    outputIndices.add(newIndex);
  }
  return [...outputIndices].map(i => arr[i]);
}

function randomInt(a, b) {
  return a + Math.floor(Math.random() * (b - a + 1));
}

function randomShuffle(arr) {
  for (let i = 0; i < arr.length - 1; i++) {
    const chosenIndex = randomInt(i, arr.length - 1);
    if (chosenIndex !== i) {
      const temp = arr[chosenIndex];
      arr[chosenIndex] = arr[i];
      arr[i] = temp;
    }
  }
}
