// IndexedDB 래퍼 + 내보내기/가져오기
const NAME = 'reviewer';
const VERSION = 1;
const STORES = ['decks', 'cards', 'logs', 'meta'];
let dbp;

export function open() {
  if (dbp) return dbp;
  dbp = new Promise((resolve, reject) => {
    if (!('indexedDB' in window)) return reject(new Error('이 브라우저는 저장소(IndexedDB)를 지원하지 않습니다.'));
    const r = indexedDB.open(NAME, VERSION);
    r.onupgradeneeded = () => {
      const d = r.result;
      d.createObjectStore('decks', { keyPath: 'id', autoIncrement: true });
      d.createObjectStore('cards', { keyPath: 'id', autoIncrement: true }).createIndex('deckId', 'deckId');
      d.createObjectStore('logs', { keyPath: 'id', autoIncrement: true }).createIndex('ts', 'ts');
      d.createObjectStore('meta', { keyPath: 'key' });
    };
    r.onsuccess = () => resolve(r.result);
    r.onerror = () => reject(r.error);
  });
  return dbp;
}

const req = (r) => new Promise((res, rej) => { r.onsuccess = () => res(r.result); r.onerror = () => rej(r.error); });

async function run(stores, mode, fn) {
  const db = await open();
  return new Promise((resolve, reject) => {
    const t = db.transaction(stores, mode);
    let out;
    Promise.resolve(fn(t)).then((v) => { out = v; }, reject);
    t.oncomplete = () => resolve(out);
    t.onabort = t.onerror = () => reject(t.error || new Error('저장에 실패했습니다.'));
  });
}

export const getAll = (store) => run(store, 'readonly', (t) => req(t.objectStore(store).getAll()));
export const put = (store, obj) => run(store, 'readwrite', (t) => req(t.objectStore(store).put(obj)));
export const del = (store, id) => run(store, 'readwrite', (t) => req(t.objectStore(store).delete(id)));

export function putMany(store, objs) {
  return run(store, 'readwrite', async (t) => {
    const s = t.objectStore(store);
    const keys = [];
    for (const o of objs) keys.push(await req(s.put(o)));
    return keys;
  });
}

export function deleteDeck(id) {
  return run(['decks', 'cards', 'logs'], 'readwrite', async (t) => {
    const cards = await req(t.objectStore('cards').index('deckId').getAllKeys(id));
    for (const k of cards) t.objectStore('cards').delete(k);
    const logs = await req(t.objectStore('logs').getAll());
    for (const l of logs) if (l.deckId === id) t.objectStore('logs').delete(l.id);
    t.objectStore('decks').delete(id);
  });
}

export async function getSetting(key, fallback) {
  const rows = await run('meta', 'readonly', (t) => req(t.objectStore('meta').get(key)));
  return rows ? rows.value : fallback;
}
export const setSetting = (key, value) => put('meta', { key, value });

export async function exportAll() {
  const [decks, cards, logs, meta] = await Promise.all(STORES.map(getAll));
  return { app: 'ebbinghaus-cards', version: 1, exportedAt: new Date().toISOString(), decks, cards, logs, meta };
}

export function validateImport(d) {
  const bad = (m) => { throw new Error('가져오기 실패: ' + m); };
  if (!d || d.app !== 'ebbinghaus-cards') bad('이 앱에서 내보낸 파일이 아닙니다.');
  if (d.version !== 1) bad('지원하지 않는 버전입니다.');
  for (const k of ['decks', 'cards', 'logs', 'meta']) if (!Array.isArray(d[k])) bad(`${k} 항목이 없습니다.`);
  const ids = new Set();
  for (const x of d.decks) {
    if (!Number.isInteger(x.id) || typeof x.name !== 'string') bad('덱 데이터가 올바르지 않습니다.');
    ids.add(x.id);
  }
  const num = Number.isFinite;
  for (const c of d.cards) {
    if (!Number.isInteger(c.id) || !ids.has(c.deckId) || typeof c.front !== 'string' || typeof c.back !== 'string'
      || !num(c.stage) || !num(c.due) || !num(c.reps) || !num(c.lapses)) bad('카드 데이터가 올바르지 않습니다.');
  }
  for (const l of d.logs) if (!num(l.ts) || typeof l.rating !== 'string') bad('기록 데이터가 올바르지 않습니다.');
  for (const m of d.meta) if (typeof m.key !== 'string') bad('설정 데이터가 올바르지 않습니다.');
}

// 검증을 통과한 데이터로 전체 교체 (한 트랜잭션: 실패 시 기존 데이터 유지)
export function replaceAll(d) {
  validateImport(d);
  return run(STORES, 'readwrite', async (t) => {
    for (const s of STORES) {
      const os = t.objectStore(s);
      os.clear();
      for (const o of d[s]) os.put(o);
    }
  });
}

export const resetAll = () => replaceAll({ app: 'ebbinghaus-cards', version: 1, decks: [], cards: [], logs: [], meta: [] });
