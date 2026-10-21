// 에빙하우스 망각곡선 기반 간격 반복 스케줄러 (순수 함수)
export const STEPS = [1, 2, 4, 7, 15, 30, 60]; // 일
export const DAY_START_HOUR = 4;
export const RELEARN_MS = 10 * 60 * 1000;
const DAY_MS = 86400000;

export function dayNumber(ts) {
  const d = new Date(ts - DAY_START_HOUR * 3600000);
  return Math.floor((Date.UTC(d.getFullYear(), d.getMonth(), d.getDate())) / DAY_MS);
}

export function newCard() {
  return { stage: -1, due: 0, reps: 0, lapses: 0 };
}

export const isNew = (c) => c.stage < 0;

export function intervalFor(stage) {
  if (stage < 0) return STEPS[0];
  const last = STEPS.length - 1;
  if (stage <= last) return STEPS[stage];
  return STEPS[last] * 2 ** (stage - last);
}

function nextStage(stage, rating) {
  switch (rating) {
    case 'again': return 0;
    case 'hard': return Math.max(stage, 0);
    case 'good': return stage + 1;
    case 'easy': return stage + 2;
    default: throw new Error('unknown rating: ' + rating);
  }
}

// 반환: { card, relearnAt? } — relearnAt은 '다시'를 눌렀을 때 같은 세션에서 재출제할 시각
export function schedule(card, rating, now = Date.now()) {
  const stage = nextStage(card.stage, rating);
  const next = {
    ...card,
    stage,
    due: dayNumber(now) + intervalFor(stage),
    reps: card.reps + 1,
    lapses: card.lapses + (rating === 'again' ? 1 : 0),
  };
  return rating === 'again' ? { card: next, relearnAt: now + RELEARN_MS } : { card: next };
}

export function formatInterval(days) {
  if (days < 7) return `${days}일`;
  if (days < 30) return `${Math.round(days / 7)}주`;
  if (days < 365) return `${Math.round(days / 30)}개월`;
  return `${(days / 365).toFixed(1)}년`;
}

export function previewLabels(card, now = Date.now()) {
  const out = { again: '10분' };
  for (const r of ['hard', 'good', 'easy']) {
    out[r] = formatInterval(schedule(card, r, now).card.due - dayNumber(now));
  }
  return out;
}
