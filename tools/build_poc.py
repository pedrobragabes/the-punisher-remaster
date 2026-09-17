"""Build verified experimental texture packages from local PNGs.
Output stays under work/packages; install only into the isolated test copy.
"""
import argparse
import json
from PIL import Image
from punisher_lab import *

def build(archive_relative, container_name, texture_name, image_path):
    source=GAME/archive_relative
    entries=vpp_index(source)['entries']
    target=next(e for e in entries if e['name']==container_name)
    original=read_entry(source,target)
    changed=replace_texture(original,texture_name,image_path)
    output=LAB/'work/packages'/archive_relative
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_bytes(rebuild_vpp(source,{container_name:changed}))
    rebuilt=vpp_index(output)['entries']
    if len(entries)!=len(rebuilt): raise ValueError('Directory count changed')
    for a,b in zip(entries,rebuilt):
        assert a['name']==b['name']
        assert read_entry(output,b)==(changed if a['name']==container_name else read_entry(source,a))
    before=ceg_index(original)['entries']; after=ceg_index(changed)['entries']
    for a,b in zip(before,after):
        if a['name']==texture_name: continue
        assert original[a['offset']:a['offset']+a['span']]==changed[b['offset']:b['offset']+b['span']]
        assert original[32+a['index']*48+4:32+a['index']*48+48]==changed[32+b['index']*48+4:32+b['index']*48+48]
    new=next(t for t in after if t['name']==texture_name)
    old=next(t for t in before if t['name']==texture_name)
    decoded=decode_texture(changed,new)
    decoded.save(LAB/'work'/f'{texture_name}-rebuilt.png')
    return dict(archive=archive_relative,container=container_name,texture=texture_name,
                image=str(image_path.relative_to(LAB)),original_size=[old['width'],old['height']],
                replacement_size=[new['width'],new['height']],
                texture_payload_bytes_before=old['span'],texture_payload_bytes_after=new['span'],
                source_sha256=digest(source.read_bytes()),output_sha256=digest(output.read_bytes()),
                image_sha256=digest(image_path.read_bytes()),
                bytes_before=source.stat().st_size,bytes_after=output.stat().st_size,
                other_archive_entries_and_textures_verified=True,
                in_game_verified=False)

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--brick',action='store_true')
    parser.add_argument('--crackhouse',action='store_true')
    args=parser.parse_args()
    # Matched visually to the user's actual APARTMENT main-menu screenshot.
    # main.tga is a different artwork; rebuilding from original also restores it.
    items=[build('dvd_pc/data/misc.vpp','int-mainmenu.ceg','apartment_bg.tga',LAB/'work/apartment-restored-generated.png')]
    if args.brick:
        items.append(build('dvd_pc/data/shipping/Chop/Chop1.vpp','Chop1.ceg','cem_fmbrick-04.tga',LAB/'work/brick-restored-generated.png'))
    if args.crackhouse:
        items.append(build('dvd_pc/data/shipping/nycrack/nycracka.vpp','nycracka.ceg','woo_kmfloora.tga',LAB/'work/floor-restored-generated.png'))
    (LAB/'reports/poc-manifest.json').write_text(json.dumps(items,indent=2),encoding='utf-8')
    print(json.dumps(items,indent=2))
