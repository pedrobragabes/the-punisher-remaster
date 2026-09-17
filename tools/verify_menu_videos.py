import json
import cv2
from punisher_lab import LAB,digest


def main():
    report=json.loads((LAB/'reports/ui-video-manifest.json').read_text())
    if not report['complete']:raise ValueError('Video conversion is not complete')
    results=[]
    for item in report['videos']:
        path=LAB/'work/ui-pack'/item['archive']
        assert digest(path.read_bytes())==item['output_sha256']
        c=cv2.VideoCapture(str(path))
        assert c.isOpened(),str(path)
        assert int(c.get(cv2.CAP_PROP_FRAME_COUNT))==item['after']['frames']
        for frame in (0,item['after']['frames']-1):
            c.set(cv2.CAP_PROP_POS_FRAMES,frame);ok,image=c.read()
            assert ok,(str(path),frame)
            assert image.shape[:2]==(item['after']['height'],item['after']['width'])
        c.release();results.append(item['archive'])
    out=dict(videos_checked=len(results),first_and_last_frame_decode=True,files=results,in_game_verified=False)
    (LAB/'reports/ui-video-verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
    print(f'{len(results)} videos: hashes, frame counts, first/last frame decode OK')


if __name__=='__main__':main()
