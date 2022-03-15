document.addEventListener('DOMContentLoaded', (e) => {
  for (const sortable of document.querySelectorAll('table.sortable')) {
    // Skip if already sorted.
    if (sortable.querySelector('.sorttable_sorted') || sortable.querySelector('.sorttable_sorted_reverse')) {
      continue;
    }
    const initialSortHeader = sortable.querySelector('th[data-sortable-initial]');
    if (!initialSortHeader) continue;

    const desc = initialSortHeader.dataset.sortableInitial === 'desc';
    // https://kryogenix.org/code/browser/sorttable/#externalcall
    sorttable.innerSortFunction.apply(initialSortHeader, []);
    if (desc) {
      sorttable.innerSortFunction.apply(initialSortHeader, []);
    }
  }
});
