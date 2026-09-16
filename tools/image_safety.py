"""Fail-closed, byte-level rules for the Japanese SLPM-65337 image assets.

These checks prove a restricted binary edit, not absence of gameplay freezes.
Runtime comparison must separately start from a cold boot or memory-card save.
"""
import hashlib
import numpy as np
from sysimg import Pack, find_packs

SOURCE_SHA256 = {
    'D_SYS': '63ecd2da54c2a413aa95a1a9ee7def98fed86aee365710cb76971b8bf51f5f67',
    'D_BG': 'db4b16fbef921566721bae959c00eef00c1131641b0c643ef3cb41823726a040',
}
SYS_GROUPS = {
    'ui': {0x40800: [31,32,33,34,35,36,37,40,41,42,43,44,45,48,49,
                       62,63,64,65,66,67,68,69,78,79,82]},
    'web': {0x96800:[1,2],0xa6000:list(range(6)),0xd6000:list(range(8))},
    'shop': {0xbf800:[4,5,6],0xd0000:list(range(6))},
    'places': {0x147800:[0,2,3,5]},
}
BG_OFFSETS = {68:0x1890800,69:0x18dc000,70:0x1927800,71:0x1973000,
              72:0x19be800,77:0x1b38000,78:0x1b83800,79:0x1bcf000,
              87:0x1d96800}


def layout(src):
    offsets = find_packs(src)
    packs = {}
    for k, off in enumerate(offsets):
        p = Pack(src, off)
        end = offsets[k+1] if k+1 < len(offsets) else len(src)
        for s in p.sprites:
            if off+s.off+p.raw_len(s.idx) > end:
                raise ValueError(f'pixel payload crosses next container: {off:#x}/{s.idx}')
        packs[off] = p
    return packs


def allowed_regions(kind, groups=None):
    if kind == 'D_SYS':
        from patch_sys import CHAPTERS
        jobs = dict(SYS_GROUPS, chapters={off:[0] for off,_ in CHAPTERS})
        selected = list(jobs) if groups is None else groups
        if not selected or set(selected)-set(jobs):
            raise ValueError('unknown/empty SYS group selection')
        return {(off,i):None for g in selected for off,ids in jobs[g].items() for i in ids}
    if kind == 'D_BG':
        from patch_bg import JOBS
        selected = list(JOBS) if groups is None else [int(g) for g in groups]
        if not selected or set(selected)-set(JOBS):
            raise ValueError('unknown/empty BG selection')
        return {(BG_OFFSETS[k],0):[box for box,_,_ in JOBS[k]] for k in selected}
    raise ValueError('unknown asset')


def validate(src, dst, kind, groups=None):
    if hashlib.sha256(src).hexdigest() != SOURCE_SHA256[kind]:
        raise ValueError('source is not the verified original '+kind)
    if len(src) != len(dst):
        raise ValueError('file size changed')
    packs = layout(src)
    regions = allowed_regions(kind,groups)
    allowed = np.zeros(len(src),dtype=np.uint8)
    for (off,i),boxes in regions.items():
        p=packs[off]; s=p.sprites[i]; start=off+s.off
        if boxes is None:
            allowed[start:start+p.raw_len(i)]=255
            if p.bpp == 4 and s.size % 2:
                allowed[start+p.raw_len(i)-1]=15
        else:
            if p.bpp != 8:
                raise ValueError('BG rectangle rule requires 8bpp')
            for x0,y0,x1,y1 in boxes:
                if not 0 <= x0 < x1 <= s.w or not 0 <= y0 < y1 <= s.h:
                    raise ValueError('rectangle outside image')
                for y in range(y0,y1):
                    allowed[start+y*s.w+x0:start+y*s.w+x1]=255
    a=np.frombuffer(src,dtype=np.uint8);b=np.frombuffer(dst,dtype=np.uint8)
    diff=np.bitwise_xor(a,b)
    illegal=np.flatnonzero(np.bitwise_and(diff,np.bitwise_not(allowed)))
    if len(illegal):
        raise ValueError(f'{len(illegal)} bytes outside approved pixels; first {int(illegal[0]):#x}')
    # Require every requested sprite to change; missing jobs must not pass.
    touched=[]
    for (off,i) in regions:
        p=packs[off];s=p.sprites[i];start=off+s.off;length=p.raw_len(i)
        if not np.any(diff[start:start+length]):
            raise ValueError(f'requested sprite unchanged: {off:#x}/{i}')
        touched.append({'pack':hex(off),'sprite':i})
    return {'kind':kind,'source_sha256':hashlib.sha256(src).hexdigest(),
            'output_sha256':hashlib.sha256(dst).hexdigest(),
            'bytes':len(src),'changed_bytes':int(np.count_nonzero(diff)),
            'containers_checked':len(packs),'sprites_changed':len(touched),
            'touched':touched,'outside_approved_pixels':0,
            'runtime_status':'not established by static validation'}
