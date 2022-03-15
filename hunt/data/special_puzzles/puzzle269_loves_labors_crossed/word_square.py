"""
Love's Labor's Crossed

Validate a user-supplied word square and return the second part of the puzzle
with bigrams matching the word square from the first part.
"""

# The content of this puzzle is Copyright (c) 2021 David Shukan.

# The code to validate the word square and deliver a response is released
# under the following license:
#
# MIT License
#
# Copyright (c) 2021 Michael Seplowitz
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import re

from hunt.data_loader.puzzle import get_puzzle_data_text

dim = 5

square_string_re = re.compile('^[a-zA-Z]{' + str(dim*dim) + '}$')

def make_word_list():
    word_list_text = get_puzzle_data_text("loves-labors-crossed", 'twl06.txt')
    assert word_list_text is not None

    word_list = set()
    for line in word_list_text.splitlines():
        if line[0] == '#':
            continue
        word_list.add(line)
    return word_list

valid_words = make_word_list()

def number_from_letter(letter):
    return (ord(letter.lower()) - ord("a") + 1) % 26

def letter_from_number(number):
    if number == 0:
        return "z"
    return chr(ord("a") + number - 1)

def validate(square_string):
    if not square_string_re.match(square_string):
        return {
            'error': 'The entered string is not a string of exactly 25 letters and nothing else.',
        }

    square_string = square_string.lower()

    square = [[]] * dim
    for row in range(dim):
        square[row] = square_string[row*dim : (row+1)*dim]

    row_ends = [""] * dim
    for row in range(dim):
        word = square[row]
        if word not in valid_words and word[::-1] not in valid_words:
            return {
                'error': f"Grid entry [{word}] is not a valid word, forwards or backwards."
            }
        row_ends[row] = letter_from_number(
            sum(number_from_letter(letter) for letter in word) % 26)

    col_ends = [""] * dim
    for col in range(dim):
        word = "".join(square[row][col] for row in range(dim))
        if word not in valid_words and word[::-1] not in valid_words:
            return {
                'error': f"Grid entry [{word}] is not a valid word, forwards or backwards."
            }
        col_ends[col] = letter_from_number(
            sum(number_from_letter(letter) for letter in word) % 26)

    if len(set(row_ends + col_ends)) != dim * 2:
        return {
            'error': "The letter-value sums of the across and down words, modulo 26,"
                     + " do not represent 10 different letters.",
        }

    row_ends_word = "".join(row_ends)
    if row_ends_word not in valid_words and row_ends_word[::-1] not in valid_words:
        return {
            'error': f"The across words form [{row_ends_word}],"
                     + " which is not a valid word, forwards or backwards",
        }

    col_ends_word = "".join(col_ends)
    if col_ends_word not in valid_words and col_ends_word[::-1] not in valid_words:
        return {
            'error': f"The down words form [{col_ends_word}],"
                     + " which is not a valid word, forwards or backwards",
        }

    bigrams = pick_bigrams(row_ends, col_ends).upper()

    return {
'nextHTML': f"""
<p class="centered">
<strong>CONGRATULATIONS!</strong><br>
Your significant other accepted your offering and responded as follows:
</p>

<p class="centered" data-skip-inline-styles="true">
Any answer can read either right, left, down, or up.<br>
The answer that is earliest alphabetically reads across (either right or left).<br>
More answers read right than left, and more answers read down than up.
</p>

<hr>

<ul>
  <li>Barrage used regularly to lock horns</li>
  <li>Bores fragment of glass counter with opening in glass for pathway, essentially</li>
  <li>Bunch of trees presented a turning to red and orange</li>
  <li>Female fish has sympathy</li>
  <li>Gala lacks source of snacks like cheeses</li>
  <li>Gullible deviant returned without clothing</li>
  <li>Mountain range located past river country</li>
  <li>Russia’s leader, following article, understood language</li>
  <li>Some rude answers, more than one notable at school</li>
  <li>Spirit mostly added in to season marble</li>
</ul>

<p class="centered" data-skip-inline-styles="true">{bigrams}</p>

<p class="centered note" data-skip-inline-styles="true">(NOTE: Please provide your answer in the form that is the title of a Wikipedia article.)</p>
"""}


def pick_bigrams(row_ends, col_ends):
    """
    abcde  1
    fghij  2
    klmno  3 < row_ends
    pqrst  4
    uvwxy  5
    67890
      ^ col_ends
    """

    table = str.maketrans({
        "1": row_ends[0],
        "2": row_ends[1],
        "3": row_ends[2],
        "4": row_ends[3],
        "5": row_ends[4],

        "6": col_ends[0],
        "7": col_ends[1],
        "8": col_ends[2],
        "9": col_ends[3],
        "0": col_ends[4],
    })

    return "20-57-61-48-19-05-39-82-10-85-58-94-83-72-93-16-71".translate(table)

if __name__ == "__main__":
    print(validate('DEANSRURALAGGIEGROVESATEF'))
    # fails

    print(validate('arecagavelimideoitarseert'))
    # UD-OT-YB-KI-BE-DO-NE-IU-BD-IO-OI-EK-IN-TU-EN-BY-TB

    print(validate('arecagazelimideoitarseert'))
    # gazel is not a valid word

    print(validate('baaedanilenotchglensserua'))
    # OK-LU-QM-EA-MC-KL-HC-AO-MK-AL-LA-CE-AH-UO-CH-MQ-UM

    print(validate('bakedanilenotchglensserua'))
    # not 10 different letters
