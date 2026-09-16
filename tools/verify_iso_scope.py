"""Compare entire ISO against original; only named replacement file ranges may differ."""
import argparse,hashlib,json
from pathlib import Path
import pycdlib

def verify(original, candidate, replacements):
    if original.stat().st_size != candidate.stat().st_size:
        raise ValueError('ISO size changed')
    iso=pycdlib.PyCdlib();iso.open(str(original))
    regions=[]
    try:
        for name,path in replacements.items():
            rec=iso.get_record(iso_path='/'+name+';1')
            start=rec.extent_location()*2048;n=rec.get_data_length()
            data=Path(path).read_bytes()
            if len(data)!=n:raise ValueError('payload size mismatch '+name)
            regions.append((start,start+n,name,data))
    finally:iso.close()
    regions.sort()
    if any(a[1]>b[0] for a,b in zip(regions,regions[1:])):
        raise ValueError('overlapping ISO files')
    h0=hashlib.sha256();h1=hashlib.sha256()
    with original.open('rb') as a,candidate.open('rb') as b:
        pos=0
        while block:=a.read(8*1024*1024):
            got=b.read(len(block));h0.update(block);h1.update(got)
            masked=bytearray(got)
            for start,end,name,data in regions:
                lo=max(pos,start);hi=min(pos+len(block),end)
                if hi<=lo:continue
                if got[lo-pos:hi-pos]!=data[lo-start:hi-start]:
                    raise ValueError('replacement mismatch '+name)
                masked[lo-pos:hi-pos]=block[lo-pos:hi-pos]
            if masked!=block:raise ValueError(f'undeclared ISO modification near {pos:#x}')
            pos+=len(block)
    return {'source_sha256':h0.hexdigest(),'output_sha256':h1.hexdigest(),
            'bytes':pos,'outside_replacement_ranges':0,
            'files':{name:{'offset':start,'bytes':end-start,'sha256':hashlib.sha256(data).hexdigest()} for start,end,name,data in regions}}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('original',type=Path);p.add_argument('candidate',type=Path)
    p.add_argument('replacements',nargs='+');p.add_argument('--report',type=Path)
    a=p.parse_args()
    result=verify(a.original,a.candidate,dict(x.split('=',1) for x in a.replacements))
    output=json.dumps(result,indent=2)+'\n'
    if a.report:a.report.write_text(output,encoding='utf8')
    print(output)
