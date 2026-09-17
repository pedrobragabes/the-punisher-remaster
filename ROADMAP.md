# Development Roadmap

**Work in Progress.** Milestones are acceptance gates, not delivery dates. A feature is complete only after it works in the game; generating files does not close its issue.

| Milestone | Deliverable | Prerequisites |
|---|---|---|
| [M0 — Reproducible baseline](https://github.com/pedrobragabes/the-punisher-remaster/milestone/1) | Stable startup, isolated regressions, and reliable rollback | None |
| [v0.1 — Main menu](https://github.com/pedrobragabes/the-punisher-remaster/milestone/2) | Apartment, readable fonts, proportionate paper, profile flow, and navigation | M0 |
| [v0.2 — Submenus](https://github.com/pedrobragabes/the-punisher-remaster/milestone/3) | War Zone, Armory, Upgrades, journal, extras, and options | v0.1 |
| [v0.3 — Mission briefing](https://github.com/pedrobragabes/the-punisher-remaster/milestone/4) | Objectives, description, and video without overlap | M0; font work from v0.1 |
| [v0.4 — HUD and Crackhouse](https://github.com/pedrobragabes/the-punisher-remaster/milestone/5) | Readable HUD/subtitles and a validated small texture set | M0; testable briefing flow |
| [v0.5 — Menu videos](https://github.com/pedrobragabes/the-punisher-remaster/milestone/6) | Higher-resolution transitions and briefings with correct framing and audio | v0.2 and v0.3 |

## Immediate sequence

[Isolate the failure #1](https://github.com/pedrobragabes/the-punisher-remaster/issues/1) → [separate components #2](https://github.com/pedrobragabes/the-punisher-remaster/issues/2) → [validate fonts #4](https://github.com/pedrobragabes/the-punisher-remaster/issues/4) → [refine Apartment #5](https://github.com/pedrobragabes/the-punisher-remaster/issues/5) → [verify navigation #6](https://github.com/pedrobragabes/the-punisher-remaster/issues/6) → [prepare the first release #7](https://github.com/pedrobragabes/the-punisher-remaster/issues/7).

## M0 — Reproducible baseline

- Reproduce startup and transition failures with a recorded component matrix.
- Separate executable, fonts, textures, tables, and videos into independently testable components.
- Verify original/test copies and preserve profiles and saves.
- Record versions, dependencies, and rollback steps.

## v0.1 — Main menu

- Increase text size while preserving glyphs, symbols, spacing, and line breaks.
- Reduce excess paper area and align it with the menu list.
- Add a documented widescreen background mode; assess cropping versus stretching explicitly.
- Validate profile selection and keyboard/mouse navigation at 1080p and 1440p.
- Publish this milestone independently of converted videos.

## v0.2 — Submenus

- War Zone: resolve the reported entry crash; validate all missions, states, maps, and descriptions.
- Armory: validate weapon/pistol panels, selection outlines, and descriptions.
- Upgrades: align names, levels, costs, points, and detail text.
- Journal and extras: validate portraits, newspapers, galleries, and grid geometry.
- Options and controls: verify labels, values, and navigation.

## v0.3 — Mission briefing

- Reproduce and eliminate the Crackhouse text/video overlap.
- Separate text layout from the engine's video-size calculations.
- Validate objectives, challenge mode, weapon selection, and mission entry.
- Keep original videos available as an independent fallback.

## v0.4 — HUD and Crackhouse

- Align health, slaughter, ammunition, score, reticles, and interaction messages.
- Make subtitles readable without clipping long lines.
- Review a small texture set in a reproducible area of the first mission.
- Test gameplay, save/reload, and return to the menu.

## v0.5 — Menu videos

- Validate all 71 converted navigation/briefing videos in the legacy renderer.
- Preserve frame count, timing, audio, aspect ratio, and transition continuity.
- Document the difference between resampling and recovered detail.
- Standalone cinematics, trailers, and credits are outside this milestone.

## Future research

PS2-inspired controller support, additional aspect ratios, memory budgets, artistic material/character restoration, further levels, and patch-based distribution. Controller work would require analog movement/aiming, menu navigation, bindings, button prompts, and device testing. These items have no committed schedule.
