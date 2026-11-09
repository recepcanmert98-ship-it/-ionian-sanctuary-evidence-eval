#!/usr/bin/env python3
"""Import downloaded, attributed Wikimedia JPEGs without making HTTP requests.

The user selects each original photograph saved from its official Commons page.
This module cannot authenticate an image's subject; it validates file integrity,
records SHA256/provenance as operator-selected, and never generates substitutes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import webbrowser

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / 'photos' / 'manifest.json'
PHOTOS = ROOT / 'photos'
MIN_BYTES = 12_000
MAX_BYTES = 45 * 1024 * 1024


def valid_jpeg(path: Path) -> tuple[bool, str]:
    if not path.is_file():
        return False, 'file not found'
    size = path.stat().st_size
    if not MIN_BYTES <= size <= MAX_BYTES:
        return False, f'file size {size:,} bytes outside 12 KB–45 MB range'
    with path.open('rb') as f:
        start = f.read(3)
        f.seek(-2, 2)
        end = f.read(2)
    if start != b'\xff\xd8\xff' or end != b'\xff\xd9':
        return False, 'not a complete JPEG image (a webpage or WebP is not acceptable)'
    return True, 'valid JPEG structure'


def items() -> list[dict]:
    return json.loads(MANIFEST.read_text(encoding='utf-8'))['photos']


def write_integrity(entries: list[dict]) -> dict:
    records = []
    for item in entries:
        file = PHOTOS / item['filename']
        valid, _ = valid_jpeg(file)
        if valid:
            records.append({'id': item['id'], 'filename': item['filename'],
                            'bytes': file.stat().st_size,
                            'sha256': hashlib.sha256(file.read_bytes()).hexdigest(),
                            'source': item['source']})
    report = {
        'retrieved': records, 'count': len(records), 'needed': len(entries),
        'format': 'JPEG',
        'method': 'user-selected manual import; the image subject must be checked by the operator',
        'note': 'A checksum proves byte integrity after import, not source identity or licensing.'
    }
    (PHOTOS / 'download_integrity.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return report


def copy_jpeg(source: Path, target: Path) -> None:
    ok, why = valid_jpeg(source)
    if not ok:
        raise ValueError(f'{source}: {why}')
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.resolve() != target.resolve():
        shutil.copyfile(source, target)
    ok, why = valid_jpeg(target)
    if not ok:
        raise ValueError(f'copied target {target}: {why}')


def select_interactively(entries: list[dict], open_pages: bool = False) -> None:
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox
    except ImportError as exc:
        raise RuntimeError('Python Tkinter is not installed. Save JPGs directly into the photos folder instead.') from exc

    root = tk.Tk()
    root.withdraw()
    try:
        for i, item in enumerate(entries, 1):
            target = PHOTOS / item['filename']
            if valid_jpeg(target)[0]:
                print(f'EXISTS {i}/4: {item["filename"]}')
                continue
            instruction = (f'Photograph {i} of {len(entries)}: {item["name"]}\n\n'
                           'Open its Wikimedia Commons source in your browser. Click the '
                           '960-pixel image preview and use Save image as... (JPEG).\n\n'
                           'Then press OK to locate the saved file using a file chooser.\n'
                           f'Target file: {item["filename"]}\n\nSource: {item["source"]}')
            print('\n' + instruction, flush=True)
            if open_pages:
                webbrowser.open_new_tab(item['source'])
            messagebox.showinfo('Ionian Sanctuary — licensed photo import', instruction, parent=root)
            while True:
                selected = filedialog.askopenfilename(
                    parent=root,
                    title=f'Select the photo of {item["name"]}',
                    initialdir=str(Path.home() / 'Downloads'),
                    filetypes=[('JPEG images', '*.jpg *.jpeg'), ('All files', '*.*')],
                )
                if not selected:
                    print(f'SKIPPED: {item["filename"]}')
                    break
                source = Path(selected)
                ok, why = valid_jpeg(source)
                if not ok:
                    messagebox.showerror('File rejected', f'{source.name}\n\n{why}\n\nSelect the actual JPEG, not an HTML page or WebP.', parent=root)
                    continue
                if not messagebox.askyesno('Confirm photograph',
                      f'Please confirm this is the photograph from the following Wikimedia source:\n\n'
                      f'{item["name"]}\n{item["source"]}\n\n'
                      f'Import selected file: {source.name}?', parent=root):
                    continue
                copy_jpeg(source, target)
                print(f'SAVED: {target.name} ({target.stat().st_size:,} bytes)')
                break
    finally:
        root.destroy()


def main(argv=None):
    parser = argparse.ArgumentParser(description='Import four real archaeological photographs; no network requests or credentials.')
    parser.add_argument('--check', action='store_true', help='Verify local JPEGs and record SHA256; never fetch')
    parser.add_argument('--interactive', action='store_true', help='Choose four photos using graphical file dialogs')
    parser.add_argument('--open-sources', action='store_true', help='Open the Commons source pages as you import')
    args=parser.parse_args(argv)
    entries=items()
    if args.interactive:
        select_interactively(entries, open_pages=args.open_sources)
    report=write_integrity(entries)
    print(f'\n{report["count"]}/{report["needed"]} genuine JPEG files stored in {PHOTOS}')
    missing=[entry for entry in entries if not valid_jpeg(PHOTOS / entry['filename'])[0]]
    if missing:
        print('Missing or invalid files:')
        for entry in missing:
            print(f'  {entry["filename"]}: {entry["source"]}')
        print('Run IMPORT_PHOTOS_WINDOWS.cmd and choose each original Wikimedia photo you saved.')
        return 2
    print('All required JPEGs are valid. Now double-click BUILD_OFFLINE_WINDOWS.cmd.')
    return 0

if __name__ == '__main__':
    sys.exit(main())
