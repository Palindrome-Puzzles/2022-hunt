import { assert, hasSpecialKey } from "@common/helpers";
import {
  StateListPuzzleManager,
  StateListPuzzleManagerOpts,
} from "@common/state-list-puzzle-manager";
import {
  Gear,
  GearLabelUpdate,
  GearInfo,
  Updates,
  Refresh,
  Partial as PartialData,
  RotationUpdates,
  GearOffsetUpdates,
} from "./types";
import {
  toDegrees,
  NUM_STOPS,
  FIXED_LETTERS,
  initializeGearLayout,
  GEARS,
  GEARS_IN_ORDER,
  INNER_RADIUS,
  ODD_GEARS,
  FIXED_PEGS,
  initializeGearDom
} from "./util";
import { PUBLIC_STATE_MANAGER } from './public';

const SVG_NAMESPACE = "http://www.w3.org/2000/svg";

initializeGearLayout();

// Export globally so the auto onload handler can find this.
window.puzzleOnLoad = puzzleOnLoad;
window.puzzleOnCopy = puzzleOnCopy;

type DomUpdateDescriptor =
  | { readonly action: "engaged" | "rotation" }
  | { readonly action: "offset"; readonly gear: Gear }
  | {
      readonly action: "label";
      labels: ReadonlyArray<{ readonly gear: Gear; readonly peg: number }>;
    };

function puzzleOnLoad() {
  puzzleManager.markPuzzleLoaded();
}

function puzzleOnCopy(copiedPuzzle: HTMLElement) {}

const puzzleManager = new (class extends StateListPuzzleManager<
  Updates,
  Refresh,
  PartialData,
  DomUpdateDescriptor
> {
  private engaged = false;
  private rotation = 0;
  private gears: Record<Gear, GearInfo> | null = null;
  private pendingCount: {
    rotation: number;
    gears: Partial<Record<Gear, number>>;
  } = { rotation: 0, gears: {} };
  private wasRefresh = false;
  private rotationUpdatesPaused = false;
  private menuWidth: number | null = null;

  private readonly debouncedUpdateRotateOrOffset = accumAndDebounce(
    (update: RotationUpdates | GearOffsetUpdates) => {
      if (update.action === "rotation") {
        this.pendingCount.rotation += 1;
      } else if (update.action === "offset") {
        this.pendingCount.gears[update.gear] =
          (this.pendingCount.gears[update.gear] || 0) + 1;
      }
      this.puzzleState.update(update);
    },
    "delta"
  );

  constructor(opts: StateListPuzzleManagerOpts) {
    super(opts, PUBLIC_STATE_MANAGER);
  }

  initializeDom() {
    // Enable rotation for each gear after the initial state has been loaded.
    setTimeout(() => {
      document.querySelector(".gears")!.classList.remove("transition-disabled");
    }, 0);

    // Initialize toggle button.
    const toggleButton =
      document.querySelector<HTMLButtonElement>(".toggle-engaged")!;
    toggleButton.addEventListener("click", (event) => {
      this.toggleEngaged(event);
    });

    // Add rotate buttons to each gear.
    for (const gear of GEARS_IN_ORDER) {
      initializeGearDom(gear, (dir, steps) => this.rotateOrOffset(gear, dir, steps));
    }

    // Add menu behaviour to each peg label.
    for (const tooth of document.querySelectorAll("svg .tooth:not(.fixed)")) {
      tooth.addEventListener("click", (event) => {
        this.showLabelMenu(event as MouseEvent);
        event.preventDefault();
      });
      tooth.addEventListener("keydown", (event) => {
        const typedEvent = event as KeyboardEvent;
        if (typedEvent.key === "Enter" || typedEvent.key === " ") {
          this.showLabelMenu(event as MouseEvent);
          event.preventDefault();
        } else {
          const target = event.target! as SVGElement;
          const gear = target.closest<SVGElement>(".gear")!.dataset
            .gear! as Gear;
          const peg = parseInt(target.dataset.peg!, 10);
          if (this.handleLetterPress(typedEvent, gear, peg)) {
            event.preventDefault();
          }
        }
      });
    }

    // Add events to letter menu.
    this.initializeLetterMenuDom();
  }

  handleRefresh(refresh: Refresh) {
    this.wasRefresh = true;
    this.engaged = refresh.engaged;
    this.rotation = refresh.rotation;
    this.gears = refresh.gears;

    this.pendingCount.rotation = 0;
    this.pendingCount.gears = {};
  }

  handleUpdate(update: PartialData) {
    assert(this.gears);
    if (update.action === "engaged") {
      this.engaged = update.engaged;
    } else if (update.action === "rotation") {
      this.pendingCount.rotation -= 1;
      if (this.pendingCount.rotation <= 0) {
        this.rotation = update.rotation;
      }
    } else if (update.action === "offset") {
      this.pendingCount.gears[update.gear] =
        (this.pendingCount.gears[update.gear] || 0) - 1;
      if (this.pendingCount.gears[update.gear]! <= 0) {
        this.gears[update.gear].offset = update.offset;
      }
    } else {
      for (const label of update.labels) {
        const peg = this.gears[label.gear].pegs[label.peg];
        if (label.value === "STOP") {
          peg.letter = null;
          peg.stop = true;
        } else if (!label.value) {
          peg.letter = null;
          peg.stop = false;
        } else {
          peg.letter = label.value;
          peg.stop = false;
        }
      }
    }
    return update;
  }

  handleRollback(rollback: Updates) {
    if (rollback.action === "rotation") {
      this.pendingCount.rotation -= 1;
    } else if (rollback.action === "offset") {
      this.pendingCount.gears[rollback.gear] =
        (this.pendingCount.gears[rollback.gear] || 0) - 1;
    }
    return rollback;
  }

  synchronizeToDom(descriptor?: DomUpdateDescriptor) {
    if (!descriptor || descriptor.action === "engaged") {
      this.updateEngaged({ serverInitiated: true });
    }
    if (!descriptor || descriptor.action === "rotation") {
      this.updateRotation({ serverInitiated: true });
    }
    if (!descriptor || descriptor.action === "offset") {
      this.updateOffset({
        serverInitiated: true,
        ref: descriptor ? { gear: descriptor.gear } : undefined,
      });
    }
    if (!descriptor || descriptor.action === "label") {
      this.updateLabel(descriptor ? descriptor.labels : undefined);
    }
  }

  private updateEngaged({ serverInitiated }: { serverInitiated: boolean }) {
    const gears = document.querySelector(".gears")!;
    const toggleButton =
      document.querySelector<HTMLButtonElement>(".toggle-engaged")!;
    toggleButton.disabled = !serverInitiated;

    // Wait for rotate animation to finish before engaging. Don't bother if
    // public access, as we abuse refreshes to make that work.
    if (!window.isPublicAccess) {
      if (this.wasRefresh) {
        gears.classList.add("refreshed");
        this.wasRefresh = false;
      } else {
        gears.classList.remove("refreshed");
      }
    }

    if (this.engaged) {
      toggleButton.innerText = "Disengage Gears";
      gears.classList.add("engaged");
      gears.classList.remove("disengaged");
    } else {
      toggleButton.innerText = "Engage Gears";
      gears.classList.remove("engaged");
      gears.classList.add("disengaged");
    }
  }

  private updateRotation({ serverInitiated }: { serverInitiated: boolean }) {
    if (this.rotationUpdatesPaused && serverInitiated) return;

    for (const gear of GEARS_IN_ORDER) {
      const { initialRotation, rotateStep } = GEARS[gear];
      const angle = initialRotation + rotateStep * this.rotation;
      const rotationEl = document.querySelector<SVGElement>(
        `.gear${gear} .gear-rotate`
      )!;
      rotationEl.style.transform = `rotate(${angle}rad)`;
    }
  }

  private updateOffset({
    serverInitiated,
    ref,
  }: {
    serverInitiated: boolean;
    ref?: { gear: Gear };
  }) {
    if (this.rotationUpdatesPaused && serverInitiated) return;

    assert(this.gears);
    const gearsToUpdate = ref ? [ref.gear] : GEARS_IN_ORDER;
    for (const gear of gearsToUpdate) {
      const { rotateStep } = GEARS[gear];
      // Offsets need to be doubled, as we need gears to stay aligned.
      const angle = rotateStep * this.gears[gear].offset * 2;
      const offsetEl = document.querySelector<SVGElement>(
        `.gear${gear} .gear-offset`
      )!;
      offsetEl.style.transform = `rotate(${angle}rad)`;
    }
  }

  private updateLabel(
    refs?: ReadonlyArray<{ readonly gear: Gear; readonly peg: number }>
  ) {
    assert(this.gears);
    if (!refs) {
      const allRefs = [];
      for (const gear of GEARS_IN_ORDER) {
        const isOdd = ODD_GEARS.has(gear);
        for (let i = 0; i < GEARS[gear].size; i++) {
          const peg = isOdd ? 2 * i + 1 : 2 * i;
          if (FIXED_PEGS[gear][peg]) continue;
          allRefs.push({ gear, peg });
        }
      }
      refs = allRefs;
    }

    for (const { gear, peg } of refs) {
      const tooth = document.querySelector(`.gear${gear} .tooth${peg}`)!;
      const toothText = tooth.querySelector(".text")!;
      const pegInfo = this.gears[gear].pegs[peg];
      if (pegInfo.stop) {
        toothText.textContent = "STOP";
        tooth.classList.add("stopped");
      } else {
        toothText.textContent = pegInfo.letter || "";
        tooth.classList.remove("stopped");
      }
    }
  }

  private togglePauseRotation(paused: boolean) {
    this.rotationUpdatesPaused = paused;
    if (!paused) {
      // Catch up on any missed rotations now that we've unpaused.
      this.updateRotation({ serverInitiated: true });
      this.updateOffset({ serverInitiated: true });
    }
  }

  private toggleEngaged(event: Event) {
    // Optimistic update for the view.
    this.engaged = !this.engaged;
    this.updateEngaged({ serverInitiated: false });

    this.puzzleState.update({
      action: "engaged",
      engaged: this.engaged,
    });
  }

  private rotateOrOffset(gear: Gear, dir: "cw" | "ccw", steps: number) {
    const deltaFactor = ODD_GEARS.has(gear) ? -1 : 1;
    const delta = deltaFactor * (dir === "cw" ? steps : -steps);
    if (this.engaged) {
      // Optimistic update.
      this.rotation += delta;
      this.updateRotation({ serverInitiated: false });
      this.debouncedUpdateRotateOrOffset({ action: "rotation", delta });
    } else {
      // Optimistic update.
      assert(this.gears);
      this.gears[gear].offset += delta;
      this.updateOffset({ serverInitiated: false, ref: { gear } });
      this.debouncedUpdateRotateOrOffset({ action: "offset", gear, delta });
    }
  }

  private initializeLetterMenuDom() {
    const menu = document.querySelector<HTMLElement>(".letter-menu")!;
    menu.addEventListener("focusout", (event) => {
      if (!event.relatedTarget || !menu.contains(event.relatedTarget as Node)) {
        this.maybeCloseLabelMenu();
      }
    });
    menu.addEventListener("keydown", (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        this.maybeCloseLabelMenu();
        event.preventDefault();
      } else {
        const gear = menu.dataset.gear! as Gear;
        const peg = parseInt(menu.dataset.peg!, 10);
        if (this.handleLetterPress(event, gear, peg)) {
          this.maybeCloseLabelMenu();
          event.preventDefault();
        }
      }
    });
    for (const button of menu.querySelectorAll<HTMLButtonElement>(
      ".letters button"
    )) {
      const letter = button.innerText;
      button.addEventListener("click", () => {
        this.performLabel(
          button.classList.contains("selected") ? null : letter,
          menu.dataset.gear! as Gear,
          parseInt(menu.dataset.peg!, 10)
        );
        this.maybeCloseLabelMenu();
      });
    }
    const stopButton = menu.querySelector<HTMLButtonElement>(".stop-button")!;
    stopButton.addEventListener("click", () => {
      this.puzzleState.update({
        action: "label",
        labels: [
          {
            gear: menu.dataset.gear! as Gear,
            peg: parseInt(menu.dataset.peg!, 10),
            value: stopButton.classList.contains("selected") ? null : "STOP",
          },
        ],
      });
      this.maybeCloseLabelMenu();
    });
  }

  private showLabelMenu(event: MouseEvent) {
    assert(this.gears);
    this.togglePauseRotation(true);

    const target = event.target! as Element;
    const rect = target.getBoundingClientRect();
    const pageX = window.pageXOffset + rect.left;
    const pageY = window.pageYOffset + rect.bottom;

    const menu = document.querySelector<HTMLElement>(".letter-menu")!;
    menu.classList.remove("hidden");
    this.menuWidth = this.menuWidth || menu.offsetWidth;

    const visualViewport = window.visualViewport;
    const distanceLeft = pageX - visualViewport.pageLeft;
    const distanceRight =
      visualViewport.pageLeft + visualViewport.width - pageX;

    let offsetX;
    const requiredSpace = 50 + this.menuWidth / 2;
    // If we're too close to the left side of the page.
    if (distanceLeft < requiredSpace) {
      offsetX = 0;
    }
    // If we're too close to the right side of the page.
    else if (distanceRight < requiredSpace) {
      offsetX = -this.menuWidth;
    } else {
      offsetX = -this.menuWidth / 2;
    }

    menu.style.left = `${pageX + offsetX}px`;
    menu.style.top = `${pageY}px`;

    const used = new Set<string>(FIXED_LETTERS);
    let stopCount = 0;
    for (const gearInfo of Object.values(this.gears)) {
      for (const peg of Object.values(gearInfo.pegs)) {
        if (peg.stop) {
          stopCount += 1;
        } else if (peg.letter) {
          used.add(peg.letter);
        }
      }
    }
    const remainingStops = Math.max(NUM_STOPS - stopCount, 0);
    const tooth = target.closest(".tooth")!;
    const selectedLetter = tooth.querySelector(".text")!.textContent;

    let elToFocus = null;
    for (const letterButton of menu.querySelectorAll<HTMLElement>(
      ".letters button"
    )) {
      letterButton.classList.toggle("used", used.has(letterButton.innerText));
      letterButton.classList.toggle(
        "selected",
        letterButton.innerText === selectedLetter
      );
      if (letterButton.innerText === selectedLetter) {
        elToFocus = letterButton;
      } else if (!elToFocus && !FIXED_LETTERS.has(letterButton.innerText)) {
        elToFocus = letterButton;
      }
    }
    if (elToFocus) {
      elToFocus.focus();
    }
    menu.querySelector<HTMLElement>(".stop-count")!.innerText =
      remainingStops.toString();

    const stopButton = menu.querySelector<HTMLButtonElement>(".stop-button")!;
    stopButton.classList.toggle("selected", selectedLetter === "STOP");
    stopButton.disabled = remainingStops === 0 && selectedLetter !== "STOP";

    menu.dataset.gear = target.closest<SVGElement>(".gear")!.dataset.gear;
    menu.dataset.peg = target.closest<SVGElement>(".tooth")!.dataset.peg;
  }

  private maybeCloseLabelMenu() {
    const menu = document.querySelector<HTMLElement>(".letter-menu")!;
    if (!menu.classList.contains("hidden")) {
      this.togglePauseRotation(false);
      menu.classList.add("hidden");

      const { gear, peg } = menu.dataset;
      document.querySelector<SVGElement>(`.gear${gear} .tooth${peg}`)!.focus();
    }
  }

  private performLabel(value: string | null, gear: Gear, peg: number) {
    assert(this.gears);
    const labels: GearLabelUpdate[] = [];
    // First remove the letter from elsewhere.
    for (const [currentGear, gearInfo] of Object.entries(this.gears)) {
      for (const [currentPeg, pegInfo] of Object.entries(gearInfo.pegs)) {
        if (pegInfo.letter === value) {
          // Do nothing if already labelled.
          if (gear === currentGear && peg === parseInt(currentPeg, 10)) {
            return;
          }
          labels.push({
            gear: currentGear as Gear,
            peg: parseInt(currentPeg, 10),
            value: null,
          });
          break;
        }
      }
    }
    labels.push({
      gear,
      peg,
      value,
    });
    this.puzzleState.update({
      action: "label",
      labels,
    });
  }

  private handleLetterPress(event: KeyboardEvent, gear: Gear, peg: number) {
    if (hasSpecialKey(event)) {
      return;
    }

    if (event.key.length === 1) {
      const charCode = event.key.toUpperCase().charCodeAt(0);
      if (charCode >= "A".charCodeAt(0) && charCode <= "Z".charCodeAt(0)) {
        const letter = event.key.toUpperCase();
        if (!FIXED_LETTERS.has(letter)) {
          this.performLabel(letter, gear, peg);
          return true;
        }
      }
    }
    return false;
  }
})({
  serverUrl: "/ws/puzzle/gears-and-arrows",
  puzzleUrl: "gears-and-arrows",
  defaultScope: "1",
  puzzleAuthToken: window.puzzleAuthToken,
  // The puzzle can't really be put into an invalid state, so no need for seq-based
  // locking. It also means we don't need to queue updates until the previous one
  // resolves.
  skipLock: true,
});

function accumAndDebounce<T, Key extends string, Other>(
  fn: (arg: { [K in Key]: number } & Other) => void,
  accumKey: Key,
  debounceTime = 300
) {
  const cache = new Map<Other, { timeout: number; accum: number }>();
  return (arg: { [K in Key]: number } & Other) => {
    const delta: number = arg[accumKey];
    const compareKeys = Object.keys(arg).filter(
      (otherKey) => otherKey !== accumKey
    ) as (keyof Other)[];
    let newAccum = delta;
    for (const [other, cacheEntry] of cache.entries()) {
      if (compareKeys.every((key) => other[key] === arg[key])) {
        clearTimeout(cacheEntry.timeout);
        newAccum += cacheEntry.accum;
        cache.delete(other);
        break;
      }
    }

    const timeout = window.setTimeout(() => {
      fn({ ...arg, [accumKey]: newAccum });
      cache.delete(arg);
    }, debounceTime);
    cache.set(arg, { timeout, accum: newAccum });
  };
}
