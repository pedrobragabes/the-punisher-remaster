# Isolated menu diagnostics

**WIP. These are diagnostic candidates, not a release.**

The original configuration works according to user feedback. The next experiment changes only `interface.vf2` and its `interface.vbm` atlas in `fonts.ceg`. All other entries in `misc.vpp` are verified byte-for-byte against the source archive.

## Current evidence

- The font-only candidate reached Apartment and displayed visibly larger text.
- Original row spacing is too tight for the enlarged glyphs; this is not a finished layout.
- Automated Return/click inputs did not establish a successful War Zone transition. Manual confirmation is pending; the crash is not considered fixed.
- A separate Apartment layout candidate changes only `ap_action_bg` and `ap_action_list` in `gui.tbl`. It has not been visually validated.
- No video, HUD, executable, or widescreen patch is part of these candidates.

## Build and switch

Build from the original installation, using the environment described in [setup](SETUP.md):

```powershell
.\.venv\Scripts\python.exe tools/build_menu_stage.py
```

Close the game before switching. The integrated pack must already be restored. The switcher rejects unknown versions of the two target archives.

```powershell
.\Set-MenuStage.ps1 -Stage Font -Launch
.\Set-MenuStage.ps1 -Stage Menu -Launch
.\Set-MenuStage.ps1 -Stage Original
```

`Font` selects the interface font only. `Menu` combines it with the unvalidated Apartment layout. `Original` restores these two archives only; it does not revert unrelated mods. Backups of the previous archives remain under `work/menu-stage/rollback-*` for recovery. Installation records are written to `reports/menu-stage-installed.json`; they do not indicate runtime approval.

## Next acceptance steps

1. Confirm War Zone entry using original videos with the font-only candidate.
2. Test the Apartment layout and determine how the engine calculates list row spacing.
3. Validate all eight entries, mouse hit areas, and keyboard navigation.
4. Address widescreen background presentation separately.
5. Repeat at 1080p and 1440p before considering a release.
