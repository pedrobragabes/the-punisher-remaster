# Local Development Setup

> **WIP:** the integrated pack has known runtime failures. This guide is for development and controlled testing, not a playable-release installation.

Use a Windows installation of the game. Clone this repository into a direct child folder named `remaster-lab`; `punisher_lab.py` treats its parent directory as the source installation.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
New-Item -ItemType Directory -Force work | Out-Null
.\.venv\Scripts\python.exe tools\punisher_lab.py inventory
.\.venv\Scripts\python.exe tools\catalog_textures.py
.\.venv\Scripts\python.exe tools\verify.py
```

UI/video experiments also require `requirements-ui.txt`. Local reports are ignored by Git.

Create a complete, separate game copy at `work/game`, excluding `remaster-lab` itself to avoid recursive copying. Do not target the source installation with an installer. Automated test-copy creation and verification remain tracked development tasks.

| Tool | Purpose |
|---|---|
| `inspect_ui.py` | Inspect layout tables and font structures |
| `build_poc.py` | Texture experiments requiring local, undistributed images |
| `build_briefing.py` | Earlier layout-only experiment; insufficient to fix briefing behavior |
| `build_ui_pack.py` | Experimental atlas, font, texture, and layout pipeline |
| `build_menu_videos.py` | Bink 1 menu/briefing conversion |
| `build_video_fix.py` | Version-locked video-size patch |
| `verify_ui_pack.py` | Font, hash, and emulated x86 checks |
| `verify_menu_videos.py` | Video checks and endpoint-frame decoding |

For video conversion, obtain [RAD Video Tools](https://www.radgametools.com/bnkdown.htm) and provide `radvideo64.exe` at `work/radtools/portable/`, together with its required components. RAD tools are not bundled here.

Building successfully does not establish runtime compatibility. Read [STATUS](STATUS.md). With complete local manifests, `Install-UI.ps1 -Restore` restores this pack's files in the test copy. Do not use `-AllowUnvalidated` outside a controlled diagnostic test.

Never commit game assets, generated outputs, saves, or reports containing personal paths. Review the staged file list and `git diff --cached` before publishing.
