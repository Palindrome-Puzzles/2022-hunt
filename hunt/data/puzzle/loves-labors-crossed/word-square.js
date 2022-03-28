// MIT License
//
// Copyright (c) 2021 Michael Seplowitz
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

function validateWordSquare() {
  var wordSquare = document.getElementById("word-square-input").value;

  var csrfToken = getCookie("csrftoken");

  fetch("/puzzle/loves-labors-crossed/check-word-square", { // TODO relative path?
    method: "POST",
    headers: {
      "X-CSRFToken": csrfToken,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ "wordSquare": wordSquare }),
  }).then(response => {
    if (!response.ok) {
      response.text().then(text => { console.log(text); alert(text) }); // TODO replace with CSS alert
      return;
    }

    contentType = response.headers.get("Content-Type");
    if (contentType != "application/json") {
      console.log("Unexpected Content-Type: " + contentType);
      alert("Unexpected Content-Type: " + contentType); // TODO replace with CSS alert
      return;
    }

    response.json().then(json => {
      if ("error" in json) {
        document.getElementById("next-html").style.display = "none";

        var error = document.getElementById("word-square-error")
        error.innerText = "Try again: " + json["error"];
        error.style.display = "block";
        return
      }

      if ("nextHTML" in json) {
        document.getElementById("word-square-error").style.display = "none";

        var nextHTML = document.getElementById("next-html");
        nextHTML.innerHTML = json["nextHTML"];
        nextHTML.style.display = "block";
        return
      }

      console.log("Unexpected JSON", json);
      alert("Unexpected JSON") // TODO replace with CSS alert
    });
  });
}
