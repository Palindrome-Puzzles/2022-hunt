import {assert} from '@common/helpers';
import { CLUES } from '../../util';

export const CLUE_ANSWERS = ['AQUI', 'ARMY', 'BAES', 'BOXES', 'CENA', 'FILE', 'FLIT', 'HING', 'JARS', 'JAWS', 'KATH', 'KNOX', 'MANCY', 'PARK', 'QAX', 'TENS', 'THARP', 'TVPG', 'VATU', 'WIG', 'WIRE', 'ZARDS', 'ZPAD']
assert(CLUES.length === CLUE_ANSWERS.length);

console.log('<table>');
console.log('<thead><tr><th>Clue</th><th>Answer</th></tr></thead>');
console.log('<tbody>');
for (let i = 0; i < CLUES.length; i++) {
  console.log('<tr>');
  console.log(`<td>${CLUES[i][0]}</td>`);
  console.log(`<td class="monospace">${CLUE_ANSWERS[i]}</td>`);
  console.log('</tr>');
}
console.log('</tbody>');
console.log('</table>');
