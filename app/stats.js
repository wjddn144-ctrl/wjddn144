// 통계 계산 (순수 함수)
import { dayNumber } from './scheduler.js';

export function dailyCounts(logs) {
  const m = new Map();
  for (const l of logs) {
    const d = dayNumber(l.ts);
    m.set(d, (m.get(d) || 0) + 1);
  }
  return m;
}

// 오늘 했으면 오늘부터, 아직 안 했으면 어제부터 연속 일수를 센다
export function streak(counts, today) {
  let d = counts.has(today) ? today : today - 1;
  let n = 0;
  while (counts.has(d)) { n++; d--; }
  return n;
}

// 최근 기간(일) 동안 '다시'가 아닌 비율. 기록이 없으면 null
export function retention(logs, today, days = 30) {
  const recent = logs.filter((l) => dayNumber(l.ts) > today - days);
  if (!recent.length) return null;
  return recent.filter((l) => l.rating !== 'again').length / recent.length;
}

// 오늘(밀린 카드 포함)부터 n일간 복습 예정 수
export function forecast(cards, today, n = 7) {
  const out = Array(n).fill(0);
  for (const c of cards) {
    if (c.stage < 0) continue;
    const i = Math.max(0, c.due - today);
    if (i < n) out[i]++;
  }
  return out;
}

export function heatLevel(count) {
  if (!count) return 0;
  if (count < 5) return 1;
  if (count < 15) return 2;
  if (count < 30) return 3;
  return 4;
}
