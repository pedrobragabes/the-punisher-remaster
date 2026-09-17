"""Build isolated main-menu candidates from original archives, never install them."""
import json
import re
import pefile
from punisher_lab import LAB, GAME, vpp_index, read_entry, rebuild_vpp, digest
from build_ui_pack import scale_font, scale_ceg
from inspect_ui import inspect_font


def build():
    output = LAB / 'work/menu-stage'
    output.mkdir(parents=True, exist_ok=True)
    previous_path = output / 'manifest.json'
    previous = json.loads(previous_path.read_text())['components'] if previous_path.exists() else []
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
                         r'\g<1>30\t92\t430\t310', text)
    text, count_list = re.subn(r'(\$Name:\s*"ap_action_list"\s+)-?\d+\s+-?\d+\s+-?\d+\s+-?\d+',
                              r'\g<1>60\t100\t380\t288', text)
    assert count == count_list and count > 0
    target = output / 'apartment-layout.vpp'
    target.write_bytes(rebuild_vpp(source, {'gui.tbl': text.encode('ascii')}))
    for entry in vpp_index(target)['entries']:
        expected = text.encode('ascii') if entry['name'] == 'gui.tbl' else read_entry(source, entries[entry['name']])
        assert read_entry(target, entry) == expected
    records.append(dict(component='apartment-layout', archive=source.relative_to(GAME).as_posix(),
                        source_sha256=digest(source.read_bytes()), output_sha256=digest(target.read_bytes()),
                        file=target.name, changed_entries=['gui.tbl']))
    # Apartment passes a fixed 20-pixel row height to the list constructor.
    # The same field controls drawing, clipping, scrolling and mouse hit testing.
    # A 30-pixel font needs larger rows; changing gui.tbl alone cannot fix this.
    source = GAME / 'pun.exe'
    original = source.read_bytes()
    if digest(original) != 'de995c66c7388532942264aa2d9455ac5d10e254d0713aeacd3ea0690098878a':
        raise ValueError('Unsupported executable for Apartment row-height patch')
    pe = pefile.PE(data=original)
    offset = pe.get_offset_from_rva(0x5ed603 - pe.OPTIONAL_HEADER.ImageBase)
    assert original[offset:offset+7] == bytes.fromhex('6a1468705d7400')
    patched = bytearray(original)
    patched[offset+1] = 36
    assert sum(a != b for a, b in zip(original, patched, strict=True)) == 1
    (output / 'apartment-rows.exe').write_bytes(patched)
    records.append(dict(component='apartment-rows', archive='pun.exe',
                        source_sha256=digest(original), output_sha256=digest(patched),
                        file='apartment-rows.exe', address='0x5ed604', before=20, after=36))
    for record in records:
        known = set()
        for old in previous:
            if old['component'] == record['component'] and old['source_sha256'] == record['source_sha256']:
                known.add(old['output_sha256'])
                known.update(old.get('previous_output_sha256', []))
        record['previous_output_sha256'] = sorted(known - {record['output_sha256']})
    report = dict(in_game_verified=False, components=records)
    (output / 'manifest.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    build()
