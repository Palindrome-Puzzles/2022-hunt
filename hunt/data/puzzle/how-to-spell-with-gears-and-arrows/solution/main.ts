import { assert } from "@common/helpers";
import { Gear } from "../types";
import {
  initializeGearLayout,
  GEARS,
  GEARS_IN_ORDER,
  ODD_GEARS,
  initializeGearDom,
} from "../util";

initializeGearLayout();

// Export globally so the auto onload handler can find this.
window.puzzleOnLoad = puzzleOnLoad;

const state = {
  engaged: false,
  rotation: 0,
  offsetByGear: {} as Partial<Record<Gear, number>>,
};

function puzzleOnLoad() {
  document.querySelector(".puzzle")!.classList.add("interactive");

  // Enable rotation for each gear after the initial state has been loaded.
  setTimeout(() => {
    document.querySelector(".gears")!.classList.remove("transition-disabled");
  }, 0);

  const toggleButton =
    document.querySelector<HTMLButtonElement>(".toggle-engaged")!;
  toggleButton.addEventListener("click", () => {
    state.engaged = !state.engaged;
    updateEngaged();
  });

  // Add rotate buttons to each gear.
  for (const gear of GEARS_IN_ORDER) {
    initializeGearDom(gear, (dir, steps) => rotateOrOffset(gear, dir, steps));
  }

  updateEngaged();
  updateRotation();
  updateOffset();
}

function updateEngaged() {
  const gears = document.querySelector(".gears")!;
  const toggleButton =
    document.querySelector<HTMLButtonElement>(".toggle-engaged")!;

  if (state.engaged) {
    toggleButton.innerText = "Disengage Gears";
    gears.classList.add("engaged");
    gears.classList.remove("disengaged");
  } else {
    toggleButton.innerText = "Engage Gears";
    gears.classList.remove("engaged");
    gears.classList.add("disengaged");
  }
}

function updateRotation() {
  for (const gear of GEARS_IN_ORDER) {
    const { initialRotation, rotateStep } = GEARS[gear];
    const angle = initialRotation + rotateStep * state.rotation;
    const rotationEl = document.querySelector<SVGElement>(
      `.gear${gear} .gear-rotate`
    )!;
    rotationEl.style.transform = `rotate(${angle}rad)`;
  }
}

function updateOffset(ref?: { gear: Gear }) {
  const gearsToUpdate = ref ? [ref.gear] : GEARS_IN_ORDER;
  for (const gear of gearsToUpdate) {
    const { rotateStep } = GEARS[gear];
    // Offsets need to be doubled, as we need gears to stay aligned.
    const angle = rotateStep * (state.offsetByGear[gear] || 0) * 2;
    const offsetEl = document.querySelector<SVGElement>(
      `.gear${gear} .gear-offset`
    )!;
    offsetEl.style.transform = `rotate(${angle}rad)`;
  }
}

function rotateOrOffset(gear: Gear, dir: "cw" | "ccw", steps: number) {
  const deltaFactor = ODD_GEARS.has(gear) ? -1 : 1;
  const delta = deltaFactor * (dir === "cw" ? steps : -steps);
  if (state.engaged) {
    // Optimistic update.
    state.rotation += delta;
    updateRotation();
  } else {
    state.offsetByGear[gear] = (state.offsetByGear[gear] || 0) + delta;
    updateOffset({ gear });
  }
}
