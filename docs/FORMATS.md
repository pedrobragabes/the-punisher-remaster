# File Format Research

These notes describe observed local files, not a complete engine specification.

## VPP

VPP version 3 uses magic `0x51890ACE` and 32-byte directory entries. Most observed archives use 2048-byte alignment; archives in `anims` use 64-byte alignment, established by comparing payloads. Animation-archive rebuilding is not supported by the builder.

Entries may be zlib-compressed. Rebuilding preserves directory order and untouched entry contents, then verifies the resulting payloads.

## CEG

CEG uses magic `0x564B4547` and 48-byte records. Observed formats include 15 (DXT5), 7 (BGRA8888), and 14 (not decoded by the basic tool). Declared lengths do not always represent physical byte spans.

In the inspected BGRA atlases, record length counts pixels and the payload uses four bytes per pixel. In the DXT5 animations accepted by the experimental editor, length describes one frame and the physical span matches frame count multiplied by frame size. The editor verifies these relationships instead of applying them to arbitrary records.

## VFNT v2

The inferred structure contains a 64-byte header, 4-byte kerning pairs, 16-byte glyph records, and two coordinate tables with 4 bytes per glyph. This interpretation still needs runtime validation; internal consistency alone does not prove engine compatibility.

## Layout and video

`gui.tbl` and `hud.tbl` contain resolution presets. Native-size sentinels such as `-1`, row/column counts, and anchored coordinates require separate handling. The installed widescreen fix also changes positions and dimensions.

The game recalculates video dimensions in code using native Bink dimensions and a 640×480 reference. Editing a layout table alone does not control that behavior. The experimental patch and arithmetic checks live in `build_video_fix.py` and `verify_ui_pack.py`; integration remains unverified.
