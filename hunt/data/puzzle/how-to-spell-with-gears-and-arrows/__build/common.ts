import { GEARS_IN_ORDER, FIXED_PEGS,ARROW_SIZE, CLUES, FIXED_LETTERS, getCircledPegTransform, LARGE_INNER_RADIUS, toDegrees, toRadians, initializeGearLayout, GearInfo, getBoundingBox, NUM_STOPS, GAP_TO_PEG_RATIO, GEARS, TOOTH_HEIGHT, TOOTH_WIDTH, ODD_GEARS, INNER_RADIUS } from '../util';
import {Gear} from '../types';

export function getPegPolygonPoints({radius, pegArcAngle, gapArcAngle}: GearInfo) {
  const peg1 = [radius * (Math.cos(-pegArcAngle / 2) - 1), radius * Math.sin(-pegArcAngle / 2) * GAP_TO_PEG_RATIO];
  const peg2 = [radius * (Math.cos(pegArcAngle / 2)  - 1), radius * Math.sin(pegArcAngle / 2) * GAP_TO_PEG_RATIO];
  const peg3 = [peg2[0] + TOOTH_HEIGHT, radius * Math.sin(pegArcAngle / 2)];
  const peg4 = [peg1[0] + TOOTH_HEIGHT, radius * Math.sin(-pegArcAngle / 2)];
  return [...peg1, ...peg2, ...peg3, ...peg4].join(' ');
}

export function getPegStopPoints(offset=.1) {
  let angle = 22.5;
  const points = [];
  const radius = TOOTH_HEIGHT * (.5 - offset);
  for (let i = 0; i < 8; i++) {
    points.push(radius * Math.cos(toRadians(angle)), radius * Math.sin(toRadians(angle)));
    angle += 45;
  }
  return points;
}

export function getPegAngle(i: number, gear: Gear, {pegArcAngle, gapArcAngle}: GearInfo) {
  const isOdd = ODD_GEARS.has(gear);
  const pegIndex = isOdd ? 2*i + 1 : 2*i;
  const numberOfGaps = pegIndex - i;
  const pegGapAlignment = isOdd ? -(GAP_TO_PEG_RATIO - 1) / 2 * pegArcAngle : 0;
  return {
    pegIndex,
    pegAngle: i * pegArcAngle + numberOfGaps * gapArcAngle + pegGapAlignment,
  };
}

export function getPegArc({radius, pegArcAngle, gapArcAngle}: GearInfo) {
  const pegRadius = radius + TOOTH_HEIGHT / 2;
  const pegTextPathStartX = pegRadius * Math.cos(-pegArcAngle / 2) - radius;
  const pegTextPathStartY = pegRadius * Math.sin(-pegArcAngle / 2);
  const pegTextPathEndX = pegRadius * Math.cos(pegArcAngle / 2) - radius;
  const pegTextPathEndY = pegRadius * Math.sin(pegArcAngle / 2);
  return `M ${pegTextPathStartX} ${pegTextPathStartY} A ${pegRadius} ${pegRadius} 0 0 1 ${pegTextPathEndX} ${pegTextPathEndY}`;
}

export function outputGearPositioningStyles() {
  console.log(`
  .refreshed.disengaged:not(.transition-disabled) .gear .gear-offset,
  .refreshed.disengaged:not(.transition-disabled) .gear .gear-rotate {
    /* Wait to disengage before animating. */
    transition-delay: .4s;
  }`);

  for (const [gear, gearInfo] of Object.entries(GEARS)) {
    const [centerX, centerY] = gearInfo.center;
    const breakpoints: [number, number, number][] = [[0, centerX, centerY]];
    for (let i = 0; i < 2; i++) {
      const frame = 100 * (i+1) / 2;
      const x = breakpoints[i][1] + (gearInfo.expandedDelta[i] ? gearInfo.expandedDelta[i][0] : 0);
      const y = breakpoints[i][2] + (gearInfo.expandedDelta[i] ? gearInfo.expandedDelta[i][1] : 0);
      breakpoints.push([frame, x, y]);
    }
    console.log(`.gear.gear${gear},
    .gear-label${gear} {
      transform: translate(${centerX}px, ${centerY}px);
    }
    .gear.gear${gear} .gear-rotate {
      transform: rotate(${gearInfo.initialRotation}rad);
    }

    ${breakpoints.length > 1
      ? `
      .disengaged .gear.gear${gear},
      .disengaged .gear-label${gear} {
        animation: .3s ease-in 1 normal disengage-gear${gear};
        transform: translate(${breakpoints[breakpoints.length - 1][1]}px, ${breakpoints[breakpoints.length - 1][2]}px);
      }

      .engaged .gear.gear${gear},
      .engaged .gear-label${gear} {
        animation: .3s ease-out 1 normal engage-gear${gear};
        transform: translate(${breakpoints[0][1]}px, ${breakpoints[0][2]}px);
      }

      .refreshed.engaged .gear.gear${gear}
      .refreshed.engaged .gear-label${gear} {
        /* Longer animation that waits for rotation to finish before engaging. */
        animation: .8s ease-in 1 normal engage-gear${gear}-wait;
      }

      @keyframes disengage-gear${gear} {
        ${breakpoints.map(([frame, x, y]) => `${frame}% { transform: translate(${x}px, ${y}px); }`).join(' ')}
      }

      @keyframes engage-gear${gear} {
        ${breakpoints.map(([frame, x, y]) => `${100 - frame}% { transform: translate(${x}px, ${y}px); }`).join(' ')}
      }

      @keyframes engage-gear${gear}-wait {
        ${breakpoints.map(([frame, x, y]) => `${50 + (100-frame)/2}% { transform: translate(${x}px, ${y}px); }`).join(' ')}
        0% { transform: translate(${breakpoints[breakpoints.length - 1][1]}px, ${breakpoints[breakpoints.length - 1][2]}px); }
      }`
      : ''
    }`);
  }
}

export function outputGearDefs() {
  console.log(`<marker id="arrowhead" markerWidth="${ARROW_SIZE}" markerHeight="${ARROW_SIZE}" refX="0" refY="${ARROW_SIZE/2}" orient="auto">
    <polygon points="0 0 ${ARROW_SIZE} ${ARROW_SIZE/2} 0 ${ARROW_SIZE}" fill="#000a"/>
  </marker>

  <mask id="gear-hole-mask">
    <rect x="-100%" y="-100%" width="200%" height="200%" fill="white"/>
    <circle r="${INNER_RADIUS}" fill="black"/>
  </mask>

  <symbol id="stop-symbol" viewbox="${-TOOTH_HEIGHT/2} ${-TOOTH_HEIGHT/2} ${TOOTH_HEIGHT} ${TOOTH_HEIGHT}">
    <polygon points="${getPegStopPoints()}"/>
    <text dominant-baseline="central" text-anchor="middle">STOP</text>
  </symbol>

  <symbol id="stop-symbol-fixed" viewbox="${-TOOTH_HEIGHT/2} ${-TOOTH_HEIGHT/2} ${TOOTH_HEIGHT} ${TOOTH_HEIGHT}">
    <polygon points="${getPegStopPoints()}"/>
    <text dominant-baseline="central" text-anchor="middle">STOP</text>
  </symbol>`);

  for (const gear of GEARS_IN_ORDER) {
    const pegTextPath = getPegArc(GEARS[gear]);
    console.log(`<path d="${pegTextPath}" id="gear${gear}-path"/>`);
  }
}
