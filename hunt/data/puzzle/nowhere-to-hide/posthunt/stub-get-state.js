// 1. Get a payload from the client containing level number, last word placed (nullable) and current grid state (nullable)
// 2. Validate current grid state
// 3. Confirm whether last placement is valid
// 4. Return valid, invalid (level failed) or success (level finished)
// 5. (if valid) Return next word in sequence

const WORDLIST_ALL = [ ["THE", "RAT", "SIS", "ROPE", "STUN", "EVE", "O", ":*&#"], ["GIVEN", "WIN", "ERA", "SPOT", "FOR", "AD", "*@&"], ["WORDS", "STAR", "ATE", "TALE", "PIN", "A", "$;~@&"], ["ARE", "SPA", "LAIR", "EAST", "LAP", "IN", "EN", "!/@=+"], ["NOT", "LATE", "USE", "CAR", "MEN", "AI", "-&@?"], ["RELEVANT", "EAR", "SOL", "PART", "ACE", "ON", "%*$"] ];
const SECRET_MAP = {"~":"S", "!":"F", "@":"O", "#":"Y", "$":"M", "%":"D", "&":"N", "*":"I", "-":"K", "+":"R", "=":"U", ":":"T", ";":"A", "?":"B", "/":"L"};

const NUM_COLS = 12;
const NUM_ROWS = 25;

class PuzzleRequest {
  constructor(payload) {
    this.level = payload.level
    this.lastWord = payload.last_word
    this.grid = this.buildGrid(JSON.parse(payload['grid']))
    this.wordlist = WORDLIST_ALL[this.level - 1]
  }

  buildGrid(grid) {
    const testGrid = []
    for (let y = 0; y < NUM_ROWS; y++) {
      testGrid.push([]);
      for (let x = 0; x < NUM_COLS; x++) {
        if (grid[y][x] in SECRET_MAP) {
          testGrid[y].push(SECRET_MAP[grid[y][x]]);
        } else {
          testGrid[y].push(grid[y][x]);
        }
      }
    }
    return testGrid;
  }

  verifyGrid() {
    // Skip some of the verification as this is the posthunt version - go ahead and cheat :)
    for (const row of this.grid) {
      const words = row.join('').split(' ').filter(el => el && el.length > 1);
      if (words.some(word => !WORD_LIST.includes(word))) {
        return false;
      }
    }
    for (let i = 0; i < NUM_COLS; i++) {
      const col = [];
      for (let j = 0; j < NUM_ROWS; j++) {
        col.push(this.grid[j][i]);
      }
      const words = col.join('').split(' ').filter(el => el && el.length > 1);
      if (words.some(word => !WORD_LIST.includes(word))) {
        return false;
      }
    }
    return true;
  }

  returnResponse() {
    return {
      'level': this.level,
      'wordlist': this.wordlist,
      'success': this.verifyGrid(),
    }
  }
}

window.stubGetState = function(payload, handler) {
  handler(new PuzzleRequest(payload).returnResponse())
};