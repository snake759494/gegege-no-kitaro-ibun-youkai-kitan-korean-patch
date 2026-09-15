"""Apply the Kitaro Ibun Youkai Kitan PS2 Korean patch v1.0.1 with input, patch and output hash verification."""
import argparse
import hashlib
from pathlib import Path
import subprocess
import sys

SOURCE_SIZE = 2316861440
SOURCE_MD5 = 'a3ba2caa94c05e13aa0191f6850367b8'
SOURCE_SHA = '89ce33d0bf65b33f1fdd9ef3bae28a9700a4b0e700199f73d45633d620ad1186'
PATCH_SHA = '5109d081f24c7f042308afd13b8e6be5b811064208135c94d7f7632a2c4a17ed'
OUTPUT_SHA = 'f3d7ba5be2e2718156eb09fa7a575453c829b2da9760b7a11d9ef2a08b3db3c9'

def digest(path, kind='sha256'):
    h = hashlib.new(kind)
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('xdelta', 'source', 'patch', 'output'):
        parser.add_argument('--' + name, required=True, type=Path)
    args = parser.parse_args()
    source, patch, output, exe = (p.resolve() for p in (args.source, args.patch, args.output, args.xdelta))
    if output.exists() or output in (source, patch, exe):
        raise ValueError('Output must be a new file, different from all inputs.')
    if source.stat().st_size != SOURCE_SIZE or digest(source, 'md5') != SOURCE_MD5 or digest(source) != SOURCE_SHA:
        raise ValueError('Original ISO hash mismatch. Use the unmodified Japanese SLPM-65337 ISO listed in README.')
    if digest(patch) != PATCH_SHA:
        raise ValueError('Patch SHA-256 mismatch.')
    print('Input and patch verified. Applying...', flush=True)
    # Reserve a new file atomically. Stream decoded output into it, never overwrite an existing path.
    with output.open('xb') as out:
        subprocess.run([str(exe), '-d', '-c', '-s', str(source), str(patch)], stdout=out, check=True)
    if output.stat().st_size != SOURCE_SIZE or digest(output) != OUTPUT_SHA:
        raise ValueError('Output verification failed. Do not use the resulting file.')
    print('PASS: output SHA-256 = ' + OUTPUT_SHA)

if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print('ERROR: ' + str(exc), file=sys.stderr)
        sys.exit(1)
