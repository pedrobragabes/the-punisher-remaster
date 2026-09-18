# Offline readability candidate

**WIP — prepared September 18, 2026. Not installed or tested in-game.**

The enlarged interface font exposed two independent limits: narrow widget rectangles and fixed list-row heights. The new candidate changes both together, with shared row height for rendering, clipping, and mouse selection.

## Scope

- 30 list constructors use 36-pixel rows for the 30-pixel English interface font. The previous values were 20 pixels, or 18 in War Zone.
- 71 `gui.tbl` fields in the `1280x960` preset receive explicit dimensions and positions. Other presets, gallery grid counts, HUD data, images, and videos remain unchanged.
- Covered lists include Apartment, War Zone, briefing actions, upgrades, journal, extras, options, controls, profiles, movies, trailers, cheats, and the pause menu.
- Armory and journal descriptions receive taller text rectangles.
- Briefing uses a left column for actions/objectives, the original video to the right, and the description below its maximum calculated extent at the two target resolutions.

The target is **English at 1920×1080 or 2560×1440**, using the existing widescreen fix's `1280x960` preset. Lower resolutions and other languages are unsupported by this candidate. Runtime code can reposition widgets; an offline geometry pass cannot establish final alignment.

## Build and verify without opening the game

Use the local dependencies from `requirements-ui.txt` and the original game files described in [setup](SETUP.md):

```powershell
.\.venv\Scripts\python.exe tools/build_readability.py
.\.venv\Scripts\python.exe tools/verify_readability.py
.\.venv\Scripts\python.exe tools/audit_menu_videos.py
```

Outputs are written to `work/readability-candidate/` and ignored local reports. These commands do not copy files to `work/game`, start the game, or control its window. The video audit expects the previously built `reports/ui-video-manifest.json` and its local candidate files.

No installer is provided for this broader candidate yet. The older `Set-MenuStage.ps1` continues to use the separate Apartment-only experiment.

## Completed offline checks

| Check | Result |
|---|---|
| Version-locked executable changes | Exactly 30 row-height immediate bytes; unsupported source hash rejected |
| Actual x86 list constructor paths | 30 pass, including widget identity, font pointer, stored row height, and stack balance |
| Actual x86 drawing loop | 281 row rectangles match the expected origin, width, height, and vertical advance |
| Actual x86 mouse-coordinate calculation | 562 first/last-pixel row boundary cases pass |
| Layout bounds and row capacity | 71 fields checked; eight Apartment rows and 16 mission rows fit |
| Font metric width checks | 29 representative menu/mission/briefing labels fit with horizontal margin |
| Original briefing video geometry | Text/video separation calculated at 1080p and 1440p |
| Archive preservation | Unchanged entries and non-target presets match source data |

The emulator runs bounded instruction ranges from local file bytes. Base-widget initialization and list callbacks are stubbed; no game process or live memory is used. These tests do not exercise actual rendering, audio, decoding, input devices, dynamic anchoring, or gameplay.

## Video audit and crash hypothesis

All 71 videos in the test copy still match their original hashes. The converted set contains 55 navigation videos at 1280×960 and 16 briefing videos at 960×720. Pixel area increases by 4× and 9× respectively. Encoded file sizes total 1,423,912,944 bytes, versus 158,771,808 bytes for the originals. Encoded size is **not** measured runtime memory consumption.

The executable registers `0x557d30` as an allocation callback through the imported `_BinkSetMemory@8`. It aligns the returned allocation and writes bookkeeping at `0x557d64`, without checking for a null result. Injecting null in an isolated emulator reproduces a write to `0xfc` at that exact instruction, matching the instruction offset in the recorded crash. Two valid-pointer cases preserve normal alignment and state.

This identifies a reproducible failure path, **not the observed runtime cause**. The actual allocation result, requested size, available memory, and component responsible were not captured. The allocator is not patched, and converted videos remain outside the readability candidate.

## Still required

- Visually inspect every changed screen and long text, including runtime anchoring, wrapping, highlights, and hit areas.
- Verify the profile flow, War Zone transitions, return paths, startup, and exit repeatedly.
- Check briefing objectives, weapon selection, challenge mode, subtitles, and description wrapping.
- Diagnose the real Bink allocation failure before integrating converted videos.
- Restore artwork, maps, newspapers, and transition continuity separately. Bicubic resampling is not recovered detail, and these videos remain 4:3.
- Resolve widescreen background fill as a separate change with a documented crop/stretch choice.

No milestone or issue is complete based on these offline checks alone.
