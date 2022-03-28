const SOLUTIONS = {
    'skeleton': 'apv',
    'kraken': 'bzq',
    'dragon': 'cwi',
    'ghost': 'dmx',
    'mummy': 'en',
    'zombie': 'foj',
    'orc': 'gk',
    'cyclops': 'hs',
    'achillesheel': 'truly',
};
const CODENAMES = {
    'cyclops': '0',
    'dragon': '1',
    'ghost': '2',
    'kraken': '3',
    'mummy': '4',
    'orc': '5',
    'skeleton': '6',
    'zombie': '7',
    'achillesheel': 'final',
};
const INPUTS = {
    'cyclops': 'gelatinous',
    'dragon': 'dimwit',
    'ghost': 'vowel',
    'kraken': 'obsolescent',
    'mummy': 'miracle',
    'orc': 'acumen',
    'skeleton': 'leopard',
    'zombie': 'profound',
};

async function getValidWords() {
  let response = await fetch(window.puzzlePosthuntStaticDirectory + "words.txt")
  let text = await response.text()

  if (!response.ok || text.startsWith("Unknown file ")) {
    throw new Error(text)
  }

  const dictionary = new Set(
    text.split("\n")
      .filter(line => !line.startsWith('#'))
      // Handle \r on windows.
      .map(line => line.trim()))
  return dictionary
}

const VALID_WORDS = getValidWords();

window.stubSend = async (data) => {
    let spell = data['spell'];
    const correct_spells = data['spells'];

    if (spell == "")
        return {
            'status': 'fail',
            'reason': 'No spell present.'
        };

    spell = spell.trim().toLowerCase();
    spell = spell.replaceAll(/\s+/g, ' ');

    const nonLetters = spell.replaceAll(/[a-z\s]/g, '');
    if (nonLetters.length > 0)
        return {
            'status': 'fail',
            'reason': 'Letters only, please.'
        };

    if (spell.length > 60)
        return JsonResponse({
            'status': 'fail',
            'reason': 'Too long.'
        })

    const words = spell.split(" ");
    const outputs = [];

    const wordsLookup = await VALID_WORDS;
    for (const word of words) {
        if (word.length < 3)
            return {
                'status': 'fail',
                'reason': 'Each word must be three letters or longer.'
            }
        if (!wordsLookup.has(word))
            return {
                'status': 'fail',
                'reason': 'Each word must be in the dictionary.'
            };

    }

    let input = words.pop();
    let output = input;
    let pattern = ""
    let message = ""

    if (words.length == 0)
        return {
            'status': 'fail',
            'reason': 'Spells must be two words or longer.'
        }

    // if you're reusing a spell, say so…
    // collect all first letters, but not from the last words
    let depleted_letters = ""
    for (const correct_spell of Object.values(correct_spells)) {
      const correctSpellWords = correct_spell.split(' ');
      const ignoreLast = correctSpellWords.slice(0, correctSpellWords.length - 1);
      depleted_letters += ignoreLast.map(w => w[0].toLowerCase()).join('');
    }

    if (spell == "truly powerful") {
      return {
          'status': 'success',
          'message': 'You certainly are. 😉'
      }
    }

    let depleted = false
    // cycle thru and apply transformations
    const reversedWords = [...words].reverse();
    for (const word of reversedWords) {
        const letter = word[0]

        if (depleted_letters.indexOf(letter) > -1)
            depleted = true

        pattern = letter + pattern;
        output = LETTER_FNS[letter](word, output).toLowerCase();
        outputs.push(output.toUpperCase())
    }

    output = output.toLowerCase().replaceAll(' ', '');
    const sol = SOLUTIONS[output];
    let codename = CODENAMES[output]
    const proper_input = INPUTS[output]
    const proper_length = sol ? sol.length : 0;
    let status = ""
    if (sol && pattern != '') {
        message = `Well this is awkward. Looks like you somehow found another way to defeat that monster. Alas, this isn't the intended spell for ${output.toUpperCase()}. Keep going.`

        if (output == 'achillesheel' && sol == pattern) {
            output = 'achilles heel'
            outputs[outputs.length-1] = 'ACHILLES HEEL'
            message = "Now that's what I call a spell. Call it in!"
            status = "final"
        } else if (!Object.values(INPUTS).includes(input))
            message = "Nice work, but you need a different final word."
        else if (proper_length != words.length)
            message = "Nice work, but that monster's spell requires a different number of words."
        else if (input != proper_input)
            message = "Clever! But that monster only responds to a different final word."
        else if (sol == pattern) {
            message = `Hooray! You destroyed the ${output.toUpperCase()}!`
            codename = codename
            status = "monster"
        }
    } else if (depleted) {
        return {
                'status': 'fail',
                'reason': 'One or more of these transformations has exhausted its magic.'
            }
    }

    return {
        'status': status,
        'spell': spell,
        'message': message,
        'codename': `monster${codename}`,
        'output': output.toUpperCase(),
    };
};

const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');
const vowels = new Set(['A', 'E','I','O','U'])
const consonants = alphabet.filter(c => !vowels.has(c));
const numbers = ['zero', 'one','two','three','four','five','six','seven','eight','nine','ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen','nineteen','twenty', 'twentyone', 'twentytwo', 'twentythree', 'twentyfour', 'twentyfive', 'twentysix', 'twentyseven', 'twentyeight', 'twentynine', 'thirty']
const greek_names =  ['alpha', 'beta', 'gamma', 'delta',
                'epsilon', 'zeta', 'eta', 'theta',
                'iota', 'kappa', 'lambda', 'mu',
                'nu', 'xi', 'omicron', 'pi', 'rho',
                'sigma', 'tau', 'upsilon', 'phi',
                'chi', 'psi', 'omega'];

function shift_string(input, shift) {
  input = input.toUpperCase();
  if (shift < 0) shift += alphabet.length;

  const shifted_alphabet = [...alphabet.slice(shift), ...alphabet.slice(0, shift)];
  return input
    .split('')
    .map(c => {
      const index = c.charCodeAt(0) - 'A'.charCodeAt(0);
      return shifted_alphabet[index];
    })
    .filter(c => !!c)
    .join('');
}

function next_letter(letter) {
  return shift_string(letter, 1);
}

function prev_letter(letter) {
  return shift_string(letter, -1);
}

function middle(input) {
  while (input.length > 2) {
    input = input.slice(1, input.length - 1);
  }
  return input;
}

function half_len(input) {
  return Math.ceil(input.length/2)
}

const num_map = [[1000, 'M'], [900, 'CM'], [500, 'D'], [400, 'CD'], [100, 'C'], [90, 'XC'],
           [50, 'L'], [40, 'XL'], [10, 'X'], [9, 'IX'], [5, 'V'], [4, 'IV'], [1, 'I']]

function to_roman_numeral(num) {
  let roman = '';
  while (num > 0) {
    for (const [i, r] of num_map) {
      while (num >= i) {
        roman += r;
        num -= i;
      }
    }
  }
  return roman;
}

const states = ['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']

// letter functions
const LETTER_FNS = {
  a: (word, input) => {
    // flip every bigram of INPUT
    const input_plus = input + " ";
    let output = "";
    for (let i = 0; i < input.length; i += 2)
      output += input_plus[i+1] + input_plus[i]
    return output.replace(' ', '');
  },
  b: (word, input) => {
    // remove last letter and prepend middlest letter
    const result = input.slice(0, input.length - 1);
    return middle(result) + result;
  },
  c: (word, input) => {
    // replace middle letters with two letters 3 apart on either side
    let left = ''
    let right = ''
    while (input.length > 2) {
      left = left + input[0]
      right = input[input.length-1] + right
      input = input.slice(1, input.length - 1)
    }
    return left + shift_string(input[0],-3) + shift_string(input[input.length-1],3) + right
  },
  d: (word, input) => {
    // alpha letter bank
    const split = [...new Set(input.split(''))];
    split.sort();
    return split.join('');
  },
  e: (word, input) => {
    // replace last letter with scrabble score of WORD
    const SCORES = {"a": 1, "c": 3, "b": 3, "e": 1, "d": 2, "g": 2,
             "f": 4, "i": 1, "h": 4, "k": 5, "j": 8, "m": 3,
             "l": 1, "o": 1, "n": 1, "q": 10, "p": 3, "s": 1,
             "r": 1, "u": 1, "t": 1, "w": 4, "v": 4, "y": 4,
             "x": 8, "z": 10}

    let total = 0
    for (const letter of word.toLowerCase())
      total += SCORES[letter];

    total = (total - 1) % 26
    const score_as_letter = alphabet[total];
    return input.slice(0, input.length-1) + score_as_letter
  },
  f: (word, input) => {
      // X + first half + Y + last half where X & Y are after and before last letter of WORD
      return prev_letter(word[word.length-1]) + input.slice(0, half_len(input)) + next_letter(word[word.length-1]) + input.slice(half_len(input))
  },
  g: (word, input) => {
      // reverse last N letters where N is pos of first letter of INPUT + 2
      const firstLetter = input[0].toUpperCase();
      const pos = alphabet.indexOf(firstLetter);
      const N = pos + 1 + 2;
      const reversed = input.split('').reverse().join('');
      return reversed.slice(0, N);
  },
  h: (word, input) => {
      // return i0 + w-1 + i(interior) + w-2 + i[-1]
      return input[0] + word[word.length-1] + input.slice(2, input.length-2) + word[word.length-2] + input[input.length-1];
  },
  i: (word, input) => {
      // LEN (word+input) as month + first letter of input
      const months = ['january','february','march','april','may','june','july','august','september','october','november','december']
      const l = (word.length + input.length - 1) % 12
      // cons = re.sub(r'[aeiou]',"",input)
      return months[l] + input[0];
  },
  j: (word, input) => {
      // solfege of WORD length around input
      const solfege = ['ti', 'do', 're', 'mi', 'fa', 'sol', 'la']
      const note = solfege[word.length % 7];
      return note[0] + input + note.slice(1);
  },
  k: (word, input) => {
      // input + metric prefix for (word length - input length)
      const larger = ['kilo', 'mega', 'giga', 'tera', 'peta', 'exa', 'zetta', 'yotta']
      const smaller = ['milli', 'micro', 'nano', 'pico', 'femto', 'atto', 'zepto', 'yocto']
      const diff = word.length - input.length
      if (diff > 0) {
          return input + larger[(diff - 1) % larger.length];
      } else if (diff < 0) {
          return input + smaller[(Math.abs(diff) - 1)  % smaller.length];
      } else {
          return input + 'equi';
      }
  },
  l: (word, input) => {
      // advance last letter and append new last letter atbashed
      const output = input.slice(0, input.length-1) + shift_string(input[input.length-1], 1)
      const letter_pos =  alphabet.indexOf(output[output.length-1].toUpperCase())
      const alphabet_reversed = [...alphabet].reverse().join('');
      return output + alphabet_reversed[letter_pos];
  },
  m: (word, input) => {
      // A-1 A word[1:] Z Z + 1
      return shift_string(input[0], -1) + input[0] + word.slice(1) + input[input.length-1] + shift_string(input[input.length-1], 1)
  },
  n: (word, input) => {
      // letter 1 + letter 2 of word + letter 1 n times until output = word length
      let output = input[0] + word[1]
      for (let x = 0; x < word.length - 2; x++)
          output += input[0];
      return output;
  },
  o: (word, input) => {
      // 2nd shifted back + 1st + last + n-1 shifted right
      return prev_letter(input[1]) + input[0] + input[input.length-1] + next_letter(input[input.length-2])
  },
  p: (word, input) => {
      // prepend state abbreviation of WORD's last letter
      return states[alphabet.indexOf(word[word.length-1].toUpperCase())] + input;
  },
  q: (word, input) => {
      // length of input in letter form + middle letter or 2 + last letter of word
      // ^ incorrect comment??
      return alphabet[input.length - 1] + input.slice(input.length-3)
  },
  r: (word, input) => {
      // Change first letter to greek letter in that same pos in alphabet
      const greek = greek_names[alphabet.indexOf(input[0].toUpperCase()) % 24]
      return greek + input.slice(1);
  },
  s: (word, input) => {
      const last_in_word = alphabet.indexOf(word[word.length-1].toUpperCase()) + 1
      return to_roman_numeral(last_in_word * word.length * input.length) + input.slice(input.length-3);
  },
  t: (word, input) => {
      return "a" + input + alphabet[(input.length + 1) % 26]
  },
  u: (word, input) => {
      // prepend length in roman & append length in alpha, twice
      const alpha_len = alphabet[(input.length - 1) % 26]
      return to_roman_numeral(input.length) + input + alpha_len + alpha_len;
  },
  v: (word, input) => {
      // letters 1 & 2 + length of WORD spelled out + letter 3
      const len_word = word.length + input.length;
      const num = numbers[len_word];
      const num_len = num.length;
      return input.slice(0, 2) + num + (input.length > 2 ? input[2] : '');
  },
  w: (word, input) => {
      // flip word and replace middle with length of WORD in letter form
      return input[input.length-1] + input[input.length-2] + alphabet[word.length - 1] + input[1] + input[0]
  },
  x: (word, input) => {
      // chem symbols of 1 and last of word
      input = input.toUpperCase()
      const symbols = ['H','He','Li','Be','B','C','N','O','F','Ne','Na','Mg','Al','Si','P','S','Cl','Ar','K','Ca','Sc','Ti','V','Cr','Mn','Fe'];
      return symbols[alphabet.indexOf(input[0])] + symbols[alphabet.indexOf(input[input.length-1])]
  },
  y: (word, input) => {
      // return last letter twice + middle 2 letters
      let left = ''
      let right = ''
      let stripped = input
      while (stripped.length > 2) {
        left = left + stripped[0];
        right = stripped[stripped.length-1] + right;
        stripped = stripped.slice(1, stripped.length-1);
      }
      return input[input.length-1] + input[input.length-1] + stripped;
  },
  z: (word, input) => {
      // rot-13 interior letters and prepend
      return shift_string(input.slice(1, input.length-1), 13) + input;
  },
}
