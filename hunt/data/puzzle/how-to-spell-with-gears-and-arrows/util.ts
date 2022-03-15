import {Gear} from './types';
import {hasSpecialKey} from '@common/helpers';

export interface GearInfo {
  readonly size: number;
  readonly arrowIndex: number;
  /** How many "peg + gap pairs" to walk from the last interlock in a CW direction to the next interlock. */
  readonly nextOffsetPegIndex: number;
  nextGearAngle: number,
  /** Where peg or gap 0 is rotated to. */
  initialRotation: number;
  readonly expandedDelta: Array<readonly [number, number]>;
  radius: number;
  arrowAngle: number;
  pegArcAngle: number;
  gapArcAngle: number;
  rotateStep: number;
  center: readonly [number, number];
}
export const GEARS: Record<Gear, GearInfo> = {
  A: {
    size: 11,
    arrowIndex: 21,
    nextOffsetPegIndex: 0,
    nextGearAngle: -1,
    expandedDelta: [],
    radius: -1,
    center: [-1, -1],
    arrowAngle: -1,
    pegArcAngle: -1,
    gapArcAngle: -1,
    rotateStep: -1,
    initialRotation: -1,
  },
  B: {
    size: 7,
    arrowIndex: 4,
    nextOffsetPegIndex: 4,
    nextGearAngle: -1,
    expandedDelta: [],
    radius: -1,
    center: [-1, -1],
    arrowAngle: -1,
    pegArcAngle: -1,
    gapArcAngle: -1,
    rotateStep: -1,
    initialRotation: -1,
  },
  C: {
    size: 13,
    arrowIndex: 9,
    nextOffsetPegIndex: 9,
    nextGearAngle: -1,
    expandedDelta: [],
    radius: -1,
    center: [-1, -1],
    arrowAngle: -1,
    pegArcAngle: -1,
    gapArcAngle: -1,
    rotateStep: -1,
    initialRotation: -1,
  },
  D: {
    size: 9,
    arrowIndex: 2,
    nextOffsetPegIndex: 3,
    nextGearAngle: -1,
    expandedDelta: [],
    radius: -1,
    center: [-1, -1],
    arrowAngle: -1,
    pegArcAngle: -1,
    gapArcAngle: -1,
    rotateStep: -1,
    initialRotation: -1,
  },
  E: {
    size: 10,
    arrowIndex: 7,
    nextOffsetPegIndex: NaN,
    nextGearAngle: NaN,
    expandedDelta: [],
    radius: -1,
    center: [-1, -1],
    arrowAngle: -1,
    pegArcAngle: -1,
    gapArcAngle: -1,
    rotateStep: -1,
    initialRotation: -1,
  },
};
export const GEARS_IN_ORDER: ReadonlyArray<Gear> = (Object.keys(GEARS) as Gear[]).sort();
export const FIXED_PEGS: Record<Gear, Record<number, string>> = {
  'A': {2: 'STOP', 10: 'A'},
  'B': {7: 'B', 9: 'STOP'},
  'C': {14: 'STOP', 16: 'C'},
  'D': {7: 'D', 11: 'STOP'},
  'E': {14: 'E', 16: 'STOP'},
};
export const NUM_STOPS = 19;
export const FIXED_LETTERS = new Set<string>(GEARS_IN_ORDER);
export const TOOTH_WIDTH = 10;
export const TOOTH_HEIGHT = 10;
export const TOOTH_GAP = 1;
export const ODD_GEARS: ReadonlySet<string> = new Set(['B', 'D']);
export const GAP_TO_PEG_RATIO = 1.2;
export const SHADOW_PADDING = 3;
export const ARROW_SIZE = 4;

export const CLUES: [string, Gear, boolean, number][] = [
  ['Here, in Barcelona', 'D', false, 2],
  ['Fighting force', 'C', false, 1],
  ['Miranda wondered where hers (like Ricky and Flula) were at in 2015', 'E', false, 3],
  ['Fights a shadow, metaphorically', 'C', false, -2],
  ['Pro wrestler whose film work runs the gamut from 2015’s Trainwreck to 2018’s Blockers', 'A', true, -3],
  ['What one can do to nails, folders, or tax returns', 'B', true, -2],
  ['Erstwhile pesticide brand for which Dr. Seuss (before he was known as such) illustrated some ads, named for how insects quickly move from place to place', 'D', false, 2],
  ['Indian spice also known as asafoetida', 'A', false, 5],
  ['Cookie locales', 'B', true, -3],
  ['Movie whose sequel used the tagline “Just when you thought it was safe to go back in the water”', 'D', true, 3],
  ['Single-season sitcom title role played by Molly Shannon', 'E', false, 0],
  ['Presidential middle name', 'B', true, 4],
  ['Suffix meaning divination', 'C', false, 0],
  ['What one of the letters on a typical automatic transmission gear selector stands for', 'D', false, 3],
  ['Conquering race in the 1982 novel Timelike Infinity', 'E', false, -2],
  ['The U.S. Treasury is on their backs', 'A', true, 2],
  ['Choreographer for the films Hair, Ragtime, Amadeus, and White Nights, as well as several Broadway productions', 'B', true, -2],
  ['Rating suggesting the upcoming broadcast contains material that some “may find unsuitable for younger children”', 'D', false, -3],
  ['Monetary unit whose name is its country’s name with three adjacent internal letters missing', 'C', false, 8],
  ['Fright, rainbow, or powdered item', 'C', false, 3],
  ['It’s best made from a ductile metal', 'D', false, -1],
  ['Grobble, NumNum, Ol’ Scarface and other super-adaptable dinosaurlike hybrid monsters appearing in AdventureQuest', 'A', true, -2],
  ['Electronic tablet series from ZTE', 'D', false, 2],
];

const EXPANDED_DELTA = 10;
const EXPAND_CENTER = 'C';
const GEAR_A_TO_B_ANGLE = toRadians(-60);

const smallestTooth = Math.min(...Object.values(GEARS).map(gear => gear.size));
const smallestRadius = gearRadius(smallestTooth);
export const INNER_RADIUS = smallestRadius / 3;
export const LARGE_INNER_RADIUS = smallestRadius / 1.5;

export function initializeGearLayout() {
  // Layout of gears.
  // First, calculate some basic properties.
  for (const [gear, gearInfo] of Object.entries(GEARS)) {
    gearInfo.radius = gearRadius(gearInfo.size);
    gearInfo.pegArcAngle = 2 * Math.PI / gearInfo.size / (1 + GAP_TO_PEG_RATIO);
    gearInfo.gapArcAngle = gearInfo.pegArcAngle * GAP_TO_PEG_RATIO;

    const dir = ODD_GEARS.has(gear) ? -1 : 1;
    gearInfo.rotateStep = dir * (gearInfo.pegArcAngle + gearInfo.gapArcAngle) / 2;
  }

  // Find relative rotations of each gear, so that they interlock.
  // We use the convention that position 0 is where each gear interlocks with the
  // previous gear, or for gear A, where it interlocks with gear B.
  // Say that gear A (which is "even" so has letters on index 0) is interlocked
  // with the gap on gear B with index 0 (and so on).
  for (let i = 0; i < GEARS_IN_ORDER.length; i++) {
    const gearInfo = GEARS[GEARS_IN_ORDER[i]];
    if (i === 0) {
      gearInfo.initialRotation = GEAR_A_TO_B_ANGLE;
      gearInfo.nextGearAngle = GEAR_A_TO_B_ANGLE;
    } else {
      const prevGearInfo = GEARS[GEARS_IN_ORDER[i - 1]];
      gearInfo.initialRotation = (prevGearInfo.nextGearAngle + Math.PI) % (2 * Math.PI);
      if (i < GEARS_IN_ORDER.length - 1) {
        const nextGearDelta = gearInfo.nextOffsetPegIndex * (gearInfo.pegArcAngle + gearInfo.gapArcAngle);
        // Add the delta, as we've expressed the offset as a clockwise angle,
        // which matches SVG coordinates.
        gearInfo.nextGearAngle = (gearInfo.initialRotation + nextGearDelta) % (2 * Math.PI);
      }
    }

    gearInfo.arrowAngle = gearInfo.arrowIndex * (gearInfo.pegArcAngle + gearInfo.gapArcAngle) / 2;
  }

  // Work out how much space to reserve when expanding.
  let expandLeft = true;
  for (let i = 0; i < GEARS_IN_ORDER.length; i++) {
    const gearInfo = GEARS[GEARS_IN_ORDER[i]];
    gearInfo.radius = gearRadius(gearInfo.size);

    if (!gearInfo.nextGearAngle) {
      break;
    }
    if (GEARS_IN_ORDER[i] === EXPAND_CENTER) {
      expandLeft = false;
    }
    if (expandLeft) {
      const expandX = EXPANDED_DELTA * Math.cos(Math.PI + gearInfo.nextGearAngle);
      const expandY = EXPANDED_DELTA * Math.sin(Math.PI + gearInfo.nextGearAngle);
      for (let j = 0; j <= i; j++) {
        const leftGear = GEARS[GEARS_IN_ORDER[j]];
        leftGear.expandedDelta.splice(0, 0, [expandX, expandY]);
      }
    } else {
      const expandX = EXPANDED_DELTA * Math.cos(gearInfo.nextGearAngle);
      const expandY = EXPANDED_DELTA * Math.sin(gearInfo.nextGearAngle);
      for (let j = i+1; j < GEARS_IN_ORDER.length; j++) {
        const rightGear = GEARS[GEARS_IN_ORDER[j]];
        rightGear.expandedDelta.push([expandX, expandY]);
      }
    }
  }

  // Find centers of each gear.
  for (let i = 0; i < GEARS_IN_ORDER.length; i++) {
    const gearInfo = GEARS[GEARS_IN_ORDER[i]];
    if (i === 0) {
      const centerX = TOOTH_HEIGHT + gearInfo.radius;
      const centerY = -(TOOTH_HEIGHT + gearInfo.radius);
      gearInfo.center = [centerX, centerY];
    } else {
      const prevGearInfo = GEARS[GEARS_IN_ORDER[i - 1]];
      const distance = prevGearInfo.radius + gearInfo.radius + TOOTH_HEIGHT + TOOTH_GAP;
      const centerX = prevGearInfo.center[0] + distance * Math.cos(prevGearInfo.nextGearAngle);
      const centerY = prevGearInfo.center[1] + distance * Math.sin(prevGearInfo.nextGearAngle);
      gearInfo.center = [centerX, centerY];
    }
  }
}

/** Find bounding box. This uses the knowledge that the gears on each edge are known. */
export function getBoundingBox() {
  const leftPadding = GEARS[GEARS_IN_ORDER[0]].expandedDelta.reduce((acc, cur) => [acc[0] + cur[0], acc[1] + cur[1]], [0, 0]);
  const rightPadding =
    GEARS[GEARS_IN_ORDER[GEARS_IN_ORDER.length - 1]].expandedDelta.reduce((acc, cur) => [acc[0] + cur[0], acc[1] + cur[1]], [0, 0]);

  const left = leftPadding[0] - SHADOW_PADDING;
  const bottom = leftPadding[1] + SHADOW_PADDING;
  const top = GEARS['C'].center[1] - GEARS['C'].radius - TOOTH_HEIGHT - SHADOW_PADDING;
  const right = GEARS['E'].center[0] + GEARS['E'].radius + TOOTH_HEIGHT + rightPadding[0] + SHADOW_PADDING;
  return [left, top, right - left, bottom - top] as const;
}

function gearRadius(numberOfTeeth: number): number {
  const circumference = 2 * numberOfTeeth * TOOTH_WIDTH;
  return circumference / 2 / Math.PI;
}

export function toRadians(degrees: number) {
  return degrees * Math.PI / 180;
}

export function toDegrees(radians: number) {
  return radians / Math.PI * 180;
}

export function getCircledPegTransform(gear: Gear, aceEngaged: boolean, peg: number) {
  const gearInfo = GEARS[gear];
  const isOdd = ODD_GEARS.has(gear);
  const pegIndex = 2*peg + ((aceEngaged === isOdd) ? 1 : 0);

  const gearRadius = gearInfo.radius + TOOTH_HEIGHT;
  const circleRadius = TOOTH_HEIGHT / 2 * 1.5;
  const proportionalSize = circleRadius / gearRadius;
  const canvasSize = 2 * gearRadius;

  const angle = gearInfo.initialRotation + pegIndex * gearInfo.rotateStep;
  const x = .5 - proportionalSize/2 + (gearInfo.radius + TOOTH_HEIGHT/2) * Math.cos(angle) / canvasSize;
  const y = .5 - proportionalSize/2 + (gearInfo.radius + TOOTH_HEIGHT/2) * Math.sin(angle) / canvasSize;

  return {size: `${proportionalSize * 100}%`, x: `${x * 100}%`, y: `${y * 100}%`};
}

const SVG_NAMESPACE = "http://www.w3.org/2000/svg";
export function initializeGearDom(gear: Gear, callback: (dir: "cw" | "ccw", steps: number) => void) {
  const { radius, arrowAngle } = GEARS[gear];
  const container = document.querySelector(`.gear${gear} .gear-offset`)!;
  for (const dir of ["cw", "ccw"] as const) {
    const button = document.createElementNS(SVG_NAMESPACE, "g");
    button.setAttributeNS(null, "role", "button");
    button.setAttributeNS(
      null,
      "aria-label",
      dir === "cw" ? "Clockwise" : "Counter-clockwise"
    );
    button.tabIndex = 0;
    button.style.cursor = "pointer";

    const label = document.createElementNS(
      SVG_NAMESPACE,
      "text"
    ) as SVGTextElement;
    label.setAttributeNS(null, "dominant-baseline", "middle");
    label.setAttributeNS(null, "text-anchor", "middle");
    label.setAttributeNS(null, "fill", "#000a");
    label.textContent = dir === "cw" ? "⤸" : "⤹";
    button.appendChild(label);

    const buttonRadius = (INNER_RADIUS + radius) / 2;
    const translateX = buttonRadius;
    const rotation =
      toDegrees(Math.PI + arrowAngle) + (dir === "cw" ? 45 : -45);
    const iconRotate = dir === "cw" ? 0 : 180;
    button.setAttributeNS(
      null,
      "transform",
      `rotate(${rotation}) translate(${translateX}, 0) rotate(${iconRotate})`
    );

    container.appendChild(button);

    button.addEventListener("click", (event) => {
      callback(dir, 1);
      // SVGs are weird, they don't focus when you click automatically...
      button.focus();
    });
    button.addEventListener("keydown", (event: KeyboardEvent) => {
      if (event.key === "Enter" || event.key === " ") {
        callback(dir, 1);
        event.preventDefault();
      }
    });
  }

  const gearContainer = document.querySelector(`.gear${gear}`)!;
  window.addEventListener('keydown', event => {
    if (hasSpecialKey(event)) {
      return;
    }
    if (!event.target || !gearContainer.contains(event.target as Element)) {
      return;
    }
    if (event.key === 'ArrowLeft') {
      callback('cw', 1);
      event.preventDefault();
    } else if (event.key === 'ArrowRight') {
      callback('ccw', 1);
      event.preventDefault();
    }
  });

  const gears = document.querySelector('.gears')!;
  const gearBody = document.querySelector<SVGElement>(`.gear${gear} .gear-body`)!;
  let mousedownX: number | undefined;
  let mousedownY: number | undefined;
  let cumulativeRotation = 0;
  let rotating = false;

  const mousemoveHandler = (event: MouseEvent) => onGearMove(event.pageX, event.pageY);
  const touchmoveHandler = (event: TouchEvent) => onGearMove(event.touches[0].pageX, event.touches[0].pageY);

  gearBody.addEventListener('mousedown', (event) => {
    const typedEvent = event as MouseEvent;
    const target = typedEvent.target as Element;
    if (!target) {
      return;
    }
    mousedownX = typedEvent.pageX;
    mousedownY = typedEvent.pageY;

    window.addEventListener('mousemove', mousemoveHandler);
    event.preventDefault();
  });
  gearBody.addEventListener('touchstart', (event: TouchEvent) => {
    const target = event.target as Element;
    if (!target || event.touches.length !== 1) {
      return;
    }
    mousedownX = event.touches[0].pageX;
    mousedownY = event.touches[0].pageY

    window.addEventListener('touchmove', touchmoveHandler);
    event.preventDefault();
  });
  window.addEventListener('mouseup', stopListeningMove);
  window.addEventListener('touchend', stopListeningMove);
  window.addEventListener('blur', stopListeningMove);

  function stopListeningMove() {
    mousedownX = undefined;
    mousedownY = undefined;
    cumulativeRotation = 0;
    rotating = false;

    window.removeEventListener('mousemove', mousemoveHandler);
    window.removeEventListener('touchmove', touchmoveHandler);
  }

  function onGearMove(pageX: number, pageY: number) {
    if (mousedownX === undefined || mousedownY === undefined) {
      return;
    }

    if (!rotating) {
      const dx = pageX - mousedownX;
      const dy = pageY - mousedownY;
      const distance = Math.sqrt(dx*dx + dy*dy);
      if (distance < 20) {
        return;
      } else {
        rotating = true;
      }
    }

    const rect = gearBody.getBoundingClientRect();
    const centerX = window.scrollX + rect.left + rect.width/2;
    const centerY = window.scrollY + rect.top + rect.height/2;
    const angle = Math.atan2(pageY - centerY, pageX - centerX) - Math.atan2(mousedownY - centerY, mousedownX - centerX);
    const isOdd = ODD_GEARS.has(gear);
    const isEngaged = gears.classList.contains('engaged');

    const {rotateStep, size} = GEARS[gear];
    const effectiveRotateStep = isEngaged ? rotateStep : rotateStep * 2;
    let rotation = (Math.round(angle / effectiveRotateStep) - cumulativeRotation) % size;
    if (rotation < 0) {
      rotation += size;
    }
    if (rotation > size / 2) {
      rotation -= size;
    }
    if (rotation > 0) {
      cumulativeRotation += rotation;
      callback(isOdd ? 'ccw' : 'cw', rotation);
    } else if (rotation < 0) {
      cumulativeRotation += rotation;
      callback(isOdd ? 'cw' : 'ccw', -rotation);
    }
  }
}
