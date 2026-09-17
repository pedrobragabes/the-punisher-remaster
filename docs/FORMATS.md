# Formatos pesquisados

## VPP

VPP versão 3, magic `0x51890ACE`, diretório de entradas de 32 bytes. A maioria dos pacotes usa alinhamento de 2048 bytes. A pasta `anims` apresenta alinhamento de 64 bytes, observado por comparação de payloads. O builder não reconstrói pacotes de animação.

Entradas podem usar zlib. O reempacotamento preserva ordem e conteúdo das entradas não alteradas e confere novamente cada payload.

## CEG

Magic `0x564B4547`, registros de 48 bytes. Formatos observados: 15 (DXT5), 7 (BGRA8888) e 14 (não decodificado pela ferramenta básica). Nem todo comprimento declarado corresponde diretamente ao tamanho físico.

Nos atlas BGRA examinados, o campo de comprimento mede pixels e o payload contém quatro bytes por pixel. Nas animações DXT5 aceitas pelo editor experimental, o campo mede um quadro e o span físico corresponde ao número de quadros multiplicado pelo tamanho de um quadro. Essas regras são verificadas antes da alteração; não são aplicadas cegamente a todos os registros.

## VFNT v2

Estrutura inferida: cabeçalho de 64 bytes, pares de kerning de 4 bytes, registros de glifos de 16 bytes e duas tabelas de coordenadas de 4 bytes por glifo. A interpretação precisa de validação integrada; arquivos consistentes não provam compatibilidade com o motor.

## Layout e vídeos

`gui.tbl` e `hud.tbl` contêm presets de resolução. Dimensões `-1`, contagens de linhas/colunas e coordenadas ancoradas exigem tratamento separado. O WidescreenFix também altera posições e tamanhos.

O jogo recalcula dimensões de vídeo em código com base no tamanho nativo do Bink e no referencial 640×480. Trocar somente a tabela não controla esse comportamento. A correção experimental e os testes estão em `build_video_fix.py` e `verify_ui_pack.py`; a integração está bloqueada pela regressão de abertura.
