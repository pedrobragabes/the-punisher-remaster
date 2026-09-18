# Isolated menu diagnostics

**WIP. These are diagnostic candidates, not a release.**

A broader [offline readability candidate](OFFLINE-READABILITY.md) was prepared on September 18. It is separate from these stages and has not been installed.

The original configuration works according to user feedback. The next experiment changes only `interface.vf2` and its `interface.vbm` atlas in `fonts.ceg`. All other entries in `misc.vpp` are verified byte-for-byte against the source archive.

## Current evidence

- The font-only candidate reached Apartment and displayed visibly larger text.
- Original row spacing is too tight for the enlarged glyphs; this is not a finished layout.
- A subsequent user-driven session reached Mission Briefing with the enlarged font and original videos. The earlier integrated crash remains unresolved, but this smaller configuration passed mission selection once.
- The first combined layout test displayed the complete War Journal label; row spacing remained too tight. Briefing labels and objectives still clip and overlap video.
- Apartment row height is hard-coded to 20 pixels at executable address `0x5ed604`, while the enlarged font is 30 pixels tall. A new candidate changes this single byte to 36, with a 288-pixel list and a 310-pixel paper panel. Runtime validation is pending.
- No video, HUD, or widescreen patch is part of these candidates. Only the `Menu` stage includes the version-locked Apartment row-height executable patch.

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

`Font` selects the interface font only. `Menu` combines it with the Apartment layout and row-height patch. `Original` restores these two archives and the executable only; it does not revert unrelated mods. Backups of previous files remain under `work/menu-stage/rollback-*` for recovery. Installation records are written to `reports/menu-stage-installed.json`; they do not indicate runtime approval.

The row-height patch is based on the Apartment constructor at `0x5ed5d0`, which passes 20 to the list constructor at `0x478b20`. The value is stored at object offset `0x5c`. Drawing uses that field for each row's clipping rectangle and vertical advance (`0x478daa`, `0x478dbc`); hit testing divides by the same field (`0x478ff6`). The build rejects any executable other than the known source hash and verifies that exactly one byte changes.

## Video status

The existing 71-video package uses bicubic resampling: navigation assets are 1280×960 and briefing assets are 960×720. These remain 4:3 and are not reconstructed HD artwork. Converted files are not active in the isolated menu tests. Higher-resolution decoding, renderer compatibility, and complete menu coverage are still pending; the package must not be advertised as a finished HD menu remaster.

## Next acceptance steps

1. Confirm War Zone entry using original videos with the font-only candidate.
2. Test the Apartment layout and determine how the engine calculates list row spacing.
3. Validate all eight entries, mouse hit areas, and keyboard navigation.
4. Address widescreen background presentation separately.
5. Repeat at 1080p and 1440p before considering a release.
