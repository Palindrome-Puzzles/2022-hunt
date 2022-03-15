import { FIXED_PEGS,ARROW_SIZE, CLUES, FIXED_LETTERS, getCircledPegTransform, LARGE_INNER_RADIUS, toDegrees, toRadians, initializeGearLayout, GearInfo, getBoundingBox, NUM_STOPS, GAP_TO_PEG_RATIO, GEARS, TOOTH_HEIGHT, TOOTH_WIDTH, ODD_GEARS, INNER_RADIUS } from '../util';
import {Gear} from '../types';
import {getPegPolygonPoints, getPegStopPoints, getPegAngle, getPegArc, outputGearDefs, outputGearPositioningStyles} from './common';

// Note: ARIA based on https://www.scottohara.me/blog/2019/05/22/contextual-images-svgs-and-a11y.html.

initializeGearLayout();

console.log(
  `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${getBoundingBox().join(' ')}" class="gears transition-disabled" aria-label="Interactive gears">`);

console.log('<style>');
outputGearPositioningStyles();
console.log('</style>');

// Based on http://thenewcode.com/1068/Making-Arrows-in-SVG.
console.log('<defs>');
outputGearDefs();

console.log(`
  <mask id="gear-large-hole-mask">
    <rect x="-100%" y="-100%" width="200%" height="200%" fill="white"/>
    <circle r="${LARGE_INNER_RADIUS}" fill="black"/>
  </mask>

  <symbol id="stop-symbol-unpadded" viewbox="${-TOOTH_HEIGHT/2} ${-TOOTH_HEIGHT/2} ${TOOTH_HEIGHT} ${TOOTH_HEIGHT}">
    <polygon points="${getPegStopPoints(0 /* offset */)}" stroke="none"/>
    <text dominant-baseline="central" text-anchor="middle">STOP</text>
  </symbol>

  <symbol id="circled-peg" viewbox="${-TOOTH_HEIGHT/2 - 1} ${-TOOTH_HEIGHT/2 - 1} ${TOOTH_HEIGHT + 2} ${TOOTH_HEIGHT + 2}">
    <circle r="${TOOTH_HEIGHT/2}" stroke="#000" fill="transparent" stroke-width="2"/>
  </symbol>`);
for (const [gear, gearInfo] of Object.entries(GEARS) as [Gear, GearInfo][]) {
  for (const aceEngaged of [true, false]) {
    console.log(`<symbol id="gear-icon${gear}${aceEngaged ? '' : '-offset'}" class="gear-icon${gear} gear-icon-symbol" viewbox="${-gearInfo.radius - TOOTH_HEIGHT} ${-gearInfo.radius - TOOTH_HEIGHT} ${2*(gearInfo.radius + TOOTH_HEIGHT)} ${2*(gearInfo.radius + TOOTH_HEIGHT)}">`);
    console.log(`<circle r="${gearInfo.radius}" mask="url(#gear-large-hole-mask)" class="gear-body"/>`);
    console.log(`<g transform="rotate(${toDegrees(gearInfo.initialRotation + (aceEngaged ? 0 : gearInfo.rotateStep))})">`);
    for (let i = 0; i < gearInfo.size; i++) {
      const {pegAngle} = getPegAngle(i, gear, gearInfo);
      console.log(`<polygon points="${getPegPolygonPoints(gearInfo)}" transform="rotate(${toDegrees(pegAngle)}) translate(${gearInfo.radius}, 0)" class="peg"/>`);
    }
    console.log(`</g>`);

    console.log(`<text dominant-baseline="central" text-anchor="middle">`);
    console.log(gear);
    console.log('</text>');
    console.log(`</symbol>`);
  }
}
console.log(`</defs>`);

for (const [gear, gearInfo] of Object.entries(GEARS) as [Gear, GearInfo][]) {
  const { size, radius, arrowAngle, initialRotation } = gearInfo;
  const [centerX, centerY] = gearInfo.center;

  console.log(`<g class="gear gear${gear}" data-gear="${gear}" tabindex="0" focusable="true" aria-label="Gear ${gear}">`);
  console.log(`<g class="gear-rotate">`);
  console.log(`<g class="gear-offset">`);

  // Rest of the gear.
  console.log(`<circle r="${radius}" mask="url(#gear-hole-mask)" class="gear-body"/>`);

  // Gear teeth.
  const pegPolygonPoints = getPegPolygonPoints(gearInfo);
  for (let i = 0; i < size; i++) {
    const {pegIndex, pegAngle} = getPegAngle(i, gear, gearInfo);
    const extraClasses = [];
    let text = '';
    const fixedValue = FIXED_PEGS[gear][pegIndex];
    if (fixedValue) {
      extraClasses.push('fixed');
      if (fixedValue === 'STOP') {
        extraClasses.push('stopped');
        text = 'STOP';
      } else {
        text = fixedValue;
      }
    }
    console.log(`<g class="tooth tooth${pegIndex} ${extraClasses.join(' ')}" tabindex="${fixedValue ? -1 : 0}" focusable="true" role="button" aria-labelledby="gear${gear}-tooth${pegIndex}-text" data-peg="${pegIndex}">`)
    console.log(`<g transform="rotate(${toDegrees(pegAngle)}) translate(${radius}, 0)">`);
    console.log(`<polygon points="${pegPolygonPoints}" class="peg"/>`);
    console.log(`<use href="#stop-symbol${fixedValue ? '-fixed' : ''}" width="${TOOTH_HEIGHT}" height="${TOOTH_HEIGHT}" transform="translate(${TOOTH_HEIGHT/2} 0) rotate(90 ${TOOTH_HEIGHT/2} 0)" class="stop"/>`);
    console.log(`<circle r="${TOOTH_HEIGHT * .4}" transform="translate(${TOOTH_HEIGHT/2}, 0)" class="letter-bg"/>`);

    console.log(`<text dominant-baseline="central" text-anchor="middle">
      <textPath class="text" startOffset="50%" href="#gear${gear}-path" id="gear${gear}-tooth${pegIndex}-text">${text}</textPath>
    </text>`);
    console.log('</g>');
    console.log('</g>');
  }

  // Arrow.
  console.log(`
  <line x1="${INNER_RADIUS}" y1="0" x2="${radius - ARROW_SIZE}" y2="0" stroke="#000a" stroke-width="1"
    marker-end="url(#arrowhead)"
    transform="rotate(${toDegrees(arrowAngle)})"/>`);

  console.log('</g>');
  console.log('</g>');
  console.log('</g>');

  // Gear labels. Outside the gear element to avoid it getting a shadow, or being rotated.
  console.log(`<text dominant-baseline="central" text-anchor="middle" class="gear-label gear-label${gear}">`);
  console.log(gear);
  console.log('</text>');
}
console.log('</svg>');

console.log('<div class="letter-menu hidden no-copy" tabindex="0">');
console.log(`<div class="letters">`);
  for (let i = 0; i < 26; i++) {
    const letter = String.fromCharCode(i + 65);
    const disabled = FIXED_LETTERS.has(letter);
    console.log(`<button class="${letter}-button"${disabled ? ' disabled="disabled"' : ''}>${letter}</button>`);
  }
console.log('</div>');

console.log(`<div class="stops">`);
console.log(`<button class="stop-button">`)
console.log(`<svg xmlns="http://www.w3.org/2000/svg" aria-label="STOP" focusable="false"><use href="#stop-symbol" aria-hidden="true"/></svg>`);
console.log(`× <span class="stop-count">0</span>`);
console.log('</button>')
console.log('</div>');

console.log('</div>');

console.log('<div class="available-letters no-copy">');
for (let i = 0; i < 26; i++) {
  const letter = String.fromCharCode(i + 65);
  const isFixed = FIXED_LETTERS.has(letter);
  console.log(`<span class="available-letter ${isFixed ? 'fixed' : ''}">${isFixed ? '&nbsp;' : letter}</span>`);
}
console.log('</div>');

console.log('<div class="available-stops no-copy">');
for (let i = 0; i < NUM_STOPS + 5; i++) {
  if (i < 5) {
    console.log(`<span class="available-letter fixed">&nbsp;</span>`);
  } else {
    console.log(`<svg xmlns="http://www.w3.org/2000/svg" aria-label="STOP" focusable="false"><use href="#stop-symbol-unpadded" aria-hidden="true"/></svg>`);
  }
}
console.log('</div>');
 /**
* console.log('<div class="no-copy">');
* console.log(`
* <p>Permanently place all Letter Pegs and Stop Pegs (some have already been placed) so that each of the words defined below can be spelled, ending with a STOP, by turning the leftmost gear in either direction (without backtracking), and writing down in order each letter or STOP identified by an arrow (that is, when the peg is at its closest approach to an adjacent gear and flanked by the two teeth on either side of the arrow of that adjacent gear).</p>
*
* <p>At no point during this process may two different arrows each identify a peg at the same time (though identifying pegs in rapid succession is fine). Before spelling each word, but not during the spelling of a word, each gear may be picked up and replaced (face up) back on its spindle in any orientation.</p>
* 
* <p>(NOTE: If an indicated spelling then STOP can be achieved in more than one way, use the one requiring the least amount of turning after the gears are set. If there are multiple ways that are tied for the least amount of turning, then use the one of those that ends on one of the five pre-placed STOPs, or if none do, use whichever you prefer.)</p>`);
* console.log('</div>');
* 
* console.log('<table>');
* for (const clue of CLUES) {
*   console.log('<tr>');
*   console.log(`<td>${clue[0]} … then STOP and look:</td>`);
*   console.log('<td>')
*   const {size, x, y} = getCircledPegTransform(clue[1], clue[2], clue[3]);
*   console.log(`<svg xmlns="http://www.w3.org/2000/svg" class="gear-icon" viewbox="0 0 100 100" aria-label="A peg in gear ${clue[1]}" focusable="false">
*     <g transform="scale(.90) translate(5,5)">
*       <use href="#gear-icon${clue[1]}${clue[2] ? '' : '-offset'}" aria-hidden="true"/>
*       <use href="#circled-peg" width="${size}" height="${size}" x="${x}" y="${y}" aria-hidden="true"/>
*     </g>
*   </svg>`);
*   console.log('</td>');
*   console.log('</tr>');
* }
* console.log('</table>');
*/