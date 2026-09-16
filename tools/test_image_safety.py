"""Regression checks using the user's local original assets; never publishes assets."""
import unittest,sys,subprocess,tempfile,struct
from pathlib import Path
from unittest.mock import patch
import koimg
from sysimg import Pack
from image_safety import validate,layout

ROOT=Path(__file__).resolve().parent.parent

class SafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src=(ROOT/'extract/D_SYS.BIN').read_bytes()
        cls.dst=(ROOT/'validation_20260916/D_SYS_candidate.BIN').read_bytes()
        cls.bg=(ROOT/'extract/D_BG.BIN').read_bytes()
        cls.bgdst=(ROOT/'validation_20260916/D_BG_candidate.BIN').read_bytes()

    def test_declared_payloads_pass(self):
        self.assertEqual(validate(self.src,self.dst,'D_SYS')['sprites_changed'],99)
        self.assertEqual(validate(self.bg,self.bgdst,'D_BG')['sprites_changed'],9)

    def test_unapproved_sprite_rejected(self):
        bad=bytearray(self.dst);p=Pack(self.src,0x40800)
        bad[p.base+p.sprites[0].off]^=1
        with self.assertRaisesRegex(ValueError,'outside approved'):validate(self.src,bad,'D_SYS')

    def test_metadata_rejected(self):
        bad=bytearray(self.dst);bad[0x40804]^=1
        with self.assertRaisesRegex(ValueError,'outside approved'):validate(self.src,bad,'D_SYS')

    def test_rectangle_outside_rejected(self):
        bad=bytearray(self.bgdst);p=Pack(self.bg,0x1890800)
        bad[p.base+p.sprites[0].off]^=1
        with self.assertRaisesRegex(ValueError,'outside approved'):validate(self.bg,bad,'D_BG')

    def test_partial_intersection_does_not_hide_escape(self):
        bad=bytearray(self.dst);p=Pack(self.src,0x40800);s=p.sprites[31]
        bad[p.base+s.off-1]^=1
        bad[p.base+s.off]^=1
        with self.assertRaisesRegex(ValueError,'outside approved'):validate(self.src,bad,'D_SYS')

    def test_wrong_source_and_size_rejected(self):
        with self.assertRaises(ValueError):validate(self.dst,self.dst,'D_SYS')
        with self.assertRaises(ValueError):validate(self.src,self.dst+b'\0','D_SYS')

    def test_wide_palette_is_still_4bpp(self):
        p=Pack(self.src,0x92000)
        self.assertEqual(p.bpp,4)
        self.assertEqual(p.raw_len(0),16384)
        self.assertLess(p.base+p.sprites[0].off+p.raw_len(0),0x96800)

    def test_all_pixels_roundtrip_without_touching_metadata(self):
        for src in (self.src,self.bg):
            for p in layout(src).values():
                for s in p.sprites:p.put_indices(s.idx,p.indices(s.idx))
                self.assertEqual(bytes(p.data),src)

    def test_out_of_range_palette_index_rejected(self):
        p=Pack(self.src,0x484800);idx=p.indices(0);idx[0]=16
        with self.assertRaises(ValueError):p.put_indices(0,idx)

    def test_palette_cache_does_not_depend_on_object_id(self):
        # Recycled ids caused cross-image cache contamination in the old code.
        koimg._NEAR.clear()
        with patch.object(koimg,'id',lambda _:7,create=True):
            self.assertEqual(koimg._nearest([(0,0,0),(255,255,255)],(255,255,255)),1)
            self.assertEqual(koimg._nearest([(255,255,255),(0,0,0)],(255,255,255)),0)

    def test_iso_existing_output_refused_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);a=p/'source.iso';b=p/'existing.iso'
            a.write_bytes(b'original');b.write_bytes(b'previous')
            result=subprocess.run([sys.executable,str(ROOT/'tools/build_iso.py'),str(a),str(b)],capture_output=True)
            self.assertNotEqual(result.returncode,0)
            self.assertEqual(a.read_bytes(),b'original')
            self.assertEqual(b.read_bytes(),b'previous')

if __name__=='__main__':unittest.main()
