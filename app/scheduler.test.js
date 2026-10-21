import test from 'node:test';
import assert from 'node:assert/strict';
import { STEPS, dayNumber, newCard, schedule, previewLabels, formatInterval } from './scheduler.js';

const at = (y, m, d, h = 12) => new Date(y, m - 1, d, h).getTime();

test('dayNumber: 새벽 4시 이전은 전날로 계산', () => {
  assert.equal(dayNumber(at(2026, 10, 21, 3)), dayNumber(at(2026, 10, 20, 23)));
  assert.equal(dayNumber(at(2026, 10, 21, 4)), dayNumber(at(2026, 10, 20, 23)) + 1);
});

test('새 카드: 좋음 → 1일 뒤, stage 0', () => {
  const now = at(2026, 10, 21);
  const r = schedule(newCard(), 'good', now);
  assert.equal(r.card.stage, 0);
  assert.equal(r.card.due, dayNumber(now) + 1);
  assert.equal(r.card.reps, 1);
});

test('좋음은 한 단계, 쉬움은 두 단계 상승', () => {
  const now = at(2026, 10, 21);
  const c = { ...newCard(), stage: 1, due: dayNumber(now), reps: 1 };
  assert.equal(schedule(c, 'good', now).card.stage, 2);
  assert.equal(schedule(c, 'good', now).card.due, dayNumber(now) + STEPS[2]);
  assert.equal(schedule(c, 'easy', now).card.stage, 3);
});

test('어려움은 단계 유지, 같은 간격 반복', () => {
  const now = at(2026, 10, 21);
  const c = { ...newCard(), stage: 3, due: dayNumber(now), reps: 4 };
  const r = schedule(c, 'hard', now);
  assert.equal(r.card.stage, 3);
  assert.equal(r.card.due, dayNumber(now) + STEPS[3]);
});

test('다시: stage 0, lapses+1, 10분 뒤 재출제', () => {
  const now = at(2026, 10, 21);
  const c = { ...newCard(), stage: 4, due: dayNumber(now), reps: 5, lapses: 0 };
  const r = schedule(c, 'again', now);
  assert.equal(r.card.stage, 0);
  assert.equal(r.card.lapses, 1);
  assert.equal(r.card.due, dayNumber(now) + 1);
  assert.equal(r.relearnAt, now + 10 * 60 * 1000);
});

test('마지막 단계 이후에는 간격 2배', () => {
  const now = at(2026, 10, 21);
  const last = STEPS.length - 1;
  const c = { ...newCard(), stage: last, due: dayNumber(now), reps: 9 };
  const r = schedule(c, 'good', now);
  assert.equal(r.card.stage, last + 1);
  assert.equal(r.card.due, dayNumber(now) + STEPS[last] * 2);
  const r2 = schedule(r.card, 'good', now);
  assert.equal(r2.card.due, dayNumber(now) + STEPS[last] * 4);
});

test('previewLabels: 네 버튼의 다음 간격 라벨', () => {
  const now = at(2026, 10, 21);
  const l = previewLabels(newCard(), now);
  assert.deepEqual(l, { again: '10분', hard: '1일', good: '1일', easy: '2일' });
});

test('formatInterval', () => {
  assert.equal(formatInterval(1), '1일');
  assert.equal(formatInterval(15), '2주');
  assert.equal(formatInterval(30), '1개월');
  assert.equal(formatInterval(60), '2개월');
  assert.equal(formatInterval(400), '1.1년');
});
