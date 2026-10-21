import { dayNumber, schedule, previewLabels, newCard } from './scheduler.js';
import { dailyCounts, streak, retention, forecast, heatLevel } from './stats.js';
import * as db from './db.js';

const $ = (s) => document.querySelector(s);
const view = $('#view'), titleEl = $('#title'), backBtn = $('#back'), actionsEl = $('#actions');
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const DEFAULT_NEW = 20;
let session = null;

/* ---------- UI helpers ---------- */
let toastTimer;
function toast(msg, err = false) {
  const t = $('#toast');
  t.textContent = msg;
  t.className = 'show' + (err ? ' toast-err' : '');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { t.className = ''; }, err ? 4000 : 1800);
}
const guard = (fn) => async (...a) => {
  try { return await fn(...a); } catch (e) { console.error(e); toast(e.message || '오류가 발생했습니다.', true); }
};

// fields: [{key,label,value,multiline,rows}] → 확인 시 값 객체, 취소 시 null
function form(title, fields, { okLabel = '확인', extra } = {}) {
  const dlg = $('#dlg');
  $('#dlgTitle').textContent = title;
  $('#dlgOk').textContent = okLabel;
  $('#dlgBody').innerHTML = fields.map((f, i) => `<div class="field"><label for="f${i}">${esc(f.label)}</label>${
    f.multiline
      ? `<textarea class="input" id="f${i}" rows="${f.rows || 3}">${esc(f.value || '')}</textarea>`
      : `<input class="input" id="f${i}" value="${esc(f.value || '')}" autocomplete="off">`}</div>`).join('')
    + (extra ? `<div class="row" style="margin-bottom:12px">${extra}</div>` : '');
  return new Promise((resolve) => {
    dlg.onclose = () => {
      const vals = dlg.returnValue === 'ok'
        ? Object.fromEntries(fields.map((f, i) => [f.key, $('#f' + i).value])) : null;
      dlg.returnValue = '';
      resolve(vals);
    };
    dlg.showModal();
    $('#f0').focus();
  });
}
const confirmBox = async (msg, okLabel = '삭제') => {
  const dlg = $('#dlg');
  $('#dlgTitle').textContent = msg;
  $('#dlgBody').innerHTML = '';
  $('#dlgOk').textContent = okLabel;
  return new Promise((resolve) => {
    dlg.onclose = () => { const ok = dlg.returnValue === 'ok'; dlg.returnValue = ''; resolve(ok); };
    dlg.showModal();
  });
};

function chrome({ title, back, actions = '' }) {
  titleEl.textContent = title;
  backBtn.hidden = !back;
  backBtn.onclick = () => { location.hash = back; };
  actionsEl.innerHTML = actions;
}
const today = () => dayNumber(Date.now());

/* ---------- 데이터 헬퍼 ---------- */
async function deckStats() {
  const [decks, cards, logs, limit] = await Promise.all([
    db.getAll('decks'), db.getAll('cards'), db.getAll('logs'), db.getSetting('newPerDay', DEFAULT_NEW)]);
  const t = today();
  const introduced = new Map();
  for (const l of logs) {
    if (dayNumber(l.ts) === t && l.prev && l.prev.stage < 0) {
      if (!introduced.has(l.deckId)) introduced.set(l.deckId, new Set());
      introduced.get(l.deckId).add(l.cardId);
    }
  }
  return { cards, logs, limit, decks: decks.map((d) => {
    const mine = cards.filter((c) => c.deckId === d.id);
    const fresh = mine.filter((c) => c.stage < 0).length;
    const left = Math.max(0, limit - (introduced.get(d.id)?.size || 0));
    return { ...d, total: mine.length, newN: Math.min(fresh, left), dueN: mine.filter((c) => c.stage >= 0 && c.due <= t).length };
  }) };
}

/* ---------- 홈 ---------- */
async function renderHome() {
  chrome({ title: '복습', actions: `<button class="icon" data-go="#/stats" aria-label="통계">📊</button><button class="icon" data-go="#/settings" aria-label="설정">⚙️</button>` });
  const { decks } = await deckStats();
  if (!decks.length) {
    view.innerHTML = `<div class="empty"><div class="big">🧠</div><h2>첫 덱을 만들어 보세요</h2>
      <p>덱은 과목이나 주제 묶음이에요.<br>카드를 넣고 복습하면 잊기 전에 알려 드려요.</p>
      <button class="primary" id="newDeck">덱 만들기</button></div>`;
  } else {
    const c = (n, cls) => `<span class="${cls} ${n ? '' : 'zero'}">${n}</span>`;
    view.innerHTML = `<div class="list">${decks.map((d) => `
      <div class="item" role="button" tabindex="0" data-go="#/review/${d.id}">
        <div class="name">${esc(d.name)}<div class="sub">카드 ${d.total}장</div></div>
        <div class="counts" title="새 카드 · 복습">${c(d.newN, 'n-new')}${c(d.dueN, 'n-rev')}</div>
        <button class="icon" data-go="#/deck/${d.id}" aria-label="카드 관리">☰</button>
      </div>`).join('')}</div>
      <p class="hint">파랑 = 새 카드, 초록 = 오늘 복습할 카드</p>
      <button class="fab" id="newDeck" aria-label="덱 추가">＋</button>`;
  }
}
const createDeck = guard(async () => {
  const v = await form('새 덱 이름', [{ key: 'name', label: '이름', value: '' }], { okLabel: '만들기' });
  if (!v || !v.name.trim()) return;
  const id = await db.put('decks', { name: v.name.trim(), createdAt: Date.now() });
  location.hash = '#/deck/' + id;
});

/* ---------- 덱(카드 관리) ---------- */
async function renderDeck(id, { mode = 'one', q = '' } = {}) {
  const decks = await db.getAll('decks');
  const deck = decks.find((d) => d.id === id);
  if (!deck) { location.hash = '#/'; return; }
  chrome({ title: deck.name, back: '#/', actions: `<button class="icon" id="deckMenu" aria-label="덱 설정">⋯</button>` });
  const cards = (await db.getAll('cards')).filter((c) => c.deckId === id).sort((a, b) => b.id - a.id);
  const shown = q ? cards.filter((c) => (c.front + c.back).toLowerCase().includes(q.toLowerCase())) : cards;
  view.innerHTML = `
    <div class="seg"><button data-mode="one" class="${mode === 'one' ? 'on' : ''}">카드 1장</button><button data-mode="bulk" class="${mode === 'bulk' ? 'on' : ''}">여러 장 붙여넣기</button></div>
    ${mode === 'one' ? `
      <div class="field"><label for="cFront">앞면 (질문)</label><textarea class="input" id="cFront" rows="2"></textarea></div>
      <div class="field"><label for="cBack">뒷면 (정답)</label><textarea class="input" id="cBack" rows="3"></textarea></div>
      <button class="primary" id="addOne" style="width:100%">카드 추가</button>`
    : `<div class="field"><label for="bulk">한 줄에 한 장 — 앞면 ; 뒷면 (또는 탭으로 구분)</label>
        <textarea class="input" id="bulk" rows="7" placeholder="apple ; 사과&#10;banana ; 바나나"></textarea></div>
        <button class="primary" id="addBulk" style="width:100%">한 번에 추가</button>`}
    <div class="section">카드 ${cards.length}장</div>
    ${cards.length > 6 ? `<input class="input" id="search" placeholder="검색" value="${esc(q)}" style="margin-bottom:10px">` : ''}
    <div class="list">${shown.map((c) => `<button class="cardrow" data-edit="${c.id}"><div class="f">${esc(c.front)}</div><div class="b">${esc(c.back)}</div>
      <div class="m">${c.stage < 0 ? '새 카드' : '다음 복습 ' + dueLabel(c.due)}</div></button>`).join('')}</div>`;
  view.dataset.deck = id; view.dataset.mode = mode;
  if (mode === 'one') $('#cFront').focus();
}
function dueLabel(due) {
  const diff = due - today();
  return diff <= 0 ? '오늘' : diff === 1 ? '내일' : `${diff}일 뒤`;
}
const addOne = guard(async (deckId) => {
  const front = $('#cFront').value.trim(), back = $('#cBack').value.trim();
  if (!front || !back) return toast('앞면과 뒷면을 모두 입력하세요.', true);
  await db.put('cards', { deckId, front, back, ...newCard(), createdAt: Date.now() });
  toast('추가했어요');
  await renderDeck(deckId);
});
const addBulk = guard(async (deckId) => {
  const rows = $('#bulk').value.split('\n').map((l) => l.trim()).filter(Boolean).map((l) => {
    const i = l.includes('\t') ? l.indexOf('\t') : l.indexOf(';');
    return i < 0 ? null : [l.slice(0, i).trim(), l.slice(i + 1).trim()];
  });
  const ok = rows.filter((r) => r && r[0] && r[1]);
  if (!ok.length) return toast('형식: 앞면 ; 뒷면 (한 줄에 한 장)', true);
  await db.putMany('cards', ok.map(([front, back]) => ({ deckId, front, back, ...newCard(), createdAt: Date.now() })));
  const skipped = rows.length - ok.length;
  toast(`${ok.length}장 추가${skipped ? `, ${skipped}줄은 형식이 달라 건너뜀` : ''}`);
  await renderDeck(deckId);
});
let editing = null; // 수정 다이얼로그에서 삭제 버튼이 참조
const editCard = guard(async (cardId, deckId) => {
  const card = (await db.getAll('cards')).find((c) => c.id === cardId);
  if (!card) return;
  editing = { cardId, deckId };
  const v = await form('카드 수정', [
    { key: 'front', label: '앞면', value: card.front, multiline: true, rows: 3 },
    { key: 'back', label: '뒷면', value: card.back, multiline: true, rows: 4 }],
  { okLabel: '저장', extra: `<button type="button" class="danger" id="delCard">카드 삭제</button>` });
  if (v && v.front.trim() && v.back.trim()) {
    await db.put('cards', { ...card, front: v.front.trim(), back: v.back.trim() });
    await renderDeck(deckId);
  }
});
const deckMenu = guard(async (deckId) => {
  const deck = (await db.getAll('decks')).find((d) => d.id === deckId);
  const v = await form('덱 이름 변경', [{ key: 'name', label: '이름', value: deck.name }],
    { okLabel: '저장', extra: `<button type="button" class="danger" id="delDeck">덱 삭제</button>` });
  if (v && v.name.trim()) { await db.put('decks', { ...deck, name: v.name.trim() }); await renderDeck(deckId); }
});

/* ---------- 복습 ---------- */
const guardRender = guard(async () => { await route(); });

async function startReview(deckId) {
  const { decks, cards } = await deckStats();
  const deck = decks.find((d) => d.id === deckId);
  if (!deck) { location.hash = '#/'; return; }
  const t = today();
  const due = cards.filter((c) => c.deckId === deckId && c.stage >= 0 && c.due <= t).sort((a, b) => a.due - b.due || a.id - b.id);
  const fresh = cards.filter((c) => c.deckId === deckId && c.stage < 0).sort((a, b) => a.id - b.id).slice(0, deck.newN);
  session = { deckId, name: deck.name, queue: [...due, ...fresh], relearn: [], undo: [], revealed: false, total: due.length + fresh.length, done: 0, current: null };
}

function pickNext() {
  const s = session, now = Date.now();
  const ready = s.relearn.findIndex((r) => r.at <= now);
  if (ready >= 0) return { card: s.relearn[ready].card, relearn: true };
  if (s.queue.length) return { card: s.queue[0], relearn: false };
  if (s.relearn.length) { const r = [...s.relearn].sort((a, b) => a.at - b.at)[0]; return { card: r.card, relearn: true }; }
  return null;
}

function renderReview() {
  const s = session;
  chrome({ title: s.name, back: '#/', actions: `<button class="icon" id="undo" aria-label="실행 취소" ${s.undo.length ? '' : 'disabled style="opacity:.3"'}>↩︎</button>` });
  const cur = (s.current = pickNext());
  if (!cur) {
    view.innerHTML = `<div class="empty"><div class="big">${s.total ? '🎉' : '✨'}</div>
      <h2>${s.total ? '오늘 복습 끝!' : '지금 복습할 카드가 없어요'}</h2>
      <p>${s.total ? `${s.done}번 복습했어요. 내일 또 만나요.` : '새 카드를 추가하거나 내일 다시 확인하세요.'}</p>
      <button class="primary" data-go="#/">덱 목록으로</button></div>`;
    return;
  }
  const left = s.queue.length + s.relearn.length;
  const pct = s.total ? Math.min(100, (s.done / (s.done + left)) * 100) : 0;
  const nNew = s.queue.filter((c) => c.stage < 0).length, nRel = s.relearn.length, nRev = s.queue.length - nNew;
  s.revealed = false;
  view.innerHTML = `<div class="stage">
    <div class="progress"><i style="width:${pct}%"></i></div>
    <div class="review-top"><div class="counts"><span class="n-new">${nNew}</span><span class="n-learn">${nRel}</span><span class="n-rev">${nRev}</span></div></div>
    <div class="scene"><div class="flip" id="flip">
      <div class="face front">${esc(cur.card.front)}</div>
      <div class="face back"><div class="q">${esc(cur.card.front)}</div>${esc(cur.card.back)}</div>
    </div></div>
    <div class="dock" id="dock"><button class="primary reveal" id="show">정답 보기</button><div class="keys">Space 정답 · 1 다시 · 2 어려움 · 3 좋음 · 4 쉬움 · Z 취소</div></div></div>`;
}
function reveal() {
  const s = session;
  if (!s || !s.current || s.revealed) return;
  s.revealed = true;
  $('#flip').classList.add('on');
  const l = previewLabels(s.current.card);
  const lab = s.current.relearn ? { again: '10분', hard: '내일', good: '내일', easy: '내일' } : l;
  $('#dock').innerHTML = `<div class="rate">
    <button class="r-again" data-rate="again">다시<small>${lab.again}</small></button>
    <button class="r-hard" data-rate="hard">어려움<small>${lab.hard}</small></button>
    <button class="r-good" data-rate="good">좋음<small>${lab.good}</small></button>
    <button class="r-easy" data-rate="easy">쉬움<small>${lab.easy}</small></button></div>`;
}
const rate = guard(async (rating) => {
  const s = session;
  if (!s || !s.current || !s.revealed) return;
  const { card, relearn } = s.current;
  const now = Date.now();
  const prev = { stage: card.stage, due: card.due, reps: card.reps, lapses: card.lapses };
  // 학습 중(10분 재출제) 카드를 통과시키면 일정은 그대로 두고 기록만 남긴다
  const graduate = relearn && rating !== 'again';
  const entry = { prev, card: { ...card }, wasRelearn: relearn, dbChanged: !graduate };
  let saved = card, relearnAt;
  if (!graduate) {
    const r = schedule(card, rating, now);
    saved = { ...card, ...r.card };
    relearnAt = r.relearnAt;
    await db.put('cards', saved);
  }
  entry.logId = await db.put('logs', { cardId: card.id, deckId: card.deckId, ts: now, rating, prev });
  s.queue = s.queue.filter((c) => c.id !== card.id);
  s.relearn = s.relearn.filter((r) => r.card.id !== card.id);
  if (relearnAt) s.relearn.push({ card: saved, at: relearnAt });
  s.undo.push(entry);
  s.done++;
  renderReview();
});
const undo = guard(async () => {
  const s = session;
  const e = s && s.undo.pop();
  if (!e) return;
  const restored = { ...e.card, ...e.prev };
  await db.del('logs', e.logId);
  if (e.dbChanged) await db.put('cards', restored);
  s.relearn = s.relearn.filter((r) => r.card.id !== restored.id);
  if (e.wasRelearn) s.relearn.unshift({ card: restored, at: 0 });
  else s.queue.unshift(restored);
  s.done = Math.max(0, s.done - 1);
  renderReview();
});

/* ---------- 통계 ---------- */
async function renderStats() {
  chrome({ title: '통계', back: '#/' });
  const [cards, logs] = await Promise.all([db.getAll('cards'), db.getAll('logs')]);
  const t = today();
  const counts = dailyCounts(logs);
  const ret = retention(logs, t);
  const fc = forecast(cards, t, 7);
  const max = Math.max(1, ...fc);
  const WEEKS = 12;
  const dow = new Date(Date.UTC(1970, 0, 1) + t * 86400000).getUTCDay(); // 오늘 요일 (0=일)
  const start = t - dow - (WEEKS - 1) * 7;
  const cells = [];
  for (let d = start; d <= t - dow + 6; d++) {
    cells.push(`<i class="${d > t ? 'future' : 'l' + heatLevel(counts.get(d) || 0)}" title="${counts.get(d) || 0}회"></i>`);
  }
  const names = ['일', '월', '화', '수', '목', '금', '토'];
  view.innerHTML = `
    <div class="tiles">
      <div class="tile"><b>${counts.get(t) || 0}</b><span>오늘 복습</span></div>
      <div class="tile"><b>${streak(counts, t)}🔥</b><span>연속 학습일</span></div>
      <div class="tile"><b>${ret === null ? '–' : Math.round(ret * 100) + '%'}</b><span>유지율 (30일)</span></div>
    </div>
    <div class="section">앞으로 7일 복습 예정</div>
    <div class="panel"><div class="bars">${fc.map((n, i) => `<div><span class="v">${n}</span><i style="height:${(n / max) * 80}px"></i><span>${i === 0 ? '오늘' : names[(dow + i) % 7]}</span></div>`).join('')}</div></div>
    <div class="section">최근 12주 학습</div>
    <div class="panel"><div class="heat">${cells.join('')}</div></div>
    <div class="section">카드 현황</div>
    <div class="panel hint" style="margin:0">전체 ${cards.length}장 · 새 카드 ${cards.filter((c) => c.stage < 0).length} · 학습 중 ${cards.filter((c) => c.stage >= 0 && c.stage < 4).length} · 장기 기억 ${cards.filter((c) => c.stage >= 4).length}</div>`;
}

/* ---------- 설정 ---------- */
async function renderSettings() {
  chrome({ title: '설정', back: '#/' });
  const limit = await db.getSetting('newPerDay', DEFAULT_NEW);
  view.innerHTML = `
    <div class="field"><label for="npd">하루 새 카드 수 (덱마다)</label><input class="input" id="npd" type="number" inputmode="numeric" min="0" max="999" value="${limit}"></div>
    <div class="section">복습 간격 (에빙하우스)</div>
    <div class="panel hint" style="margin:0 0 8px">1일 → 2일 → 4일 → 7일 → 15일 → 30일 → 60일 → 이후 2배씩.<br>좋음은 한 단계, 쉬움은 두 단계 올라가고, 어려움은 같은 간격을 반복하며, 다시는 처음 단계로 돌아갑니다.</div>
    <div class="section">백업</div>
    <div class="list">
      <button class="ghost" id="export">📤 내보내기 (JSON)</button>
      <button class="ghost" id="import">📥 가져오기</button>
      <input type="file" id="file" accept="application/json,.json" hidden>
      <button class="danger" id="wipe">모든 데이터 삭제</button>
    </div>
    <p class="hint">데이터는 이 기기의 브라우저에만 저장돼요. 기기를 바꾸거나 정기 백업할 때 내보내기를 쓰세요.</p>`;
}
const exportData = guard(async () => {
  const data = JSON.stringify(await db.exportAll(), null, 1);
  const name = `복습백업-${new Date().toISOString().slice(0, 10)}.json`;
  const file = new File([data], name, { type: 'application/json' });
  if (navigator.canShare && navigator.canShare({ files: [file] })) {
    try { await navigator.share({ files: [file] }); return; } catch (e) { if (e.name === 'AbortError') return; }
  }
  const a = document.createElement('a');
  a.href = URL.createObjectURL(file); a.download = name;
  document.body.append(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 5000);
  toast('내보냈어요');
});
const importData = guard(async (file) => {
  let data;
  try { data = JSON.parse(await file.text()); } catch { throw new Error('가져오기 실패: JSON 파일이 아닙니다.'); }
  db.validateImport(data);
  if (!(await confirmBox('현재 데이터를 모두 지우고 이 파일로 바꿀까요?', '바꾸기'))) return;
  await db.replaceAll(data);
  toast(`카드 ${data.cards.length}장을 가져왔어요`);
  location.hash = '#/';
});

/* ---------- 라우터 ---------- */
async function route() {
  const [, page, arg] = (location.hash || '#/').split('/');
  const id = Number(arg);
  if (page !== 'review') session = null;
  if (page === 'review') {
    if (!session || session.deckId !== id) await startReview(id);
    if (session) renderReview();
  } else if (page === 'deck') await renderDeck(id);
  else if (page === 'stats') await renderStats();
  else if (page === 'settings') await renderSettings();
  else await renderHome();
  window.scrollTo(0, 0);
}

/* ---------- 이벤트 ---------- */
document.addEventListener('click', guard(async (e) => {
  const t = e.target.closest('button, [data-go]');
  if (!t) return;
  const set = (k) => t.dataset[k];
  if (t.id === 'dlgCancel') return;
  if (set('go')) { e.stopPropagation(); location.hash = set('go'); return; }
  if (t.id === 'newDeck') return createDeck();
  if (t.id === 'show') return reveal();
  if (set('rate')) return rate(set('rate'));
  if (t.id === 'undo') return undo();
  const deckId = Number(view.dataset.deck);
  if (set('mode')) return renderDeck(deckId, { mode: set('mode') });
  if (t.id === 'addOne') return addOne(deckId);
  if (t.id === 'addBulk') return addBulk(deckId);
  if (set('edit')) return editCard(Number(set('edit')), deckId);
  if (t.id === 'deckMenu') return deckMenu(deckId);
  if (t.id === 'export') return exportData();
  if (t.id === 'import') return $('#file').click();
  if (t.id === 'wipe') {
    if (await confirmBox('모든 덱과 카드, 기록을 삭제할까요? 되돌릴 수 없어요.', '모두 삭제')) { await db.resetAll(); toast('삭제했어요'); location.hash = '#/'; await route(); }
  }
}));
document.addEventListener('change', guard(async (e) => {
  if (e.target.id === 'file' && e.target.files[0]) { const f = e.target.files[0]; e.target.value = ''; await importData(f); }
  if (e.target.id === 'npd') {
    const n = Math.max(0, Math.min(999, parseInt(e.target.value, 10) || 0));
    await db.setSetting('newPerDay', n); e.target.value = n; toast('저장했어요');
  }
}));
document.addEventListener('input', (e) => {
  if (e.target.id === 'search') {
    const pos = e.target.selectionStart;
    renderDeck(Number(view.dataset.deck), { mode: view.dataset.mode, q: e.target.value }).then(() => {
      const s = $('#search'); if (s) { s.focus(); s.setSelectionRange(pos, pos); }
    });
  }
});
document.addEventListener('keydown', (e) => {
  if ($('#dlg').open || /^(INPUT|TEXTAREA)$/.test(e.target.tagName) || e.metaKey || e.ctrlKey) return;
  if (!session || !location.hash.startsWith('#/review')) {
    if (e.key === 'Enter' && e.target.dataset?.go) location.hash = e.target.dataset.go;
    return;
  }
  if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); session.revealed ? rate('good') : reveal(); }
  else if (e.key === 'z' || e.key === 'Z') undo();
  else if (session.revealed && '1234'.includes(e.key) && e.key) rate(['again', 'hard', 'good', 'easy'][Number(e.key) - 1]);
});
window.addEventListener('hashchange', guardRender);

// 덱 수정/카드 수정 다이얼로그 안의 삭제 버튼
$('#dlgBody').addEventListener('click', guard(async (e) => {
  const b = e.target.closest('#delCard, #delDeck');
  if (!b) return;
  const deckId = Number(view.dataset.deck);
  if (b.id === 'delDeck') {
    if (!(await confirmAfterClose('이 덱과 안의 카드를 모두 삭제할까요?'))) return;
    await db.deleteDeck(deckId); location.hash = '#/';
  } else if (editing) {
    if (!(await confirmAfterClose('이 카드를 삭제할까요?'))) return;
    await db.del('cards', editing.cardId);
    await renderDeck(editing.deckId);
  }
}));
function confirmAfterClose(msg) {
  $('#dlg').close('cancel');
  return new Promise((r) => setTimeout(() => r(confirmBox(msg)), 30));
}

/* ---------- 시작 ---------- */
guard(async () => {
  await db.open();
  if (navigator.storage?.persist) navigator.storage.persist().catch(() => {});
  await route();
  if ('serviceWorker' in navigator) navigator.serviceWorker.register('sw.js').catch(() => {});
})();
