// We don't overflow in the y direction, so use screen Y coordinates.
const html = document.querySelector('html');

for (const pannable of document.querySelectorAll('.round-map.pannable')) {
  pannable.scrollLeft = (pannable.scrollWidth - pannable.clientWidth) / 2;

  // Based on https://htmldom.dev/drag-to-scroll/.
  let startPos = null;
  pannable.addEventListener('mousedown', (event) => {
    startPos = {
      left: pannable.scrollLeft,
      top: html.scrollTop,
      x: event.clientX,
      y: event.screenY,
    };
    pannable.classList.toggle('panning', true);
    document.addEventListener('mousemove', handleMousemove);
    document.addEventListener('mouseup', handleMouseup);
  });

  function handleMousemove(event) {
    if (!startPos) return;

    const dx = event.clientX - startPos.x;
    const dy = event.screenY - startPos.y;

    pannable.scrollLeft = startPos.left - dx;
    html.scrollTop = startPos.top - dy;
  }

  function handleMouseup(event) {
    startPos = null;
    pannable.classList.toggle('panning', false);
    document.removeEventListener('mousemove', handleMousemove);
    document.removeEventListener('mouseup', handleMouseup);
  }
}
