"""Read-only stdlib integrity check; never imports the scientific modules."""
from pathlib import Path, PurePosixPath
import hashlib
import json

def main():
    root = Path(__file__).resolve().parent
    manifest = root / 'MANIFEST_SHA256.json'
    data = json.loads(manifest.read_text(encoding='utf-8'))
    rows = data['files']
    expected = set()
    folded = set()
    failures = []
    for row in rows:
        name = row['path']
        rel = PurePosixPath(name)
        if (not name or rel.is_absolute() or '..' in rel.parts or str(rel) != name
                or '\\' in name or ':' in name or name == manifest.name
                or name.casefold() in folded):
            raise ValueError('Invalid or duplicate manifest path')
        folded.add(name.casefold())
        expected.add(name)
        path = root / name
        if any(p.is_symlink() for p in [path, *path.parents] if p != root.parent):
            raise ValueError('Symlink not accepted')
        if not path.is_file() or not path.resolve().is_relative_to(root):
            failures.append({'path': name, 'reason': 'missing_or_outside'})
            continue
        content = path.read_bytes()
        if len(content) != row['bytes'] or hashlib.sha256(content).hexdigest() != row['sha256']:
            failures.append({'path': name, 'reason': 'size_or_sha256'})
    actual = set()
    for path in root.rglob('*'):
        if path.is_symlink():
            raise ValueError('Unexpected symlink')
        if path.is_file() and path != manifest:
            actual.add(path.relative_to(root).as_posix())
    extra = sorted(actual - expected)
    missing = sorted(expected - actual)
    result = {'scope': 'file integrity only; no scientific execution',
              'manifest_entries': len(rows), 'failures': failures,
              'extra_files': extra, 'missing_files': missing,
              'successful': not (failures or extra or missing),
              'manifest_sha256': hashlib.sha256(manifest.read_bytes()).hexdigest()}
    print(json.dumps(result, indent=2))
    if not result['successful']:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
