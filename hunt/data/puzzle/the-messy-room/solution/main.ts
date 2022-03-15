import { initializeVirtualScrolling, restoreInitialGridOrder } from '../common';
import { assert } from '@common/helpers';

// Export globally so the auto onload handler can find this.
window.puzzleOnLoad = puzzleOnLoad;

function puzzleOnLoad() {
  const puzzleWrapper = document.querySelector('.puzzle')!;
  const scrollContainer = document.querySelector<HTMLElement>(".scroll-container")!;

  const toggleInteractiveWrapper = document.querySelector('.toggle-interactive-wrapper')!;
  toggleInteractiveWrapper.classList.remove('hidden');

  const toggleInteractive = toggleInteractiveWrapper.querySelector<HTMLButtonElement>('button')!;

  let cleanupVirtualScrolling: (() => void) | null = null;
  toggleInteractive.addEventListener('click', () => toggleInteractiveHandler());
  toggleInteractiveHandler(true);

  function toggleInteractiveHandler(force?: boolean) {
    const isInteractive = force === undefined ? !puzzleWrapper.classList.contains('interactive') : force;
    if (isInteractive) {
      assert(!cleanupVirtualScrolling);
      puzzleWrapper.classList.add('interactive');
      toggleInteractive.innerText = 'Expand';
      cleanupVirtualScrolling = initializeVirtualScrolling();
    } else {
      assert(cleanupVirtualScrolling);
      puzzleWrapper.classList.remove('interactive');
      toggleInteractive.innerText = 'Collapse';
      restoreInitialGridOrder(scrollContainer);
      cleanupVirtualScrolling();
      cleanupVirtualScrolling = null;
    }
  }
}
