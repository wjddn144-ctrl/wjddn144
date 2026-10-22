# 한 번만 실행하면 30분마다 자동으로 새 영상을 C:\Users\wjddn\Videos\클로드영상 으로 받아옵니다.
$base = "C:\Users\wjddn\Videos"
$dest = Join-Path $base "클로드영상"
New-Item -ItemType Directory -Force -Path $dest | Out-Null

$sync = @'
$dest = "C:\Users\wjddn\Videos\클로드영상"
$tmp  = Join-Path $env:TEMP "gwangsan-videos"
if (Test-Path $tmp) { Remove-Item -Recurse -Force $tmp }
git clone --depth 1 --branch claude/adoring-faraday-cx3ol9 https://github.com/wjddn144-ctrl/wjddn144.git $tmp
if (Test-Path "$tmp\다운로드") { Copy-Item "$tmp\다운로드\*.mp4" $dest -Force }
Remove-Item -Recurse -Force $tmp
'@
$syncPath = Join-Path $base "클로드영상_동기화.ps1"
[System.IO.File]::WriteAllText($syncPath, $sync, (New-Object System.Text.UTF8Encoding($true)))

schtasks /Create /F /SC MINUTE /MO 30 /TN "클로드영상 자동동기화" /TR "powershell -NoProfile -ExecutionPolicy Bypass -File `"$syncPath`""
& powershell -NoProfile -ExecutionPolicy Bypass -File $syncPath
Write-Host "완료: 지금 한 번 받아왔고, 이후 30분마다 자동으로 받아옵니다."
explorer $dest
