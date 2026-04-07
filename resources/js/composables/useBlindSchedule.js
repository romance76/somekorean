// ═══════════════════════════════════════════════════════════════
// BLIND SCHEDULE
// ═══════════════════════════════════════════════════════════════
export const BLIND_SCHEDULE = [
  { sb: 10, bb: 20, ante: 0, dur: 15 },
  { sb: 15, bb: 30, ante: 0, dur: 15 },
  { sb: 25, bb: 50, ante: 5, dur: 15 },
  { sb: 50, bb: 100, ante: 10, dur: 15 },
  { sb: 75, bb: 150, ante: 15, dur: 12 },
  { sb: 100, bb: 200, ante: 25, dur: 12 },
  { sb: 150, bb: 300, ante: 25, dur: 12 },
  { sb: 200, bb: 400, ante: 50, dur: 10 },
  { sb: 300, bb: 600, ante: 75, dur: 10 },
  { sb: 400, bb: 800, ante: 100, dur: 10 },
  { sb: 500, bb: 1000, ante: 100, dur: 10 },
  { sb: 600, bb: 1200, ante: 200, dur: 8 },
  { sb: 800, bb: 1600, ante: 200, dur: 8 },
  { sb: 1000, bb: 2000, ante: 300, dur: 8 },
  { sb: 1500, bb: 3000, ante: 400, dur: 8 },
  { sb: 2000, bb: 4000, ante: 500, dur: 8 },
];

// ═══════════════════════════════════════════════════════════════
// HELPER FUNCTIONS
// ═══════════════════════════════════════════════════════════════

/**
 * Returns the blind schedule entry for the given level,
 * clamped to the array bounds.
 */
export function getCurrentBlind(level) {
  return BLIND_SCHEDULE[Math.min(level, BLIND_SCHEDULE.length - 1)];
}

/**
 * Returns the next blind schedule entry (level + 1),
 * clamped to the array bounds.
 */
export function getNextBlind(level) {
  return BLIND_SCHEDULE[Math.min(level + 1, BLIND_SCHEDULE.length - 1)];
}

/**
 * Formats seconds as "M:SS" (e.g. 125 -> "2:05")
 */
export function fmtTime(s) {
  return `${Math.floor(s / 60)}:${(s % 60).toString().padStart(2, "0")}`;
}

/**
 * Formats elapsed seconds as "Xh Ym" or "Xm"
 */
export function fmtElapsed(s) {
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  return h > 0 ? `${h}h ${m}m` : `${m}m`;
}
