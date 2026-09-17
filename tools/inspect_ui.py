"""Read-only inventory of menu layout and observed VFNT v2 structures.

Field meanings below are inferred from the local game files, not an engine SDK.
Never patches fonts: bitmap offsets and header bookkeeping need runtime validation.
"""
import json
import re
import struct
from punisher_lab import LAB, GAME, vpp_index, read_entry, ceg_index


def inspect_font(data):
    if len(data) < 64 or data[:4] != b'VFNT':
        raise ValueError('Not a supported VFNT header')
    header = struct.unpack_from('<16I', data)
    version, count, first, height, pairs = header[1], header[3], header[4], header[6], header[8]
    if version != 2 or len(data) != 64 + pairs * 4 + count * 24:
        raise ValueError('Unexpected VFNT v2 layout')
    base = 64 + pairs * 4
    xy = base + count * 16
    glyphs = []
    for i in range(count):
        advance, width, offset, kern, flags = struct.unpack_from('<iiihH', data, base+i*16)
        x = struct.unpack_from('<i', data, xy+i*4)[0]
        y = struct.unpack_from('<i', data, xy+(count+i)*4)[0]
        glyphs.append(dict(code=first+i, advance=advance, width=width,
                           bitmap_offset=offset, kerning_index=kern, flags=flags, x=x, y=y))
    return dict(version=version, height=height, glyph_count=count, first_code=first,
                kerning_pair_count=pairs, header_raw=list(header), glyphs=glyphs,
                interpretation='inferred from local files; no runtime patch validation')


def main():
    result = dict(fonts={}, layouts={}, containers={})
    misc = GAME/'dvd_pc/data/misc.vpp'
    for entry in vpp_index(misc)['entries']:
        if entry['name'].endswith('.vf2'):
            result['fonts'][entry['name']] = inspect_font(read_entry(misc, entry))
        elif entry['name'] in ('fonts.ceg', 'int-mainmenu.ceg', 'int-warzone.ceg', 'int-journal.ceg'):
            result['containers'][entry['name']] = ceg_index(read_entry(misc, entry))['entries']
    tables = GAME/'dvd_pc/data/tables.vpp'
    for entry in vpp_index(tables)['entries']:
        if entry['name'] not in ('gui.tbl', 'hud.tbl'):
            continue
        text = read_entry(tables, entry).decode('ascii')
        section = None
        sections = {}
        for line in text.splitlines():
            if re.fullmatch(r'#\d+x\d+', line.strip()):
                section = line.strip()[1:]
                sections[section] = []
            match = re.match(r'\$Name:\s*"([^"]+)"\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)', line)
            if match and section:
                sections[section].append(dict(name=match[1], values=[int(match[i]) for i in range(2, 6)]))
        result['layouts'][entry['name']] = sections
    out = LAB/'reports/ui-inventory.json'
    out.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(dict(report=str(out), fonts=len(result['fonts']),
                         layout_sections={k:len(v) for k,v in result['layouts'].items()})))


if __name__ == '__main__':
    main()
