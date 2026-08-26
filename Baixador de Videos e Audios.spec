# -*- mode: python ; coding: utf-8 -*-

a = Analysis(['app.py'], pathex=[], binaries=[
    ('assets/tools/yt-dlp.exe', 'tools'),
    ('assets/tools/ffmpeg.exe', 'tools'),
    ('assets/tools/ffprobe.exe', 'tools'),
    ('assets/tools/deno.exe', 'tools'),
], datas=[], hiddenimports=[], hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=[], noarchive=False, optimize=0)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name='Baixador de Videos e Audios', icon='assets/app.ico', debug=False, bootloader_ignore_signals=False, strip=False, upx=True, upx_exclude=[], runtime_tmpdir=None, console=False, disable_windowed_traceback=False, argv_emulation=False, target_arch=None, codesign_identity=None, entitlements_file=None)
