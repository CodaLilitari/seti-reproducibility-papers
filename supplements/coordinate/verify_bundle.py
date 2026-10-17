#!/usr/bin/env python3
"""Read-only check of this writing bundle's file manifest, not scientific truth."""
from pathlib import Path
import hashlib, json, sys

def main(root: Path) -> None:
    root=root.resolve()
    data=json.loads((root/'MANIFEST_SHA256.json').read_text(encoding='utf-8'))
    names=set()
    for r in data['files']:
        p=(root/r['path']).resolve()
        if not p.is_relative_to(root) or r['path'] in names:raise ValueError('Unsafe or duplicate member')
        names.add(r['path'])
        raw=p.read_bytes()
        if len(raw)!=r['bytes'] or hashlib.sha256(raw).hexdigest()!=r['sha256']:raise ValueError('Mismatch: '+r['path'])
    actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    if actual!=names|{'MANIFEST_SHA256.json'}:raise ValueError('Unlisted or missing files')
    print(f'PASS: {len(names)} payload sizes and SHA-256 hashes. No scientific pipelines executed.')
if __name__=='__main__':
    try: main(Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent)
    except (OSError,ValueError,KeyError) as exc: raise SystemExit(f'VERIFICATION FAILED: {exc}')
