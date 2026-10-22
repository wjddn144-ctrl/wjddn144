# 광산장년회 응원 영상 제작 도구

옛날 TV 광고 영상에 광산장년회 응원 자막, 로고 교체, 카메라 효과, 엔딩 화면을 입히는 스크립트 모음입니다.
(클라우드 세션에서 만든 것이라 경로가 `/tmp/...`로 되어 있습니다. 내 컴퓨터에서 쓰려면 각 파일 맨 위의 `S=` 경로와
`/root/.claude/uploads/...` 같은 원본 영상 경로를 내 컴퓨터 경로로 바꿔야 합니다.)

## 필요한 것
- Python 3.10 이상, ffmpeg (`winget install Gyan.FFmpeg`)
- `pip install pillow numpy opencv-python-headless faster-whisper`
- 글씨체 (구글 폰트): Black Han Sans, Do Hyeon, Jua, Gaegu, Song Myung, East Sea Dokdo, Single Day, Gugi / 나눔 글꼴(나눔스퀘어, 나눔명조, 나눔붓, 나눔펜)

## 파일 설명
| 파일 | 만든 영상 |
|---|---|
| gen.py | 따봉(델몬트) |
| gen3.py + plate.py | 티코 (번호판 1004 교체는 plate.py) |
| gen_mc.py, gen_gb.py, gen_gb2.py | 엠씨스퀘어 구역장님 / 총무부(영화 엔딩은 epic_end.py + gen_gb2.py) |
| gen_hm2.py | 하이마트 |
| gen_en.py + patch_en.py | 에너자이저 |
| gen_sp.py + assets_sp.py | 솔표(판소리) |
| gen_dd.py + patch_dd.py | 다시다 |
| gen_gt.py + patch_gt.py | 게토레이 |
| gen_mc10.py + patch_mc.py | 잘했군 잘했어 |

## 작업 규칙 (지금까지 정한 것)
- 자막은 원래 음성 그대로. 상품 이름만 광산장년회/구역장님 이야기로 바꿈
- 오른쪽(또는 왼쪽) 위 귀퉁이에 "광산장년회" 표기
- 영상에 원본 광고 음성이 그대로 있으므로 구역 모임 안에서만 공유
- 오디오가 두 개 이상이면 한국어 트랙만 사용 (영어 더빙 섞이지 않게)
- 만든 영상은 항상 `C:\Users\wjddn\Videos\클로드영상` 에 저장
