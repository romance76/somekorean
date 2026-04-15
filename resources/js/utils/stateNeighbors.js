/**
 * 미국 50개 주 + DC 인접 맵 (자기 자신 포함).
 * 서버 app/Support/StateNeighbors.php 와 일치해야 함.
 *
 * state_plus 프로모션 UI 에서 "이 공고를 올리면 어떤 주에 노출되는지" 미리보기용.
 */
export const STATE_NEIGHBORS = {
  AL: ['AL','FL','GA','MS','TN'],
  AK: ['AK'],
  AZ: ['AZ','CA','CO','NM','NV','UT'],
  AR: ['AR','LA','MO','MS','OK','TN','TX'],
  CA: ['CA','AZ','NV','OR'],
  CO: ['CO','AZ','KS','NE','NM','OK','UT','WY'],
  CT: ['CT','MA','NY','RI'],
  DE: ['DE','MD','NJ','PA'],
  FL: ['FL','AL','GA'],
  GA: ['GA','AL','FL','NC','SC','TN'],
  HI: ['HI'],
  ID: ['ID','MT','NV','OR','UT','WA','WY'],
  IL: ['IL','IA','IN','KY','MO','WI'],
  IN: ['IN','IL','KY','MI','OH'],
  IA: ['IA','IL','MN','MO','NE','SD','WI'],
  KS: ['KS','CO','MO','NE','OK'],
  KY: ['KY','IL','IN','MO','OH','TN','VA','WV'],
  LA: ['LA','AR','MS','TX'],
  ME: ['ME','NH'],
  MD: ['MD','DE','PA','VA','WV','DC'],
  MA: ['MA','CT','NH','NY','RI','VT'],
  MI: ['MI','IN','OH','WI'],
  MN: ['MN','IA','ND','SD','WI'],
  MS: ['MS','AL','AR','LA','TN'],
  MO: ['MO','AR','IA','IL','KS','KY','NE','OK','TN'],
  MT: ['MT','ID','ND','SD','WY'],
  NE: ['NE','CO','IA','KS','MO','SD','WY'],
  NV: ['NV','AZ','CA','ID','OR','UT'],
  NH: ['NH','MA','ME','VT'],
  NJ: ['NJ','DE','NY','PA'],
  NM: ['NM','AZ','CO','OK','TX','UT'],
  NY: ['NY','CT','MA','NJ','PA','VT'],
  NC: ['NC','GA','SC','TN','VA'],
  ND: ['ND','MN','MT','SD'],
  OH: ['OH','IN','KY','MI','PA','WV'],
  OK: ['OK','AR','CO','KS','MO','NM','TX'],
  OR: ['OR','CA','ID','NV','WA'],
  PA: ['PA','DE','MD','NJ','NY','OH','WV'],
  RI: ['RI','CT','MA'],
  SC: ['SC','GA','NC'],
  SD: ['SD','IA','MN','MT','ND','NE','WY'],
  TN: ['TN','AL','AR','GA','KY','MO','MS','NC','VA'],
  TX: ['TX','AR','LA','NM','OK'],
  UT: ['UT','AZ','CO','ID','NM','NV','WY'],
  VT: ['VT','MA','NH','NY'],
  VA: ['VA','KY','MD','NC','TN','WV','DC'],
  WA: ['WA','ID','OR'],
  WV: ['WV','KY','MD','OH','PA','VA'],
  WI: ['WI','IA','IL','MI','MN'],
  WY: ['WY','CO','ID','MT','NE','SD','UT'],
  DC: ['DC','MD','VA'],
}

export function neighborsOf(state) {
  if (!state) return []
  const k = String(state).trim().toUpperCase()
  return STATE_NEIGHBORS[k] || [k]
}
