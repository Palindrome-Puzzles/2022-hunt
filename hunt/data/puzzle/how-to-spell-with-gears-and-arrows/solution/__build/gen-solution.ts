import { FIXED_PEGS,ARROW_SIZE, CLUES, FIXED_LETTERS, getCircledPegTransform, LARGE_INNER_RADIUS, toDegrees, toRadians, initializeGearLayout, GearInfo, getBoundingBox, NUM_STOPS, GAP_TO_PEG_RATIO, GEARS, TOOTH_HEIGHT, TOOTH_WIDTH, ODD_GEARS, INNER_RADIUS } from '../../util';
import {getPegPolygonPoints, getPegStopPoints, getPegAngle, getPegArc, outputGearDefs, outputGearPositioningStyles} from '../../__build/common';
import {Gear} from '../../types';

initializeGearLayout();

const PEG_SOLUTION: Record<Gear, Record<number, string>> = {
  'A': {0: 'O', 4: 'G', 10: 'A', 18: 'L'},
  'B': {1: 'F', 5: 'X', 7: 'B', 11: 'N', 13: 'R'},
  'C': {6: 'H', 8: 'U', 16: 'C', 18: 'W', 24: 'S'},
  'D': {1: 'Q', 3: 'Y', 7: 'D', 9: 'I', 15: 'P', 17: 'T'},
  'E': {2: 'K', 4: 'V', 8: 'M', 12: 'Z', 14: 'E', 18: 'J'},
};

console.log(
  `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${getBoundingBox().join(' ')}" class="gears transition-disabled" aria-label="Gear solution">`);

console.log('<style>');
outputGearPositioningStyles();
console.log('</style>');

// Based on http://thenewcode.com/1068/Making-Arrows-in-SVG.
console.log('<defs>');
outputGearDefs();
console.log(`</defs>`);

for (const [gear, gearInfo] of Object.entries(GEARS) as [Gear, GearInfo][]) {
  const { size, radius, arrowAngle, initialRotation } = gearInfo;
  const [centerX, centerY] = gearInfo.center;

  console.log(`<g class="gear gear${gear}" data-gear="${gear}" tabindex="0" focusable="true">`);
  console.log(`<g class="gear-rotate">`);
  console.log(`<g class="gear-offset">`);

  // Rest of the gear.
  console.log(`<circle r="${radius}" mask="url(#gear-hole-mask)" class="gear-body"/>`);

  // Gear teeth.
  const pegPolygonPoints = getPegPolygonPoints(gearInfo);
  for (let i = 0; i < size; i++) {
    const {pegIndex, pegAngle} = getPegAngle(i, gear, gearInfo);
    const extraClasses = [];
    const isFixed = !!FIXED_PEGS[gear][pegIndex];
    const text = PEG_SOLUTION[gear][pegIndex] || 'STOP';
    const isStopped = text === 'STOP';
    if (isFixed || !isStopped) {
      extraClasses.push('fixed');
    }
    if (isStopped) {
      extraClasses.push('stopped');
    }
    console.log(`<g class="tooth tooth${pegIndex} ${extraClasses.join(' ')}" focusable="true" aria-labelledby="gear${gear}-tooth${pegIndex}-text">`)
    console.log(`<g transform="rotate(${toDegrees(pegAngle)}) translate(${radius}, 0)">`);
    console.log(`<polygon points="${pegPolygonPoints}" class="peg"/>`);
    console.log(`<use href="#stop-symbol${isFixed ? '-fixed' : ''}" width="${TOOTH_HEIGHT}" height="${TOOTH_HEIGHT}" transform="translate(${TOOTH_HEIGHT/2} 0) rotate(90 ${TOOTH_HEIGHT/2} 0)" class="stop"/>`);

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
