import json
from punisher_lab import *

report=[]
errors=[]
for archive in json.loads((LAB/'reports/inventory.json').read_text())['archives']:
    for entry in archive['entries']:
        if not entry['name'].lower().endswith('.ceg'): continue
        try:
            data=read_entry(GAME/archive['path'],entry)
            info=ceg_index(data)
            report.append(dict(archive=archive['path'],name=entry['name'],textures=info['entries']))
        except Exception as exc:
            errors.append(dict(archive=archive['path'],name=entry['name'],error=str(exc)))
result=dict(containers=report,errors=errors)
(LAB/'reports/textures.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(dict(containers=len(report),records=sum(len(c['textures']) for c in report),errors=errors),indent=2))
