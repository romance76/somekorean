import { eval5, evalHand, preflopStr, RV } from './useHandEvaluation.js';

// ═══════════════════════════════════════════════════════════════
// AI PROFILES
// ═══════════════════════════════════════════════════════════════
export const AI_PROFILES = [
  { name: "대니얼", style: "tight-aggressive", emoji: "🧔", desc: "타이트-어그레시브", color: "#e74c3c" },
  { name: "소피아", style: "loose-aggressive", emoji: "👩‍🦰", desc: "루즈-어그레시브", color: "#9b59b6" },
  { name: "재민", style: "tight-passive", emoji: "👨‍💼", desc: "타이트-패시브", color: "#3498db" },
  { name: "린다", style: "loose-passive", emoji: "👩‍🏫", desc: "루즈-패시브", color: "#e67e22" },
  { name: "마이크", style: "maniac", emoji: "🤠", desc: "매니악(올인 머신)", color: "#e74c3c" },
  { name: "유나", style: "balanced", emoji: "👩‍💻", desc: "밸런스드", color: "#1abc9c" },
  { name: "빅터", style: "nit", emoji: "🧓", desc: "극타이트(닛)", color: "#7f8c8d" },
  { name: "하나", style: "tricky", emoji: "👩‍🎤", desc: "트리키(블러프 多)", color: "#f39c12" },
];

// ═══════════════════════════════════════════════════════════════
// AI DECISION ENGINE
// ═══════════════════════════════════════════════════════════════
export function aiAct(cards, comm, pot, toCall, chips, style, blindLvl, activePlayers) {
  const all = [...cards, ...comm];
  const hs = all.length >= 5 ? evalHand(all).rank : preflopStr(cards);
  const r = Math.random();
  const m = chips / blindLvl.bb;
  const styleAdj = {
    "tight-aggressive": { foldTh: 3, raiseBonus: 0.2, bluff: 0.1 },
    "loose-aggressive": { foldTh: 1, raiseBonus: 0.3, bluff: 0.25 },
    "tight-passive": { foldTh: 4, raiseBonus: -0.1, bluff: 0.05 },
    "loose-passive": { foldTh: 2, raiseBonus: -0.2, bluff: 0.15 },
    "maniac": { foldTh: 1, raiseBonus: 0.4, bluff: 0.35 },
    "balanced": { foldTh: 2, raiseBonus: 0.1, bluff: 0.15 },
    "nit": { foldTh: 5, raiseBonus: 0, bluff: 0.03 },
    "tricky": { foldTh: 2, raiseBonus: 0.15, bluff: 0.3 },
  }[style] || { foldTh: 2, raiseBonus: 0.1, bluff: 0.15 };

  // Short stack push/fold
  if (m <= 8 && toCall > 0) {
    if (hs >= 5 || (hs >= 3 && r < 0.4)) return { action: "allin" };
    return { action: "fold" };
  }
  if (m <= 8 && hs >= 4) return { action: "allin" };

  if (hs >= 8) {
    const amt = Math.floor(Math.min(Math.max(pot, toCall * 3), chips));
    return toCall > 0
      ? { action: "raise", amount: amt }
      : { action: "raise", amount: Math.floor(Math.min(pot * 0.8, chips)) };
  }
  if (hs >= 6) {
    if (toCall > 0) return r > 0.3
      ? { action: "raise", amount: Math.floor(Math.min(toCall * 2.5, chips)) }
      : { action: "call" };
    return { action: "raise", amount: Math.floor(Math.min(blindLvl.bb * 3, chips)) };
  }
  if (hs >= styleAdj.foldTh + 1) {
    if (toCall > chips * 0.3) return { action: "fold" };
    if (toCall > 0) return r > (0.4 - styleAdj.raiseBonus)
      ? { action: "call" }
      : { action: "raise", amount: Math.floor(Math.min(toCall * 2, chips)) };
    return r > (0.5 - styleAdj.raiseBonus)
      ? { action: "raise", amount: Math.floor(Math.min(blindLvl.bb * (2 + r * 2), chips)) }
      : { action: "check" };
  }
  if (hs >= styleAdj.foldTh) {
    if (toCall > chips * 0.15) return { action: "fold" };
    if (toCall > 0) return r > 0.5 ? { action: "call" } : { action: "fold" };
    return r < styleAdj.bluff
      ? { action: "raise", amount: Math.floor(Math.min(blindLvl.bb * 2.5, chips)) }
      : { action: "check" };
  }
  // Weak hand - bluff or fold
  if (toCall > 0) return r < styleAdj.bluff * 0.5 ? { action: "call" } : { action: "fold" };
  return r < styleAdj.bluff
    ? { action: "raise", amount: Math.floor(Math.min(blindLvl.bb * 2, chips)) }
    : { action: "check" };
}

// ═══════════════════════════════════════════════════════════════
// AI CHAT / TABLE TALK
// ═══════════════════════════════════════════════════════════════
export const CHAT_LINES = {
  fold: ["ㅎㅎ 접는다~", "이건 패스", "안되겠다 폴드", "가비지 핸드 ㅋ", "다음 판에 보자"],
  call: ["콜~", "한번 보자", "따라간다", "흠… 콜", "수딧이냐?", "오… 콜해볼게"],
  raise: ["올린다!", "레이즈!", "좀 치자", "슬슬 올려볼까", "이거 괜찮은데?", "자신있어?"],
  allin: ["올인!!! 💥", "다 걸어!", "받아라!!", "올인이다 ㄱㄱ", "갈 때 가자!"],
  check: ["체크~", "넘긴다", "지켜보자", "패스"],
  win: ["나이스~! 🎉", "고마워 ㅋㅋ", "이건 내 팟", "잘 먹겠습니다~"],
  lose: ["아… 운이 없네", "다음엔 이긴다", "졌다 ㅠ", "괜찮아 다음 판"],
  bighand: ["와 수딧 플러시?!", "풀하우스 ㄷㄷ", "이건 못 이기지", "대박 핸드 나왔네"],
  bluff: ["읽힌 건가…", "블러프 들켰네 ㅋ", "속일 뻔했는데"],
  react_raise: ["에이 또 올리네", "부담스럽다…", "크게 나왔네", "뭘 들고 있는 거야"],
  react_allin: ["올인?! 진짜?", "ㄷㄷㄷ", "미쳤다 ㅋㅋ", "이거 실화?"],
  greeting: ["반갑습니다~", "잘 부탁해요", "어느 테이블에서 왔어요?"],
  eliminated: ["GG", "수고했습니다", "다음엔 잘하겠지…"],
};

export function getChat(action, style) {
  const lines = CHAT_LINES[action];
  if (!lines || Math.random() > 0.4) return null; // 40% chance to talk
  return lines[Math.floor(Math.random() * lines.length)];
}

// ═══════════════════════════════════════════════════════════════
// FOLD REASON ANALYZER
// ═══════════════════════════════════════════════════════════════
export function getFoldReason(cards, comm, toCall, chips, style, pos, blindBB) {
  const hs = comm.length >= 3 ? evalHand([...cards, ...comm]).rank : preflopStr(cards);
  const m = chips / blindBB;
  const reasons = [];
  // Hand weakness
  if (hs <= 1) reasons.push("매우 약한 핸드 (하이카드 이하)");
  else if (hs <= 2) reasons.push("약한 핸드 (로우 페어/하이카드)");
  else if (hs <= 3) reasons.push("보통 핸드지만 상대 베팅 대비 약함");
  // Position
  if (pos <= 3) reasons.push("얼리 포지션이라 리스크가 큼");
  // Bet sizing
  if (toCall > 0) {
    const potOdds = toCall / (toCall + chips * 0.1);
    if (toCall > chips * 0.2) reasons.push(`콜 비용(${toCall})이 스택의 ${Math.round(toCall / chips * 100)}% — 너무 비쌈`);
    else if (toCall > blindBB * 5) reasons.push(`큰 베팅(${toCall})에 약한 핸드로 콜하면 손해`);
  }
  // Style
  const styleDesc = {
    "tight-aggressive": "타이트한 플레이어라 약한 핸드는 바로 폴드",
    "tight-passive": "보수적 스타일 — 확실한 핸드만 플레이",
    "nit": "극도로 타이트 — 프리미엄 핸드 외 전부 폴드",
    "balanced": "밸런스 플레이 — 이 상황에서 폴드가 +EV",
    "loose-aggressive": "보통 넓게 플레이하지만 이 핸드는 너무 약함",
    "loose-passive": "루즈하지만 베팅 압박에 약해서 폴드",
    "tricky": "트리키 플레이어지만 이번엔 블러프 포기",
    "maniac": "매니악도 포기할 정도로 상황이 안 좋음",
  }[style] || "";
  if (styleDesc) reasons.push(styleDesc);
  return reasons.slice(0, 2).join(". ") + "." || "약한 핸드로 판단하여 폴드.";
}
