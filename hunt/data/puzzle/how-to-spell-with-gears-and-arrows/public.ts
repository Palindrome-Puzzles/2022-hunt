import { Updates, Refresh } from './types';
import { PublicStateManager } from "@common/team-puzzle-state";
import { GEARS } from './util';
import { cloneDeep } from 'lodash-es';

const INITIAL: Refresh = {
  "engaged": false,
  "rotation": 0,
  "gears": {
    "A": {
      "offset": 0,
      "pegs": {
        "0": {
          "index": 0,
          "letter": null,
          "stop": false
        },
        "4": {
          "index": 4,
          "letter": null,
          "stop": false
        },
        "6": {
          "index": 6,
          "letter": null,
          "stop": false
        },
        "8": {
          "index": 8,
          "letter": null,
          "stop": false
        },
        "12": {
          "index": 12,
          "letter": null,
          "stop": false
        },
        "14": {
          "index": 14,
          "letter": null,
          "stop": false
        },
        "16": {
          "index": 16,
          "letter": null,
          "stop": false
        },
        "18": {
          "index": 18,
          "letter": null,
          "stop": false
        },
        "20": {
          "index": 20,
          "letter": null,
          "stop": false
        }
      }
    },
    "B": {
      "offset": 0,
      "pegs": {
        "1": {
          "index": 1,
          "letter": null,
          "stop": false
        },
        "3": {
          "index": 3,
          "letter": null,
          "stop": false
        },
        "5": {
          "index": 5,
          "letter": null,
          "stop": false
        },
        "11": {
          "index": 11,
          "letter": null,
          "stop": false
        },
        "13": {
          "index": 13,
          "letter": null,
          "stop": false
        }
      }
    },
    "C": {
      "offset": 0,
      "pegs": {
        "0": {
          "index": 0,
          "letter": null,
          "stop": false
        },
        "2": {
          "index": 2,
          "letter": null,
          "stop": false
        },
        "4": {
          "index": 4,
          "letter": null,
          "stop": false
        },
        "6": {
          "index": 6,
          "letter": null,
          "stop": false
        },
        "8": {
          "index": 8,
          "letter": null,
          "stop": false
        },
        "10": {
          "index": 10,
          "letter": null,
          "stop": false
        },
        "12": {
          "index": 12,
          "letter": null,
          "stop": false
        },
        "18": {
          "index": 18,
          "letter": null,
          "stop": false
        },
        "20": {
          "index": 20,
          "letter": null,
          "stop": false
        },
        "22": {
          "index": 22,
          "letter": null,
          "stop": false
        },
        "24": {
          "index": 24,
          "letter": null,
          "stop": false
        }
      }
    },
    "D": {
      "offset": 0,
      "pegs": {
        "1": {
          "index": 1,
          "letter": null,
          "stop": false
        },
        "3": {
          "index": 3,
          "letter": null,
          "stop": false
        },
        "5": {
          "index": 5,
          "letter": null,
          "stop": false
        },
        "9": {
          "index": 9,
          "letter": null,
          "stop": false
        },
        "13": {
          "index": 13,
          "letter": null,
          "stop": false
        },
        "15": {
          "index": 15,
          "letter": null,
          "stop": false
        },
        "17": {
          "index": 17,
          "letter": null,
          "stop": false
        }
      }
    },
    "E": {
      "offset": 0,
      "pegs": {
        "0": {
          "index": 0,
          "letter": null,
          "stop": false
        },
        "2": {
          "index": 2,
          "letter": null,
          "stop": false
        },
        "4": {
          "index": 4,
          "letter": null,
          "stop": false
        },
        "6": {
          "index": 6,
          "letter": null,
          "stop": false
        },
        "8": {
          "index": 8,
          "letter": null,
          "stop": false
        },
        "10": {
          "index": 10,
          "letter": null,
          "stop": false
        },
        "12": {
          "index": 12,
          "letter": null,
          "stop": false
        },
        "18": {
          "index": 18,
          "letter": null,
          "stop": false
        }
      }
    }
  }
};

const LOCAL_STORAGE_KEY = 'hunt:how-to-spell-with-gears-and-arrows:public';
const fromStorage = localStorage.getItem(LOCAL_STORAGE_KEY);
const parsedFromStorage: Refresh | null = fromStorage ? JSON.parse(fromStorage) : null;
let state = parsedFromStorage || INITIAL;

// In the live hunt, this was done by the server so the state could be synced
// across teams.
export const PUBLIC_STATE_MANAGER: PublicStateManager<Updates, Refresh> = {
  initial: () => {
    return cloneDeep(state);
  },
  onMessage: (message) => {
    // No need to handle refresh/abandon for this puzzle.
    if (message.type !== 'state.update') return null;

    const update = message.updates;
    if (update.action === 'engaged') {
      state = {...state, engaged: !state.engaged};
    } else if (update.action === 'rotation') {
      state = {...state, rotation: state.rotation + update.delta};
    } else if (update.action === 'offset') {
      state = {
        ...state,
        gears: {
          ...state.gears,
          [update.gear]: {
            ...state.gears[update.gear],
            offset: state.gears[update.gear].offset + update['delta'],
          }
        },
      }
    } else if (update.action === 'label') {
      for (const label of update.labels) {
        state = {
          ...state,
          gears: {
            ...state.gears,
            [label.gear]: {
              ...state.gears[label.gear],
              pegs: {
                ...state.gears[label.gear].pegs,
                [label.peg]: {
                  ...state.gears[label.gear].pegs[label.peg],
                  letter: label.value === 'STOP' ? null : label.value,
                  stop: label.value === 'STOP',
                },
              },
            },
          },
        };
      }
    }
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(state));
    return cloneDeep(state);
  },
}

