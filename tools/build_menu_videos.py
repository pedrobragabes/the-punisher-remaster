"""Resample menu/briefing videos with the official Bink 1 encoder.
Preserves frame counts, timebase and audio track count; original files untouched.
"""
import json
import struct
import subprocess
from concurrent.futures import ThreadPoolExecutor,as_completed
from punisher_lab import LAB,GAME,digest


def header(path):
    with path.open('rb') as f: raw=f.read(44)
    v=struct.unpack('<4s10I',raw)
    if v[1]+8 != path.stat().st_size: raise ValueError(f'Incomplete Bink file: {path}')
    return dict(magic=v[0].decode('ascii'),frames=v[2],width=v[5],height=v[6],fps_num=v[7],fps_den=v[8],audio_tracks=v[10])


def main():
    encoder=LAB/'work/radtools/portable/radvideo64.exe'
    output=LAB/'work/ui-pack'
    manifest=[]
    videos=[p for p in (GAME/'dvd_pc/data/movies').rglob('*.bik') if p.name.startswith(('bf_','wz_')) or '_' in p.stem]
    def convert(source):
        relative=source.relative_to(GAME); target=output/relative;target.parent.mkdir(parents=True,exist_ok=True)
        old=header(source)
        w,h=(960,720) if source.name.startswith('bf_') else (1280,960)
        temporary=target.with_suffix('.building.bik')
        args=[str(encoder),'binkc',str(source),str(temporary),f'/({w}',f'/){h}','/D2000000','/L0','/U4','/O','/#']
        try:
            existing=header(target)
            reusable=existing['frames']==old['frames'] and (existing['width'],existing['height'])==(w,h)
        except (OSError,ValueError,struct.error): reusable=False
        if not reusable:
            startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
            result=subprocess.run(args,timeout=600,startupinfo=startup,creationflags=subprocess.CREATE_NO_WINDOW)
            if result.returncode:raise RuntimeError(f'Encoder failed: {source.name}: {result.returncode}')
            header(temporary)
            temporary.replace(target)
        new=header(target)
        assert new['magic']==old['magic']=='BIKi'
        assert (new['width'],new['height'])==(w,h)
        for k in ('frames','fps_num','fps_den','audio_tracks'):assert new[k]==old[k],(source.name,k,old[k],new[k])
        return dict(archive=relative.as_posix(),source_sha256=digest(source.read_bytes()),output_sha256=digest(target.read_bytes()),before=old,after=new)
    with ThreadPoolExecutor(max_workers=3) as executor:
        for future in as_completed([executor.submit(convert,p) for p in videos]):
            result=future.result();manifest.append(result)
            (LAB/'reports/ui-video-manifest.json').write_text(json.dumps(dict(complete=len(manifest)==len(videos),videos=manifest,total=len(videos),method='Bink bicubic resampling; no AI detail reconstruction'),indent=2),encoding='utf-8')
            print(f"{len(manifest)}/{len(videos)} {result['archive']}",flush=True)


if __name__=='__main__':main()
