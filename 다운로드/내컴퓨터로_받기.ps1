# 광산장년회 응원 영상을 내 컴퓨터 폴더로 받아오는 스크립트
$dest = "C:\Users\wjddn\Videos\클로드영상"
$tmp  = Join-Path $env:TEMP "gwangsan-videos"

New-Item -ItemType Directory -Force -Path $dest | Out-Null
if (Test-Path $tmp) { Remove-Item -Recurse -Force $tmp }

git clone --depth 1 --branch claude/adoring-faraday-cx3ol9 https://github.com/wjddn144-ctrl/wjddn144.git $tmp
Copy-Item "$tmp\다운로드\*.mp4" $dest -Force
Remove-Item -Recurse -Force $tmp

Write-Host "완료: $dest"
explorer $dest
