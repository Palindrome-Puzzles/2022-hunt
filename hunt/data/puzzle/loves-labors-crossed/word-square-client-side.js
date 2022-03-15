// *****************************************************************************
// Warning: This code contains spoilers for the second phase of the puzzle!
//
// Reading this code is not part of the puzzle. This logic was originally
// performed server-side to prevent bypassing the first phase of the puzzle.
// *****************************************************************************

// MIT License
//
// Copyright (c) 2022 Michael Seplowitz
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

var dictionary = undefined

async function getValidWords() {
  if (typeof dictionary !== "undefined") {
    return dictionary
  }

  let response = await fetch(window.puzzleStaticDirectory + "twl06.txt")
  let text = await response.text()

  if (!response.ok || text.startsWith("Unknown file ")) {
    showError(text)
    throw new Error(text)
  }

  dictionary = new Set(text.split("\n").filter(line => !line.startsWith('#')))
  return dictionary
}

function numberFromLetter(letter) {
  return (letter.toLowerCase().codePointAt(0) - "a".codePointAt(0) + 1) % 26
}

function letterFromNumber(number) {
  if (number === 0) {
    return "z"
  }

  return String.fromCodePoint("a".codePointAt(0) + number - 1)
}

function showError(error) {
  document.getElementById("next-html").style.display = "none"

  let errorDiv = document.getElementById("word-square-error")
  errorDiv.innerHTML = "Try again: " + error
  errorDiv.style.display = "block"
}

async function validateWordSquare() {
  let validWords = await getValidWords()

  let wordSquare = document.getElementById("word-square-input").value.toLowerCase();

  if (!/^[a-z]{25}$/.test(wordSquare)) {
    showError('The entered string is not a string of exactly 25 letters and nothing else.')
    return
  }

  const dim = 5

  let square = []
  for (let row = 0; row < dim; row++) {
    square[row] = wordSquare.slice(row*dim, (row+1)*dim)
  }

  let rowEnds = Array(dim).fill("")
  for (let row = 0; row < dim; row++) {
    var word = square[row]
    if (!validWords.has(word) && !validWords.has(word.split("").reverse().join(""))) {
      showError(`Grid entry [${word}] is not a valid word, forwards or backwards.`)
      return
    }

    rowEnds[row] = letterFromNumber(
      word.split("").map(numberFromLetter).reduce((a, b) => a+b) % 26)
  }

  let colEnds = Array(dim).fill("")
  for (let col = 0; col < dim; col++) {
    let word = ""
    for (let row = 0; row < dim; row++) {
      word += square[row][col]
    }
    if (!validWords.has(word) && !validWords.has(word.split("").reverse().join(""))) {
      showError(`Grid entry [${word}] is not a valid word, forwards or backwards.`)
      return
    }

    colEnds[col] = letterFromNumber(
      word.split("").map(numberFromLetter).reduce((a, b) => a+b) % 26)
  }

  if (new Set(rowEnds.concat(colEnds)).size != dim * 2) {
    showError("The letter-value sums of the across and down words, modulo 26,"
      + " do not represent 10 different letters.")
    return
  }

  let rowEndsWord = rowEnds.join("")
  if (!validWords.has(rowEndsWord) && !validWords.has(rowEndsWord.split("").reverse().join(""))) {
    showError(`The across words form [${rowEndsWord}],`
      + " which is not a valid word, forwards or backwards")
    return
  }

  let colEndsWord = colEnds.join("")
  if (!validWords.has(colEndsWord) && !validWords.has(colEndsWord.split("").reverse().join(""))) {
    showError(`The down words form [${colEndsWord}],`
      + " which is not a valid word, forwards or backwards")
    return
  }

  let bigrams = pickBigrams(rowEnds, colEnds).toUpperCase()

  document.getElementById("word-square-error").style.display = "none";

  let nextHTML = document.getElementById("next-html");
  nextHTML.innerHTML = `
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

<p class="centered" data-skip-inline-styles="true">${bigrams}</p>

<p class="centered note" data-skip-inline-styles="true">(NOTE: Please provide your answer in the form that is the title of a Wikipedia article.)</p>
`
  nextHTML.style.display = "block";
}

function pickBigrams(rowEnds, colEnds) {
  // abcde  1
  // fghij  2
  // klmno  3 < rowEnds
  // pqrst  4
  // uvwxy  5
  // 67890
  //   ^ colEnds

  const coords = "20-57-61-48-19-05-39-82-10-85-58-94-83-72-93-16-71"

  // This is not efficient, but it is very clear. :)
  return coords
    .replaceAll("1", rowEnds[0])
    .replaceAll("2", rowEnds[1])
    .replaceAll("3", rowEnds[2])
    .replaceAll("4", rowEnds[3])
    .replaceAll("5", rowEnds[4])
    .replaceAll("6", colEnds[0])
    .replaceAll("7", colEnds[1])
    .replaceAll("8", colEnds[2])
    .replaceAll("9", colEnds[3])
    .replaceAll("0", colEnds[4])
}
