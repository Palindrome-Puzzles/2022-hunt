const Card = {
  BLUE: 'blue',
  BROWN: 'brown',
  GREEN: 'green',
  GREY: 'grey',
  ORANGE: 'orange',
  PINK: 'pink',
  PURPLE: 'purple',
  RED: 'red',
  WHITE: 'white',
  YELLOW: 'yellow',

  // Are not available at the start.
  BLACK: 'black',
  GOLD: 'gold',
  MAROON: 'maroon',
  TURQUOISE: 'turquoise',
};
const INITIAL_CARDS = [Card.BLUE, Card.BROWN, Card.GREEN, Card.GREY, Card.ORANGE, Card.PINK, Card.PURPLE, Card.RED, Card.WHITE, Card.YELLOW];
const COMBINATIONS = {
    [Card.BROWN]: {
        [Card.RED]: Card.BLUE,
        [Card.GREY]: Card.PURPLE,
        [Card.GREEN]: Card.ORANGE,
        [Card.BLUE]: Card.GOLD,
        [Card.PINK]: Card.GREY,
        [Card.WHITE]: Card.GREY,
        [Card.PURPLE]: Card.MAROON,
        [Card.YELLOW]: Card.GREEN,
        [Card.ORANGE]: Card.WHITE,
    },
    [Card.RED]: {
        [Card.BROWN]: Card.GOLD,
        [Card.GREY]: Card.TURQUOISE,
        [Card.GREEN]: Card.PURPLE,
        [Card.BLUE]: Card.PINK,
        [Card.PINK]: Card.ORANGE,
        [Card.WHITE]: Card.BLUE,
        [Card.PURPLE]: Card.BLUE,
        [Card.YELLOW]: Card.ORANGE,
        [Card.ORANGE]: Card.YELLOW,
    },
    [Card.GREY]: {
        [Card.BROWN]: Card.MAROON,
        [Card.RED]: Card.GOLD,
        [Card.GREEN]: Card.BLACK,
        [Card.BLUE]: Card.GOLD,
        [Card.PINK]: Card.YELLOW,
        [Card.WHITE]: Card.BLUE,
        [Card.PURPLE]: Card.TURQUOISE,
        [Card.YELLOW]: Card.PINK,
        [Card.ORANGE]: Card.PURPLE,
    },
    [Card.GREEN]: {
        [Card.BROWN]: Card.TURQUOISE,
        [Card.RED]: Card.WHITE,
        [Card.GREY]: Card.TURQUOISE,
        [Card.BLUE]: Card.MAROON,
        [Card.PINK]: Card.PURPLE,
        [Card.WHITE]: Card.BLACK,
        [Card.PURPLE]: Card.BLACK,
        [Card.YELLOW]: Card.WHITE,
        [Card.ORANGE]: Card.YELLOW,
    },
    [Card.BLUE]: {
        [Card.BROWN]: Card.YELLOW,
        [Card.RED]: Card.GREY,
        [Card.GREY]: Card.ORANGE,
        [Card.GREEN]: Card.PURPLE,
        [Card.PINK]: Card.GOLD,
        [Card.WHITE]: Card.BROWN,
        [Card.PURPLE]: Card.TURQUOISE,
        [Card.YELLOW]: Card.GREEN,
        [Card.ORANGE]: Card.RED
    },
    [Card.PINK]: {
        [Card.BROWN]: Card.BLACK,
        [Card.RED]: Card.GREEN,
        [Card.GREY]: Card.GREEN,
        [Card.GREEN]: Card.BLACK,
        [Card.BLUE]: Card.PURPLE,
        [Card.WHITE]: Card.YELLOW,
        [Card.PURPLE]: Card.GOLD,
        [Card.YELLOW]: Card.WHITE,
        [Card.ORANGE]: Card.GREEN,
    },
    [Card.WHITE]: {
        [Card.BROWN]: Card.GOLD,
        [Card.RED]: Card.YELLOW,
        [Card.GREY]: Card.YELLOW,
        [Card.GREEN]: Card.GREY,
        [Card.BLUE]: Card.PINK,
        [Card.PINK]: Card.MAROON,
        [Card.PURPLE]: Card.MAROON,
        [Card.YELLOW]: Card.MAROON,
        [Card.ORANGE]: Card.WHITE,
    },
    [Card.PURPLE]: {
        [Card.BROWN]: Card.MAROON,
        [Card.RED]: Card.TURQUOISE,
        [Card.GREY]: Card.WHITE,
        [Card.GREEN]: Card.GOLD,
        [Card.BLUE]: Card.RED,
        [Card.PINK]: Card.BLACK,
        [Card.WHITE]: Card.BLUE,
        [Card.YELLOW]: Card.PINK,
        [Card.ORANGE]: Card.BLACK,
    },
    [Card.YELLOW]: {
        [Card.BROWN]: Card.PURPLE,
        [Card.RED]: Card.RED,
        [Card.GREY]: Card.WHITE,
        [Card.GREEN]: Card.PINK,
        [Card.BLUE]: Card.GOLD,
        [Card.PINK]: Card.MAROON,
        [Card.WHITE]: Card.TURQUOISE,
        [Card.PURPLE]: Card.BLUE,
        [Card.ORANGE]: Card.TURQUOISE,
    },
    [Card.ORANGE]: {
        [Card.BROWN]: Card.RED,
        [Card.RED]: Card.TURQUOISE,
        [Card.GREY]: Card.BLACK,
        [Card.GREEN]: Card.GREY,
        [Card.BLUE]: Card.TURQUOISE,
        [Card.PINK]: Card.BROWN,
        [Card.WHITE]: Card.YELLOW,
        [Card.PURPLE]: Card.PINK,
        [Card.YELLOW]: Card.GREEN,
    }
};
const RECIPES = [
    {
        'inputs': [Card.RED, Card.WHITE, Card.MAROON],
        'name': 'DEY-YIC',
        'message': 'It auto-activates, and in the nearby Subzero Kitchen Delta (SKD), the ship\u2019s Sleeping Secondary Captain (SSC) is released from a Suspended Animation Tank (SAT).',
        'result': {
            'progress': 2,
            'under_progress_message': 'The captain cannot breathe the lack of air, and quickly dies.',
            'at_progress_message': null,
        }
    },
    {
        'inputs': [Card.ORANGE, Card.GOLD, Card.TURQUOISE],
        'name': 'TEL-AST-URY',
        'message': 'It auto-activates, and in the Subzero Kitchen Delta (SKD), a Developments Information Monitor (DIM) powers on, and displays the recent happenings with the ship. It then turns off.',
        'result': {
            'progress': 3,
            'under_progress_message': null,
            'at_progress_message': 'The captain, now briefed, nods to you and walks down the Upper Hallway Alpha (UHA) to stand on the Matter Teleport Dais (MTD).',
        }
    },
    {
        'inputs': [Card.YELLOW, Card.PURPLE],
        'name': 'CMD',
        'message': null,
        'result': {
            'progress': 4,
            'under_progress_message': 'It auto-activates, and you can see the Matter Teleport Dais (MTD) in nearby Upper Hallway Alpha (UHA) glows briefly.',
            'at_progress_message': 'It auto-activates, and teleports the captain from the Matter Teleport Dais (MTD) to the bridge, where they negotiate with the aliens. You soon receive a message from the captain, thanking you for saving the ship and possibly the entire Trigra-M civilization. It would be good to find a simple reply, that conveys what you saw during all this. You know the triads of components that come out of your replicator, and the designations of various items you have encountered. Perhaps by relating them you can form some appropriate message.',
        }
    },
    {
        'inputs': [Card.GREEN, Card.BLUE, Card.GREY],
        'name': 'YST-ARS',
        'message': 'It auto-activates.  Just outside your Droid Storage Alcove (DSA), you see the Hull Repair Machine (HRM) repair the hole in the ship\u2019s Duranium Inner Hull (DIH).',
        'result': {
            'progress': 0,
            'under_progress_message': null,
            'at_progress_message': null,
        }
    },
    {
        'inputs': [Card.BLUE, Card.PINK, Card.BLACK],
        'name': 'TRY',
        'message': 'It auto-activates.  You can hear Traditional Dioxygenated Air (TDA) from the Concentrated Air Supply (CAS) being pumped into the Large Upper Yard (LUY) outside your Droid Storage Alcove (DSA).',
        'result': {
            'progress': 1,
            'under_progress_message': 'It immediately escapes through the hole in the ship\u2019s hull.',
            'at_progress_message': null,
        }
    }
];

let state = null;

window.stubSend = async (body) => {
  if (body.__seq === 0) {
    state = initialState();
    return {...projectState(state), __sid: 'abc', __status: 'success'};
  } else {
    transformState(state, body);
    return {
      ...projectState(state),
      __sid: 'abc',
      __status: state.completed ? 'complete' : 'success',
    };
  }
};

function initialState() {
  return {
    'progress': 0,
    'cards': INITIAL_CARDS,
    'components': [],
    'message': null,
  };
}

function projectState(state) {
  return {
    'cards': state['cards'],
    'components': state['components'],
    'recipes': get_available_recipes(state['components']),
    'message': state['message'],
  };
}

function transformState(state, body) {
  // NB: can skip consistency assertions.
  if (body.action === 'component') {
    const available_cards = new Set(state.cards);
    const used_cards = body.cards;
    const created = COMBINATIONS[used_cards[0]][used_cards[1]];
    const did_drop_items = state['components'].length >= 3;

    let message = `
      <p>The Component Replicator Unit (CRU) takes the <em>${used_cards[0]}</em> and <em>${used_cards[1]}</em> cards, rattles a bit, and creates a triad of components on your conveyor belt.</p>
      <p>You get, in order: <em>${used_cards[0]}</em> component, <em>${created}</em> component, and <em>${used_cards[1]}</em> component.</p>
      `;
    if (did_drop_items) {
      message += '<p>Your conveyor belt only has room for 5 components, so the oldest fell on the floor and broke.</p>';
    }

    state.cards = state.cards.filter(card => !used_cards.includes(card));
    state.components = [...state.components, used_cards[0], created, used_cards[1]];
    if (state.components.length > 5) {
      state.components = state.components.slice(state.components.length - 5);
    }
    state.message = message;
  } else {
    const recipe = RECIPES[body.recipe - 1];
    const components_in_use_order = state.components.filter(c => recipe['inputs'].includes(c));
    const should_advance = state.progress === recipe.result.progress;
    let message_parts = [];
    if (components_in_use_order.length === 3) {
      message_parts.push(`<p>You combine the ${components_in_use_order[0]} component, the ${components_in_use_order[1]} component, and the ${components_in_use_order[2]} component to build the ${recipe["name"]} device.</p>`);
    } else {
      message_parts.push(`<p>You combine the ${components_in_use_order[0]} component and the ${components_in_use_order[1]} component to build the ${recipe["name"]} device.</p>`);
    }

    if (recipe.message) {
      message_parts.push(`<p>${recipe["message"]}</p>`);
    }
    if (should_advance && recipe['result']['at_progress_message']) {
      message_parts.push(`<p>${recipe["result"]["at_progress_message"]}</p>`);
    }
    if (!should_advance && recipe['result']['under_progress_message']) {
      message_parts.push(`<p>${recipe["result"]["under_progress_message"]}</p>`);
    }

    // If there are multiple components of the same color, be careful to only
    // remove one of them.
    const new_components = [...state['components']]
    for (const input of recipe['inputs']) {
      const index = new_components.indexOf(input);
      new_components.splice(index, 1);
    }

    state.progress = should_advance ? state.progress + 1 : state.progress;
    state.components = new_components;
    state.message = message_parts.join('\n');
  }
}

function get_available_recipes(components) {
  const components_set = new Set(components)
  const recipes = [];
  for (let i = 0; i < RECIPES.length; i++) {
    if (RECIPES[i]['inputs'].every(input => components_set.has(input))) {
      recipes.push(i + 1);
    }
  }
  return recipes;
}
