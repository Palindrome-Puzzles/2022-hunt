function updateImage(ref, shown) {
  const imageCell = document.getElementById(`${ref}-image-top`);
  if (!imageCell) return;

  while (imageCell.firstChild)
    imageCell.removeChild(imageCell.firstChild);

  if (shown) {
    var img = document.createElement('img');
    img.src = window.puzzlePosthuntStaticDirectory + 'equations/' + ref + '.png';
    img.alt = 'A mathematical assignment statement';
    img.className = "result no-copy"
    var copySpan = document.createElement('span');
    copySpan.className = "copy-only"
    copySpan.innerHTML = "[See original puzzle for image.]"
    imageCell.innerHTML=''
    imageCell.appendChild(img)
    imageCell.appendChild(copySpan)
  }
}

window.stubCheckboxes = () => {
  ['playplace', 'sunblock', 'mouse-taken','to-do','castle-crisis','the-cracked-crystal','the-pitch','off-the-grid','historical-pictures','unfinished-symphonies'].forEach(ref => {
    const checkbox = document.getElementById(`${ref}-checkbox-top`);
    if(checkbox) {
      checkbox.addEventListener('change', function() {
        updateImage(ref, checkbox.checked)
      });
      updateImage(ref, checkbox.checked)
    }
  });
};
