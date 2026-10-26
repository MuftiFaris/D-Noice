import base64
import importlib.util
import json
import random
import time
import unittest
from pathlib import Path
import denoise_manual as core
import server
from test_lesson_engine import Request


class VisualTests(unittest.TestCase):
    def test_every_preview_contains_only_completed_output_rows(self):
        rng=random.Random(3)
        image=[[rng.randrange(256) for x in range(9)] for y in range(25)]
        for fn in (core.median_filter,core.adaptive_median_filter,core.gaussian_filter):
            snapshots=[]
            result=fn(image,on_preview=lambda rows,done,total:snapshots.append((done,total,[r[:] for r in rows[:done]])))
            self.assertEqual(len(snapshots),25)
            for done,total,rows in snapshots:
                self.assertEqual(total,25)
                self.assertEqual(rows,result[:done])

    def test_streamed_frames_match_manual_partial_and_final_images(self):
        image=[[255 if (x+y)%4==0 else x*10+y for x in range(9)] for y in range(25)]
        token='visual-test'
        server.SESSIONS[token]=dict(clean=image,noisy=image,results={},created=time.monotonic(),busy=False)
        try:
            for method,fn in enumerate((core.median_filter,core.adaptive_median_filter,core.gaussian_filter)):
                req=Request('/api/process',dict(session=token,method=method));server.Handler.do_POST(req)
                events=[json.loads(line) for line in req.wfile.getvalue().splitlines()]
                frames=[e for e in events if e['type']=='preview']
                self.assertGreater(len(frames),1)
                restored=fn(image)
                for frame in frames:
                    expected=restored[:frame['done']]+image[frame['done']:]
                    self.assertEqual(base64.b64decode(frame['image'].split(',')[1]),core.png_gray_bytes(expected))
                self.assertEqual(frames[-1]['done'],25)
                self.assertEqual(frames[-1]['image'],events[-1]['image'])
                self.assertFalse(server.SESSIONS[token]['busy'])
        finally:server.SESSIONS.pop(token,None)

    def test_formula_functions_are_owned_by_one_package(self):
        import lesson_engine
        for name in ('pad_image','median_filter','adaptive_median_filter','gaussian_filter','add_salt_pepper','psnr','ssim_block_average'):
            self.assertTrue(getattr(core,name).__module__.startswith('rumus_manual.'),name)
        for name in ('filter_trace','manual_metrics','image_analysis'):
            self.assertTrue(getattr(lesson_engine,name).__module__.startswith('rumus_manual.'),name)
        self.assertEqual(server.detailed_metrics.__module__,'rumus_manual.metrics')


if __name__=='__main__':unittest.main()
