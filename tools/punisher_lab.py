"""Local research tools. Original implementation based on observed files and
format descriptions in Gibbed.Volition (punisher branch) and gdkchan/CEGTool.
Never writes to the source game installation. See README.md for limitations.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import struct
import zlib

LAB = Path(__file__).resolve().parents[1]
GAME = LAB.parent

def digest(data):
    return hashlib.sha256(data).hexdigest()

def align(n):
    return (n + 2047) // 2048 * 2048

def vpp_index(path):
    # Local anims archives use 64-byte payload alignment, unlike scene packs.
    # Confirmed by matching complete animation payloads in scene archives.
    block = 64 if path.parent.name.lower() == 'anims' else 2048
    size = path.stat().st_size
    with path.open('rb') as f:
        magic, version, count, declared = struct.unpack('<4I', f.read(16))
        if (magic, version) != (0x51890ACE, 3):
            raise ValueError(f'Unsupported VPP: {path}')
        if count > (size - 2048) // 32:
            raise ValueError('Directory out of bounds')
        f.seek(2048)
        records = f.read(count * 32)
    offset = align(2048 + count * 32)
    entries = []
    for i in range(count):
        raw, length, stored = struct.unpack_from('<24sII', records, i*32)
        name = raw.split(b'\0')[0].decode('ascii')
        if not name or any(c in name for c in '/\\:') or name in ('.', '..'):
            raise ValueError(f'Unsafe name: {name!r}')
        if offset + stored > size:
            raise ValueError(f'Entry outside archive: {name}')
        entries.append(dict(index=i, name=name, length=length, stored=stored, offset=offset))
        offset += (stored + block - 1) // block * block
    return dict(path=str(path), size=size, declared_size=declared, entries=entries, end=offset, alignment=block)

def read_entry(path, entry):
    with path.open('rb') as f:
        f.seek(entry['offset'])
        data = f.read(entry['stored'])
    if entry['stored'] != entry['length']:
        data = zlib.decompress(data)
    if len(data) != entry['length']:
        raise ValueError('Entry size mismatch')
    return data

def ceg_index(data):
    magic, version, header, size, count = struct.unpack_from('<5I', data)
    if magic != 0x564B4547 or version != 1 or 32 + count*48 > len(data):
        raise ValueError('Unsupported CEG header')
    entries = []
    for i in range(count):
        p = 32 + i*48
        offset, w, h, descriptor, unknown = struct.unpack_from('<IHHII', data, p)
        name = data[p+16:p+40].split(b'\0')[0].decode('ascii')
        length = struct.unpack_from('<I', data, p+40)[0]
        if offset >= len(data) or not w or not h:
            raise ValueError(f'Invalid texture {name}')
        entries.append(dict(index=i, name=name, width=w, height=h,
                            format=descriptor & 255, frames_or_levels=descriptor >> 24,
                            descriptor=descriptor, offset=offset, length=length))
    for e in entries:
        following = [x['offset'] for x in entries if x['offset'] > e['offset']]
        e['span'] = min(following, default=len(data)) - e['offset']
        e['length_exceeds_span'] = e['length'] > e['span']
    return dict(version=version, header_length=header, declared_size=size, entries=entries)

def rebuild_vpp(source, replacements):
    """Preserve directory order, unknown bytes and unmodified stored payloads."""
    original = source.read_bytes()
    info = vpp_index(source)
    if info['alignment'] != 2048:
        raise ValueError('Repacking animation archives is outside the texture prototype')
    entries = info['entries']
    if not entries:
        raise ValueError('Empty archive not supported')
    if set(replacements) - {e['name'] for e in entries}:
        raise ValueError('Replacement not present in source archive')
    if len({e['name'] for e in entries}) != len(entries):
        raise ValueError('Duplicate entry names need explicit index selection')
    result = bytearray(original[:entries[0]['offset']])
    for i, e in enumerate(entries):
        end = entries[i+1]['offset'] if i+1 < len(entries) else len(original)
        replacement = replacements.get(e['name'])
        if replacement is None or replacement == read_entry(source,e):
            result.extend(original[e['offset']:end])
            continue
        stored = zlib.compress(replacement,9) if e['stored'] != e['length'] else replacement
        struct.pack_into('<II',result,2048+i*32+24,len(replacement),len(stored))
        result.extend(stored)
        result.extend(bytes(align(len(stored))-len(stored)))
    struct.pack_into('<I',result,12,info['declared_size'] + len(result)-len(original))
    return bytes(result)

def decode_texture(data, entry):
    from PIL import Image
    w,h = entry['width'],entry['height']
    raw = data[entry['offset']:entry['offset']+entry['span']]
    if entry['format'] == 15:
        image = Image.frombytes('RGBA',(1<<(w-1).bit_length(),1<<(h-1).bit_length()),raw,'bcn',3)
        return image.crop((0,0,w,h))
    if entry['format'] == 7:
        return Image.frombytes('RGBA',(w,h),raw[:w*h*4],'raw','BGRA')
    raise ValueError(f"Unsupported format: {entry['format']}")

def replace_texture(data, name, image_path):
    """Experimental static DXT5 replacement, retaining all unrelated CEG bytes."""
    import io
    from PIL import Image
    entries = ceg_index(data)['entries']
    matches = [e for e in entries if e['name'] == name]
    if len(matches) != 1:
        raise ValueError('Texture must be unique')
    e = matches[0]
    if e['format'] != 15 or e['frames_or_levels'] != 1 or e['span'] != e['length']:
        raise ValueError('Only single-image DXT5 records supported for replacement')
    im = Image.open(image_path).convert('RGBA')
    w,h = im.size
    if not (0 < w <= 4096 and 0 < h <= 4096):
        raise ValueError('Research texture dimensions outside supported limits')
    padded = Image.new('RGBA',(1<<(w-1).bit_length(),1<<(h-1).bit_length()))
    padded.paste(im,(0,0))
    stream = io.BytesIO()
    padded.save(stream,format='DDS',pixel_format='DXT5')
    encoded = stream.getvalue()[128:]
    start,end = e['offset'],e['offset']+e['length']
    if any(other['index'] != e['index'] and start <= other['offset'] < end for other in entries):
        raise ValueError('Overlapping texture offsets')
    result = bytearray(data[:start] + encoded + data[end:])
    delta = len(encoded)-e['length']
    declared = struct.unpack_from('<I',data,12)[0]
    struct.pack_into('<I',result,12,declared+delta)
    for other in entries:
        p=32+other['index']*48
        if other['offset'] >= end:
            struct.pack_into('<I',result,p,other['offset']+delta)
    p=32+e['index']*48
    struct.pack_into('<HH',result,p+4,w,h)
    struct.pack_into('<I',result,p+40,len(encoded))
    ceg_index(result)
    return bytes(result)

def inventory():
    archives, errors = [], []
    for path in sorted((GAME/'dvd_pc').rglob('*.vpp')):
        try:
            info = vpp_index(path)
            info['path'] = str(path.relative_to(GAME))
            archives.append(info)
        except Exception as exc:
            errors.append(dict(path=str(path), error=str(exc)))
    binaries = []
    for path in list(GAME.glob('*.exe')) + list(GAME.glob('*.dll')) + list((GAME/'scripts').glob('*')):
        data = path.read_bytes()
        item = dict(path=str(path.relative_to(GAME)), bytes=len(data), sha256=digest(data))
        if data[:2] == b'MZ':
            pe = struct.unpack_from('<I', data, 60)[0]
            machine, sections, timestamp = struct.unpack_from('<HHI', data, pe+4)
            optional = pe + 24
            item.update(machine=hex(machine), sections=sections, pe_timestamp=timestamp,
                        large_address_aware=bool(struct.unpack_from('<H',data,pe+22)[0]&32),
                        image_base=hex(struct.unpack_from('<I',data,optional+28)[0]))
        binaries.append(item)
    result = dict(binaries=binaries, archives=archives, errors=errors)
    (LAB/'reports'/'inventory.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    counts = collections.Counter(Path(e['name']).suffix.lower() for a in archives for e in a['entries'])
    print(json.dumps(dict(archives=len(archives), entries=sum(len(a['entries']) for a in archives),
                         extensions=counts, errors=errors), indent=2))

def extract(archive, name, output):
    matches = [e for e in vpp_index(archive)['entries'] if e['name'] == name]
    if len(matches) != 1:
        raise ValueError(f'Expected unique entry, got {len(matches)}')
    output = output.resolve()
    if not output.is_relative_to(LAB/'work'):
        raise ValueError('Output must be inside remaster-lab/work')
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('xb') as f:
        f.write(read_entry(archive, matches[0]))
    print(output)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('inventory')
    p = sub.add_parser('extract')
    p.add_argument('archive', type=Path)
    p.add_argument('name')
    p.add_argument('output', type=Path)
    p = sub.add_parser('ceg-info')
    p.add_argument('path', type=Path)
    args = parser.parse_args()
    if args.command == 'inventory': inventory()
    elif args.command == 'extract': extract(args.archive, args.name, args.output)
    else: print(json.dumps(ceg_index(args.path.read_bytes()), indent=2))
