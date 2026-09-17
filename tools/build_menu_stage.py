"""Build isolated main-menu candidates from original archives, never install them."""
import json
import re
from punisher_lab import LAB, GAME, vpp_index, read_entry, rebuild_vpp, digest
from build_ui_pack import scale_font, scale_ceg
from inspect_ui import inspect_font


def build():
    output = LAB / 'work/menu-stage'
    output.mkdir(parents=True, exist_ok=True)
    records = []
    source = GAME / 'dvd_pc/data/misc.vpp'
    entries = {e['name']: e for e in vpp_index(source)['entries']}
    font = read_entry(source, entries['interface.vf2'])
    replacements = {
        'interface.vf2': scale_font(font),
        'fonts.ceg': scale_ceg(read_entry(source, entries['fonts.ceg']), 'fonts.ceg',
                               select=lambda e: e['name'] == 'interface.vbm',
                               font={'interface.vbm': inspect_font(font)}),
    }
    for label, path, changes in [('interface-font', source, replacements)]:
        target = output / (label + '.vpp')
        target.write_bytes(rebuild_vpp(path, changes))
        for entry in vpp_index(target)['entries']:
            assert read_entry(target, entry) == changes.get(entry['name'], read_entry(path, entries[entry['name']]))
        records.append(dict(component=label, archive=path.relative_to(GAME).as_posix(),
                            source_sha256=digest(path.read_bytes()), output_sha256=digest(target.read_bytes()),
                            file=target.name, changed_entries=list(changes)))
    source = GAME / 'dvd_pc/data/tables.vpp'
    entries = {e['name']: e for e in vpp_index(source)['entries']}
    original = read_entry(source, entries['gui.tbl'])
    # Only Apartment changes. Other screens retain the original layout for isolation.
    text = original.decode('ascii')
    text, count = re.subn(r'(\$Name:\s*"ap_action_bg"\s+)-?\d+\s+-?\d+\s+-?\d+\s+-?\d+',
                         r'\g<1>30\t92\t430\t280', text)
    text, count_list = re.subn(r'(\$Name:\s*"ap_action_list"\s+)-?\d+\s+-?\d+\s+-?\d+\s+-?\d+',
                              r'\g<1>60\t100\t380\t260', text)
    assert count == count_list and count > 0
    target = output / 'apartment-layout.vpp'
    target.write_bytes(rebuild_vpp(source, {'gui.tbl': text.encode('ascii')}))
    for entry in vpp_index(target)['entries']:
        expected = text.encode('ascii') if entry['name'] == 'gui.tbl' else read_entry(source, entries[entry['name']])
        assert read_entry(target, entry) == expected
    records.append(dict(component='apartment-layout', archive=source.relative_to(GAME).as_posix(),
                        source_sha256=digest(source.read_bytes()), output_sha256=digest(target.read_bytes()),
                        file=target.name, changed_entries=['gui.tbl']))
    report = dict(in_game_verified=False, components=records)
    (output / 'manifest.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    build()
