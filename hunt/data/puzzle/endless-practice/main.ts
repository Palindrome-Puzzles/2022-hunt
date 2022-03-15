import { ManagedWebSocket } from "@common/managed-web-socket";
import { MinipuzzleProgress } from "@common/helpers"
import Cookies from "js-cookie";

function updateImage(ref: string) {
  const imageCell = document.getElementById(`${ref}-image-top`);
  if(imageCell){
    const checkbox = <HTMLInputElement>document.getElementById(`${ref}-checkbox-top`);
    if(checkbox && !checkbox.checked){
      imageCell.innerHTML='';
    }
    else {
      var url = window.puzzleUrl + "result/?ref=" + ref
      var csrftoken = Cookies.get("csrftoken")??"";
      fetch(url, {
        method: 'POST',
        headers: {"X-CSRFToken": csrftoken},
      })
      .then( response => {
        var contentType = response.headers.get('Content-Type')??"";
        if(contentType == "image/png"){
          var alt = response.headers.get('X-Image-Alt')??"";
          response.blob().then(responseBlob => {
            var img = document.createElement('img');
            img.src = URL.createObjectURL(responseBlob)
            img.alt = alt
            img.className = "result no-copy"
            var copySpan = document.createElement('span');
            copySpan.className = "copy-only"
            copySpan.innerHTML = "[See original puzzle for image.]"
            imageCell.innerHTML=''
            imageCell.appendChild(img)
            imageCell.appendChild(copySpan)
          })
        }
      })
    }
  }
}

const socket = new ManagedWebSocket<void, MinipuzzleProgress>("/ws/puzzle/endless-practice", window.puzzleAuthToken);
socket.addListener((message) => {
  if (message.type === 'minipuzzle') {
    for (const update of message.updates) {
      if(update.answer !== null){
        const answerCell = document.getElementById(`${update.ref}-answer-top`);
        if(answerCell){
          answerCell.innerHTML = update.answer
        }
        updateImage(update.ref)
      }
      const iframe = document.querySelector<HTMLIFrameElement>(`.${update.ref}-answers`);
      if (iframe) {
        iframe.src = iframe.src;
      }
    }
  }
});

if(window.isPublicAccess){
  ['playplace', 'sunblock', 'mouse-taken','to-do','castle-crisis','the-cracked-crystal','the-pitch','off-the-grid','historical-pictures','unfinished-symphonies'].forEach(ref => {
    const checkbox = <HTMLInputElement>document.getElementById(`${ref}-checkbox-top`);
    if(checkbox) {
      checkbox.addEventListener('change', function() {updateImage(ref)});
    }
  });
}