import math
import re
import string

alphabet = string.ascii_uppercase
vowels = set(['A', 'E','I','O','U'])
consonants = set([c for c in alphabet if c not in vowels])
letter_number = dict(zip(alphabet, range(26), ))

numbers = ['zero', 'one','two','three','four','five','six','seven','eight','nine','ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen','nineteen','twenty', 'twentyone', 'twentytwo', 'twentythree', 'twentyfour', 'twentyfive', 'twentysix', 'twentyseven', 'twentyeight', 'twentynine', 'thirty',]

element_names =  ['H','He','Li','Be','B','C','N','O','F','Ne','Na','Mg','Al','Si','P','S','Cl','Ar','K','Ca','Sc','Ti','V','Cr','Mn','Fe']
element = dict(zip(range(len(element_names)), [e.upper() for e in element_names]))

greek_names =  ['alpha', 'beta', 'gamma', 'delta',
                'epsilon', 'zeta', 'eta', 'theta',
                'iota', 'kappa', 'lambda', 'mu',
                'nu', 'xi', 'omicron', 'pi', 'rho',
                'sigma', 'tau', 'upsilon', 'phi',
                'chi', 'psi', 'omega',]
greeks = dict(zip(range(len(greek_names)), [e.upper() for e in greek_names]))

def shift_string(input, shift):
    input = input.upper()
    shifted_alphabet = alphabet[shift:] + alphabet[:shift]
    table = str.maketrans(alphabet, shifted_alphabet)
    return input.translate(table)

def next_letter(letter):
    return shift_string(letter, 1)

def prev_letter(letter):
    return shift_string(letter, -1)

def middle(input):
    while (len(input) > 2):
        input = input[1:-1]
    return input

def half_len(input):
	return int(math.ceil(len(input)/2.))

num_map = [(1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'), (100, 'C'), (90, 'XC'),
           (50, 'L'), (40, 'XL'), (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')]

def to_roman_numeral(num):
    roman = ''

    while num > 0:
        for i, r in num_map:
            while num >= i:
                roman += r
                num -= i

    return roman

states = ['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']

### letter functions

def a(word, input):
    # flip every bigram of INPUT
    input_plus = input + " "
    output = ""
    for i in range(0,len(input),2):
        output += input_plus[i+1] + input_plus[i]
    return re.sub(" ","",output)

def b(word, input):
    # remove last letter and prepend middlest letter
    result = input[:-1]
    return middle(result) + result

def c(word, input):
    # replace middle letters with two letters 3 apart on either side
    left = ''
    right = ''
    while (len(input) > 2):
        left = left + input[0]
        right = input[-1] + right
        input = input[1:-1]
    return left + shift_string(input[0],-3) + shift_string(input[-1],3) + right

def d(word, input):
    # alpha letter bank
    return "".join(sorted(set(input)))

def e(word, input):
    # replace last letter with scrabble score of WORD
    SCORES = {"a": 1, "c": 3, "b": 3, "e": 1, "d": 2, "g": 2,
             "f": 4, "i": 1, "h": 4, "k": 5, "j": 8, "m": 3,
             "l": 1, "o": 1, "n": 1, "q": 10, "p": 3, "s": 1,
             "r": 1, "u": 1, "t": 1, "w": 4, "v": 4, "y": 4,
             "x": 8, "z": 10}

    total = 0
    for letter in word.lower():
        total += SCORES[letter]

    total = (total - 1) % 26
    score_as_letter = alphabet[total]
    return input[:-1] + score_as_letter

def f(word, input):
    # X + first half + Y + last half where X & Y are after and before last letter of WORD
    return prev_letter(word[-1]) + input[:half_len(input)] + next_letter(word[-1]) + input[half_len(input):]

def g(word, input):
    # reverse last N letters where N is pos of first letter of INPUT + 2
    l = alphabet.index(input.upper()[0]) + 1 + 2
    return input[::-1][:l]

def h(word, input):
    # return i0 + w-1 + i(interior) + w-2 + i[-1]
    return input[0] + word[-1] + input[2:-2] + word[-2] + input[-1]

def i(word, input):
    # LEN (word+input) as month + first letter of input
    months = ['january','february','march','april','may','june','july','august','september','october','november','december']
    l = (len(word + input) - 1) % 12
    # cons = re.sub(r'[aeiou]',"",input)
    return months[l] + input[0]

def j(word, input):
    # solfege of WORD length around input
    solfege = ['ti', 'do', 're', 'mi', 'fa', 'sol', 'la']
    note = solfege[len(word) % 7]
    return note[0] + input + note[1:]

def k(word, input):
    # input + metric prefix for (word length - input length)
    larger = ['kilo', 'mega', 'giga', 'tera', 'peta', 'exa', 'zetta', 'yotta']
    smaller = ['milli', 'micro', 'nano', 'pico', 'femto', 'atto', 'zepto', 'yocto']
    diff = len(word) - len(input)
    if diff > 0:
        return input + larger[(diff - 1) % len(larger)]
    elif diff < 0:
        return input + smaller[(abs(diff) - 1)  % len(smaller)]
    else:
        return input + 'equi'
    pass

def l(word, input):
    # advance last letter and append new last letter atbashed
    output = input[:-1] + shift_string(input[-1], 1)
    letter_pos =  alphabet.index(output.upper()[-1])
    alphabet_reversed = alphabet[::-1]
    return output + alphabet_reversed[letter_pos]

def m(word, input):
    # A-1 A word[1:] Z Z + 1
    return shift_string(input[0], -1) + input[0] + word[1:] + input[-1] + shift_string(input[-1], 1)

def n(word, input):
    # letter 1 + letter 2 of word + letter 1 n times until output = word length
    output = input[0] + word[1]
    for x in range(len(word) - 2):
        output += input[0]
    return output

def o(word, input):
    # 2nd shifted back + 1st + last + n-1 shifted right
    return prev_letter(input[1]) + input[0] + input[-1] + next_letter(input[-2])

def p(word, input):
    # prepend state abbreviation of WORD's last letter
    return states[alphabet.index(word.upper()[-1])] + input

def q(word, input):
    # length of input in letter form + middle letter or 2 + last letter of word
    return alphabet[len(input) - 1] + input[-3:]

def r(word, input):
    # Change first letter to greek letter in that same pos in alphabet
    greek = greek_names[alphabet.index(input.upper()[0]) % 24]
    return greek + input[1:]

def s(word, input):
    last_in_word = alphabet.index(word.upper()[-1]) + 1
    return to_roman_numeral(last_in_word * len(word) * len(input)) + input[-3:]

def t(word, input):
    return "a" + input + alphabet[(len(input) + 1) % 26]

def u(word, input):
    # prepend length in roman & append length in alpha, twice
    alpha_len = alphabet[(len(input) - 1) % 26]
    return to_roman_numeral(len(input)) + input + alpha_len + alpha_len

def v(word, input):
    # letters 1 & 2 + length of WORD spelled out + letter 3
    len_word = len(word) + len (input)
    num = numbers[len_word]
    num_len = len(num)
    return input[:2] + num + (input[2] if len(input) > 2 else '')

def w(word, input):
    # flip word and replace middle with length of WORD in letter form
    return input[-1] + input[-2] + alphabet[len(word.upper()) - 1] + input[1] + input[0]

def x(word, input):
    # chem symbols of 1 and last of word
    input = input.upper()
    symbols = ['H','He','Li','Be','B','C','N','O','F','Ne','Na','Mg','Al','Si','P','S','Cl','Ar','K','Ca','Sc','Ti','V','Cr','Mn','Fe']
    return symbols[alphabet.index(input[0])] + symbols[alphabet.index(input[-1])]

def y(word, input):
    # return last letter twice + middle 2 letters
    left = ''
    right = ''
    stripped = input
    while (len(stripped) > 2):
        left = left + stripped[0]
        right = stripped[-1] + right
        stripped = stripped[1:-1]
    return input[-1] + input[-1] + stripped

def z(word, input):
    # rot-13 interior letters and prepend
    return shift_string(input[1:-1], 13) + input
