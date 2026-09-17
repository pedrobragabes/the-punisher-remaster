# Estado em 16/09/2026

## Verificado em arquivos

- Inventário de 167 VPP e 68.395 entradas.
- Round-trip de pacote sem alterações: byte a byte idêntico.
- Validação de entradas reconstruídas e preservação dos recursos não alterados.
- 18 arquivos de fonte com métricas/coordenadas ampliadas e contagem de glifos preservada.
- 71 vídeos com hashes, quadros, taxa e quantidade de trilhas conferidos; primeiro e último quadro decodificados.
- 24 casos do cálculo de dimensões testados em emulação x86, com preservação de registradores, flags e pilha.

## Não aprovado em execução

O pacote integrado instalado em uma cópia isolada travou na abertura. O usuário confirmou a tela travada/preta. O processo foi observado como não responsivo.

O diagnóstico começou com executável original e recursos novos; a abertura ainda não foi aprovada. Um teste subsequente com `misc.vpp` original e os demais componentes modificados encerrou com exceção `0xc0000005`, no deslocamento `0x00157d64` de `pun.exe`. **Isso não identifica sozinho o componente causador.**

Os 119 arquivos do pacote integrado foram revertidos para os originais na cópia de teste. Não foi concluída uma nova validação visual de baseline após essa reversão. As saídas experimentais continuam locais para investigação.

O instalador agora exige `-AllowUnvalidated` para reaplicar o experimento conhecido como instável. Isso não é um fluxo de instalação recomendado ao jogador.

## Limites conhecidos

- Reamostragem 2× e Bink bicúbico não recuperam detalhes perdidos.
- Duas barras mínimas da mira têm layout de textura ainda não suportado.
- O patch de executável aceita apenas o SHA-256 documentado no código; não foi aprovado em integração.
- Há formatos/registros CEG que as ferramentas deliberadamente não alteram.
- Imagens de cenário e fundo geradas anteriormente não estão incluídas no repositório.
- Os nove vídeos avulsos da raiz de `movies` não fazem parte do lote de 71 menus/briefings.

**Próxima conclusão válida:** baseline estável e causa do travamento isolada. Depois disso, o menu Apartment poderá ser publicado separadamente.
