import test from 'node:test';
import assert from 'node:assert/strict';
import { dailyCounts, streak, retention, forecast, heatLevel } from './stats.js';
import { dayNumber } from './scheduler.js';

const ts = (d, h = 12) => new Date(2026, 9, d, h).getTime();
const T = dayNumber(ts(21));

test('streak: 오늘 안 했어도 어제까지 연속이면 유지', () => {
  const logs = [ts(19), ts(20)].map((t) => ({ ts: t, rating: 'good' }));
  assert.equal(streak(dailyCounts(logs), T), 2);
  logs.push({ ts: ts(21), rating: 'good' });
  assert.equal(streak(dailyCounts(logs), T), 3);
  assert.equal(streak(dailyCounts([{ ts: ts(18), rating: 'good' }]), T), 0);
});

test('retention', () => {
  assert.equal(retention([], T), null);
  const logs = ['good', 'easy', 'again', 'hard'].map((r) => ({ ts: ts(20), rating: r }));
  assert.equal(retention(logs, T), 0.75);
});

test('forecast: 밀린 카드는 오늘에 합산, 새 카드 제외', () => {
  const cards = [
    { stage: 1, due: T - 3 }, { stage: 1, due: T }, { stage: 2, due: T + 2 },
    { stage: 2, due: T + 9 }, { stage: -1, due: 0 },
  ];
  assert.deepEqual(forecast(cards, T, 7), [2, 0, 1, 0, 0, 0, 0]);
});

test('heatLevel', () => {
  assert.deepEqual([0, 1, 5, 15, 30].map(heatLevel), [0, 1, 2, 3, 4]);
});
