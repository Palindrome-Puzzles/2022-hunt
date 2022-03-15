import { ALLOCATIONS, LETTERS, WIDTH, NUM_GRIDS } from './data';
import {tab, outputBoard, outputLetters} from './util';

// Output grid and cross off cells from perColumnCheck as we go.
console.log('<div class="grid-container">')
console.log('<div class="scroll-container">')
for (let i = 0; i < NUM_GRIDS; i++) {
  outputBoard(i);
  outputLetters(i);
}
console.log('</div>')
console.log('</div>\n')
