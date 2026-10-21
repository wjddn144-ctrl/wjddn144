// 모든 모듈을 합쳐 더블클릭으로 열리는 단일 파일 review.html 생성: node build-single.mjs
import { readFileSync, writeFileSync } from 'node:fs';
const read = (f) => readFileSync(new URL(f, import.meta.url), 'utf8');
const strip = (s) => s.replace(/^import .*$/gm, '').replace(/^export (async function|function|const|let)/gm, '$1');

const dbNames = ['open', 'getAll', 'put', 'del', 'putMany', 'deleteDeck', 'getSetting', 'setSetting', 'exportAll', 'validateImport', 'replaceAll', 'resetAll'];
const js = [
  strip(read('scheduler.js')),
  strip(read('stats.js')),
  `const db = (() => {\n${strip(read('db.js'))}\nreturn { ${dbNames.join(', ')} };\n})();`,
  strip(read('app.js')),
].join('\n');

const svg = encodeURIComponent(read('icon.svg').trim());
const html = read('index.html')
  .replace(/<link rel="manifest".*\n/, '')
  .replace(/<link rel="apple-touch-icon".*\n/, '')
  .replace(/<link rel="icon".*\n/, `<link rel="icon" href="data:image/svg+xml,${svg}">\n`)
  .replace('<link rel="stylesheet" href="style.css">', () => `<style>\n${read('style.css')}</style>`)
  .replace('<script type="module" src="app.js"></script>', () => `<script type="module">\n${js}\n</script>`);
writeFileSync(new URL('review.html', import.meta.url), html);
console.log('review.html', Math.round(html.length / 1024) + 'KB');
