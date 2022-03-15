import { ALLOCATIONS, LETTERS, WIDTH, NUM_GRIDS } from '../../__build/data';
import {tab, outputSolutionBoard, outputLetters} from '../../__build/util';

// Output grid and cross off cells from perColumnCheck as we go.
console.log('<div class="grid-container">')
console.log('<div class="scroll-container">')
for (let i = 0; i < NUM_GRIDS; i++) {
  outputSolutionBoard(i);
  outputLetters(i);
}
console.log('</div>')
console.log('</div>\n')
