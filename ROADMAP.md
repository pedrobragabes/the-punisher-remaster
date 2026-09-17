# Roadmap

Cada milestone resulta em uma entrega verificável. Uma funcionalidade só é concluída depois de funcionar dentro do jogo; exportar arquivos não fecha a issue.

| Milestone | Resultado | Depende de |
|---|---|---|
| M0 — Base reproduzível | Abertura estável, isolamento de regressões e rollback confiável | — |
| v0.1 — Menu principal | Apartment, fonte, papel, seleção e perfil legíveis em 1080p/1440p | M0 |
| v0.2 — Submenus | War Zone, Armory, Upgrades, diário, extras e opções validados | v0.1 |
| v0.3 — Briefing | Texto, objetivos e janela de vídeo sem sobreposição | v0.1 e M0 |
| v0.4 — HUD e Crackhouse | HUD, legendas e texturas selecionadas na primeira missão | M0; briefing testável |
| v0.5 — Vídeos dos menus | Transições e briefings maiores, enquadramento e áudio preservados | v0.2 e v0.3 |

## M0 — Base reproduzível

- Reproduzir o travamento do pacote integrado e registrar a matriz de testes.
- Separar executável, fontes, imagens, tabelas e vídeos em componentes instaláveis.
- Conferir cópia original e cópia de teste; manter saves fora da instalação do mod.
- Documentar versões, dependências e restauração.

## v0.1 — Menu principal

- Fonte maior com todos os glifos e símbolos corretos.
- Papel e lista com tamanho coerente, sem linhas cortadas.
- Apartment com composição preservada.
- Entrada/saída de perfil e seleção por teclado/mouse.
- Comparação antes/depois em 1080p e 1440p; não depende dos novos vídeos.

## v0.2 — Submenus

- Missões: lista completa, nomes longos, estados e mapas.
- Arsenal: armas/pistolas, contorno de seleção e descrições.
- Upgrades: colunas, preços, pontos e descrições sem corte.
- Diário/extras: retratos, jornais, galerias, opções e controles.

## v0.3 — Briefing

- Reproduzir a sobreposição observada em Crackhouse.
- Separar layout da interface do cálculo de tamanho do vídeo.
- Validar objetivos, desafio, troca de armas e início da missão nas duas resoluções.
- Manter vídeos originais como fallback independente da correção de texto.

## v0.4 — HUD e Crackhouse

- Vida, slaughter, munição, pontuação, mira e mensagens alinhadas.
- Legendas legíveis, sem cortar frases longas.
- Uma seleção pequena de texturas aprovada por comparação no cenário.
- Carregar, jogar, salvar/recarregar e voltar ao menu sem regressões.

## v0.5 — Vídeos

- Validar os 71 vídeos convertidos no renderizador antigo, além do decodificador externo.
- Preservar quadros, taxa, áudio, proporção e continuidade das transições.
- Documentar o limite da ampliação; não chamar interpolação de detalhe recuperado.
- Cinemáticas, trailers e créditos avulsos ficam para uma etapa posterior.

## Depois das primeiras entregas

Restauração artística de materiais, personagens e outras fases; investigação de limites de memória, outras proporções de tela e distribuição por patches. Cada expansão depende de estabilidade, não da quantidade de arquivos gerados.
