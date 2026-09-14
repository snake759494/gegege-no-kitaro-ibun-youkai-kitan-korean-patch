"""Reject unintended Git files and verify the publication allowlist hashes."""
import hashlib, json, subprocess
from pathlib import Path
r = Path(__file__).resolve().parent
m = json.loads((r / 'publication_manifest.json').read_text(encoding='utf8'))
actual = set(subprocess.check_output(['git', 'ls-files', '-z'], cwd=r).decode().split('\0')) - {''}
expected = set(m['files']) | {'publication_manifest.json'}
assert actual == expected, ('unexpected/missing files', actual ^ expected)
for name, info in m['files'].items():
    p = r / name
    assert p.suffix.lower() not in {'.iso', '.bin', '.xdelta', '.ttf', '.exe', '.dll', '.png', '.jpg', '.ps1'}, name
    assert p.stat().st_size == info['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest() == info['sha256'], name
print('PASS publication allowlist:', len(actual), 'files; no game images, fonts or external executables')
