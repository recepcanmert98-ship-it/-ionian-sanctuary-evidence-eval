"""Freeze and verify source/task/photograph manifests without relying on a digital signature."""
from __future__ import annotations
from pathlib import Path
import hashlib,json,argparse
ROOT=Path(__file__).resolve().parent
PATHS=['README.md','PHOTO_RECOVERY.md','PHOTOGRAPH_CREDITS.md','photos/manifest.json','sources/source_manifest.json','reference/answers.json','grade_responses.py','build_worksheet.py','fetch_photos.py','import_photos.py','package_offline.py','verify_package.py','START_WINDOWS.cmd','IMPORT_PHOTOS_WINDOWS.cmd','BUILD_OFFLINE_WINDOWS.cmd']
PATHS += [str(p.relative_to(ROOT)).replace('\\','/') for p in sorted((ROOT/'tasks').glob('*.json'))]

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def run(freeze=False):
    path=ROOT/'source_integrity.json'
    if freeze:
        data={'hash_algorithm':'SHA-256','files':{p:digest(ROOT/p) for p in PATHS}}
        path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
        print('Manifest frozen:',len(PATHS),'files');return True
    data=json.loads(path.read_text(encoding='utf-8'))['files']
    wrong=[p for p,h in data.items() if not (ROOT/p).exists() or digest(ROOT/p)!=h]
    print('Source integrity:', 'PASS' if not wrong else 'FAIL',f'({len(data)-len(wrong)}/{len(data)})')
    for p in wrong:print('Mismatch:',p)
    photos=ROOT/'photos'/'download_integrity.json'
    if photos.exists():
        record=json.loads(photos.read_text(encoding='utf-8'))
        wrong_media=[x['filename'] for x in record.get('retrieved',[]) if not (ROOT/'photos'/x['filename']).exists() or digest(ROOT/'photos'/x['filename'])!=x['sha256']]
        print('Downloaded photograph integrity:', 'PASS' if not wrong_media else 'FAIL')
        wrong.extend(wrong_media)
    else:print('Local photograph integrity: no download yet (online gallery is available)')
    return not wrong
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--freeze',action='store_true');args=parser.parse_args();raise SystemExit(0 if run(args.freeze) else 1)
