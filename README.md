# The Punisher Remaster Lab

Ferramentas e pesquisa para melhorar a interface e os recursos visuais de **The Punisher (PC, 2005)**, com entregas pequenas e reversíveis.

**Estado: experimental. Não existe uma versão jogável do pacote completo aprovada.** O primeiro pacote integrado de interface apresentou travamento na abertura. As ferramentas de inventário e as verificações de arquivos estão disponíveis; os resultados visuais ainda precisam ser validados no jogo.

## Primeira entrega

Concluir **Apartment / menu principal** com fonte legível, papel proporcional e navegação funcionando em 1920×1080 e 2560×1440. Publicar essa etapa separadamente, sem esperar briefing, HUD, vídeos ou todas as fases.

- [Roadmap e versões previstas](ROADMAP.md)
- [Estado real dos testes](docs/STATUS.md)
- [Preparação do ambiente](docs/SETUP.md)
- [Formato dos arquivos e limitações](docs/FORMATS.md)
- [Critérios para publicar uma versão](docs/RELEASING.md)
- [Issues](https://github.com/pedrobragabes/the-punisher-remaster/issues) e [milestones](https://github.com/pedrobragabes/the-punisher-remaster/milestones)

## O que já existe

- Inventário e leitura de VPP, com extração local e reconstrução verificada de pacotes suportados.
- Catálogo, decodificação e substituição experimental de texturas CEG.
- Inspeção de fontes VFNT v2 e protótipo de ampliação de atlas/métricas.
- Protótipos de layout de menus, briefing e HUD.
- Conversão local de vídeos de menus/briefing com ferramentas oficiais Bink.
- Pesquisa sobre o cálculo de dimensões dos vídeos e patch experimental restrito a uma versão do executável.
- Instalação/reversão na cópia de teste com verificação de hashes.

Foram catalogados localmente 167 VPP, 68.395 entradas e 26.593 registros de textura. O experimento integrado gerou 632 imagens ampliadas, 18 fontes e 71 vídeos; **essas contagens indicam arquivos processados, não funcionalidades aprovadas**.

## Conteúdo publicado

Código, documentação e planejamento. Não contém o jogo, executáveis modificados, bibliotecas comerciais, perfis, texturas extraídas, vídeos ou ferramentas da RAD. Os testes que dependem desses arquivos são executados localmente com uma instalação obtida pelo usuário.

Os recursos são gerados em `work/`, e os relatórios em `reports/`; essas saídas não são versionadas. O código assume que esta pasta está diretamente dentro da pasta do jogo. Veja [SETUP](docs/SETUP.md) antes de executar.

## Desenvolvimento por etapas

1. Reproduzir e eliminar o travamento de abertura.
2. Entregar o menu principal.
3. Acrescentar missões, arsenal, upgrades e demais submenus.
4. Corrigir briefing e depois HUD/legendas em Crackhouse.
5. Integrar vídeos em resolução maior após validar o renderizador.

Ampliação por reamostragem preserva a arte, mas não recupera detalhes perdidos. Uma restauração artística posterior é trabalho separado. Não há promessa de prazo ou de remaster completo em uma única entrega.

## Referências técnicas

- [Gibbed.Volition, branch punisher](https://github.com/UncleHunk/Gibbed.Volition/tree/punisher): pesquisa sobre VPP.
- [CEGTool](https://github.com/gdkchan/CEGTool): referência de CEG e compressão de texturas.
- [WidescreenFixesPack](https://github.com/ThirteenAG/WidescreenFixesPack): comportamento da correção widescreen.
- [RAD Video Tools](https://www.radgametools.com/bnkdown.htm): conversão Bink local; observar os termos da ferramenta.

Projeto não oficial, sem vínculo com os titulares do jogo.
