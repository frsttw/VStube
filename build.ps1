$ErrorActionPreference = 'Stop'
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$toolsDir = Join-Path $projectDir 'assets\tools'
New-Item -ItemType Directory -Force $toolsDir | Out-Null

function Find-WinGetTool([string]$name, [string]$packagePattern) {
    $root = Join-Path $env:LOCALAPPDATA 'Microsoft\WinGet\Packages'
    $match = Get-ChildItem $root -Filter "$name.exe" -Recurse -ErrorAction SilentlyContinue |
        Where-Object FullName -Like "*$packagePattern*" |
        Select-Object -First 1 -ExpandProperty FullName
    if (-not $match) { throw "$name não foi encontrado. Instale as dependências indicadas no README." }
    return $match
}

Copy-Item (Find-WinGetTool 'yt-dlp' 'yt-dlp.yt-dlp') (Join-Path $toolsDir 'yt-dlp.exe') -Force
Copy-Item (Find-WinGetTool 'ffmpeg' 'Gyan.FFmpeg') (Join-Path $toolsDir 'ffmpeg.exe') -Force
Copy-Item (Find-WinGetTool 'ffprobe' 'Gyan.FFmpeg') (Join-Path $toolsDir 'ffprobe.exe') -Force
Copy-Item (Find-WinGetTool 'deno' 'DenoLand.Deno') (Join-Path $toolsDir 'deno.exe') -Force

Push-Location $projectDir
try {
    python -m PyInstaller --noconfirm --clean '.\VStube.spec'
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao compilar o aplicativo.' }
    $iscc = Join-Path $env:LOCALAPPDATA 'Programs\Inno Setup 6\ISCC.exe'
    if (-not (Test-Path $iscc)) { throw 'Inno Setup não foi encontrado.' }
    & $iscc '.\installer.iss'
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao compilar o instalador.' }
} finally {
    Pop-Location
}
