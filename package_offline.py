#!/usr/bin/env python3
"""Build the final all-local photo-inclusive ZIP after fetching the public JPEGs."""
from pathlib import Path
import json,zipfile,hashlib,sys
ROOT=Path(__file__).resolve().parent
PARENT=ROOT.parent
photo_meta=json.loads((ROOT/'photos/manifest.json').read_text(encoding='utf-8'))['photos']
missing=[]
for p in photo_meta:
    file=ROOT/'photos'/p['filename']
    if not file.exists() or file.stat().st_size < 15000 or file.read_bytes()[:3]!=b'\xff\xd8\xff':
        missing.append(p['filename'])
if missing:
    print('OFFLINE PACKAGE NOT CREATED. These licensed JPEGs are missing:')
    print('  '+'\n  '.join(missing))
    print('Run GET_PHOTOS_WINDOWS.cmd, or follow PHOTO_RECOVERY.md to save them manually.')
    print('Every file must be a real JPEG saved in the photos subfolder.')
    raise SystemExit(2)
name=PARENT/'IONIAN_SANCTUARY_OFFLINE_WITH_PHOTOS.zip'
exclude={'UI_PREVIEW.png','package_offline.pyc'}
with zipfile.ZipFile(name,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for path in sorted(ROOT.rglob('*')):
        if not path.is_file() or '__pycache__' in path.parts or path.name in exclude or path.suffix=='.pyc':continue
        rel=path.relative_to(ROOT)
        if rel.parts and rel.parts[0]=='results' and path.suffix not in {'.json','.md','.html','.jsonl'}:continue
        z.write(path,arcname=f'{ROOT.name}/{rel.as_posix()}')
size=name.stat().st_size
print('OFFLINE ZIP:',name)
print('Size:',f'{size/1024**2:.1f} MB')
print('Four original licensed photographs included as local JPEG files.')
print('SHA-256:',hashlib.sha256(name.read_bytes()).hexdigest())
if size>50*1024**2:
    print('WARNING: Over the 50 MB limit. Reduce nonrequired results before submission.',file=sys.stderr)
    raise SystemExit(3)
