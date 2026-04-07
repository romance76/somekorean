import { evalHand, preflopStr, RV } from './useHandEvaluation.js';

// ═══════════════════════════════════════════════════════════════
// POSITION CONSTANTS
// ═══════════════════════════════════════════════════════════════
export const POSITION_NAMES = {
  0: "BTN", 1: "SB", 2: "BB", 3: "UTG", 4: "UTG+1", 5: "MP", 6: "MP+1", 7: "HJ", 8: "CO"
};

export const POS_FULL = {
  BTN: "버튼(딜러)", SB: "스몰 블라인드", BB: "빅 블라인드",
  UTG: "언더 더 건", "UTG+1": "언더 더 건+1", MP: "미들 포지션",
  "MP+1": "미들 포지션+1", HJ: "하이잭", CO: "컷오프"
};

export const POS_TIP = {
  BTN: "가장 유리한 자리! 마지막에 행동하므로 넓은 범위로 플레이 가능.",
  SB: "블라인드를 내야 하고 플랍 후 먼저 행동. 불리한 자리.",
  BB: "블라인드 투자됨. 적절한 핸드로 디펜드 가능.",
  UTG: "가장 먼저 행동. 프리미엄 핸드만 플레이!",
  "UTG+1": "여전히 얼리 포지션. 타이트하게.",
  MP: "중간 포지션. 조금 더 넓게 플레이 가능.",
  "MP+1": "미들 후반. 괜찮은 핸드 추가 가능.",
  HJ: "레이트 포지션 시작. 스틸 기회 있음.",
  CO: "버튼 바로 앞. 공격적 플레이 가능."
};

// ═══════════════════════════════════════════════════════════════
// EQUITY / WIN PROBABILITY ESTIMATOR
// ═══════════════════════════════════════════════════════════════
export function estimateEquity(cards, comm, numOpponents) {
  if (!cards || cards.length < 2) return 50;
  const hs = comm.length >= 3 ? evalHand([...cards, ...comm]).rank : 0;
  const ps = preflopStr(cards);
  // Preflop equity approximation based on hand strength vs number of opponents
  const preflopEq = { 9: 85, 8: 78, 7: 70, 6: 62, 5: 55, 4: 48, 3: 40, 2: 32, 1: 22 };
  let baseEq = preflopEq[ps] || 30;
  // Adjust for number of opponents
  if (numOpponents > 1) baseEq = Math.max(10, baseEq - ((numOpponents - 1) * 4));
  // Postflop adjustment
  if (comm.length >= 3) {
    const postEq = { 10: 99, 9: 97, 8: 94, 7: 85, 6: 78, 5: 70, 4: 58, 3: 45, 2: 35, 1: 20 };
    baseEq = postEq[hs] || baseEq;
    if (numOpponents > 1) baseEq = Math.max(8, baseEq - ((numOpponents - 1) * 3));
  }
  return Math.min(99, Math.max(5, Math.round(baseEq)));
}

// ═══════════════════════════════════════════════════════════════
// RECOMMENDATION ENGINE
// ═══════════════════════════════════════════════════════════════
export function getRecommendation(equity, potOdds, m, pos, toCall, pot, chips) {
  // Push/fold mode
  if (m <= 8) {
    if (equity >= 40) return { action: "올인", color: "#ef4444", reason: `숏스택(${Math.round(m)}BB) — 좋은 핸드면 올인으로 승부` };
    return { action: "폴드", color: "#666666", reason: `숏스택이지만 승률 ${equity}%로 부족. 더 좋은 기회를 기다리세요` };
  }
  // Has to call
  if (toCall > 0) {
    const potOddsPct = Math.round(toCall / (pot + toCall) * 100);
    if (equity >= 65) return { action: "레이즈", color: "#e8b730", reason: `승률 ${equity}% > 필요 ${potOddsPct}%. 강한 핸드로 밸류 레이즈!` };
    if (equity >= potOddsPct + 5) return { action: "콜", color: "#22c55e", reason: `승률 ${equity}% > 팟오즈 ${potOddsPct}%. 콜할 가치 있음` };
    if (equity >= potOddsPct - 5) return { action: "콜/폴드", color: "#f59e0b", reason: `승률 ${equity}% ≈ 팟오즈 ${potOddsPct}%. 경계선 — 상대 성향에 따라 판단` };
    return { action: "폴드", color: "#666666", reason: `승률 ${equity}% < 팟오즈 ${potOddsPct}%. 콜 비용 대비 이득 부족` };
  }
  // No bet to call (can check or bet)
  if (equity >= 65) return { action: "베팅", color: "#e8b730", reason: `승률 ${equity}%로 강함. 밸류벳으로 팟을 키우세요` };
  if (equity >= 40) return { action: "체크", color: "#5dade2", reason: `승률 ${equity}%. 무리하지 말고 체크 후 상황 관찰` };
  return { action: "체크/폴드", color: "#888888", reason: `승률 ${equity}%로 약함. 체크하고 상대 베팅 시 폴드 고려` };
}

// ═══════════════════════════════════════════════════════════════
// COACHING SYSTEM
// ═══════════════════════════════════════════════════════════════
export function getCoach(pCards, comm, stage, pot, chips, pos, blindLvl, remaining, paidSlots, activeCnt, toCall) {
  const m = chips / blindLvl.bb;
  const posName = POSITION_NAMES[pos] || "?";
  const equity = estimateEquity(pCards, comm, Math.max(1, activeCnt - 1));
  const potOddsPct = toCall > 0 ? Math.round(toCall / (pot + toCall) * 100) : 0;
  const rec = getRecommendation(equity, potOddsPct, m, pos, toCall || 0, pot, chips);

  // Hand description
  let handDesc = "";
  if (pCards.length === 2) {
    const v1 = RV[pCards[0].rank], v2 = RV[pCards[1].rank];
    const paired = v1 === v2, suited = pCards[0].suit === pCards[1].suit;
    const high = Math.max(v1, v2);
    if (paired) handDesc = `포켓 페어 (${pCards[0].rank}${pCards[0].rank})`;
    else if (high === 14) handDesc = `에이스 핸드 (A+${Math.min(v1, v2) >= 10 ? "페이스카드" : "로우"})`;
    else if (suited) handDesc = "수티드 (같은 무늬)";
    else handDesc = "오프수트 (다른 무늬)";
  }
  let madeHand = "";
  if (comm.length >= 3) {
    const ev = evalHand([...pCards, ...comm]);
    madeHand = ev.name || "";
  }

  // Situation flag
  let situation = "normal";
  if (remaining <= paidSlots * 1.2 && remaining > paidSlots) situation = "bubble";
  else if (remaining <= paidSlots) situation = "itm";

  return {
    posName,
    posFullName: POS_FULL[posName] || posName,
    posTip: POS_TIP[posName] || "",
    posIndex: pos, // 0=BTN(best)..8=CO
    equity,
    potOddsPct,
    rec,
    handDesc,
    madeHand,
    m: Math.round(m),
    toCall: toCall || 0,
    pot,
    chips,
    situation,
    remaining,
    paidSlots,
    activeCnt,
    bb: blindLvl.bb,
  };
}

// ═══════════════════════════════════════════════════════════════
// CONTEXTUAL TERMINOLOGY
// ═══════════════════════════════════════════════════════════════
export const TERMS = {
  "fold": { en: "Fold", kr: "폴드", desc: "카드를 버리고 핸드를 포기. 이미 넣은 칩은 돌려받지 못합니다." },
  "check": { en: "Check", kr: "체크", desc: "베팅 없이 다음 사람에게 넘김. 아무도 베팅하지 않았을 때만 가능." },
  "call": { en: "Call", kr: "콜", desc: "앞 사람의 베팅과 같은 금액을 내고 계속 참여." },
  "raise": { en: "Raise", kr: "레이즈", desc: "앞 사람의 베팅보다 더 올려서 베팅. 상대에게 압박을 줌." },
  "allin": { en: "All-in", kr: "올인", desc: "보유한 모든 칩을 걸기. 더 이상 베팅 결정이 없음." },
  "blind": { en: "Blind", kr: "블라인드", desc: "카드를 받기 전에 의무적으로 내는 베팅. SB(스몰)와 BB(빅)가 있음." },
  "ante": { en: "Ante", kr: "앤티", desc: "모든 플레이어가 핸드 시작 전에 내는 소액 의무 베팅." },
  "pot": { en: "Pot", kr: "팟", desc: "현재 핸드에서 모든 플레이어가 베팅한 칩의 총합." },
  "flop": { en: "Flop", kr: "플랍", desc: "커뮤니티 카드 3장이 동시에 공개되는 두 번째 베팅 라운드." },
  "turn": { en: "Turn", kr: "턴", desc: "4번째 커뮤니티 카드가 공개되는 세 번째 베팅 라운드." },
  "river": { en: "River", kr: "리버", desc: "5번째(마지막) 커뮤니티 카드가 공개. 최종 베팅 라운드." },
  "btn": { en: "Button (BTN)", kr: "버튼/딜러", desc: "딜러 포지션. 포스트플랍에서 마지막에 행동하여 가장 유리. 넓은 범위로 플레이 가능." },
  "SB": { en: "Small Blind", kr: "스몰 블라인드", desc: "딜러 왼쪽. BB의 절반을 의무 베팅. 플랍 이후 먼저 행동해야 해서 불리." },
  "BB": { en: "Big Blind", kr: "빅 블라인드", desc: "SB 왼쪽. 테이블 최소 베팅액을 의무 베팅. 프리플랍에서 마지막에 행동." },
  "utg": { en: "Under the Gun", kr: "언더더건", desc: "BB 바로 왼쪽. 프리플랍에서 가장 먼저 행동. 정보 없이 결정해야 해서 가장 불리." },
  "UTG+1": { en: "UTG+1", kr: "언더더건+1", desc: "UTG 바로 왼쪽. 여전히 얼리 포지션으로 프리미엄 핸드만 플레이 권장." },
  "MP": { en: "Middle Position", kr: "미들 포지션", desc: "테이블 중간. 앞에 몇 명이 행동을 봤으므로 약간 더 넓게 플레이 가능." },
  "MP+1": { en: "MP+1", kr: "미들 포지션+1", desc: "미들 후반. 레이트 포지션에 가까워 괜찮은 핸드 추가 가능." },
  "HJ": { en: "Hijack", kr: "하이잭", desc: "CO 바로 앞. 레이트 포지션의 시작. 스틸 시도 가능한 자리." },
  "co": { en: "Cutoff (CO)", kr: "컷오프", desc: "버튼 바로 앞. 버튼이 폴드하면 사실상 가장 유리한 자리. 공격적 플레이 가능." },
  "bubble": { en: "Bubble", kr: "버블", desc: "입상권 직전 상태. 1명만 더 탈락하면 남은 모두 상금 수령." },
  "shortstack": { en: "Short Stack", kr: "숏스택", desc: "칩이 적은 상태 (보통 10BB 이하). 푸시/폴드 전략 필요." },
  "potodds": { en: "Pot Odds", kr: "팟오즈", desc: "콜 비용 대비 팟 크기의 비율. 승률이 팟오즈보다 높으면 콜이 이익 (+EV)." },
  "steal": { en: "Steal", kr: "스틸", desc: "레이트 포지션에서 약한 핸드로 레이즈하여 블라인드를 훔치는 전략." },
  "cbet": { en: "Continuation Bet", kr: "씨벳", desc: "프리플랍 레이저가 플랍에서도 이어서 베팅하는 것." },
  "ev": { en: "Expected Value", kr: "기대값(EV)", desc: "+EV는 장기적으로 이익인 플레이, -EV는 손해. 항상 +EV를 선택하세요." },
  "valuebet": { en: "Value Bet", kr: "밸류벳", desc: "상대가 더 약한 핸드로 콜해줄 것을 기대하고 하는 베팅. 강한 핸드일 때 사용." },
  "underdog": { en: "Underdog", kr: "언더독", desc: "승률이 50% 미만인 약자. 반대는 페이버릿(favorite, 유리한 쪽)." },
  "equity": { en: "Equity", kr: "에퀴티/승률", desc: "현재 핸드가 최종적으로 이길 확률(%). 높을수록 유리." },
};

export function getTermForAction(action, stage, pos) {
  if (action.includes("폴드")) return TERMS.fold;
  if (action.includes("체크")) return TERMS.check;
  if (action.includes("콜")) return TERMS.call;
  if (action.includes("레이즈")) return TERMS.raise;
  if (action.includes("올인")) return TERMS.allin;
  if (stage === "flop") return TERMS.flop;
  if (stage === "turn") return TERMS.turn;
  if (stage === "river") return TERMS.river;
  return null;
}
