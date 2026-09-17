# Project Status

**Work in Progress — updated September 16, 2026.** No integrated playable build has passed acceptance testing.

## Verified outside the game

- Inventory of 167 VPP archives and 68,395 entries.
- Byte-identical round-trip for an unchanged archive.
- Rebuilt entry-content checks and preservation of untouched resources.
- Metrics/coordinate checks for 18 enlarged font files, preserving glyph counts.
- Hashes, frame counts, timebases, and audio-track counts for 71 converted videos; first and last frames decoded.
- 24 x86-emulated video-sizing cases, including register, flag, and stack preservation.

Source-check CI covers Python and PowerShell syntax only. It does not test rendering, gameplay, or asset compatibility.

## Runtime evidence and open regressions

The integrated prototype was reported as frozen/black at startup, and the process was observed as unresponsive. Isolation began with the original executable and modified resources; no successful integrated startup was established.

A subsequent test with the original executable and `misc.vpp`, but other modified components, exited with `0xc0000005` at executable offset `0x00157d64`. This does not identify the responsible component by itself.

Later user feedback shows visible paper scaling in a diagnostic main-menu capture, but text remains too small, the background appears restricted to 4:3, and entering War Zone crashes. The precise component set used for that capture has not been independently confirmed. Partial visual progress is not a stability pass.

The 119 files from the integrated pack were restored to their originals in the isolated test copy. A complete baseline navigation test has not yet been recorded. Generated experimental outputs remain local for investigation.

The installer requires `-AllowUnvalidated` to reapply the known-unstable integrated experiment. This is a developer safeguard, not a recommended player installation flow.

## Known limitations

- 2× resampling and bicubic Bink conversion do not recover missing detail.
- Two minimal reticle-bar textures use a layout the editor does not yet support.
- The executable patch is restricted to the hash specified in its source and has not passed integration testing.
- Unsupported or ambiguous CEG records are deliberately left unchanged.
- Previously generated background/level artwork is not distributed in this repository.
- Nine standalone videos in the root `movies` directory are outside the 71-video navigation/briefing batch.
- PS2-style controller support is a future research item, not an implemented feature.

## Next acceptance gate

Establish a reproducible baseline, identify the failure-inducing component set, then validate and release Apartment independently. Track this work in [M0](https://github.com/pedrobragabes/the-punisher-remaster/milestone/1) and [v0.1](https://github.com/pedrobragabes/the-punisher-remaster/milestone/2).
