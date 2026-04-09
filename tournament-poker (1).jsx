import { useState, useEffect, useCallback, useRef, useMemo } from "react";

// ═══════════════════════════════════════════════════════════════
// CONSTANTS & UTILITIES
// ═══════════════════════════════════════════════════════════════
const SUITS = ["♠","♥","♦","♣"];
const SC = {"♠":"#1a1a2e","♥":"#cc0000","♦":"#cc0000","♣":"#1a1a2e"};
const RANKS = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"];
const RV = {2:2,3:3,4:4,5:5,6:6,7:7,8:8,9:9,10:10,J:11,Q:12,K:13,A:14};

const POSITION_NAMES = {
  0:"BTN", 1:"SB", 2:"BB", 3:"UTG", 4:"UTG+1", 5:"MP", 6:"MP+1", 7:"HJ", 8:"CO"
};
const POS_FULL = {
  BTN:"버튼(딜러)", SB:"스몰 블라인드", BB:"빅 블라인드",
  UTG:"언더 더 건", "UTG+1":"언더 더 건+1", MP:"미들 포지션",
  "MP+1":"미들 포지션+1", HJ:"하이잭", CO:"컷오프"
};
const POS_TIP = {
  BTN:"가장 유리한 자리! 마지막에 행동하므로 넓은 범위로 플레이 가능.",
  SB:"블라인드를 내야 하고 플랍 후 먼저 행동. 불리한 자리.",
  BB:"블라인드 투자됨. 적절한 핸드로 디펜드 가능.",
  UTG:"가장 먼저 행동. 프리미엄 핸드만 플레이!",
  "UTG+1":"여전히 얼리 포지션. 타이트하게.",
  MP:"중간 포지션. 조금 더 넓게 플레이 가능.",
  "MP+1":"미들 후반. 괜찮은 핸드 추가 가능.",
  HJ:"레이트 포지션 시작. 스틸 기회 있음.",
  CO:"버튼 바로 앞. 공격적 플레이 가능."
};

const AI_PROFILES = [
  {name:"대니얼",style:"tight-aggressive",emoji:"🧔",desc:"타이트-어그레시브",color:"#e74c3c"},
  {name:"소피아",style:"loose-aggressive",emoji:"👩‍🦰",desc:"루즈-어그레시브",color:"#9b59b6"},
  {name:"재민",style:"tight-passive",emoji:"👨‍💼",desc:"타이트-패시브",color:"#3498db"},
  {name:"린다",style:"loose-passive",emoji:"👩‍🏫",desc:"루즈-패시브",color:"#e67e22"},
  {name:"마이크",style:"maniac",emoji:"🤠",desc:"매니악(올인 머신)",color:"#e74c3c"},
  {name:"유나",style:"balanced",emoji:"👩‍💻",desc:"밸런스드",color:"#1abc9c"},
  {name:"빅터",style:"nit",emoji:"🧓",desc:"극타이트(닛)",color:"#7f8c8d"},
  {name:"하나",style:"tricky",emoji:"👩‍🎤",desc:"트리키(블러프 多)",color:"#f39c12"},
];

const BLIND_SCHEDULE = [
  {sb:10,bb:20,ante:0,dur:15},{sb:15,bb:30,ante:0,dur:15},
  {sb:25,bb:50,ante:5,dur:15},{sb:50,bb:100,ante:10,dur:15},
  {sb:75,bb:150,ante:15,dur:12},{sb:100,bb:200,ante:25,dur:12},
  {sb:150,bb:300,ante:25,dur:12},{sb:200,bb:400,ante:50,dur:10},
  {sb:300,bb:600,ante:75,dur:10},{sb:400,bb:800,ante:100,dur:10},
  {sb:500,bb:1000,ante:100,dur:10},{sb:600,bb:1200,ante:200,dur:8},
  {sb:800,bb:1600,ante:200,dur:8},{sb:1000,bb:2000,ante:300,dur:8},
  {sb:1500,bb:3000,ante:400,dur:8},{sb:2000,bb:4000,ante:500,dur:8},
];

function createDeck(){const d=[];for(const s of SUITS)for(const r of RANKS)d.push({rank:r,suit:s});return d;}
function shuffle(d){const a=[...d];for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}

// ═══════════════════════════════════════════════════════════════
// HAND EVALUATION
// ═══════════════════════════════════════════════════════════════
function getCombos(a,k){if(k===0)return[[]];if(a.length<k)return[];const[f,...r]=a;return[...getCombos(r,k-1).map(c=>[f,...c]),...getCombos(r,k)];}
function eval5(cards){
  const v=cards.map(c=>RV[c.rank]).sort((a,b)=>b-a);
  const ss=cards.map(c=>c.suit);const fl=ss.every(s=>s===ss[0]);
  let str=false,sh=0;const uv=[...new Set(v)].sort((a,b)=>b-a);
  if(uv.length===5){if(uv[0]-uv[4]===4){str=true;sh=uv[0];}if(uv[0]===14&&uv[1]===5){str=true;sh=5;}}
  const ct={};v.forEach(x=>{ct[x]=(ct[x]||0)+1;});
  const g=Object.entries(ct).map(([val,cnt])=>({v:+val,c:cnt})).sort((a,b)=>b.c-a.c||b.v-a.v);
  if(fl&&str&&sh===14)return{rank:10,name:"로열 플러시",score:10e8};
  if(fl&&str)return{rank:9,name:"스트레이트 플러시",score:9e8+sh};
  if(g[0].c===4)return{rank:8,name:"포카드",score:8e8+g[0].v*100+g[1].v};
  if(g[0].c===3&&g[1].c===2)return{rank:7,name:"풀하우스",score:7e8+g[0].v*100+g[1].v};
  if(fl)return{rank:6,name:"플러시",score:6e8+v[0]*1e4+v[1]*1e3+v[2]*100+v[3]*10+v[4]};
  if(str)return{rank:5,name:"스트레이트",score:5e8+sh};
  if(g[0].c===3)return{rank:4,name:"트리플",score:4e8+g[0].v*1e4+g[1].v*100+(g[2]?g[2].v:0)};
  if(g[0].c===2&&g[1].c===2)return{rank:3,name:"투페어",score:3e8+Math.max(g[0].v,g[1].v)*1e4+Math.min(g[0].v,g[1].v)*100+(g[2]?g[2].v:0)};
  if(g[0].c===2)return{rank:2,name:"원페어",score:2e8+g[0].v*1e6+g[1].v*1e4+g[2].v*100+(g[3]?g[3].v:0)};
  return{rank:1,name:"하이카드",score:1e8+v[0]*1e6+v[1]*1e4+v[2]*100+v[3]*10+v[4]};
}
function evalHand(cards){
  if(cards.length<5)return{rank:0,name:"-",score:0,best:cards};
  let best=null;for(const c of getCombos(cards,5)){const e=eval5(c);if(!best||e.score>best.score)best={...e,best:c};}return best;
}

// ═══════════════════════════════════════════════════════════════
// AI DECISION ENGINE
// ═══════════════════════════════════════════════════════════════
function preflopStr(cards){
  const v1=RV[cards[0].rank],v2=RV[cards[1].rank];
  const p=v1===v2,s=cards[0].suit===cards[1].suit,h=Math.max(v1,v2),l=Math.min(v1,v2);
  if(p&&h>=12)return 9;if(p&&h>=10)return 8;if(p&&h>=7)return 6;if(p)return 4;
  if(h===14&&l>=12)return s?8:7;if(h===14&&l>=10)return s?6:5;if(h===14)return s?4:3;
  if(s&&h-l<=2&&h>=9)return 5;if(h>=12&&l>=10)return s?5:4;
  return l>=9?3:h>=10?2:1;
}
function aiAct(cards,comm,pot,toCall,chips,style,blindLvl,activePlayers){
  const all=[...cards,...comm];
  const hs=all.length>=5?evalHand(all).rank:preflopStr(cards);
  const r=Math.random();const m=chips/blindLvl.bb;
  const styleAdj={
    "tight-aggressive":{foldTh:3,raiseBonus:0.2,bluff:0.1},
    "loose-aggressive":{foldTh:1,raiseBonus:0.3,bluff:0.25},
    "tight-passive":{foldTh:4,raiseBonus:-0.1,bluff:0.05},
    "loose-passive":{foldTh:2,raiseBonus:-0.2,bluff:0.15},
    "maniac":{foldTh:1,raiseBonus:0.4,bluff:0.35},
    "balanced":{foldTh:2,raiseBonus:0.1,bluff:0.15},
    "nit":{foldTh:5,raiseBonus:0,bluff:0.03},
    "tricky":{foldTh:2,raiseBonus:0.15,bluff:0.3},
  }[style]||{foldTh:2,raiseBonus:0.1,bluff:0.15};

  // Short stack push/fold
  if(m<=8&&toCall>0){
    if(hs>=5||(hs>=3&&r<0.4))return{action:"allin"};
    return{action:"fold"};
  }
  if(m<=8&&hs>=4)return{action:"allin"};

  if(hs>=8){
    const amt=Math.floor(Math.min(Math.max(pot,toCall*3),chips));
    return toCall>0?{action:"raise",amount:amt}:{action:"raise",amount:Math.floor(Math.min(pot*0.8,chips))};
  }
  if(hs>=6){
    if(toCall>0)return r>0.3?{action:"raise",amount:Math.floor(Math.min(toCall*2.5,chips))}:{action:"call"};
    return{action:"raise",amount:Math.floor(Math.min(blindLvl.bb*3,chips))};
  }
  if(hs>=styleAdj.foldTh+1){
    if(toCall>chips*0.3)return{action:"fold"};
    if(toCall>0)return r>(0.4-styleAdj.raiseBonus)?{action:"call"}:{action:"raise",amount:Math.floor(Math.min(toCall*2,chips))};
    return r>(0.5-styleAdj.raiseBonus)?{action:"raise",amount:Math.floor(Math.min(blindLvl.bb*(2+r*2),chips))}:{action:"check"};
  }
  if(hs>=styleAdj.foldTh){
    if(toCall>chips*0.15)return{action:"fold"};
    if(toCall>0)return r>0.5?{action:"call"}:{action:"fold"};
    return r<styleAdj.bluff?{action:"raise",amount:Math.floor(Math.min(blindLvl.bb*2.5,chips))}:{action:"check"};
  }
  // Weak hand - bluff or fold
  if(toCall>0)return r<styleAdj.bluff*0.5?{action:"call"}:{action:"fold"};
  return r<styleAdj.bluff?{action:"raise",amount:Math.floor(Math.min(blindLvl.bb*2,chips))}:{action:"check"};
}

// ═══════════════════════════════════════════════════════════════
// EQUITY / WIN PROBABILITY ESTIMATOR
// ═══════════════════════════════════════════════════════════════
function estimateEquity(cards,comm,numOpponents){
  if(!cards||cards.length<2)return 50;
  const hs=comm.length>=3?evalHand([...cards,...comm]).rank:0;
  const ps=preflopStr(cards);
  // Preflop equity approximation based on hand strength vs number of opponents
  const preflopEq={9:85,8:78,7:70,6:62,5:55,4:48,3:40,2:32,1:22};
  let baseEq=preflopEq[ps]||30;
  // Adjust for number of opponents
  if(numOpponents>1)baseEq=Math.max(10,baseEq-((numOpponents-1)*4));
  // Postflop adjustment
  if(comm.length>=3){
    const postEq={10:99,9:97,8:94,7:85,6:78,5:70,4:58,3:45,2:35,1:20};
    baseEq=postEq[hs]||baseEq;
    if(numOpponents>1)baseEq=Math.max(8,baseEq-((numOpponents-1)*3));
  }
  return Math.min(99,Math.max(5,Math.round(baseEq)));
}

function getRecommendation(equity,potOdds,m,pos,toCall,pot,chips){
  // Push/fold mode
  if(m<=8){
    if(equity>=40)return{action:"올인",color:"#ef4444",reason:`숏스택(${Math.round(m)}BB) — 좋은 핸드면 올인으로 승부`};
    return{action:"폴드",color:"#666666",reason:`숏스택이지만 승률 ${equity}%로 부족. 더 좋은 기회를 기다리세요`};
  }
  // Has to call
  if(toCall>0){
    const potOddsPct=Math.round(toCall/(pot+toCall)*100);
    if(equity>=65)return{action:"레이즈",color:"#e8b730",reason:`승률 ${equity}% > 필요 ${potOddsPct}%. 강한 핸드로 밸류 레이즈!`};
    if(equity>=potOddsPct+5)return{action:"콜",color:"#22c55e",reason:`승률 ${equity}% > 팟오즈 ${potOddsPct}%. 콜할 가치 있음`};
    if(equity>=potOddsPct-5)return{action:"콜/폴드",color:"#f59e0b",reason:`승률 ${equity}% ≈ 팟오즈 ${potOddsPct}%. 경계선 — 상대 성향에 따라 판단`};
    return{action:"폴드",color:"#666666",reason:`승률 ${equity}% < 팟오즈 ${potOddsPct}%. 콜 비용 대비 이득 부족`};
  }
  // No bet to call (can check or bet)
  if(equity>=65)return{action:"베팅",color:"#e8b730",reason:`승률 ${equity}%로 강함. 밸류벳으로 팟을 키우세요`};
  if(equity>=40)return{action:"체크",color:"#5dade2",reason:`승률 ${equity}%. 무리하지 말고 체크 후 상황 관찰`};
  return{action:"체크/폴드",color:"#888888",reason:`승률 ${equity}%로 약함. 체크하고 상대 베팅 시 폴드 고려`};
}

// ═══════════════════════════════════════════════════════════════
// COACHING SYSTEM (with specific percentages & recommendations)
// ═══════════════════════════════════════════════════════════════
function getCoach(pCards,comm,stage,pot,chips,pos,blindLvl,remaining,paidSlots,activeCnt,toCall){
  const m=chips/blindLvl.bb;
  const posName=POSITION_NAMES[pos]||"?";
  const equity=estimateEquity(pCards,comm,Math.max(1,activeCnt-1));
  const potOddsPct=toCall>0?Math.round(toCall/(pot+toCall)*100):0;
  const rec=getRecommendation(equity,potOddsPct,m,pos,toCall||0,pot,chips);

  // Hand description
  let handDesc="";
  if(pCards.length===2){
    const v1=RV[pCards[0].rank],v2=RV[pCards[1].rank];
    const paired=v1===v2,suited=pCards[0].suit===pCards[1].suit;
    const high=Math.max(v1,v2);
    if(paired)handDesc=`포켓 페어 (${pCards[0].rank}${pCards[0].rank})`;
    else if(high===14)handDesc=`에이스 핸드 (A+${Math.min(v1,v2)>=10?"페이스카드":"로우"})`;
    else if(suited)handDesc="수티드 (같은 무늬)";
    else handDesc="오프수트 (다른 무늬)";
  }
  let madeHand="";
  if(comm.length>=3){
    const ev=evalHand([...pCards,...comm]);
    madeHand=ev.name||"";
  }

  // Situation flag
  let situation="normal";
  if(remaining<=paidSlots*1.2&&remaining>paidSlots)situation="bubble";
  else if(remaining<=paidSlots)situation="itm";

  return{
    posName,
    posFullName:POS_FULL[posName]||posName,
    posTip:POS_TIP[posName]||"",
    posIndex:pos, // 0=BTN(best)..8=CO
    equity,
    potOddsPct,
    rec,
    handDesc,
    madeHand,
    m:Math.round(m),
    toCall:toCall||0,
    pot,
    chips,
    situation,
    remaining,
    paidSlots,
    activeCnt,
    bb:blindLvl.bb,
  };
}

// ═══════════════════════════════════════════════════════════════
// FOLD REASON ANALYZER
// ═══════════════════════════════════════════════════════════════
function getFoldReason(cards,comm,toCall,chips,style,pos,blindBB){
  const hs=comm.length>=3?evalHand([...cards,...comm]).rank:preflopStr(cards);
  const m=chips/blindBB;
  const reasons=[];
  // Hand weakness
  if(hs<=1)reasons.push("매우 약한 핸드 (하이카드 이하)");
  else if(hs<=2)reasons.push("약한 핸드 (로우 페어/하이카드)");
  else if(hs<=3)reasons.push("보통 핸드지만 상대 베팅 대비 약함");
  // Position
  if(pos<=3)reasons.push("얼리 포지션이라 리스크가 큼");
  // Bet sizing
  if(toCall>0){
    const potOdds=toCall/(toCall+chips*0.1);
    if(toCall>chips*0.2)reasons.push(`콜 비용(${toCall})이 스택의 ${Math.round(toCall/chips*100)}% — 너무 비쌈`);
    else if(toCall>blindBB*5)reasons.push(`큰 베팅(${toCall})에 약한 핸드로 콜하면 손해`);
  }
  // Style
  const styleDesc={"tight-aggressive":"타이트한 플레이어라 약한 핸드는 바로 폴드",
    "tight-passive":"보수적 스타일 — 확실한 핸드만 플레이",
    "nit":"극도로 타이트 — 프리미엄 핸드 외 전부 폴드",
    "balanced":"밸런스 플레이 — 이 상황에서 폴드가 +EV",
    "loose-aggressive":"보통 넓게 플레이하지만 이 핸드는 너무 약함",
    "loose-passive":"루즈하지만 베팅 압박에 약해서 폴드",
    "tricky":"트리키 플레이어지만 이번엔 블러프 포기",
    "maniac":"매니악도 포기할 정도로 상황이 안 좋음"}[style]||"";
  if(styleDesc)reasons.push(styleDesc);
  return reasons.slice(0,2).join(". ")+"."||"약한 핸드로 판단하여 폴드.";
}

// ═══════════════════════════════════════════════════════════════
// CONTEXTUAL TERMINOLOGY
// ═══════════════════════════════════════════════════════════════
const TERMS={
  "fold":{en:"Fold",kr:"폴드",desc:"카드를 버리고 핸드를 포기. 이미 넣은 칩은 돌려받지 못합니다."},
  "check":{en:"Check",kr:"체크",desc:"베팅 없이 다음 사람에게 넘김. 아무도 베팅하지 않았을 때만 가능."},
  "call":{en:"Call",kr:"콜",desc:"앞 사람의 베팅과 같은 금액을 내고 계속 참여."},
  "raise":{en:"Raise",kr:"레이즈",desc:"앞 사람의 베팅보다 더 올려서 베팅. 상대에게 압박을 줌."},
  "allin":{en:"All-in",kr:"올인",desc:"보유한 모든 칩을 걸기. 더 이상 베팅 결정이 없음."},
  "blind":{en:"Blind",kr:"블라인드",desc:"카드를 받기 전에 의무적으로 내는 베팅. SB(스몰)와 BB(빅)가 있음."},
  "ante":{en:"Ante",kr:"앤티",desc:"모든 플레이어가 핸드 시작 전에 내는 소액 의무 베팅."},
  "pot":{en:"Pot",kr:"팟",desc:"현재 핸드에서 모든 플레이어가 베팅한 칩의 총합."},
  "flop":{en:"Flop",kr:"플랍",desc:"커뮤니티 카드 3장이 동시에 공개되는 두 번째 베팅 라운드."},
  "turn":{en:"Turn",kr:"턴",desc:"4번째 커뮤니티 카드가 공개되는 세 번째 베팅 라운드."},
  "river":{en:"River",kr:"리버",desc:"5번째(마지막) 커뮤니티 카드가 공개. 최종 베팅 라운드."},
  "btn":{en:"Button (BTN)",kr:"버튼/딜러",desc:"딜러 포지션. 포스트플랍에서 마지막에 행동하여 가장 유리. 넓은 범위로 플레이 가능."},
  "SB":{en:"Small Blind",kr:"스몰 블라인드",desc:"딜러 왼쪽. BB의 절반을 의무 베팅. 플랍 이후 먼저 행동해야 해서 불리."},
  "BB":{en:"Big Blind",kr:"빅 블라인드",desc:"SB 왼쪽. 테이블 최소 베팅액을 의무 베팅. 프리플랍에서 마지막에 행동."},
  "utg":{en:"Under the Gun",kr:"언더더건",desc:"BB 바로 왼쪽. 프리플랍에서 가장 먼저 행동. 정보 없이 결정해야 해서 가장 불리."},
  "UTG+1":{en:"UTG+1",kr:"언더더건+1",desc:"UTG 바로 왼쪽. 여전히 얼리 포지션으로 프리미엄 핸드만 플레이 권장."},
  "MP":{en:"Middle Position",kr:"미들 포지션",desc:"테이블 중간. 앞에 몇 명이 행동을 봤으므로 약간 더 넓게 플레이 가능."},
  "MP+1":{en:"MP+1",kr:"미들 포지션+1",desc:"미들 후반. 레이트 포지션에 가까워 괜찮은 핸드 추가 가능."},
  "HJ":{en:"Hijack",kr:"하이잭",desc:"CO 바로 앞. 레이트 포지션의 시작. 스틸 시도 가능한 자리."},
  "co":{en:"Cutoff (CO)",kr:"컷오프",desc:"버튼 바로 앞. 버튼이 폴드하면 사실상 가장 유리한 자리. 공격적 플레이 가능."},
  "bubble":{en:"Bubble",kr:"버블",desc:"입상권 직전 상태. 1명만 더 탈락하면 남은 모두 상금 수령."},
  "shortstack":{en:"Short Stack",kr:"숏스택",desc:"칩이 적은 상태 (보통 10BB 이하). 푸시/폴드 전략 필요."},
  "potodds":{en:"Pot Odds",kr:"팟오즈",desc:"콜 비용 대비 팟 크기의 비율. 승률이 팟오즈보다 높으면 콜이 이익 (+EV)."},
  "steal":{en:"Steal",kr:"스틸",desc:"레이트 포지션에서 약한 핸드로 레이즈하여 블라인드를 훔치는 전략."},
  "cbet":{en:"Continuation Bet",kr:"씨벳",desc:"프리플랍 레이저가 플랍에서도 이어서 베팅하는 것."},
  "ev":{en:"Expected Value",kr:"기대값(EV)",desc:"+EV는 장기적으로 이익인 플레이, -EV는 손해. 항상 +EV를 선택하세요."},
  "valuebet":{en:"Value Bet",kr:"밸류벳",desc:"상대가 더 약한 핸드로 콜해줄 것을 기대하고 하는 베팅. 강한 핸드일 때 사용."},
  "underdog":{en:"Underdog",kr:"언더독",desc:"승률이 50% 미만인 약자. 반대는 페이버릿(favorite, 유리한 쪽)."},
  "equity":{en:"Equity",kr:"에퀴티/승률",desc:"현재 핸드가 최종적으로 이길 확률(%). 높을수록 유리."},
};

function getTermForAction(action,stage,pos){
  if(action.includes("폴드"))return TERMS.fold;
  if(action.includes("체크"))return TERMS.check;
  if(action.includes("콜"))return TERMS.call;
  if(action.includes("레이즈"))return TERMS.raise;
  if(action.includes("올인"))return TERMS.allin;
  if(stage==="flop")return TERMS.flop;
  if(stage==="turn")return TERMS.turn;
  if(stage==="river")return TERMS.river;
  return null;
}
// ═══════════════════════════════════════════════════════════════
// TOOLTIP COMPONENT (hover to see term explanation)
// ═══════════════════════════════════════════════════════════════
function Tip({term,children,style:s}){
  const [show,setShow]=useState(false);
  const t=TERMS[term];
  if(!t)return <span style={s}>{children}</span>;
  return(
    <span style={{position:"relative",display:"inline",...s}} onMouseEnter={()=>setShow(true)} onMouseLeave={()=>setShow(false)} onClick={()=>setShow(!show)}>
      <span style={{borderBottom:"1px dotted rgba(93,173,226,0.5)",cursor:"help"}}>{children}</span>
      {show&&(
        <div style={{position:"absolute",top:"50%",left:"calc(100% + 8px)",transform:"translateY(-50%)",background:"rgba(10,20,40,0.95)",border:"1px solid #5dade2",borderRadius:8,padding:"8px 12px",minWidth:180,maxWidth:250,zIndex:100,boxShadow:"0 4px 16px rgba(0,0,0,0.6)",pointerEvents:"none"}}>
          <div style={{color:"#5dade2",fontSize:11,fontWeight:700,marginBottom:3}}>{t.kr} ({t.en})</div>
          <div style={{color:"#ccd6e0",fontSize:10,lineHeight:1.4}}>{t.desc}</div>
          <div style={{position:"absolute",top:"50%",left:-5,transform:"translateY(-50%) rotate(45deg)",width:10,height:10,background:"rgba(10,20,40,0.95)",borderLeft:"1px solid #5dade2",borderBottom:"1px solid #5dade2"}}/>
        </div>
      )}
    </span>
  );
}

// ═══════════════════════════════════════════════════════════════
// CARD COMPONENT (Rich poker-style)
// ═══════════════════════════════════════════════════════════════
function PokerCard({card,faceDown,highlight,tiny,winner}){
  const w=tiny?36:58,h=tiny?50:80;
  if(faceDown)return(
    <div style={{width:w,height:h,borderRadius:7,background:"linear-gradient(145deg,#1a3a6a,#0c2040)",border:"2px solid #3060a0",display:"flex",alignItems:"center",justifyContent:"center",flexShrink:0,boxShadow:"0 3px 10px rgba(0,0,0,0.6),inset 0 1px 0 rgba(255,255,255,0.1)"}}>
      <div style={{width:w*0.5,height:h*0.6,borderRadius:3,background:"radial-gradient(circle,#2a5a9a,#1a3a6a)",border:"1px solid #3a6aaa",display:"flex",alignItems:"center",justifyContent:"center"}}>
        <div style={{fontSize:tiny?10:16,opacity:0.4}}>♠</div>
      </div>
    </div>
  );
  const color=SC[card.suit];
  const sz=tiny?16:24;
  return(
    <div style={{width:w,height:h,borderRadius:7,background:winner?"linear-gradient(145deg,#fff8e1,#ffecb3)":highlight?"linear-gradient(145deg,#fffde7,#fff9c4)":"linear-gradient(145deg,#fff,#f5f5f5)",border:winner?"2px solid #ffa000":highlight?"2px solid #f59e0b":"2px solid #bbb",display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",gap:tiny?1:2,flexShrink:0,boxShadow:winner?"0 0 16px rgba(255,160,0,0.6),0 3px 8px rgba(0,0,0,0.3)":highlight?"0 0 10px rgba(245,158,11,0.4)":"0 2px 6px rgba(0,0,0,0.2)"}}>
      <div style={{fontSize:tiny?14:20,fontWeight:800,color,lineHeight:1,marginTop:tiny?-1:-2}}>{card.rank}</div>
      <SuitIcon suit={card.suit} size={sz} color={color}/>
    </div>
  );
}

// SVG suit icons - all exactly the same visual size
function SuitIcon({suit,size,color}){
  const s=size||24;
  if(suit==="♥")return(
    <svg width={s} height={s} viewBox="0 0 100 100"><path d="M50 88 C25 65,0 45,0 28 A25 25 0 0 1 50 20 A25 25 0 0 1 100 28 C100 45,75 65,50 88Z" fill={color}/></svg>
  );
  if(suit==="♦")return(
    <svg width={Math.round(s*1.15)} height={Math.round(s*1.15)} viewBox="0 0 100 100"><path d="M50 2 Q78 30,96 50 Q78 70,50 98 Q22 70,4 50 Q22 30,50 2Z" fill={color}/></svg>
  );
  if(suit==="♣")return(
    <svg width={s} height={s} viewBox="0 0 100 100"><circle cx="50" cy="30" r="22" fill={color}/><circle cx="28" cy="58" r="22" fill={color}/><circle cx="72" cy="58" r="22" fill={color}/><rect x="45" y="55" width="10" height="30" fill={color}/></svg>
  );
  // ♠
  return(
    <svg width={s} height={s} viewBox="0 0 100 100"><path d="M50 5 C50 5,0 45,0 62 A25 25 0 0 0 42 80 L38 95 62 95 58 80 A25 25 0 0 0 100 62 C100 45,50 5,50 5Z" fill={color}/></svg>
  );
}

// Hand rank label component
function HandLabel({name,isWinner}){
  if(!name||name==="-")return null;
  const colors={
    "로열 플러시":"#ffd700","스트레이트 플러시":"#ff6b35","포카드":"#e040fb",
    "풀하우스":"#ff9800","플러시":"#29b6f6","스트레이트":"#66bb6a",
    "트리플":"#42a5f5","투페어":"#ab47bc","원페어":"#78909c","하이카드":"#607d8b"
  };
  const c=colors[name]||"#90a4ae";
  return(
    <div style={{background:`linear-gradient(135deg,${c}dd,${c}88)`,borderRadius:4,padding:"2px 8px",display:"inline-block",boxShadow:isWinner?`0 0 12px ${c}88`:"none",border:isWinner?`1px solid ${c}`:"1px solid transparent"}}>
      <span style={{color:"#fff",fontSize:10,fontWeight:800,letterSpacing:0.5,textShadow:"0 1px 2px rgba(0,0,0,0.5)"}}>{isWinner?"🏆 WINNER · ":""}{name.toUpperCase()}</span>
    </div>
  );
}

// Chip stack visual component
function ChipStack({amount,bb}){
  if(!amount||amount<=0)return null;
  const label=amount>=10000?Math.round(amount/1000)+"K":amount>=1000?Math.round(amount/1000)+"K":amount.toString();
  const chipColors=amount>=bb*20?["#e74c3c","#c0392b"]:amount>=bb*5?["#27ae60","#1e8449"]:["#2980b9","#1f6dad"];
  const count=Math.min(Math.ceil(amount/bb),6);
  return(
    <div style={{display:"flex",alignItems:"center",gap:3}}>
      <div style={{position:"relative",width:20,height:Math.min(count*5+4,34)}}>
        {Array.from({length:count}).map((_,i)=>(
          <div key={i} style={{position:"absolute",bottom:i*4,left:0,width:20,height:6,borderRadius:10,background:`linear-gradient(180deg,${chipColors[0]},${chipColors[1]})`,border:"1px solid rgba(255,255,255,0.3)",boxShadow:"0 1px 2px rgba(0,0,0,0.3)"}}/>
        ))}
      </div>
      <span style={{color:"#fff",fontSize:10,fontWeight:700,textShadow:"0 1px 3px rgba(0,0,0,0.8)",fontFamily:"'Courier New',monospace"}}>{label}</span>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// SEAT POSITIONS AROUND TABLE (elliptical layout)
// ═══════════════════════════════════════════════════════════════
function getSeatXY(idx,total){
  // Player is always at bottom center (index = playerSeatIdx)
  // Others arranged clockwise
  const angle = (Math.PI*2*idx/total) - Math.PI/2;
  const rx=46,ry=38;
  return {x:50+rx*Math.cos(angle),y:50+ry*Math.sin(angle)};
}

// ═══════════════════════════════════════════════════════════════
// AI CHAT / TABLE TALK
// ═══════════════════════════════════════════════════════════════
const CHAT_LINES={
  fold:["ㅎㅎ 접는다~","이건 패스","안되겠다 폴드","가비지 핸드 ㅋ","다음 판에 보자"],
  call:["콜~","한번 보자","따라간다","흠… 콜","수딧이냐?","오… 콜해볼게"],
  raise:["올린다!","레이즈!","좀 치자","슬슬 올려볼까","이거 괜찮은데?","자신있어?"],
  allin:["올인!!! 💥","다 걸어!","받아라!!","올인이다 ㄱㄱ","갈 때 가자!"],
  check:["체크~","넘긴다","지켜보자","패스"],
  win:["나이스~! 🎉","고마워 ㅋㅋ","이건 내 팟","잘 먹겠습니다~"],
  lose:["아… 운이 없네","다음엔 이긴다","졌다 ㅠ","괜찮아 다음 판"],
  bighand:["와 수딧 플러시?!","풀하우스 ㄷㄷ","이건 못 이기지","대박 핸드 나왔네"],
  bluff:["읽힌 건가…","블러프 들켰네 ㅋ","속일 뻔했는데"],
  react_raise:["에이 또 올리네","부담스럽다…","크게 나왔네","뭘 들고 있는 거야"],
  react_allin:["올인?! 진짜?","ㄷㄷㄷ","미쳤다 ㅋㅋ","이거 실화?"],
  greeting:["반갑습니다~","잘 부탁해요","어느 테이블에서 왔어요?"],
  eliminated:["GG","수고했습니다","다음엔 잘하겠지…"],
};
function getChat(action,style){
  const lines=CHAT_LINES[action];
  if(!lines||Math.random()>0.4)return null; // 40% chance to talk
  return lines[Math.floor(Math.random()*lines.length)];
}

// ═══════════════════════════════════════════════════════════════
// MAIN COMPONENT
// ═══════════════════════════════════════════════════════════════
export default function TournamentPoker(){
  // ─── Tournament Config ────────────────────────────────
  const [screen,setScreen]=useState("setup");
  const [config,setConfig]=useState({buyIn:400,totalPlayers:90,startChips:15000});

  // ─── Tournament State ─────────────────────────────────
  const [blindLevel,setBlindLevel]=useState(0);
  const [handsInLevel,setHandsInLevel]=useState(0);
  const [totalRemaining,setTotalRemaining]=useState(0);
  const [myRank,setMyRank]=useState(1);
  const [handNum,setHandNum]=useState(0);
  const [tourneyLog,setTourneyLog]=useState([]);
  const [myBounties,setMyBounties]=useState([]); // knocked out players
  const [chatBubbles,setChatBubbles]=useState({}); // {seatIdx: {text,time}}

  // ─── Table State ──────────────────────────────────────
  const [seats,setSeats]=useState([]); // {id,name,chips,cards,emoji,style,folded,bet,isPlayer,isOut,allIn}
  const [dealerIdx,setDealerIdx]=useState(0);
  const [community,setCommunity]=useState([]);
  const [pot,setPot]=useState(0);
  const [sidePots,setSidePots]=useState([]);
  const [stage,setStage]=useState("preflop");
  const [actIdx,setActIdx]=useState(-1);
  const [lastAction,setLastAction]=useState("");
  const [isPlayerTurn,setIsPlayerTurn]=useState(false);
  const [gameOver,setGameOver]=useState(false);
  const [showdown,setShowdown]=useState(false);
  const [raiseAmt,setRaiseAmt]=useState(0);
  const [coachTips,setCoachTips]=useState(null);
  const [showCoach,setShowCoach]=useState(true);
  const [showLobby,setShowLobby]=useState(false);
  const [showBlindSched,setShowBlindSched]=useState(false);
  const [bustMsg,setBustMsg]=useState("");
  const [handResults,setHandResults]=useState(null);
  const [tourneyOver,setTourneyOver]=useState(false);
  const [finalPlace,setFinalPlace]=useState(0);
  const [currentBetLevel,setCurrentBetLevel]=useState(0);
  const [levelTimer,setLevelTimer]=useState(0);
  const [showMonitor,setShowMonitor]=useState(false);
  const [elapsedTime,setElapsedTime]=useState(0);
  const [foldReveals,setFoldReveals]=useState([]); // {name,emoji,cards,reason,posLabel}
  const [termTip,setTermTip]=useState(null); // {term,meaning} - contextual terminology
  const deckRef=useRef([]);
  const actionTimeoutRef=useRef(null);
  const seatsRef=useRef([]);

  const bl=BLIND_SCHEDULE[Math.min(blindLevel,BLIND_SCHEDULE.length-1)];
  const nextBl=BLIND_SCHEDULE[Math.min(blindLevel+1,BLIND_SCHEDULE.length-1)];
  const paidSlots=Math.max(1,Math.floor(config.totalPlayers*0.15));

  // Sync ref
  useEffect(()=>{seatsRef.current=seats;},[seats]);

  // Blind level countdown timer
  useEffect(()=>{
    if(screen!=="game"||tourneyOver)return;
    const interval=setInterval(()=>{
      setLevelTimer(t=>{
        if(t<=1){
          setBlindLevel(lv=>{
            const newLv=Math.min(lv+1,BLIND_SCHEDULE.length-1);
            setTourneyLog(l=>[...l,`⬆️ 블라인드 레벨 ${newLv+1}: ${BLIND_SCHEDULE[newLv].sb}/${BLIND_SCHEDULE[newLv].bb}${BLIND_SCHEDULE[newLv].ante>0?` (앤티 ${BLIND_SCHEDULE[newLv].ante})`:""}`]);
            return newLv;
          });
          return BLIND_SCHEDULE[Math.min(blindLevel+1,BLIND_SCHEDULE.length-1)].dur*60;
        }
        return t-1;
      });
      setElapsedTime(t=>t+1);
      if(Math.random()<0.03){setTotalRemaining(r=>{const la=seatsRef.current.filter(x=>!x.isOut).length;return Math.max(la,r-1);});}
    },1000);
    return()=>clearInterval(interval);
  },[screen,tourneyOver,blindLevel]);

  const fmtTime=(s)=>`${Math.floor(s/60)}:${(s%60).toString().padStart(2,"0")}`;
  const fmtElapsed=(s)=>{const h=Math.floor(s/3600);const m=Math.floor((s%3600)/60);return h>0?`${h}h ${m}m`:`${m}m`;};

  // ─── Prize Structure ──────────────────────────────────
  const prizePool=config.buyIn*config.totalPlayers;
  const prizes=useMemo(()=>{
    const p=[];const ps=paidSlots;
    if(ps>=10){p.push({place:"1st",pct:25},{place:"2nd",pct:16},{place:"3rd",pct:11},{place:"4~6th",pct:7},{place:"7~10th",pct:4});
      const rem=100-25-16-11-7*3-4*4;if(ps>10)p.push({place:`11~${ps}th`,pct:Math.max(1,rem/(ps-10))});
    }else{p.push({place:"1st",pct:50},{place:"2nd",pct:30},{place:"3rd",pct:20});}
    return p;
  },[paidSlots]);

  // ─── INITIALIZE TOURNAMENT ────────────────────────────
  const startTournament=useCallback(()=>{
    const tableSize=9;
    const profiles=shuffle([...AI_PROFILES,...AI_PROFILES,...AI_PROFILES]).slice(0,tableSize-1);
    const newSeats=profiles.map((p,i)=>({
      id:i+1,name:p.name,chips:config.startChips,cards:[],emoji:p.emoji,style:p.style,desc:p.desc,color:p.color||"#888",
      folded:false,bet:0,isPlayer:false,isOut:false,allIn:false,showCards:false
    }));
    const playerSeat={id:0,name:"나",chips:config.startChips,cards:[],emoji:"😎",style:"player",desc:"플레이어",color:"#2196f3",
      folded:false,bet:0,isPlayer:true,isOut:false,allIn:false,showCards:true};
    // Insert player at seat index 4 (bottom-center when rendered)
    newSeats.splice(4,0,playerSeat);
    setSeats(newSeats);
    setTotalRemaining(config.totalPlayers);
    setBlindLevel(0);setHandNum(0);setHandsInLevel(0);
    setDealerIdx(0);setTourneyOver(false);setFinalPlace(0);
    setBustMsg("");setTourneyLog([]);setMyBounties([]);setChatBubbles({});
    setLevelTimer(BLIND_SCHEDULE[0].dur*60);setElapsedTime(0);setShowMonitor(false);
    setScreen("game");
    setTimeout(()=>dealHand(newSeats,0,0),500);
  },[config]);

  // ─── DEAL HAND ────────────────────────────────────────
  const dealHand=useCallback((currentSeats,dlrIdx,blLvl)=>{
    const s=currentSeats||seatsRef.current;
    const active=s.filter(x=>!x.isOut);
    if(active.length<=1){endTourney(active[0]?.isPlayer?1:totalRemaining);return;}

    const deck=shuffle(createDeck());
    let di=0;
    const newSeats=s.map(seat=>{
      if(seat.isOut)return{...seat,cards:[],folded:true,bet:0,allIn:false,showCards:false};
      const cards=[deck[di],deck[di+1]];di+=2;
      return{...seat,cards,folded:false,bet:0,allIn:false,showCards:seat.isPlayer};
    });
    deckRef.current=deck.slice(di);

    const bLevel=BLIND_SCHEDULE[Math.min(blLvl,BLIND_SCHEDULE.length-1)];
    // Post blinds & antes
    let pot=0;
    const liveIdxs=newSeats.map((s,i)=>s.isOut?-1:i).filter(i=>i>=0);
    const sbIdx=liveIdxs[(liveIdxs.indexOf(dlrIdx)+1)%liveIdxs.length];
    const bbIdx=liveIdxs[(liveIdxs.indexOf(dlrIdx)+2)%liveIdxs.length];

    // Antes
    if(bLevel.ante>0){
      newSeats.forEach((s,i)=>{
        if(!s.isOut){const a=Math.min(bLevel.ante,s.chips);newSeats[i]={...s,chips:s.chips-a};pot+=a;}
      });
    }
    // SB
    const sbAmt=Math.min(bLevel.sb,newSeats[sbIdx].chips);
    newSeats[sbIdx]={...newSeats[sbIdx],chips:newSeats[sbIdx].chips-sbAmt,bet:sbAmt};pot+=sbAmt;
    // BB
    const bbAmt=Math.min(bLevel.bb,newSeats[bbIdx].chips);
    newSeats[bbIdx]={...newSeats[bbIdx],chips:newSeats[bbIdx].chips-bbAmt,bet:bbAmt};pot+=bbAmt;

    // First to act preflop = UTG (after BB)
    const utgIdx=liveIdxs[(liveIdxs.indexOf(bbIdx)+1)%liveIdxs.length];

    setSeats(newSeats);setCommunity([]);setPot(pot);setStage("preflop");
    setCurrentBetLevel(bLevel.bb);setShowdown(false);setGameOver(false);
    setHandResults(null);setBustMsg("");setFoldReveals([]);setTermTip(null);setChatBubbles({});
    setHandNum(h=>h+1);setHandsInLevel(h=>h+1);
    setDealerIdx(dlrIdx);

    // Coaching
    const playerSeat=newSeats.find(s=>s.isPlayer);
    if(playerSeat&&!playerSeat.isOut){
      const posOffset=liveIdxs.indexOf(newSeats.indexOf(playerSeat));
      const dlrOffset=liveIdxs.indexOf(dlrIdx);
      const relPos=(posOffset-dlrOffset+liveIdxs.length)%liveIdxs.length;
      const tips=getCoach(playerSeat.cards,[],"preflop",pot,playerSeat.chips,relPos,bLevel,totalRemaining,paidSlots,liveIdxs.length,0);
      setCoachTips(tips);
    }

    // Start action
    setTimeout(()=>processAction(newSeats,utgIdx,pot,bLevel.bb,"preflop",[],dlrIdx,blLvl),800);
  },[totalRemaining,paidSlots]);

  // ─── ACTION LOOP ──────────────────────────────────────
  const processAction=(curSeats,seatIdx,curPot,curBetLvl,curStage,curComm,dlrIdx,blLvl)=>{
    const s=[...curSeats];
    const live=s.map((x,i)=>(!x.isOut&&!x.folded&&!x.allIn)?i:-1).filter(i=>i>=0);
    if(live.length<=1){
      // Check if only one non-folded player or all but one are all-in
      const notFolded=s.filter(x=>!x.isOut&&!x.folded);
      if(notFolded.length<=1){resolveHand(s,curPot,curComm,dlrIdx,blLvl);return;}
      // If others are all-in, run out board
      if(live.length<=1){runOutBoard(s,curPot,curComm,dlrIdx,blLvl);return;}
    }

    const seat=s[seatIdx];
    if(!seat||seat.isOut||seat.folded||seat.allIn){
      const nextIdx=findNextActor(s,seatIdx);
      if(nextIdx===null||checkRoundComplete(s,curBetLvl)){
        advanceStage(s,curPot,curBetLvl,curStage,curComm,dlrIdx,blLvl);return;
      }
      processAction(s,nextIdx,curPot,curBetLvl,curStage,curComm,dlrIdx,blLvl);return;
    }

    if(seat.isPlayer){
      setSeats(s);setPot(curPot);setCurrentBetLevel(curBetLvl);setActIdx(seatIdx);
      setIsPlayerTurn(true);
      const bLevel=BLIND_SCHEDULE[Math.min(blLvl,BLIND_SCHEDULE.length-1)];
      setRaiseAmt(Math.min(Math.max(curBetLvl*2,bLevel.bb*2),seat.chips));
      // Update coaching
      const liveIdxs=s.map((x,i)=>x.isOut?-1:i).filter(i=>i>=0);
      const posOff=liveIdxs.indexOf(seatIdx);
      const dlrOff=liveIdxs.indexOf(dlrIdx);
      const relPos=(posOff-dlrOff+liveIdxs.length)%liveIdxs.length;
      const playerToCall=Math.max(0,curBetLvl-seat.bet);
      const tips=getCoach(seat.cards,curComm,curStage,curPot,seat.chips,relPos,bLevel,totalRemaining,paidSlots,liveIdxs.length,playerToCall);
      setCoachTips(tips);
      return;
    }

    // AI action
    setActIdx(seatIdx);setIsPlayerTurn(false);
    const toCall=Math.max(0,curBetLvl-seat.bet);
    const bLevel=BLIND_SCHEDULE[Math.min(blLvl,BLIND_SCHEDULE.length-1)];
    const dec=aiAct(seat.cards,curComm,curPot,toCall,seat.chips,seat.style,bLevel,live.length);
    let newBetLvl=curBetLvl,newPot=curPot;

    if(dec.action==="fold"){
      s[seatIdx]={...s[seatIdx],folded:true,showCards:true};
      const liveIdxs3=s.map((x,j)=>x.isOut?-1:j).filter(j=>j>=0);
      const dlrOff3=liveIdxs3.indexOf(dlrIdx);const sOff3=liveIdxs3.indexOf(seatIdx);
      const relP3=(sOff3-dlrOff3+liveIdxs3.length)%liveIdxs3.length;
      const reason=getFoldReason(seat.cards,curComm,toCall,seat.chips,seat.style,relP3,bLevel.bb);
      setFoldReveals(prev=>[...prev,{name:seat.name,emoji:seat.emoji,cards:[...seat.cards],reason,posLabel:POSITION_NAMES[relP3]||"?"}]);
      setLastAction(`${seat.emoji} ${seat.name}: 폴드`);
      setTermTip(TERMS.fold);
      const chat=getChat("fold",seat.style);
      if(chat)setChatBubbles(prev=>({...prev,[seatIdx]:{text:chat,time:Date.now()}}));
    }else if(dec.action==="check"){
      setLastAction(`${seat.emoji} ${seat.name}: 체크`);
      setTermTip(TERMS.check);
      const chat=getChat("check",seat.style);
      if(chat)setChatBubbles(prev=>({...prev,[seatIdx]:{text:chat,time:Date.now()}}));
    }else if(dec.action==="call"){
      const cost=Math.min(toCall,seat.chips);
      s[seatIdx]={...s[seatIdx],chips:seat.chips-cost,bet:seat.bet+cost,allIn:seat.chips-cost<=0};
      newPot+=cost;
      setLastAction(`${seat.emoji} ${seat.name}: 콜 (${cost})`);
      setTermTip(TERMS.call);
      const chat=getChat("call",seat.style);
      if(chat)setChatBubbles(prev=>({...prev,[seatIdx]:{text:chat,time:Date.now()}}));
    }else if(dec.action==="raise"){
      const amt=Math.floor(Math.min(dec.amount||curBetLvl*2,seat.chips));
      const totalCost=Math.floor(Math.min(toCall+amt,seat.chips));
      s[seatIdx]={...s[seatIdx],chips:seat.chips-totalCost,bet:seat.bet+totalCost,allIn:seat.chips-totalCost<=0};
      newBetLvl=s[seatIdx].bet;newPot+=totalCost;
      setLastAction(`${seat.emoji} ${seat.name}: 레이즈 → ${newBetLvl}`);
      setTermTip(TERMS.raise);
      const chat=getChat("raise",seat.style);
      if(chat)setChatBubbles(prev=>({...prev,[seatIdx]:{text:chat,time:Date.now()}}));
      // Other players react to raise
      s.forEach((other,oi)=>{if(!other.isOut&&!other.folded&&oi!==seatIdx&&Math.random()<0.2){const rc=getChat("react_raise");if(rc)setChatBubbles(prev=>({...prev,[oi]:{text:rc,time:Date.now()+200}}));}});
    }else if(dec.action==="allin"){
      const cost=seat.chips;
      s[seatIdx]={...s[seatIdx],chips:0,bet:seat.bet+cost,allIn:true};
      if(s[seatIdx].bet>newBetLvl)newBetLvl=s[seatIdx].bet;
      newPot+=cost;
      setLastAction(`${seat.emoji} ${seat.name}: 올인! (${cost})`);
      setTermTip(TERMS.allin);
      const chat=getChat("allin",seat.style);
      if(chat)setChatBubbles(prev=>({...prev,[seatIdx]:{text:chat,time:Date.now()}}));
      // Others react to allin
      s.forEach((other,oi)=>{if(!other.isOut&&!other.folded&&oi!==seatIdx&&Math.random()<0.35){const rc=getChat("react_allin");if(rc)setChatBubbles(prev=>({...prev,[oi]:{text:rc,time:Date.now()+300}}));}});
    }

    setSeats([...s]);setPot(newPot);setCurrentBetLevel(newBetLvl);

    const nextIdx=findNextActor(s,seatIdx);
    actionTimeoutRef.current=setTimeout(()=>{
      if(nextIdx===null||checkRoundComplete(s,newBetLvl)){
        advanceStage(s,newPot,newBetLvl,curStage,curComm,dlrIdx,blLvl);
      }else{
        processAction(s,nextIdx,newPot,newBetLvl,curStage,curComm,dlrIdx,blLvl);
      }
    },600);
  };

  const findNextActor=(s,fromIdx)=>{
    const total=s.length;
    for(let i=1;i<total;i++){
      const idx=(fromIdx+i)%total;
      if(!s[idx].isOut&&!s[idx].folded&&!s[idx].allIn)return idx;
    }
    return null;
  };

  const checkRoundComplete=(s,betLvl)=>{
    const active=s.filter(x=>!x.isOut&&!x.folded&&!x.allIn);
    return active.every(x=>x.bet===betLvl);
  };

  // ─── ADVANCE STAGE ────────────────────────────────────
  const advanceStage=(s,curPot,betLvl,curStage,curComm,dlrIdx,blLvl)=>{
    // Reset bets
    const newSeats=s.map(x=>({...x,bet:0}));
    const stages=["preflop","flop","turn","river"];
    const si=stages.indexOf(curStage);

    const notFolded=newSeats.filter(x=>!x.isOut&&!x.folded);
    if(notFolded.length<=1){resolveHand(newSeats,curPot,curComm,dlrIdx,blLvl);return;}
    // If only all-in players remain (no one left to act)
    const canAct=notFolded.filter(x=>!x.allIn);
    if(canAct.length<=1&&si<3){runOutBoard(newSeats,curPot,curComm,dlrIdx,blLvl);return;}

    if(si>=3){resolveHand(newSeats,curPot,curComm,dlrIdx,blLvl);return;}

    let newComm=[...curComm];const d=[...deckRef.current];
    if(si===0){newComm=[d[0],d[1],d[2]];deckRef.current=d.slice(3);}
    else{newComm.push(d[0]);deckRef.current=d.slice(1);}

    const nextStage=stages[si+1];
    setCommunity(newComm);setStage(nextStage);setCurrentBetLevel(0);
    setSeats(newSeats);

    // First to act post-flop: first live after dealer
    const liveIdxs=newSeats.map((x,i)=>(!x.isOut&&!x.folded&&!x.allIn)?i:-1).filter(i=>i>=0);
    if(liveIdxs.length===0){resolveHand(newSeats,curPot,newComm,dlrIdx,blLvl);return;}
    const firstAct=liveIdxs.find(i=>i>dlrIdx)||liveIdxs[0];

    setTimeout(()=>processAction(newSeats,firstAct,curPot,0,nextStage,newComm,dlrIdx,blLvl),500);
  };

  const runOutBoard=(s,curPot,curComm,dlrIdx,blLvl)=>{
    let comm=[...curComm];const d=[...deckRef.current];
    while(comm.length<5){comm.push(d.shift());}
    deckRef.current=d;
    setCommunity(comm);setStage("river");
    setTimeout(()=>resolveHand(s,curPot,comm,dlrIdx,blLvl),800);
  };

  // ─── RESOLVE HAND ─────────────────────────────────────
  const resolveHand=(s,curPot,comm,dlrIdx,blLvl)=>{
    const newSeats=[...s.map(x=>({...x,bet:0}))];
    const notFolded=newSeats.filter(x=>!x.isOut&&!x.folded);

    if(notFolded.length===1){
      const winner=notFolded[0];const wi=newSeats.findIndex(x=>x.id===winner.id);
      newSeats[wi]={...newSeats[wi],chips:newSeats[wi].chips+curPot};
      setHandResults({winners:[{name:winner.name,emoji:winner.emoji,hand:"-",pot:curPot}],msg:`${winner.emoji} ${winner.name} 승리! (상대 전원 폴드)`});
    }else{
      // Showdown
      let results=notFolded.map(p=>{
        const ev=comm.length>=3?evalHand([...p.cards,...comm]):{rank:0,name:"-",score:0};
        return{...p,eval:ev};
      }).sort((a,b)=>b.eval.score-a.eval.score);

      const winner=results[0];
      const wi=newSeats.findIndex(x=>x.id===winner.id);
      newSeats[wi]={...newSeats[wi],chips:newSeats[wi].chips+curPot};
      // Show all cards at showdown
      notFolded.forEach(p=>{const i=newSeats.findIndex(x=>x.id===p.id);newSeats[i]={...newSeats[i],showCards:true};});

      setHandResults({
        winners:[{name:winner.name,emoji:winner.emoji,hand:winner.eval.name,pot:curPot}],
        all:results.map(r=>({name:r.name,emoji:r.emoji,hand:r.eval.name})),
        msg:`${winner.emoji} ${winner.name} 승리! (${winner.eval.name})`
      });
    }

    // Eliminate busted players + BOUNTY
    const busted=[];
    const winnerSeat=notFolded.length===1?notFolded[0]:notFolded.length>0?notFolded.sort((a,b)=>(evalHand([...b.cards,...comm]).score||0)-(evalHand([...a.cards,...comm]).score||0))[0]:null;
    newSeats.forEach((seat,i)=>{
      if(seat.chips<=0&&!seat.isOut){
        newSeats[i]={...seat,isOut:true,chips:0};
        busted.push({...seat,eliminatedBy:winnerSeat?.name||"?"});
        // Eliminated player says GG
        const ggChat=getChat("eliminated");
        if(ggChat)setChatBubbles(prev=>({...prev,[i]:{text:ggChat,time:Date.now()}}));
      }
    });

    // Award bounties to player
    const bountyAmt=Math.floor(config.buyIn*0.1); // 10% of buy-in as bounty
    if(busted.length>0){
      busted.forEach(b=>{
        if(winnerSeat?.isPlayer){
          setMyBounties(prev=>[...prev,{name:b.name,emoji:b.emoji,amount:bountyAmt}]);
        }
      });
    }

    // Background: simulate other table eliminations
    let newRemaining=totalRemaining-busted.length;
    const otherTables=Math.max(0,Math.floor((newRemaining-newSeats.filter(x=>!x.isOut).length)/9));
    if(otherTables>0&&Math.random()<0.3){
      const otherBusts=Math.floor(Math.random()*3)+1;
      newRemaining=Math.max(newSeats.filter(x=>!x.isOut).length,newRemaining-otherBusts);
    }
    setTotalRemaining(newRemaining);

    if(busted.length>0){
      const msgs=busted.map(b=>{
        const bountyMsg=b.eliminatedBy==="나"?` 💰 바운티 $${bountyAmt} 획득!`:"";
        return `${b.emoji} ${b.name} 탈락! (${b.eliminatedBy}에게 제거)${bountyMsg}`;
      });
      setBustMsg(msgs.join(" | "));
      setTourneyLog(l=>[...l,...msgs]);
    }

    // Calculate rank
    const playerSeat=newSeats.find(s=>s.isPlayer);
    if(playerSeat&&!playerSeat.isOut){
      const betterStacks=newSeats.filter(s=>!s.isOut&&!s.isPlayer&&s.chips>playerSeat.chips).length;
      const estimatedBetter=Math.floor(betterStacks/8*newRemaining);
      setMyRank(Math.max(1,estimatedBetter+1));
    }

    // Check if player busted
    if(playerSeat&&playerSeat.chips<=0){
      setTourneyOver(true);setFinalPlace(newRemaining+busted.filter(b=>b.isPlayer).length);
      setScreen("result");
    }

    // Blind level now handled by timer (no hand-based increment)
    let newBlLvl=blindLevel;

    // Refill empty seats from other tables (with table number)
    const liveCount=newSeats.filter(x=>!x.isOut).length;
    const tableNum=Math.ceil(newRemaining/9);
    if(liveCount<7&&newRemaining>liveCount){
      const emptySlots=newSeats.map((s,i)=>s.isOut?i:-1).filter(i=>i>=0);
      const fillCount=Math.min(emptySlots.length,Math.min(2,newRemaining-liveCount));
      for(let fi=0;fi<fillCount;fi++){
        if(fi>=emptySlots.length)break;
        const fillIdx=emptySlots[fi];
        const avgChips=newSeats.filter(x=>!x.isOut).reduce((a,b)=>a+b.chips,0)/Math.max(1,liveCount);
        const np=shuffle(AI_PROFILES)[0];
        const fromTable=Math.floor(Math.random()*(tableNum-1))+1;
        const suffix=fi===0?"":"③";
        newSeats[fillIdx]={id:Date.now()+fi,name:np.name+suffix,chips:Math.floor(avgChips*(0.5+Math.random()*1.0)),
          cards:[],emoji:np.emoji,style:np.style,desc:np.desc,color:np.color||"#888888",folded:false,bet:0,isPlayer:false,isOut:false,allIn:false,showCards:false,fromTable};
        setTourneyLog(l=>[...l,`➕ ${np.emoji} ${np.name}${suffix} 합류 (테이블 #${fromTable}에서 이동)`]);
        // New player greets
        const greet=CHAT_LINES.greeting[Math.floor(Math.random()*CHAT_LINES.greeting.length)];
        setChatBubbles(prev=>({...prev,[fillIdx]:{text:greet,time:Date.now()}}));
      }
    }

    setSeats(newSeats);setShowdown(true);setGameOver(true);setPot(curPot);
    // Next dealer
    const liveIdxs=newSeats.map((x,i)=>x.isOut?-1:i).filter(i=>i>=0);
    const nextDlr=liveIdxs[(liveIdxs.indexOf(dlrIdx)+1)%liveIdxs.length]||0;

    // Store for next hand
    seatsRef.current=newSeats;
    setDealerIdx(nextDlr);
  };

  const endTourney=(place)=>{setTourneyOver(true);setFinalPlace(place);setScreen("result");};

  // ─── PLAYER ACTIONS ───────────────────────────────────
  const doPlayerAction=(action,amount=0)=>{
    if(!isPlayerTurn)return;
    setIsPlayerTurn(false);
    const s=[...seatsRef.current];
    const pi=s.findIndex(x=>x.isPlayer);
    const seat=s[pi];
    const toCall=Math.max(0,currentBetLevel-seat.bet);
    let newPot=pot,newBetLvl=currentBetLevel;

    if(action==="fold"){s[pi]={...seat,folded:true};setLastAction("😎 나: 폴드");}
    else if(action==="check"){setLastAction("😎 나: 체크");}
    else if(action==="call"){
      const cost=Math.min(toCall,seat.chips);
      s[pi]={...seat,chips:seat.chips-cost,bet:seat.bet+cost,allIn:seat.chips-cost<=0};
      newPot+=cost;setLastAction(`😎 나: 콜 (${cost})`);
    }else if(action==="raise"){
      const totalCost=Math.min(toCall+amount,seat.chips);
      s[pi]={...seat,chips:seat.chips-totalCost,bet:seat.bet+totalCost,allIn:seat.chips-totalCost<=0};
      newBetLvl=s[pi].bet;newPot+=totalCost;setLastAction(`😎 나: 레이즈 → ${newBetLvl}`);
    }else if(action==="allin"){
      const cost=seat.chips;s[pi]={...seat,chips:0,bet:seat.bet+cost,allIn:true};
      if(s[pi].bet>newBetLvl)newBetLvl=s[pi].bet;
      newPot+=cost;setLastAction(`😎 나: 올인! (${cost})`);
    }
    setSeats(s);setPot(newPot);setCurrentBetLevel(newBetLvl);

    const nextIdx=findNextActor(s,pi);
    setTimeout(()=>{
      if(nextIdx===null||checkRoundComplete(s,newBetLvl)){
        advanceStage(s,newPot,newBetLvl,stage,community,dealerIdx,blindLevel);
      }else{
        processAction(s,nextIdx,newPot,newBetLvl,stage,community,dealerIdx,blindLevel);
      }
    },400);
  };

  const nextHand=()=>{dealHand(null,dealerIdx,blindLevel);};

  // ─── SETUP SCREEN ─────────────────────────────────────
  if(screen==="setup"){
    return(
      <div style={{minHeight:"100vh",background:"linear-gradient(170deg,#0a0e17,#111927,#0d1520)",display:"flex",alignItems:"center",justifyContent:"center",fontFamily:"'Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo',sans-serif",padding:16}}>
        <div style={{maxWidth:480,width:"100%",textAlign:"center"}}>
          <div style={{fontSize:48,marginBottom:8}}>🏆</div>
          <h1 style={{color:"#e8b730",fontSize:28,fontWeight:700,letterSpacing:1,marginBottom:4}}>토너먼트 포커</h1>
          <p style={{color:"#6b7d93",fontSize:12,letterSpacing:4,marginBottom:40}}>TOURNAMENT SIMULATOR</p>

          <div style={{background:"rgba(255,255,255,0.03)",border:"1px solid rgba(232,183,48,0.15)",borderRadius:16,padding:24,marginBottom:24,textAlign:"left"}}>
            <h3 style={{color:"#e8b730",fontSize:15,marginBottom:20}}>대회 설정</h3>
            {[
              {label:"바이인 ($)",key:"buyIn",min:50,max:10000,step:50},
              {label:"총 참가자",key:"totalPlayers",min:18,max:1000,step:9},
              {label:"시작 칩",key:"startChips",min:5000,max:100000,step:1000},
            ].map(f=>(
              <div key={f.key} style={{marginBottom:16}}>
                <div style={{display:"flex",justifyContent:"space-between",marginBottom:6}}>
                  <span style={{color:"#8899aa",fontSize:13}}>{f.label}</span>
                  <span style={{color:"#e8b730",fontWeight:700,fontSize:15}}>{f.key==="buyIn"?`$${config[f.key].toLocaleString()}`:config[f.key].toLocaleString()}</span>
                </div>
                <input type="range" min={f.min} max={f.max} step={f.step} value={config[f.key]} onChange={e=>setConfig({...config,[f.key]:+e.target.value})}
                  style={{width:"100%",accentColor:"#e8b730"}}/>
              </div>
            ))}
          </div>

          <div style={{background:"rgba(255,255,255,0.03)",border:"1px solid rgba(232,183,48,0.1)",borderRadius:12,padding:16,marginBottom:24,textAlign:"left"}}>
            <div style={{color:"#8899aa",fontSize:12,marginBottom:8}}>📊 대회 요약</div>
            <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:8}}>
              {[
                ["총 상금",`$${prizePool.toLocaleString()}`],
                ["입상 인원",`${paidSlots}명`],
                ["테이블 수",`${Math.ceil(config.totalPlayers/9)}개`],
                ["블라인드 시작",`${BLIND_SCHEDULE[0].sb}/${BLIND_SCHEDULE[0].bb}`],
              ].map(([l,v],i)=>(
                <div key={i}><span style={{color:"#667",fontSize:11}}>{l}</span><div style={{color:"#ccd6e0",fontSize:14,fontWeight:600}}>{v}</div></div>
              ))}
            </div>
          </div>

          <button onClick={startTournament} style={{width:"100%",padding:"14px 0",borderRadius:12,border:"none",background:"linear-gradient(135deg,#e8b730,#c49a20)",color:"#0a0e17",fontWeight:700,fontSize:17,cursor:"pointer",fontFamily:"inherit",letterSpacing:1}}>
            🎮 대회 시작
          </button>
        </div>
      </div>
    );
  }

  // ─── RESULT SCREEN ────────────────────────────────────
  if(screen==="result"){
    const inMoney=finalPlace<=paidSlots;
    return(
      <div style={{minHeight:"100vh",background:"linear-gradient(170deg,#0a0e17,#111927)",display:"flex",alignItems:"center",justifyContent:"center",fontFamily:"'Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo',sans-serif",padding:16}}>
        <div style={{textAlign:"center",maxWidth:420}}>
          <div style={{fontSize:64,marginBottom:16}}>{inMoney?"🏆":"💀"}</div>
          <h2 style={{color:inMoney?"#e8b730":"#ef4444",fontSize:28,marginBottom:8}}>{inMoney?"입상 축하합니다!":"탈락"}</h2>
          <div style={{color:"#ccd6e0",fontSize:20,marginBottom:4}}>최종 순위: <b style={{color:"#e8b730"}}>{finalPlace}위</b> / {config.totalPlayers}명</div>
          {inMoney&&<div style={{color:"#22c55e",fontSize:18,marginBottom:8}}>상금: ${Math.floor(prizePool*(finalPlace===1?0.25:finalPlace<=3?0.15:0.05)).toLocaleString()}</div>}
          {myBounties.length>0&&<div style={{color:"#ffd700",fontSize:16,marginBottom:8}}>💰 바운티: {myBounties.length}명 제거 → ${(myBounties.length*Math.floor(config.buyIn*0.1)).toLocaleString()}</div>}
          {myBounties.length>0&&<div style={{display:"flex",gap:4,justifyContent:"center",marginBottom:16,flexWrap:"wrap"}}>{myBounties.map((b,i)=><span key={i} style={{background:"rgba(255,215,0,0.1)",border:"1px solid rgba(255,215,0,0.2)",borderRadius:6,padding:"2px 8px",fontSize:11,color:"#ffd700"}}>{b.emoji} {b.name}</span>)}</div>}
          <div style={{color:"#6b7d93",fontSize:13,marginBottom:32}}>플레이한 핸드: {handNum} | 최고 블라인드: {BLIND_SCHEDULE[Math.min(blindLevel,BLIND_SCHEDULE.length-1)].sb}/{BLIND_SCHEDULE[Math.min(blindLevel,BLIND_SCHEDULE.length-1)].bb}</div>
          <button onClick={()=>setScreen("setup")} style={{padding:"12px 40px",borderRadius:10,border:"none",background:"#e8b730",color:"#0a0e17",fontWeight:700,cursor:"pointer",fontSize:15,fontFamily:"inherit"}}>다시 도전</button>
        </div>
      </div>
    );
  }

  // ─── GAME SCREEN ──────────────────────────────────────
  const playerSeat=seats.find(s=>s.isPlayer);
  const liveSeats=seats.filter(s=>!s.isOut);
  const canCheck=currentBetLevel<=(playerSeat?.bet||0);
  const callAmt=Math.max(0,currentBetLevel-(playerSeat?.bet||0));

  // Arrange seats: player at bottom, others clockwise
  const playerIdx=seats.indexOf(playerSeat);
  const displayOrder=[];
  for(let i=0;i<seats.length;i++){displayOrder.push(seats[(playerIdx+i)%seats.length]);}
  // Position mapping for visual layout
  const seatPositions=[
    {x:50,y:82},   // 0: player (bottom)
    {x:12,y:74},   // 1: left-bottom
    {x:3,y:50},    // 2: left
    {x:12,y:26},   // 3: left-top
    {x:32,y:8},    // 4: top-left
    {x:50,y:2},    // 5: top center
    {x:68,y:8},    // 6: top-right
    {x:88,y:26},   // 7: right-top
    {x:97,y:50},   // 8: right
  ];

  const stageNames={preflop:"프리플랍",flop:"플랍",turn:"턴",river:"리버"};

  return(
    <div style={{minHeight:"100vh",background:"linear-gradient(170deg,#080c14,#0e1525,#0b1018)",fontFamily:"'Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo',sans-serif",display:"flex",flexDirection:"column",overflow:"hidden"}}>
      {/* ═══ WSOP-STYLE TOURNAMENT MONITOR ═══ */}
      <div style={{background:"linear-gradient(180deg,#0a1628,#0d1f38)",borderBottom:"2px solid #1a3a6a",flexShrink:0,padding:"6px 10px"}}>
        {/* Compact info bar (always visible) */}
        <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",flexWrap:"wrap",gap:4}}>
          <div style={{display:"flex",alignItems:"center",gap:6}}>
            <div style={{background:"#c0392b",borderRadius:4,padding:"2px 8px",fontSize:11,fontWeight:800,color:"#fff",letterSpacing:1}}>LEVEL {blindLevel+1}</div>
            <div style={{color:"#5dade2",fontSize:14,fontWeight:700,fontFamily:"'Courier New',monospace"}}>{bl.sb.toLocaleString()}/{bl.bb.toLocaleString()}</div>
            {bl.ante>0&&<div style={{color:"#aab5c0",fontSize:10}}>앤티 {bl.ante}</div>}
            <div style={{background:levelTimer<=60?"rgba(231,76,60,0.3)":"rgba(255,255,255,0.05)",borderRadius:4,padding:"2px 8px",border:levelTimer<=60?"1px solid #e74c3c":"1px solid rgba(255,255,255,0.1)"}}>
              <span style={{color:levelTimer<=60?"#e74c3c":"#2ecc71",fontSize:14,fontWeight:700,fontFamily:"'Courier New',monospace"}}>{fmtTime(levelTimer)}</span>
            </div>
          </div>
          <div style={{display:"flex",alignItems:"center",gap:6}}>
            <div style={{color:totalRemaining<=paidSlots?"#2ecc71":totalRemaining<=paidSlots*1.2?"#f39c12":"#8899aa",fontSize:11}}>
              <span style={{fontWeight:700,fontSize:13}}>{totalRemaining}</span>/{config.totalPlayers}명
            </div>
            {myBounties.length>0&&(
              <div style={{color:"#ffd700",fontSize:11,fontWeight:700}}>💰×{myBounties.length}</div>
            )}
            <button onClick={()=>setShowMonitor(!showMonitor)} style={{background:showMonitor?"rgba(93,173,226,0.2)":"transparent",border:"1px solid rgba(93,173,226,0.3)",borderRadius:4,padding:"3px 8px",color:"#5dade2",cursor:"pointer",fontSize:10,fontWeight:700}}>
              {showMonitor?"▲ 닫기":"▼ 모니터"}
            </button>
            <button onClick={()=>setShowCoach(!showCoach)} style={{background:showCoach?"rgba(232,183,48,0.15)":"transparent",border:"1px solid rgba(232,183,48,0.2)",borderRadius:4,padding:"3px 8px",color:"#e8b730",cursor:"pointer",fontSize:10}}>💡</button>
          </div>
        </div>
      </div>

      {/* ═══ FLOATING MONITOR OVERLAY (top-right) ═══ */}
      {showMonitor&&(
        <div style={{position:"fixed",top:44,right:8,width:260,background:"rgba(8,20,40,0.88)",backdropFilter:"blur(12px)",border:"1px solid rgba(93,173,226,0.25)",borderRadius:12,padding:0,zIndex:50,boxShadow:"0 8px 32px rgba(0,0,0,0.5)",overflow:"hidden"}}>
          {/* Header */}
          <div style={{background:"rgba(26,58,106,0.5)",padding:"6px 10px",display:"flex",justifyContent:"space-between",alignItems:"center",borderBottom:"1px solid rgba(93,173,226,0.15)"}}>
            <span style={{color:"#5dade2",fontSize:10,fontWeight:700,letterSpacing:1}}>🏆 TOURNAMENT</span>
            <button onClick={()=>setShowMonitor(false)} style={{background:"none",border:"none",color:"#5dade2",cursor:"pointer",fontSize:12,padding:0}}>✕</button>
          </div>
          {/* Timer */}
          <div style={{textAlign:"center",padding:"8px 0 4px"}}>
            <div style={{color:"#667d94",fontSize:8,letterSpacing:2}}>LEVEL {blindLevel+1} · {bl.sb}/{bl.bb}{bl.ante>0?` (A${bl.ante})`:""}</div>
            <div style={{color:levelTimer<=60?"#e74c3c":"#2ecc71",fontSize:36,fontWeight:800,fontFamily:"'Courier New',monospace",lineHeight:1,textShadow:levelTimer<=60?"0 0 12px rgba(231,76,60,0.3)":"none"}}>{fmtTime(levelTimer)}</div>
            <div style={{width:"80%",height:3,background:"rgba(255,255,255,0.06)",borderRadius:2,margin:"4px auto 0",overflow:"hidden"}}>
              <div style={{width:`${(levelTimer/(bl.dur*60))*100}%`,height:"100%",borderRadius:2,background:levelTimer<=60?"#e74c3c":"linear-gradient(90deg,#2ecc71,#5dade2)",transition:"width 1s"}}/>
            </div>
            <div style={{color:"#556b7f",fontSize:8,marginTop:2}}>NEXT: {nextBl.sb}/{nextBl.bb} · 경과 {fmtElapsed(elapsedTime)}</div>
          </div>
          {/* Stats */}
          <div style={{padding:"4px 10px 6px"}}>
            {[
              {l:"REMAINING",v:`${totalRemaining}/${config.totalPlayers}`,c:totalRemaining<=paidSlots?"#2ecc71":"#5dade2"},
              {l:"AVG STACK",v:Math.floor(config.startChips*config.totalPlayers/Math.max(1,totalRemaining)).toLocaleString(),c:"#e8b730"},
              {l:"MY STACK",v:(playerSeat?.chips||0).toLocaleString(),c:playerSeat&&playerSeat.chips<bl.bb*10?"#e74c3c":"#fff"},
              {l:"MY RANK",v:`~${myRank}위`,c:myRank<=paidSlots?"#2ecc71":"#aaa"},
              {l:"BOUNTIES",v:myBounties.length>0?`${myBounties.length} ($${myBounties.length*Math.floor(config.buyIn*0.1)})`:"0",c:myBounties.length>0?"#ffd700":"#556b7f"},
            ].map((s,i)=>(
              <div key={i} style={{display:"flex",justifyContent:"space-between",padding:"2px 0",borderBottom:"1px solid rgba(255,255,255,0.03)"}}>
                <span style={{color:"#556b7f",fontSize:8,letterSpacing:0.5}}>{s.l}</span>
                <span style={{color:s.c,fontSize:11,fontWeight:700,fontFamily:"'Courier New',monospace"}}>{s.v}</span>
              </div>
            ))}
          </div>
          {/* Prize */}
          <div style={{padding:"3px 10px 6px",borderTop:"1px solid rgba(255,255,255,0.04)"}}>
            <div style={{display:"flex",justifyContent:"space-between"}}>
              <span style={{color:"#556b7f",fontSize:8}}>PRIZE POOL</span>
              <span style={{color:"#e8b730",fontSize:10,fontWeight:700}}>${prizePool.toLocaleString()}</span>
            </div>
            <div style={{display:"flex",justifyContent:"space-between"}}>
              <span style={{color:"#556b7f",fontSize:8}}>1st / 입상</span>
              <span style={{color:"#8899aa",fontSize:9}}>${Math.floor(prizePool*0.25).toLocaleString()} / {paidSlots}명</span>
            </div>
          </div>
          {/* Bubble/ITM alert */}
          {totalRemaining<=paidSlots*1.2&&totalRemaining>paidSlots&&(
            <div style={{background:"rgba(243,156,18,0.15)",padding:"4px 10px",textAlign:"center"}}>
              <span style={{color:"#f39c12",fontSize:9,fontWeight:700}}>🫧 BUBBLE — {totalRemaining-paidSlots}명 남음</span>
            </div>
          )}
          {totalRemaining<=paidSlots&&(
            <div style={{background:"rgba(46,204,113,0.1)",padding:"4px 10px",textAlign:"center"}}>
              <span style={{color:"#2ecc71",fontSize:9,fontWeight:700}}>💰 IN THE MONEY</span>
            </div>
          )}
          {/* Blind schedule mini */}
          <div style={{padding:"4px 8px 6px",borderTop:"1px solid rgba(255,255,255,0.04)",display:"flex",gap:3,flexWrap:"wrap"}}>
            {BLIND_SCHEDULE.slice(0,10).map((b,i)=>(
              <span key={i} style={{fontSize:7,color:i===blindLevel?"#5dade2":i<blindLevel?"#334":"#556b7f",background:i===blindLevel?"rgba(93,173,226,0.15)":"none",borderRadius:2,padding:"1px 3px"}}>{i+1}:{b.sb}/{b.bb}</span>
            ))}
          </div>
        </div>
      )}

      {/* ═══ POKER TABLE ═══ */}
      <div style={{flex:1,position:"relative",minHeight:400,margin:"0 auto",width:"100%",maxWidth:720}}>
        {/* Table shadow/glow */}
        <div style={{position:"absolute",left:"8%",right:"8%",top:"10%",bottom:"18%",borderRadius:"50%",background:"rgba(0,0,0,0.4)",filter:"blur(20px)"}}/>
        {/* Table border (wood rim) */}
        <div style={{position:"absolute",left:"7%",right:"7%",top:"9%",bottom:"17%",borderRadius:"50%",background:"linear-gradient(145deg,#5d3a1a,#3e2510,#5d3a1a)",padding:6}}>
          {/* Felt */}
          <div style={{width:"100%",height:"100%",borderRadius:"50%",background:"radial-gradient(ellipse at 40% 40%,#2d7a4a 0%,#1a5c35 30%,#13442a 60%,#0d3320 100%)",position:"relative",boxShadow:"inset 0 4px 30px rgba(0,0,0,0.4),inset 0 0 60px rgba(0,0,0,0.2)",overflow:"visible"}}>
            {/* Felt texture overlay */}
            <div style={{position:"absolute",inset:0,borderRadius:"50%",background:"url('data:image/svg+xml,<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"4\" height=\"4\"><rect width=\"4\" height=\"4\" fill=\"rgba(0,0,0,0.03)\"/><rect width=\"1\" height=\"1\" fill=\"rgba(255,255,255,0.02)\"/></svg>')",opacity:0.5}}/>

            {/* Community Cards */}
            <div style={{position:"absolute",top:"42%",left:"50%",transform:"translate(-50%,-50%)",textAlign:"center",zIndex:4}}>
              <div style={{display:"flex",gap:5,justifyContent:"center",marginBottom:8}}>
                {community.map((c,i)=><PokerCard key={i} card={c} winner={handResults&&handResults.winners[0]?.name}/>)}
                {community.length<5&&!showdown&&Array.from({length:5-community.length}).map((_,i)=>(
                  <div key={`e${i}`} style={{width:58,height:80,borderRadius:7,border:"2px dashed rgba(255,255,255,0.1)",background:"rgba(0,0,0,0.1)"}}/>
                ))}
              </div>
              {/* Stage label on felt */}
              <div style={{color:"#90c4a8",fontSize:9,letterSpacing:2,marginBottom:4,textTransform:"uppercase"}}>{stageNames[stage]||stage} {stage==="preflop"?"· 카드 배분 후 첫 베팅":stage==="flop"?"· 커뮤니티 3장 오픈":stage==="turn"?"· 4번째 카드 오픈":stage==="river"?"· 마지막 카드 오픈":""}</div>
            </div>

            {/* Pot display */}
            <div style={{position:"absolute",top:"62%",left:"50%",transform:"translate(-50%,-50%)",zIndex:4,display:"flex",flexDirection:"column",alignItems:"center",gap:3}}>
              {/* Pot chips visual */}
              <div style={{display:"flex",gap:3,justifyContent:"center"}}>
                {pot>0&&Array.from({length:Math.min(Math.ceil(pot/(bl.bb*4)),6)}).map((_,ci)=>(
                  <div key={ci} style={{display:"flex",flexDirection:"column",alignItems:"center"}}>
                    {Array.from({length:Math.min(Math.ceil((ci+1)*0.8),4)}).map((_,si)=>(
                      <div key={si} style={{width:18,height:5,borderRadius:9,marginTop:-2,
                        background:ci%4===0?"linear-gradient(180deg,#e74c3c,#c0392b)":ci%4===1?"linear-gradient(180deg,#2ecc71,#27ae60)":ci%4===2?"linear-gradient(180deg,#3498db,#2980b9)":"linear-gradient(180deg,#1a1a2e,#333)",
                        border:"1px solid rgba(255,255,255,0.35)",boxShadow:"0 1px 2px rgba(0,0,0,0.4)"}}/>
                    ))}
                  </div>
                ))}
              </div>
              <div style={{background:"rgba(0,0,0,0.55)",borderRadius:20,padding:"4px 16px",display:"flex",alignItems:"center",gap:6,backdropFilter:"blur(4px)",border:"1px solid rgba(255,255,255,0.1)"}}>
                <span style={{color:"#aaa",fontSize:9,fontWeight:600}}>POT</span>
                <span style={{color:"#ffd700",fontSize:18,fontWeight:800,fontFamily:"'Courier New',monospace",textShadow:"0 0 8px rgba(255,215,0,0.3)"}}>{pot.toLocaleString()}</span>
              </div>
            </div>

            {/* Dealer chip */}
            {seats[dealerIdx]&&!seats[dealerIdx].isOut&&(()=>{
              const dDispIdx=displayOrder.indexOf(seats[dealerIdx]);
              if(dDispIdx<0)return null;
              const dp=seatPositions[dDispIdx];
              const dx=(50-dp.x)*0.25,dy=(50-dp.y)*0.25;
              return <div style={{position:"absolute",left:`${dp.x+dx*0.5}%`,top:`${dp.y+dy*0.5}%`,transform:"translate(-50%,-50%)",background:"linear-gradient(135deg,#fff,#e0e0e0)",color:"#333",fontSize:9,fontWeight:900,width:22,height:22,borderRadius:"50%",display:"flex",alignItems:"center",justifyContent:"center",border:"2px solid #ffd700",zIndex:8,boxShadow:"0 2px 6px rgba(0,0,0,0.4)"}}>D</div>;
            })()}
          </div>
        </div>

        {/* ═══ PLAYER SEATS ═══ */}
        {displayOrder.map((seat,i)=>{
          if(!seat)return null;
          const pos=seatPositions[i];
          const seatGlobalIdx=seats.indexOf(seat);
          const isAct=actIdx===seatGlobalIdx&&!gameOver;
          const isMe=seat.isPlayer;
          const liveIdxs2=seats.map((x,j)=>x.isOut?-1:j).filter(j=>j>=0);
          const dlrOff2=liveIdxs2.indexOf(dealerIdx);
          const myOff2=liveIdxs2.indexOf(seatGlobalIdx);
          const relPos2=(myOff2-dlrOff2+liveIdxs2.length)%liveIdxs2.length;
          const posLabel=POSITION_NAMES[relPos2]||"";
          const isWinner=handResults&&handResults.winners&&handResults.winners[0]?.name===seat.name&&gameOver;
          const seatColor=seat.color||"#888";

          // Bet chip position (between seat and center)
          const chipX=pos.x+(50-pos.x)*0.4;
          const chipY=pos.y+(50-pos.y)*0.4;

          // Evaluate hand for showdown label
          let handEval=null;
          if(showdown&&seat.showCards&&seat.cards.length===2&&community.length>=3){
            handEval=evalHand([...seat.cards,...community]);
          }

          return(
            <div key={seat.id+"-"+i} style={{position:"absolute",left:`${pos.x}%`,top:`${pos.y}%`,transform:"translate(-50%,-50%)",zIndex:isMe?10:isAct?8:3,opacity:seat.isOut?0.2:1,transition:"all 0.3s"}}>
              {/* Cards above avatar */}
              <div style={{display:"flex",gap:3,justifyContent:"center",marginBottom:isMe?6:3,minHeight:isMe?80:50,opacity:seat.folded?0.35:1}}>
                {seat.cards.length>0&&seat.cards.map((c,j)=>(
                  <PokerCard key={j} card={c} faceDown={!seat.showCards&&!isMe} highlight={isMe} tiny={!isMe} winner={isWinner}/>
                ))}
              </div>

              {/* Hand label at showdown */}
              {handEval&&handEval.name&&handEval.name!=="-"&&(
                <div style={{textAlign:"center",marginBottom:3}}>
                  <HandLabel name={handEval.name} isWinner={isWinner}/>
                </div>
              )}

              {/* Avatar + Info plate */}
              <div style={{display:"flex",flexDirection:"column",alignItems:"center"}}>
                {/* Circular avatar */}
                <div style={{width:isMe?52:42,height:isMe?52:42,borderRadius:"50%",background:`linear-gradient(135deg,${seatColor},${seatColor}88)`,display:"flex",alignItems:"center",justifyContent:"center",border:isAct?`3px solid #ffd700`:isWinner?`3px solid #ffa000`:`2px solid ${seatColor}88`,boxShadow:isAct?`0 0 16px ${seatColor}88,0 0 24px rgba(255,215,0,0.4)`:isWinner?`0 0 20px rgba(255,160,0,0.6)`:`0 2px 8px rgba(0,0,0,0.4)`,position:"relative",transition:"all 0.3s"}}>
                  <span style={{fontSize:isMe?26:20}}>{seat.emoji}</span>
                  {/* Position badge */}
                  {!seat.isOut&&posLabel&&(
                    <div style={{position:"absolute",top:-4,right:-4,zIndex:2}}>
                      <Tip term={posLabel}>
                        <span style={{display:"inline-block",background:posLabel==="BTN"?"#ffd700":posLabel==="SB"?"#5dade2":posLabel==="BB"?"#e74c3c":"#555",borderRadius:3,padding:"1px 4px",fontSize:7,fontWeight:800,color:"#fff",border:"1px solid rgba(255,255,255,0.3)",lineHeight:1.2,cursor:"help"}}>{posLabel}</span>
                      </Tip>
                    </div>
                  )}
                  {/* Winner crown */}
                  {isWinner&&<div style={{position:"absolute",top:-14,left:"50%",transform:"translateX(-50%)",fontSize:16}}>👑</div>}
                </div>

                {/* Name + Chips */}
                <div style={{background:"rgba(0,0,0,0.7)",borderRadius:6,padding:"3px 10px",marginTop:-4,textAlign:"center",minWidth:isMe?80:60,backdropFilter:"blur(4px)",border:isWinner?"1px solid rgba(255,160,0,0.4)":"1px solid rgba(255,255,255,0.08)"}}>
                  <div style={{color:isMe?"#64b5f6":"#ddd",fontSize:isMe?11:9,fontWeight:700,whiteSpace:"nowrap"}}>{seat.name}</div>
                  <div style={{color:seat.isOut?"#666":"#ffd700",fontSize:isMe?12:10,fontWeight:800,fontFamily:"'Courier New',monospace"}}>{seat.isOut?"탈락":seat.chips.toLocaleString()}</div>
                  {seat.allIn&&!seat.isOut&&<div style={{color:"#ff5252",fontSize:8,fontWeight:800,letterSpacing:1}}>ALL-IN</div>}
                </div>
              </div>

              {/* Bet chips (positioned toward center) */}
              {seat.bet>0&&!gameOver&&(
                <div style={{position:"absolute",left:`${(chipX-pos.x)*3}px`,top:`${(chipY-pos.y)*2}px`,zIndex:6,pointerEvents:"none"}}>
                  <ChipStack amount={seat.bet} bb={bl.bb}/>
                </div>
              )}
              {/* Chat bubble */}
              {chatBubbles[seatGlobalIdx]&&Date.now()-chatBubbles[seatGlobalIdx].time<4000&&(
                <div style={{position:"absolute",top:isMe?-10:-6,left:isMe?"110%":"105%",background:"rgba(255,255,255,0.95)",borderRadius:8,padding:"3px 8px",maxWidth:120,zIndex:20,boxShadow:"0 2px 8px rgba(0,0,0,0.3)",pointerEvents:"none"}}>
                  <div style={{color:"#333",fontSize:9,fontWeight:600,lineHeight:1.3}}>{chatBubbles[seatGlobalIdx].text}</div>
                  <div style={{position:"absolute",left:-4,top:"50%",transform:"translateY(-50%) rotate(45deg)",width:8,height:8,background:"rgba(255,255,255,0.95)"}}/>
                </div>
              )}
              {/* From table label (new arrivals) */}
              {seat.fromTable&&!seat.isOut&&(
                <div style={{textAlign:"center",marginTop:1}}>
                  <span style={{color:"#5dade2",fontSize:7,background:"rgba(93,173,226,0.15)",borderRadius:3,padding:"1px 4px"}}>T#{seat.fromTable}에서 이동</span>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* ═══ ACTION LOG + TERM TIP ═══ */}
      <div style={{textAlign:"center",padding:"2px 12px",flexShrink:0}}>
        {lastAction&&!gameOver&&(
          <div style={{display:"inline-flex",alignItems:"center",gap:8,background:"rgba(0,0,0,0.3)",borderRadius:8,padding:"4px 12px",marginBottom:2}}>
            <span style={{color:"#ccd6e0",fontSize:12}}>{lastAction}</span>
            {termTip&&<span style={{color:"#5dade2",fontSize:10,borderLeft:"1px solid #334",paddingLeft:8}}>💬 {termTip.kr}({termTip.en}): {termTip.desc}</span>}
          </div>
        )}
        {bustMsg&&<div style={{color:"#ef4444",fontSize:12,marginBottom:2}}>{bustMsg}</div>}
        {handResults&&gameOver&&(
          <div style={{background:handResults.winners[0]?.name==="나"?"rgba(34,197,94,0.1)":"rgba(239,68,68,0.06)",border:`1px solid ${handResults.winners[0]?.name==="나"?"rgba(34,197,94,0.2)":"rgba(239,68,68,0.15)"}`,borderRadius:10,padding:"8px 14px",marginBottom:4,display:"inline-block"}}>
            <div style={{color:"#ccd6e0",fontSize:13,fontWeight:600}}>{handResults.msg}</div>
            {handResults.all&&<div style={{color:"#7a8a9a",fontSize:11,marginTop:4}}>{handResults.all.map(a=>`${a.emoji}${a.name}: ${a.hand}`).join(" | ")}</div>}
          </div>
        )}
      </div>

      {/* ═══ INFO PANELS (side by side) ═══ */}
      {(foldReveals.length>0||(showCoach&&coachTips&&!gameOver))&&(
        <div style={{display:"flex",gap:6,padding:"4px 10px",flexShrink:0}}>
          {/* LEFT: Fold reveals */}
          {foldReveals.length>0&&(
            <div style={{flex:foldReveals.length>0&&showCoach&&coachTips?"0 0 40%":"1",background:"rgba(40,30,15,0.4)",border:"1px solid rgba(200,150,50,0.15)",borderRadius:8,padding:"5px 8px",minWidth:0}}>
              <div style={{color:"#a08050",fontSize:9,fontWeight:700,letterSpacing:1,marginBottom:3}}>🃏 폴드 카드</div>
              {foldReveals.slice(-3).map((fr,i)=>(
                <div key={i} style={{display:"flex",alignItems:"center",gap:5,marginBottom:3}}>
                  <span style={{fontSize:11,flexShrink:0}}>{fr.emoji}</span>
                  <div style={{display:"flex",gap:1,flexShrink:0}}>
                    {fr.cards.map((c,j)=><PokerCard key={j} card={c} tiny/>)}
                  </div>
                  <div style={{minWidth:0,overflow:"hidden"}}>
                    <div style={{color:"#bbb",fontSize:9,fontWeight:600,whiteSpace:"nowrap",overflow:"hidden",textOverflow:"ellipsis"}}>{fr.name} ({fr.posLabel})</div>
                    <div style={{color:"#8a7040",fontSize:8,lineHeight:1.2,display:"-webkit-box",WebkitLineClamp:2,WebkitBoxOrient:"vertical",overflow:"hidden"}}>{fr.reason}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
          {/* RIGHT: Smart Coaching */}
          {showCoach&&coachTips&&!gameOver&&(
            <div style={{flex:1,background:"rgba(15,25,40,0.6)",border:"1px solid rgba(93,173,226,0.15)",borderRadius:8,padding:"6px 10px",minWidth:0}}>
              {/* Row 1: Position + Stack */}
              <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:4}}>
                <div style={{display:"flex",alignItems:"center",gap:4}}>
                  <Tip term={coachTips.posName==="BTN"?"btn":coachTips.posName==="CO"?"co":coachTips.posName==="UTG"?"utg":null}>
                    <span style={{background:"rgba(93,173,226,0.2)",border:"1px solid rgba(93,173,226,0.3)",borderRadius:4,padding:"1px 6px",color:"#5dade2",fontSize:10,fontWeight:700}}>{coachTips.posName}</span>
                  </Tip>
                  <span style={{color:"#8899aa",fontSize:9}}>{coachTips.posFullName}</span>
                </div>
                <div style={{color:coachTips.m<=10?"#ef4444":coachTips.m<=20?"#f59e0b":"#8899aa",fontSize:9,fontWeight:600}}>{coachTips.m}BB</div>
              </div>

              {/* Row 2: Equity bar + percentage */}
              <div style={{marginBottom:4}}>
                <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:2}}>
                  <span style={{color:"#8899aa",fontSize:9}}>승률</span>
                  <span style={{color:coachTips.equity>=60?"#22c55e":coachTips.equity>=40?"#f59e0b":"#ef4444",fontSize:14,fontWeight:800}}>{coachTips.equity}%</span>
                </div>
                <div style={{width:"100%",height:6,background:"rgba(255,255,255,0.08)",borderRadius:3,overflow:"hidden"}}>
                  <div style={{width:`${coachTips.equity}%`,height:"100%",borderRadius:3,background:coachTips.equity>=60?"linear-gradient(90deg,#22c55e,#16a34a)":coachTips.equity>=40?"linear-gradient(90deg,#f59e0b,#d97706)":"linear-gradient(90deg,#ef4444,#dc2626)",transition:"width 0.5s"}}/>
                </div>
              </div>

              {/* Row 3: Pot odds (if facing bet) */}
              {coachTips.toCall>0&&(
                <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:3,background:"rgba(0,0,0,0.2)",borderRadius:4,padding:"2px 6px"}}>
                  <Tip term="potodds"><span style={{color:"#8899aa",fontSize:9}}>팟오즈</span></Tip>
                  <span style={{color:"#ccc",fontSize:9}}><Tip term="call"><span>{coachTips.toCall}</span></Tip> 콜 / {coachTips.pot+coachTips.toCall} 팟 = <span style={{color:"#5dade2",fontWeight:700}}>{coachTips.potOddsPct}%</span> 필요</span>
                </div>
              )}

              {/* Row 4: Recommendation */}
              <div style={{display:"flex",alignItems:"center",gap:6,background:`${coachTips.rec.color}15`,border:`1px solid ${coachTips.rec.color}30`,borderRadius:6,padding:"4px 8px"}}>
                <span style={{color:coachTips.rec.color,fontSize:12,fontWeight:800,flexShrink:0}}>→ {coachTips.rec.action}</span>
                <span style={{color:"#aab5c0",fontSize:9,lineHeight:1.3}}>{coachTips.rec.reason}</span>
              </div>

              {/* Row 5: Hand description */}
              {(coachTips.handDesc||coachTips.madeHand)&&(
                <div style={{color:"#667d94",fontSize:8,marginTop:3}}>{coachTips.madeHand?`메이드: ${coachTips.madeHand}`:coachTips.handDesc} {coachTips.situation==="bubble"?"| 🫧 버블 근처!":coachTips.situation==="itm"?"| 💰 인더머니":""}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* PLAYER ACTIONS */}
      <div style={{padding:"8px 12px 12px",flexShrink:0,background:"rgba(0,0,0,0.2)",borderTop:"1px solid rgba(232,183,48,0.08)"}}>
        {isPlayerTurn&&!gameOver?(
          <div>
            <div style={{display:"flex",gap:6,justifyContent:"center",marginBottom:6,flexWrap:"wrap"}}>
              <button onClick={()=>doPlayerAction("fold")} style={{padding:"10px 16px",borderRadius:8,border:"none",background:"#b91c1c",color:"#fff",cursor:"pointer",fontWeight:700,fontSize:13,fontFamily:"inherit"}}>폴드</button>
              {canCheck?
                <button onClick={()=>doPlayerAction("check")} style={{padding:"10px 16px",borderRadius:8,border:"none",background:"#2563eb",color:"#fff",cursor:"pointer",fontWeight:700,fontSize:13,fontFamily:"inherit"}}>체크</button>:
                <button onClick={()=>doPlayerAction("call")} style={{padding:"10px 16px",borderRadius:8,border:"none",background:"#16a34a",color:"#fff",cursor:"pointer",fontWeight:700,fontSize:13,fontFamily:"inherit"}}>콜 ({callAmt.toLocaleString()})</button>
              }
              <button onClick={()=>doPlayerAction("allin")} style={{padding:"10px 16px",borderRadius:8,border:"none",background:"#c2410c",color:"#fff",cursor:"pointer",fontWeight:700,fontSize:13,fontFamily:"inherit"}}>올인</button>
            </div>
            <div style={{display:"flex",gap:6,justifyContent:"center",alignItems:"center"}}>
              <input type="range" min={Math.max(currentBetLevel*2,bl.bb*2)} max={Math.max(currentBetLevel*2,playerSeat?.chips||0)} step={bl.bb} value={raiseAmt} onChange={e=>setRaiseAmt(+e.target.value)} style={{flex:1,maxWidth:220,accentColor:"#e8b730"}}/>
              <button onClick={()=>doPlayerAction("raise",raiseAmt)} disabled={raiseAmt>=(playerSeat?.chips||0)} style={{padding:"10px 16px",borderRadius:8,border:"none",background:"#e8b730",color:"#0a0e17",cursor:"pointer",fontWeight:700,fontSize:13,fontFamily:"inherit"}}>레이즈 {raiseAmt.toLocaleString()}</button>
            </div>
          </div>
        ):gameOver?(
          <div style={{textAlign:"center"}}>
            <button onClick={nextHand} style={{padding:"12px 36px",borderRadius:10,border:"none",background:"linear-gradient(135deg,#e8b730,#c49a20)",color:"#0a0e17",cursor:"pointer",fontWeight:700,fontSize:15,fontFamily:"inherit"}}>다음 핸드 →</button>
          </div>
        ):(
          <div style={{textAlign:"center",color:"#556",fontSize:12,padding:8}}>⏳ AI 턴...</div>
        )}
      </div>
    </div>
  );
}
