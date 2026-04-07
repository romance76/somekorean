// ═══════════════════════════════════════════════════════════════
// CONSTANTS & UTILITIES
// ═══════════════════════════════════════════════════════════════
export const SUITS = ["♠","♥","♦","♣"];
export const SC = {"♠":"#1a1a2e","♥":"#cc0000","♦":"#cc0000","♣":"#1a1a2e"};
export const RANKS = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"];
export const RV = {2:2,3:3,4:4,5:5,6:6,7:7,8:8,9:9,10:10,J:11,Q:12,K:13,A:14};

export function createDeck() {
  const d = [];
  for (const s of SUITS) for (const r of RANKS) d.push({ rank: r, suit: s });
  return d;
}

export function shuffle(d) {
  const a = [...d];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

// ═══════════════════════════════════════════════════════════════
// HAND EVALUATION
// ═══════════════════════════════════════════════════════════════
export function getCombos(a, k) {
  if (k === 0) return [[]];
  if (a.length < k) return [];
  const [f, ...r] = a;
  return [...getCombos(r, k - 1).map(c => [f, ...c]), ...getCombos(r, k)];
}

export function eval5(cards) {
  const v = cards.map(c => RV[c.rank]).sort((a, b) => b - a);
  const ss = cards.map(c => c.suit);
  const fl = ss.every(s => s === ss[0]);
  let str = false, sh = 0;
  const uv = [...new Set(v)].sort((a, b) => b - a);
  if (uv.length === 5) {
    if (uv[0] - uv[4] === 4) { str = true; sh = uv[0]; }
    if (uv[0] === 14 && uv[1] === 5) { str = true; sh = 5; }
  }
  const ct = {};
  v.forEach(x => { ct[x] = (ct[x] || 0) + 1; });
  const g = Object.entries(ct).map(([val, cnt]) => ({ v: +val, c: cnt })).sort((a, b) => b.c - a.c || b.v - a.v);
  if (fl && str && sh === 14) return { rank: 10, name: "로열 플러시", score: 10e8 };
  if (fl && str) return { rank: 9, name: "스트레이트 플러시", score: 9e8 + sh };
  if (g[0].c === 4) return { rank: 8, name: "포카드", score: 8e8 + g[0].v * 100 + g[1].v };
  if (g[0].c === 3 && g[1].c === 2) return { rank: 7, name: "풀하우스", score: 7e8 + g[0].v * 100 + g[1].v };
  if (fl) return { rank: 6, name: "플러시", score: 6e8 + v[0] * 1e4 + v[1] * 1e3 + v[2] * 100 + v[3] * 10 + v[4] };
  if (str) return { rank: 5, name: "스트레이트", score: 5e8 + sh };
  if (g[0].c === 3) return { rank: 4, name: "트리플", score: 4e8 + g[0].v * 1e4 + g[1].v * 100 + (g[2] ? g[2].v : 0) };
  if (g[0].c === 2 && g[1].c === 2) return { rank: 3, name: "투페어", score: 3e8 + Math.max(g[0].v, g[1].v) * 1e4 + Math.min(g[0].v, g[1].v) * 100 + (g[2] ? g[2].v : 0) };
  if (g[0].c === 2) return { rank: 2, name: "원페어", score: 2e8 + g[0].v * 1e6 + g[1].v * 1e4 + g[2].v * 100 + (g[3] ? g[3].v : 0) };
  return { rank: 1, name: "하이카드", score: 1e8 + v[0] * 1e6 + v[1] * 1e4 + v[2] * 100 + v[3] * 10 + v[4] };
}

export function evalHand(cards) {
  if (cards.length < 5) return { rank: 0, name: "-", score: 0, best: cards };
  let best = null;
  for (const c of getCombos(cards, 5)) {
    const e = eval5(c);
    if (!best || e.score > best.score) best = { ...e, best: c };
  }
  return best;
}

// ═══════════════════════════════════════════════════════════════
// PREFLOP STRENGTH (1-9)
// ═══════════════════════════════════════════════════════════════
export function preflopStr(cards) {
  const v1 = RV[cards[0].rank], v2 = RV[cards[1].rank];
  const p = v1 === v2, s = cards[0].suit === cards[1].suit, h = Math.max(v1, v2), l = Math.min(v1, v2);
  if (p && h >= 12) return 9;
  if (p && h >= 10) return 8;
  if (p && h >= 7) return 6;
  if (p) return 4;
  if (h === 14 && l >= 12) return s ? 8 : 7;
  if (h === 14 && l >= 10) return s ? 6 : 5;
  if (h === 14) return s ? 4 : 3;
  if (s && h - l <= 2 && h >= 9) return 5;
  if (h >= 12 && l >= 10) return s ? 5 : 4;
  return l >= 9 ? 3 : h >= 10 ? 2 : 1;
}
