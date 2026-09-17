# Ambiente local

Use uma instalação do jogo no Windows. Clone este repositório numa subpasta `remaster-lab` dentro dela. `punisher_lab.py` identifica a pasta pai como instalação de origem.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe tools\punisher_lab.py inventory
.\.venv\Scripts\python.exe tools\catalog_textures.py
.\.venv\Scripts\python.exe tools\verify.py
```

Os experimentos de UI/vídeos também usam `requirements-ui.txt`. Relatórios locais são ignorados pelo Git.

Crie uma cópia completa e separada do jogo em `work/game`, excluindo a própria pasta `remaster-lab` da cópia para evitar recursão. Não execute os instaladores sobre a pasta original. A criação/verificação automatizada dessa cópia ainda está no backlog. Crie a pasta `work` antes de executar `verify.py`.

| Ferramenta | Finalidade |
|---|---|
| `inspect_ui.py` | Inventário de tabelas e fontes |
| `build_poc.py` | Texturas experimentais; requer imagens locais não distribuídas |
| `build_briefing.py` | Experimento antigo de layout; insuficiente para corrigir o briefing |
| `build_ui_pack.py` | Experimento integrado de atlas, fontes e tabelas |
| `build_menu_videos.py` | Conversão de menus/briefings com Bink 1 |
| `build_video_fix.py` | Patch de tamanho dos vídeos, restrito por hash |
| `verify_ui_pack.py` | Fontes, hashes e aritmética x86 |
| `verify_menu_videos.py` | Verificação e decodificação de quadros extremos |

Obtenha [RAD Video Tools](https://www.radgametools.com/bnkdown.htm) para a conversão e disponibilize `radvideo64.exe` em `work/radtools/portable/`, com os componentes exigidos pela ferramenta. Ela não é fornecida no repositório.

**O pacote integrado tem falha de abertura conhecida.** Construí-lo não o torna uma versão jogável. Consulte [STATUS](STATUS.md). Reversão, quando houver manifestos locais completos: `Install-UI.ps1 -Restore`.

Não versione arquivos do jogo, saídas, saves ou relatórios com caminhos pessoais. Antes de publicar, confira `git diff --cached` e a lista de arquivos.
