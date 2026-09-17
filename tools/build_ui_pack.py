"""Experimental 2x UI pack. Builds from originals; never writes the installation.
Texture resampling preserves artwork, it is not AI detail reconstruction.
"""
import io
import json
import re
import struct
from PIL import Image
from punisher_lab import LAB, GAME, vpp_index, read_entry, ceg_index, rebuild_vpp, digest, replace_texture
from inspect_ui import inspect_font

OUT = LAB/'work/ui-pack'
CHANGES = []
SKIPPED = []


def pow2(n):
    return max(4, 1 << (n-1).bit_length())


def scale_ceg(data, container, select=lambda e: True, font=False):
    entries = ceg_index(data)['entries']
    payloads = {}
    for e in entries:
        if not select(e):
            continue
        w, h, n = e['width'], e['height'], e['frames_or_levels']
        if e['format'] == 7 and n == 1 and e['span'] == w*h*4 and e['length'] == w*h:
            source_image = Image.frombytes('RGBA', (w,h), data[e['offset']:e['offset']+e['span']], 'raw', 'BGRA')
            im = source_image.resize((w*2,h*2), Image.Resampling.NEAREST if font else Image.Resampling.LANCZOS)
            if isinstance(font,dict) and e['name'] in font:
                f=font[e['name']]
                for g in f['glyphs']:
                    if g['width']<=0: continue
                    x,y=g['x'],g['y'];gw=g['width'];gh=f['height']
                    assert x>=0 and y>=0 and x+gw<=w and y+gh<=h
                    # Filter each glyph separately so neighbouring characters never bleed in.
                    tile=source_image.crop((x,y,x+gw,y+gh)).resize((gw*2,gh*2),Image.Resampling.LANCZOS)
                    im.paste(tile,(x*2,y*2))
            payloads[e['index']] = (im.tobytes('raw','BGRA'), w*2,h*2,w*h*4)
        elif e['format'] == 15 and n >= 1 and e['length'] == pow2(w)*pow2(h) and e['span'] == e['length']*n:
            frames = []
            for f in range(n):
                start = e['offset']+f*e['length']
                im = Image.frombytes('RGBA',(pow2(w),pow2(h)),data[start:start+e['length']],'bcn',3).crop((0,0,w,h))
                im = im.resize((w*2,h*2),Image.Resampling.LANCZOS)
                padded = Image.new('RGBA',(pow2(w*2),pow2(h*2)))
                padded.paste(im,(0,0))
                stream = io.BytesIO(); padded.save(stream,format='DDS',pixel_format='DXT5')
                frames.append(stream.getvalue()[128:])
            payloads[e['index']] = (b''.join(frames),w*2,h*2,len(frames[0]))
        else:
            SKIPPED.append(dict(container=container,texture=e['name'],reason='Unverified pixel layout'))
            continue
        CHANGES.append(dict(container=container,texture=e['name'],before=[w,h],after=[w*2,h*2],frames=n))
    if not payloads:
        return data
    ordered = sorted(entries,key=lambda e:e['offset'])
    assert len({e['offset'] for e in entries}) == len(entries)
    result = bytearray(data[:ordered[0]['offset']])
    for e in ordered:
        offset = len(result)
        p = 32+48*e['index']
        if e['index'] in payloads:
            payload,w,h,length = payloads[e['index']]
            result.extend(payload)
            struct.pack_into('<HH',result,p+4,w,h)
            struct.pack_into('<I',result,p+40,length)
        else:
            result.extend(data[e['offset']:e['offset']+e['span']])
        struct.pack_into('<I',result,p,offset)
    struct.pack_into('<I',result,12,struct.unpack_from('<I',data,12)[0]+len(result)-len(data))
    new = ceg_index(result)['entries']
    for a,b in zip(entries,new,strict=True):
        if a['index'] not in payloads:
            assert data[a['offset']:a['offset']+a['span']] == result[b['offset']:b['offset']+b['span']]
        else:
            assert result[b['offset']:b['offset']+b['span']] == payloads[a['index']][0]
    return bytes(result)


def scale_font(data):
    info = inspect_font(data)
    out = bytearray(data)
    count = info['glyph_count']; pairs = info['kerning_pair_count']
    # Width/height metrics; source bitmap byte counts/offsets describe 16-bit pixels.
    for offset in (20,24):
        struct.pack_into('<I',out,offset,struct.unpack_from('<I',data,offset)[0]*2)
    struct.pack_into('<I',out,36,struct.unpack_from('<I',data,36)[0]*4)
    for i in range(pairs):
        k = struct.unpack_from('<b',data,64+i*4+2)[0]*2
        if not -128 <= k <= 127:
            raise ValueError('Kerning overflow')
        struct.pack_into('<b',out,64+i*4+2,k)
    base = 64+pairs*4
    for i in range(count):
        p = base+i*16
        a,w,o = struct.unpack_from('<iii',data,p)
        struct.pack_into('<iii',out,p,a*2,w*2,o*4)
    for i in range(count*2):
        p = base+count*16+i*4
        struct.pack_into('<i',out,p,struct.unpack_from('<i',data,p)[0]*2)
    check = inspect_font(out)
    assert check['height'] == info['height']*2
    assert check['glyph_count'] == count
    return bytes(out)


def gui(data):
    lines = []
    section = ''
    # Fullscreen surfaces keep their preset geometry for the widescreen hook.
    surfaces = {'main_pic','loading_pic','wz_map_bmp','walls_bmp','ay_movie','ay_weapons','cc_photos','nc_clippings'}
    briefing = {
        'bf_action_list':(60,100,500,220), 'bf_movie':(650,100,960,720),
        'bf_detail_bg':(30,340,560,460), 'bf_heading_text':(60,360,500,50),
        'bf_obj_1':(60,420,500,100), 'bf_obj_2':(60,540,500,100),
        'bf_obj_3':(60,660,500,100), 'bf_challenge':(60,420,500,330),
        'bf_rifle':(100,440,-1,-1), 'bf_l_pistol':(100,550,-1,-1),
        'bf_r_pistol':(100,660,-1,-1), 'bf_briefing_text':(650,860,1000,160),
    }
    for line in data.decode('ascii').splitlines(keepends=True):
        if line.startswith('#'): section=line.strip()[1:]
        m = re.match(r'(\$Name:\s*"([^"]+)"\s+)(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)([^\r\n]*)(\r?\n)?$',line)
        if m and re.fullmatch(r'\d+x\d+',section):
            name=m[2]; old=[int(m[i]) for i in range(3,7)]; values=old[:]
            if name in briefing:
                values=briefing[name]
            elif name not in surfaces:
                values=[v*2 if v != -1 else v for v in old]
                if name.startswith('cg_') and name.endswith('_sizing'):
                    values=old # Fixed grid: higher-resolution textures, same cell geometry.
                if name == 'cg_thumb_area': values=old
                if name in ('start_text','exit_text'):
                    values=[old[0],old[1]+(30 if name=='exit_text' else 0),old[2]*2,old[3]*2]
                if name in ('ay_name','ay_desc','cc_name','cc_desc','nc_name'):
                    values=[old[0]*2,old[1]*2,old[2],old[3]*2]
                if name == 'ap_action_bg': values=[60,184,600,360]
                if name in ('wz_high_score_text','wz_high_score','wz_medal_text','wz_medal_bmp'):
                    values=[old[0],old[1]*2,old[2]*2 if old[2]>0 else old[2],old[3]*2 if old[3]>0 else old[3]]
            line=m[1]+'\t'.join(map(str,values))+m[7]+(m[8] or '')
        lines.append(line)
    return ''.join(lines).encode('ascii')


def hud(data):
    # Match the categories treated specially by upstream HudHook.
    section=''; row=0; lines=[]
    relative={0,2,3,4,5,8,9,10,11}
    for line in data.decode('ascii').splitlines(keepends=True):
        if line.startswith('#'):
            section=line.strip()[1:];row=0
        m=re.match(r'(\s*)(-?\d+)\s+(-?\d+)(\s*//.*?)(\r?\n)?$',line)
        if m and re.fullmatch(r'\d+x\d+',section):
            w,h=map(int,section.split('x'));x,y=int(m[2]),int(m[3])
            if row in relative: x*=2;y*=2
            elif row==1: x*=2;y=h-180 # Leave room for the enlarged health cluster.
            elif row in (7,15,28): x=w-2*(w-x);y=max(50,y-50)
            line=f'{m[1]}{x}\t{y}{m[4]}'+(m[5] or '')
            row+=1
        lines.append(line)
    return ''.join(lines).encode('ascii')


def package(relative, transforms):
    source=GAME/relative; entries=vpp_index(source)['entries']; replacements={}
    for e in entries:
        if e['name'] in transforms:
            old=read_entry(source,e); new=transforms[e['name']](old)
            if new != old: replacements[e['name']]=new
    if not replacements: return None
    path=OUT/relative;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(rebuild_vpp(source,replacements))
    after=vpp_index(path)['entries']
    for a,b in zip(entries,after,strict=True):
        assert a['name']==b['name']
        assert read_entry(path,b)==replacements.get(a['name'],read_entry(source,a))
    return dict(archive=relative,source_sha256=digest(source.read_bytes()),output_sha256=digest(path.read_bytes()),entries_changed=list(replacements),entries_verified=len(entries))


def main():
    manifest=[]
    misc=GAME/'dvd_pc/data/misc.vpp';transforms={}
    misc_entries={e['name']:e for e in vpp_index(misc)['entries']}
    for e in misc_entries.values():
        name=e['name']
        if name.endswith('.vf2'):
            transforms[name]=scale_font
        elif name.startswith('fonts') and name.endswith('.ceg'):
            suffix=name[len('fonts'):-len('.ceg')]
            metrics={}
            for stem in ('digital_small','hud','interface','score','title'):
                vf=stem+suffix+'.vf2'
                if vf not in misc_entries: vf=stem+'.vf2'
                metrics[stem+'.vbm']=inspect_font(read_entry(misc,misc_entries[vf]))
            transforms[name]=lambda d,n=name,f=metrics:scale_ceg(d,n,font=f)
        elif name.startswith(('int-','wep_icons')) and name.endswith('.ceg'):
            transforms[name]=lambda d,n=name:scale_ceg(d,n)
    apartment=LAB/'work/apartment-restored-generated.png'
    if apartment.exists():
        resized=LAB/'work/apartment-ui-1280.png'
        Image.open(apartment).convert('RGBA').resize((1280,960),Image.Resampling.LANCZOS).save(resized)
        transforms['int-mainmenu.ceg']=lambda d:replace_texture(scale_ceg(d,'int-mainmenu.ceg'),'apartment_bg.tga',resized)
    manifest.append(package('dvd_pc/data/misc.vpp',transforms))
    pc=GAME/'dvd_pc/data/misc_pc.vpp'
    if pc.exists():
        result=package('dvd_pc/data/misc_pc.vpp',{e['name']:(lambda d,n=e['name']:scale_ceg(d,n)) for e in vpp_index(pc)['entries'] if e['name'].startswith('int-') and e['name'].endswith('.ceg')})
        if result:manifest.append(result)
    manifest.append(package('dvd_pc/data/tables.vpp',{'gui.tbl':gui,'hud.tbl':hud}))
    prefixes=('meters_','health.','slaughter.','reserve_bar.','score_blood.','paper_popup.','ret_','reticle_','ingame_menu_bg.')
    manifest.append(package('dvd_pc/data/mini.vpp',{'always_loaded.ceg':lambda d:scale_ceg(d,'always_loaded.ceg',lambda e:e['name'].startswith(prefixes))}))
    # Extras remain separate packages, preserving labels and page artwork.
    for source in sorted((GAME/'dvd_pc/data/extras').rglob('*.vpp')):
        trans={e['name']:(lambda d,n=e['name']:scale_ceg(d,n)) for e in vpp_index(source)['entries'] if e['name'].endswith('.ceg')}
        result=package(source.relative_to(GAME).as_posix(),trans)
        if result:manifest.append(result)
    report=dict(packages=manifest,textures=CHANGES,skipped=SKIPPED,font_scale=2,
                in_game_verified=False,method='2x texture resampling, matching VFNT metrics, menu/HUD layout edits; not reconstructed detail')
    (LAB/'reports/ui-pack-manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(dict(packages=len(manifest),textures=len(CHANGES),skipped=len(SKIPPED))),flush=True)


if __name__=='__main__':main()
