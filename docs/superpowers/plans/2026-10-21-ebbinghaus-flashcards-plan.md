# 구현 계획

스펙: `docs/superpowers/specs/2026-10-21-ebbinghaus-flashcards-design.md`

1. `app/scheduler.js` + `app/scheduler.test.js` — TDD로 먼저 (Red → Green).
2. `app/db.js` — IndexedDB 래퍼(덱/카드/로그/설정, 내보내기·가져오기 검증).
3. `app/index.html`, `app/style.css` — 모바일 우선, 다크 모드, 안전영역.
4. `app/app.js` — 라우팅과 5개 화면, 복습 큐(새 카드 제한, 재출제), 실행 취소, 단축키.
5. PWA: `manifest.webmanifest`, `sw.js`, 아이콘.
6. Playwright로 아이폰 크기 E2E 확인, 스크린샷 점검.
7. 커밋 후 브랜치에 push, README에 아이폰 설치 방법 기재.
