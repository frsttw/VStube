$ErrorActionPreference = 'Stop'
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$toolsDir = Join-Path $projectDir 'assets\tools'
New-Item -ItemType Directory -Force $toolsDir | Out-Null

function Find-WinGetTool([string]$name, [string]$packagePattern) {
    $root = Join-Path $env:LOCALAPPDATA 'Microsoft\WinGet\Packages'
    $match = Get-ChildItem $root -Filter "$name.exe" -Recurse -ErrorAction SilentlyContinue |
        Where-Object FullName -Like "*$packagePattern*" |
        Select-Object -First 1 -ExpandProperty FullName
    if (-not $match) { throw "$name was not found. Install the dependencies listed in the README." }
    return $match
}

$ytdlpPath = Join-Path $toolsDir 'yt-dlp.exe'
Copy-Item (Find-WinGetTool 'yt-dlp' 'yt-dlp.yt-dlp') $ytdlpPath -Force
# YouTube changes media endpoints frequently; bundle the latest nightly
# correction with every installer.
& $ytdlpPath --update-to nightly
if ($LASTEXITCODE -ne 0) { throw 'Could not update yt-dlp to a compatible version.' }
Copy-Item (Find-WinGetTool 'ffmpeg' 'Gyan.FFmpeg') (Join-Path $toolsDir 'ffmpeg.exe') -Force
Copy-Item (Find-WinGetTool 'ffprobe' 'Gyan.FFmpeg') (Join-Path $toolsDir 'ffprobe.exe') -Force
Copy-Item (Find-WinGetTool 'deno' 'DenoLand.Deno') (Join-Path $toolsDir 'deno.exe') -Force

Push-Location $projectDir
try {
    python -m unittest test_app -v
    if ($LASTEXITCODE -ne 0) { throw 'Application tests failed.' }
    python -m PyInstaller --noconfirm --clean '.\VStube.spec'
    if ($LASTEXITCODE -ne 0) { throw 'Application compilation failed.' }
    $iscc = Join-Path $env:LOCALAPPDATA 'Programs\Inno Setup 6\ISCC.exe'
    if (-not (Test-Path $iscc)) { throw 'Inno Setup was not found.' }
    & $iscc '.\installer.iss'
    if ($LASTEXITCODE -ne 0) { throw 'Installer compilation failed.' }
} finally {
    Pop-Location
}
