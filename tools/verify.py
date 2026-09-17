"""Integration checks against the user's local assets; no installation writes."""
import json
from pathlib import Path
from punisher_lab import *

def run():
    source=GAME/'dvd_pc/data/misc.vpp'
    entries=vpp_index(source)['entries']
    target=next(e for e in entries if e['name']=='int-mainmenu.ceg')
    original=read_entry(source,target)
    results={}
    rebuilt=rebuild_vpp(source,{'int-mainmenu.ceg':original})
    assert rebuilt==source.read_bytes()
    results['unchanged_archive_byte_identical']=True
    texture=next(e for e in ceg_index(original)['entries'] if e['name']=='main.tga')
    image=decode_texture(original,texture)
    sample=LAB/'work/main-original.png'
    image.save(sample)
    # A real encode/decode cycle, with no artistic changes, exercises replacement.
    changed=replace_texture(original,'main.tga',sample)
    before=ceg_index(original)['entries']; after=ceg_index(changed)['entries']
    for a,b in zip(before,after):
        if a['name']=='main.tga': continue
        assert original[a['offset']:a['offset']+a['span']]==changed[b['offset']:b['offset']+b['span']]
        assert original[32+a['index']*48+4:32+a['index']*48+48]==changed[32+b['index']*48+4:32+b['index']*48+48]
    results['other_textures_and_metadata_preserved']=True
    output=LAB/'work/verification.vpp'; output.write_bytes(rebuild_vpp(source,{'int-mainmenu.ceg':changed}))
    output_entries=vpp_index(output)['entries']
    for a,b in zip(entries,output_entries):
        assert a['name']==b['name']
        expected=changed if a['name']=='int-mainmenu.ceg' else read_entry(source,a)
        assert read_entry(output,b)==expected
    results['all_rebuilt_archive_payloads_verified']=True
    # Truncation must be rejected, rather than producing partial extraction.
    bad=LAB/'work/truncated.vpp'; bad.write_bytes(source.read_bytes()[:4096])
    try: vpp_index(bad)
    except ValueError: results['truncated_archive_rejected']=True
    else: raise AssertionError('Truncated VPP accepted')
    try: extract(source,'int-mainmenu.ceg',GAME/'must-not-write.ceg')
    except ValueError: results['installation_output_rejected']=True
    else: raise AssertionError('Unsafe output accepted')
    (LAB/'reports/verification.json').write_text(json.dumps(results,indent=2))
    print(json.dumps(results,indent=2))

if __name__=='__main__': run()
