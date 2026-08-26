<p align="center">
  <img src="assets/vstube-icon.png" width="128" alt="Ícone do VStube">
</p>

<h1 align="center">VStube</h1>

<p align="center">
  Baixe vídeos e extraia áudios com uma interface elegante, rápida e totalmente local.
</p>

<p align="center">
  <img alt="Windows" src="https://img.shields.io/badge/Windows-10%20%7C%2011-7c4dff?style=for-the-badge&logo=windows11&logoColor=white">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.13-a866ff?style=for-the-badge&logo=python&logoColor=white">
  <img alt="Versão" src="https://img.shields.io/badge/versão-2.0.0-40e0d0?style=for-the-badge">
  <img alt="Licença" src="https://img.shields.io/badge/licença-MIT-f4f4f5?style=for-the-badge">
</p>

<p align="center">
  <a href="https://github.com/frsttw/VStube/releases/latest/download/VStube-Setup.exe"><strong>⬇ Baixar o VStube para Windows</strong></a>
</p>

<p align="center">
  <img src="docs/vstube-preview.png" width="860" alt="Interface do VStube">
</p>

## Sobre

O **VStube** transforma o fluxo do `yt-dlp` e do FFmpeg em uma experiência visual simples. Cole um link, escolha vídeo ou áudio, defina a qualidade e faça o download sem abrir o terminal.

## Destaques

- Download de vídeos em até 4K.
- Extração de áudio em MP3 ou M4A.
- Compatibilidade com links individuais e playlists.
- Processamento de vários links, um por linha.
- Barra de progresso e cancelamento em tempo real.
- Memória automática da última pasta escolhida.
- Interface escura responsiva com identidade visual própria.
- Instalador independente com todos os componentes necessários.

## Como usar

1. Baixe o `VStube-Setup.exe` na página de Releases.
2. Execute o instalador e abra o VStube pelo atalho criado.
3. Cole um ou mais links, um por linha.
4. Escolha vídeo ou áudio e defina a qualidade.
5. Selecione a pasta de destino e clique em **INICIAR DOWNLOAD**.

> [!NOTE]
> O instalador ainda não possui assinatura digital. O Windows pode exibir um aviso do SmartScreen na primeira execução. O código-fonte está disponível neste repositório para auditoria.

## Tecnologias

| Camada | Tecnologia |
| --- | --- |
| Interface | Python + Tkinter/ttk |
| Downloads | yt-dlp |
| Áudio e vídeo | FFmpeg + FFprobe |
| Runtime auxiliar | Deno |
| Empacotamento | PyInstaller |
| Instalador | Inno Setup |

## Estrutura

```text
VStube/
├── app.py                 # Interface e lógica principal
├── assets/                # Identidade visual
├── docs/                  # Imagens da documentação
├── VStube.spec            # Empacotamento do executável
├── installer.iss          # Configuração do instalador
└── build.ps1              # Build automatizado para Windows
```

## Compilar no Windows

Instale Python, PyInstaller, Inno Setup, yt-dlp, FFmpeg e Deno. Em seguida:

```powershell
.\build.ps1
```

O script reúne as ferramentas, gera `VStube.exe` e cria `VStube-Setup.exe`.

## Privacidade

O VStube funciona localmente e não mantém servidor próprio, conta de usuário ou telemetria. Links, preferências e arquivos permanecem no computador do usuário. A única configuração persistida é a última pasta de destino escolhida.

## Uso responsável

Use o VStube somente para conteúdo próprio, de domínio público ou que você tenha autorização para baixar. O aplicativo não contorna proteções nem acessa conteúdo privado.

---

<p align="center">Desenvolvido por <strong>@frsttw</strong></p>
