# Baixador de Vídeos e Áudios

Aplicativo pessoal para Windows com interface gráfica para baixar vídeos ou extrair áudio usando yt-dlp e FFmpeg.

## Recursos

- Vídeo em várias resoluções.
- Áudio em MP3 ou M4A.
- Links individuais ou playlists.
- Vários links, um por linha.
- Barra de progresso e cancelamento.
- Memoriza automaticamente a última pasta de destino.
- Instalador inclui yt-dlp, FFmpeg, FFprobe e Deno.
- Interface escura inspirada na estética cyberpunk do Kerosene.

Use somente para conteúdo próprio, de domínio público ou que você tenha permissão para baixar.

## Compilação

No Windows, instale Python, PyInstaller, Inno Setup, yt-dlp, FFmpeg e Deno. Depois execute `build.ps1`. O script reúne as ferramentas, cria o aplicativo portátil e gera o instalador.
