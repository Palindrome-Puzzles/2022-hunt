export function initializeVirtualScrolling() {
  // Make the container infinite scroll.
  // Based on https://codepen.io/geraldfullam/pen/NqxJEo.
  const gridContainer = document.querySelector<HTMLElement>(".grid-container")!;
  const scrollContainer =
    document.querySelector<HTMLElement>(".scroll-container")!;
  gridContainer.addEventListener("scroll", handleVirtualScroll);

  // Inject spacers so that (1) it's hard to scroll to the top of .scroll-container
  // and accidentally scroll the document instead, and (2) the jumpiness of the
  // scrollbar is more subtle.
  const spacerSize = 800;
  const topSpacer = document.createElement("div");
  topSpacer.classList.add("spacer");
  topSpacer.style.height = `${spacerSize}px`;
  const bottomSpacer = topSpacer.cloneNode(true) as Element;
  scrollContainer.insertBefore(topSpacer, scrollContainer.firstChild);
  scrollContainer.appendChild(bottomSpacer);

  // Initial infinite scroll position.
  handleVirtualScroll();

  function handleVirtualScroll() {
    const scrollPosition = gridContainer.scrollTop - spacerSize;
    const scrollHeight =
      scrollContainer.offsetHeight -
      gridContainer.offsetHeight -
      spacerSize * 2;
    const hysteresis = scrollHeight / 10;
    if (scrollPosition > scrollHeight - hysteresis) {
      // Rotate items from beginning to the end.
      let totalDelta = 0;
      while (totalDelta < hysteresis) {
        const firstChild = topSpacer.nextSibling!;
        if (firstChild.nodeType === Node.ELEMENT_NODE) {
          totalDelta += (firstChild as HTMLElement).offsetHeight;
        }
        scrollContainer.insertBefore(firstChild, bottomSpacer);
      }
      gridContainer.scrollTop -= totalDelta;
    } else if (scrollPosition < hysteresis) {
      // Rotate items from end to the beginning.
      let totalDelta = 0;
      while (totalDelta < hysteresis) {
        const lastChild = bottomSpacer.previousSibling!;
        if (lastChild.nodeType === Node.ELEMENT_NODE) {
          totalDelta += (lastChild as HTMLElement).offsetHeight;
        }
        scrollContainer.insertBefore(lastChild, topSpacer.nextSibling);
      }
      gridContainer.scrollTop += totalDelta;
    }
  }

  return () => {
    gridContainer.removeEventListener("scroll", handleVirtualScroll)
    topSpacer.remove();
    bottomSpacer.remove();
  };
}

export function restoreInitialGridOrder(container: HTMLElement) {
  // Rotate items (by scrolling up) until the first child is the first .crossword.
  let firstChild = container.firstChild!;
  while (
    firstChild.nodeType !== Node.ELEMENT_NODE ||
    !(firstChild as HTMLElement).classList.contains("crossword") ||
    (firstChild as HTMLElement).dataset.board !== '0'
  ) {
    container.appendChild(firstChild);
    firstChild = container.firstChild!;
  }
}
