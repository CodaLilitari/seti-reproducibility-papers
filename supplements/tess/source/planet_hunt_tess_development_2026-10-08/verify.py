"""Read-only verification of the delivered package; no network access."""
from pathlib import Path
import hashlib,json,gzip
p=Path(__file__).resolve().parent
rows=json.loads((p/'MANIFEST.json').read_text())
for r in rows:
    f=p/r['path'];b=f.read_bytes()
    if len(b)!=r['bytes'] or hashlib.sha256(b).hexdigest()!=r['sha256']:
        raise RuntimeError('Integrity mismatch: '+r['path'])
if gzip.decompress((p/'data/toi270_s4_binned.csv.gz').read_bytes())!=(p/'data/toi270_s4_binned.csv').read_bytes():
    raise RuntimeError('Decompression mismatch')
print(f'PASS: {len(rows)} manifest files and byte-identical CSV decompression')
