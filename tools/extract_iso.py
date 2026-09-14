#!/usr/bin/env python3
"""Copy files out of the original PS2 ISO into extract/ (the inputs of every patch script).

Usage: python tools/extract_iso.py [ISO] [NAME ...]
Defaults: ISO = 'Gegege no Kitarou Ibun Youkai Kitan.iso' in the project root,
NAME = D_MOJI.BIN D_MESS.BIN D_CHFONT.BIN D_SYS.BIN D_BG.BIN. NAME is the ISO9660 file
name without ';1'. Existing files in extract/ are left alone.
"""
import os, sys
import pycdlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_ISO = os.path.join(ROOT, 'Gegege no Kitarou Ibun Youkai Kitan.iso')
DEFAULT_NAMES = ['D_MOJI.BIN', 'D_MESS.BIN', 'D_CHFONT.BIN', 'D_SYS.BIN', 'D_BG.BIN']

def main():
    args = sys.argv[1:]
    iso_path = args.pop(0) if args and args[0].lower().endswith('.iso') else DEFAULT_ISO
    names = args or DEFAULT_NAMES
    out_dir = os.path.join(ROOT, 'extract')
    os.makedirs(out_dir, exist_ok=True)
    iso = pycdlib.PyCdlib(); iso.open(iso_path)
    for name in names:
        dst = os.path.join(out_dir, name)
        if os.path.exists(dst):
            print(f'{name}: already extracted'); continue
        rec = iso.get_record(iso_path=f'/{name};1')
        iso.get_file_from_iso(dst, iso_path=f'/{name};1')
        print(f'{name}: LBA {rec.extent_location()}, {rec.get_data_length()} bytes -> {dst}')
    iso.close()

if __name__ == '__main__':
    main()
