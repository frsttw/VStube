# Changelog

Todas as mudanças relevantes do VStube são registradas neste arquivo.

## [3.3.0] - 2026-08-29

- Adicionado histórico persistente do `yt-dlp` para ignorar vídeos repetidos em páginas com itens duplicados.
- O histórico é separado por pasta, modo e qualidade para manter downloads intencionais disponíveis.

## [3.2.0] - 2026-08-27

- Atualizado o `yt-dlp` incluído para acompanhar as mudanças recentes do YouTube e corrigir falhas HTTP 403 durante downloads.
- O processo de build passa a atualizar o componente automaticamente antes de gerar o instalador.

## [3.1.0] - 2026-08-26

- Adicionada assinatura discreta `frstt.dev` no rodapé do aplicativo.
- Crédito clicável na tela Sobre e no README.

## [3.0.0] - 2026-08-26

- Nova interface com navegação superior, cartões de vídeo/áudio e paleta violeta/ciano.
- Abas Atividade, Preferências e Sobre com ações funcionais.
- Preferências gravadas atomicamente, incluindo formato e qualidade.
- Execução por fila de eventos para manter a interface livre durante downloads.
- Cancelamento de download e conversão, com confirmação ao fechar durante uma tarefa.
- Deduplicação de links e tratamento de erros na pasta de destino.
- Testes automatizados e integração de vídeo/MP3 com mídia sintética local.

## [2.1.0] - 2026-08-26

- Aplicativo renomeado para Vsy ytd, com preferências anteriores preservadas.
- Executável, instalador e atalhos atualizados com o novo nome.

### Corrigido

- Transparência real nos cantos do ícone.
- Remoção da borda escura residual nas extremidades.
- Melhor acabamento do ícone no GitHub e em tamanhos pequenos do Windows.

## [2.0.0] - 2026-08-26

### Adicionado

- Nova identidade visual e nome VStube.
- Interface escura com detalhes em violeta e ciano.
- Instalador independente para Windows 10 e 11.
- Memória automática da última pasta de destino.
- Download de vídeos em várias resoluções.
- Extração de áudio em MP3 e M4A.
- Suporte a playlists e múltiplos links.
- Barra de progresso e cancelamento.
