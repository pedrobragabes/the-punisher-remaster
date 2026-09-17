"""Resource integrity and emulated x86 arithmetic tests; not visual gameplay QA."""
import json
import struct
import pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
from PIL import Image,ImageDraw
from punisher_lab import LAB,GAME,vpp_index,read_entry,ceg_index,decode_texture,digest
from inspect_ui import inspect_font


def main():
    report=json.loads((LAB/'reports/ui-exe-manifest.json').read_text())
    pe=pefile.PE(str(LAB/'work/ui-pack/pun.exe'))
    data=pe.get_memory_mapped_image();tests=0
    for dim,entry in report['functions'].items():
        for width,factor in [(320,1),(640,1),(1280,2),(960,4 if dim=='width' else 3)]:
            for raw in (720,1440,3840):
                mu=Uc(UC_ARCH_X86,UC_MODE_32);mu.mem_map(0x400000,0xe00000)
                mu.mem_write(0x400000,data);mu.mem_map(0x2000000,0x2000)
                mu.mem_write(0x10ffecc,struct.pack('<I',0x2000000));mu.mem_write(0x2000000,struct.pack('<I',width))
                mu.reg_write(UC_X86_REG_ESP,0x2001000);mu.mem_write(0x2001000,struct.pack('<I',0x2001800))
                mu.reg_write(UC_X86_REG_ECX,0x12345678);mu.reg_write(UC_X86_REG_EDX,0x87654321)
                mu.reg_write(UC_X86_REG_EAX,raw);mu.reg_write(UC_X86_REG_EFLAGS,0x246)
                # Float conversion is unchanged; emulate its integer return, then run new code.
                mu.emu_start(entry+5,0x2001800,count=100)
                assert mu.reg_read(UC_X86_REG_EAX)==raw//factor
                assert mu.reg_read(UC_X86_REG_ECX)==0x12345678
                assert mu.reg_read(UC_X86_REG_EDX)==0x87654321
                assert mu.reg_read(UC_X86_REG_EFLAGS)==0x246
                assert mu.reg_read(UC_X86_REG_ESP)==0x2001004
                tests+=1
    manifest=json.loads((LAB/'reports/ui-pack-manifest.json').read_text())
    for p in manifest['packages']:
        assert digest((GAME/p['archive']).read_bytes())==p['source_sha256']
        assert digest((LAB/'work/ui-pack'/p['archive']).read_bytes())==p['output_sha256']
    original=GAME/'dvd_pc/data/misc.vpp';changed=LAB/'work/ui-pack/dvd_pc/data/misc.vpp'
    a={e['name']:e for e in vpp_index(original)['entries']};b={e['name']:e for e in vpp_index(changed)['entries']}
    fonts=0
    for name in a:
        if not name.endswith('.vf2'):continue
        old=inspect_font(read_entry(original,a[name]));new=inspect_font(read_entry(changed,b[name]))
        assert len(old['glyphs'])==len(new['glyphs'])
        for g,h in zip(old['glyphs'],new['glyphs']):
            for field in ('advance','width','x','y'):assert h[field]==g[field]*2
            for field in ('code','kerning_index','flags'):assert h[field]==g[field]
        fonts+=1
    canvas=Image.new('RGB',(1050,380),'#302e29');draw=ImageDraw.Draw(canvas)
    for idx,src in enumerate([original,changed]):
        entries={e['name']:e for e in vpp_index(src)['entries']};d=read_entry(src,entries['fonts.ceg'])
        f=inspect_font(read_entry(src,entries['interface.vf2']))
        e=next(e for e in ceg_index(d)['entries'] if e['name']=='interface.vbm');atlas=decode_texture(d,e)
        y=50+idx*170;draw.text((20,y-25),'ORIGINAL' if idx==0 else 'PACOTE 2x - recursos extraidos, nao captura do jogo',fill='white')
        for text in ['WAR ZONE   ARMORY   UPGRADES','OBJECTIVES: KILL THE CRACKHOUSE LEADER']:
            x=20
            for c in text:
                g=f['glyphs'][ord(c)-f['first_code']];tile=atlas.crop((g['x'],g['y'],g['x']+g['width'],g['y']+f['height']))
                canvas.paste(tile,(x,y),tile);x+=g['advance']
            y+=f['height']+12
    canvas.save(LAB/'reports/ui-font-comparison.png')
    result=dict(emulated_video_arithmetic_cases=tests,fonts_verified=fonts,package_hashes_verified=len(manifest['packages']),in_game_verified=False)
    (LAB/'reports/ui-verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))


if __name__=='__main__':main()
