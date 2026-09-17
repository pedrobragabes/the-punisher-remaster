# The Punisher Remaster Lab

![Status: Work in Progress](https://img.shields.io/badge/status-Work%20in%20Progress-yellow)
[![Source checks](https://github.com/pedrobragabes/the-punisher-remaster/actions/workflows/source-checks.yml/badge.svg)](https://github.com/pedrobragabes/the-punisher-remaster/actions/workflows/source-checks.yml)

An experimental modding and research project for **The Punisher (PC, 2005)**, focused on readable UI, improved widescreen presentation, and incremental visual upgrades.

> **WORK IN PROGRESS — Development tools, not a playable release.**
> The integrated prototype has unresolved startup and menu-transition failures. Successful asset conversion or CI checks do not establish in-game compatibility.

## Current focus

Deliver a small, independently testable **Apartment / main-menu update**: readable text, proportionate paper panels, consistent navigation, and verified behavior at **1920×1080** and **2560×1440**. This milestone does not require every submenu, briefing video, or level to be finished.

The latest user feedback confirms that paper scaling is visible in a diagnostic build, while text remains too small, the background appears pillarboxed, and entering War Zone crashes. These are open development items, not completed features.

## Project status

| Area | Current state |
|---|---|
| Archive tooling | Local inventory, extraction, rebuilding, and integrity checks implemented |
| Texture and font tooling | Experimental conversion pipelines; runtime validation incomplete |
| Main menu | Partial visual progress; typography, panel proportions, and widescreen behavior need work |
| Briefing and HUD | Prototypes only; not approved for use |
| Menu videos | Converted locally and checked externally; in-game integration remains unverified |
| Playable release | **Not available** |

Local research covers **167 VPP archives**, **68,395 entries**, and **26,593 texture records**. An integrated experiment processed 632 images, 18 font files, and 71 videos. These numbers describe generated resources, **not validated features**.

## Documentation and tracking

- [Roadmap](ROADMAP.md) — staged delivery plan
- [Current status](docs/STATUS.md) — evidence, regressions, and limitations
- [Local setup](docs/SETUP.md) — development environment
- [File formats](docs/FORMATS.md) — research notes and supported cases
- [Release criteria](docs/RELEASING.md) — requirements for a testable build
- [Contributing](CONTRIBUTING.md)
- [Issues](https://github.com/pedrobragabes/the-punisher-remaster/issues) · [Milestones](https://github.com/pedrobragabes/the-punisher-remaster/milestones)

## What is included

Source code, documentation, and project planning. The repository does **not** contain the game, modified executables, proprietary libraries, extracted textures, videos, saves, or RAD tools. Asset-dependent tests run locally against a user-provided installation.

Generated resources belong in `work/`; local reports belong in `reports/`. Both are excluded from version control. The current tools expect this repository to be a direct child of the game installation directory; read the setup guide before running them.

## Delivery approach

1. Establish a reproducible baseline and isolate regressions.
2. Release the main menu as a standalone milestone.
3. Expand to mission selection, the armory, upgrades, and other submenus.
4. Validate briefing, HUD, subtitles, and a limited Crackhouse texture set.
5. Integrate higher-resolution menu videos after renderer compatibility is established.

Resampling preserves and enlarges existing artwork; it does not recover missing detail. Artistic restoration is a separate task. Controller support inspired by the PS2 version is a future research direction, not an implemented or scheduled feature.

## Technical references

- [Gibbed.Volition — punisher branch](https://github.com/UncleHunk/Gibbed.Volition/tree/punisher): VPP format research.
- [CEGTool](https://github.com/gdkchan/CEGTool): CEG and texture-compression reference.
- [WidescreenFixesPack](https://github.com/ThirteenAG/WidescreenFixesPack): existing widescreen behavior.
- [RAD Video Tools](https://www.radgametools.com/bnkdown.htm): local Bink conversion, subject to the tool's terms.

This is an unofficial project with no affiliation with the game's rights holders.
