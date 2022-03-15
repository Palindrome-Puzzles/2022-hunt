export type Gear = 'A' | 'B' | 'C' | 'D' | 'E';

export interface GearInfo {
  offset: number;
  readonly pegs: {
    readonly [index: number]: PegInfo;
  }
}

export interface PegInfo {
  readonly index: number;
  letter: string | null;
  stop: boolean;
}

export interface EngagedUpdates {
  readonly action: 'engaged';
  readonly engaged: boolean;
}
export interface RotationUpdates {
  readonly action: 'rotation';
  readonly delta: number;
}
export interface GearOffsetUpdates {
  readonly action: 'offset';
  readonly gear: Gear;
  readonly delta: number;
}
export interface GearLabelUpdate {
  readonly gear: Gear;
  readonly peg: number;
  readonly value: string | null;
}
export interface GearLabelUpdates {
  readonly action: 'label';
  readonly labels: ReadonlyArray<GearLabelUpdate>;
}
export type Updates = EngagedUpdates | RotationUpdates | GearOffsetUpdates | GearLabelUpdates;

export interface Refresh {
  readonly engaged: boolean;
  readonly rotation: number;
  readonly gears: Record<Gear, GearInfo>;
}

export type EngagedPartial = EngagedUpdates;
export interface RotationPartial {
  readonly action: 'rotation';
  readonly rotation: number;
  readonly delta: number;
}
export interface GearOffsetPartial {
  readonly action: 'offset';
  readonly gear: Gear;
  readonly offset: number;
  readonly delta: number;
}
export type GearLabelPartial = GearLabelUpdates;

export type Partial = EngagedPartial | RotationPartial | GearOffsetPartial | GearLabelPartial;
