#!/usr/bin/env python3
"""Patch files of the same size into a copy of the PS2 ISO in place (no filesystem rebuild).

Usage: python build_iso.py ORIG.iso OUT.iso NAME=replacement.bin [NAME=file ...]
NAME is the ISO9660 file name without ';1', e.g. D_MOJI.BIN
"""
import sys, os, shutil
import pycdlib

def main():
    orig, out = sys.argv[1], sys.argv[2]
    repl = dict(a.split('=', 1) for a in sys.argv[3:])
    iso = pycdlib.PyCdlib(); iso.open(orig)
    plan = []
    for name, path in repl.items():
        rec = iso.get_record(iso_path=f'/{name};1')
        lba, size = rec.extent_location(), rec.get_data_length()
        data = open(path, 'rb').read()
        if len(data) != size:
            sys.exit(f'{name}: replacement is {len(data)} bytes, original is {size}; sizes must match')
        plan.append((name, lba, size, data))
        print(f'{name}: LBA {lba} (offset {lba*2048:#x}), {size} bytes <- {path}')
    iso.close()
    if not (os.path.exists(out) and os.path.getsize(out) == os.path.getsize(orig)):
        print('copying ISO ...'); shutil.copyfile(orig, out)
    else:
        print('reusing existing output ISO (same size); overwriting patched regions')
    with open(out, 'r+b') as f:
        for name, lba, size, data in plan:
            f.seek(lba * 2048); f.write(data)
        # verify
        for name, lba, size, data in plan:
            f.seek(lba * 2048); assert f.read(size) == data, name
    print('done:', out)

if __name__ == '__main__':
    main()
