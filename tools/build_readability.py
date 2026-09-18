"""Prepare, but never install or launch, a high-resolution menu candidate."""
import json
from punisher_lab import LAB, GAME, vpp_index, read_entry, rebuild_vpp, digest
from build_ui_pack import scale_font, scale_ceg
from inspect_ui import inspect_font
from menu_readability import patch_layout, patch_rows

OUT = LAB / 'work/readability-candidate'


def archive(relative, replacements):
    source = GAME / relative
    target = OUT / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(rebuild_vpp(source, replacements))
    old, new = vpp_index(source)['entries'], vpp_index(target)['entries']
    for a, b in zip(old, new, strict=True):
        assert a['name'] == b['name']
        assert read_entry(target, b) == replacements.get(a['name'], read_entry(source, a))
    return dict(archive=relative, source_sha256=digest(source.read_bytes()),
                output_sha256=digest(target.read_bytes()), changed_entries=list(replacements),
                entries_verified=len(old))


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    # Validate the supported executable before producing any component.
    original = (GAME / 'pun.exe').read_bytes()
    executable, patches = patch_rows(original)
    misc = GAME / 'dvd_pc/data/misc.vpp'
    entries = {e['name']: e for e in vpp_index(misc)['entries']}
    font = read_entry(misc, entries['interface.vf2'])
    records = [archive('dvd_pc/data/misc.vpp', {
        'interface.vf2': scale_font(font),
        'fonts.ceg': scale_ceg(read_entry(misc, entries['fonts.ceg']), 'fonts.ceg',
                               select=lambda e: e['name'] == 'interface.vbm',
                               font={'interface.vbm': inspect_font(font)}),
    })]
    tables = GAME / 'dvd_pc/data/tables.vpp'
    entry = next(e for e in vpp_index(tables)['entries'] if e['name'] == 'gui.tbl')
    gui, changes = patch_layout(read_entry(tables, entry))
    records.append(archive('dvd_pc/data/tables.vpp', {'gui.tbl': gui}))
    (OUT / 'pun.exe').write_bytes(executable)
    records.append(dict(archive='pun.exe', source_sha256=digest(original),
                        output_sha256=digest(executable), patches=patches))
    report = dict(status='offline candidate, not installed', in_game_verified=False,
                  resolutions=['1920x1080', '2560x1440'], preset='1280x960', language='English',
                  components=records, layout_changes=changes,
                  required_video_set='original', widescreen_background='unchanged',
                  limits=['English interface font only; other languages are not supported.',
                          'Lower resolutions are unsupported by this candidate.',
                          'Runtime widget repositioning still requires visual checks.',
                          'Original videos only; converted Bink files are incompatible with this layout without separate renderer work.'])
    (OUT / 'manifest.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(dict(output=str(OUT.relative_to(LAB)), components=len(records),
                         layout_changes=len(changes), row_patches=len(patches), installed=False)))


if __name__ == '__main__':
    build()
