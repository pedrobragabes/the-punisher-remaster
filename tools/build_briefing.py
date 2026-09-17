"""Build a reversible, unvalidated-in-game high-resolution briefing layout.

Only changes the 1280x960 table preset used by current upstream widescreen fix
at 1080p/1440p. Keeps movie native size: its renderer may ignore table dimensions.
"""
import json
import re
from punisher_lab import LAB, GAME, vpp_index, read_entry, rebuild_vpp, digest


PATCH = {
    'bf_action_list': (50, 100, 420, 120),
    'bf_movie': (550, 100, -1, -1),
    'bf_detail_bg': (30, 245, 460, 340),
    'bf_heading_text': (58, 260, 400, 30),
    'bf_obj_1': (58, 305, 400, 70),
    'bf_obj_2': (58, 390, 400, 70),
    'bf_obj_3': (58, 475, 400, 70),
    'bf_challenge': (58, 305, 400, 240),
    'bf_rifle': (80, 315, -1, -1),
    'bf_l_pistol': (80, 395, -1, -1),
    'bf_r_pistol': (80, 475, -1, -1),
    'bf_briefing_text': (58, 650, 420, 300),
}


def patch_layout(data):
    section = None
    seen = set()
    changes = []
    output = []
    for line in data.decode('ascii').splitlines(keepends=True):
        if line.startswith('#'):
            section = line.strip()[1:]
        match = re.match(r'(\$Name:\s*"([^"]+)"\s+)(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)([^\r\n]*)(\r?\n)?$', line)
        if section == '1280x960' and match and match[2] in PATCH:
            name = match[2]
            if name in seen:
                raise ValueError('Duplicate layout item')
            seen.add(name)
            changes.append(dict(name=name, before=[int(match[i]) for i in range(3, 7)], after=PATCH[name]))
            line = match[1] + '\t'.join(map(str, PATCH[name])) + match[7] + (match[8] or '')
        output.append(line)
    if seen != PATCH.keys():
        raise ValueError('Missing expected briefing fields')
    return ''.join(output).encode('ascii'), changes


def main():
    relative = 'dvd_pc/data/tables.vpp'
    source = GAME/relative
    entries = vpp_index(source)['entries']
    original = read_entry(source, next(e for e in entries if e['name'] == 'gui.tbl'))
    changed, changes = patch_layout(original)
    # Each non-target line and every other resolution preset must remain intact.
    for a, b in zip(original.splitlines(), changed.splitlines(), strict=True):
        if a != b:
            assert any(('"'+name+'"').encode() in a for name in PATCH)
    assert len([1 for a,b in zip(original.splitlines(),changed.splitlines()) if a != b]) == len(PATCH)
    out = LAB/'work/briefing-packages'/relative
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(rebuild_vpp(source, {'gui.tbl': changed}))
    after = vpp_index(out)['entries']
    for a, b in zip(entries, after, strict=True):
        assert a['name'] == b['name']
        assert read_entry(out, b) == (changed if a['name'] == 'gui.tbl' else read_entry(source, a))
    (LAB/'work/gui-briefing-candidate.tbl').write_bytes(changed)
    report = dict(archive=relative, source_sha256=digest(source.read_bytes()),
                  output_sha256=digest(out.read_bytes()), changes=changes,
                  archive_entries_verified=len(entries), in_game_verified=False,
                  scope='Briefing layout only; no font scaling, HD movie or HUD scaling',
                  target_resolutions=['1920x1080', '2560x1440'],
                  dependency='Installed widescreen fix must choose the 1280x960 preset')
    (LAB/'reports/briefing-manifest.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
