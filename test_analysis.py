import json
import tempfile
import unittest
from pathlib import Path

import denoise_manual as core
import lesson_engine as engine
import server
from test_lesson_engine import Request


class AnalysisTests(unittest.TestCase):
    def test_histogram_and_profile_use_exact_pixels(self):
        image=[[0,128,255],[0,64,255],[1,2,3]]
        data=engine.image_analysis(image)
        self.assertEqual(data['profile_row'],1)
        self.assertEqual(data['profile'],[0,64,255])
        self.assertEqual(len(data['histogram']),256)
        self.assertEqual(sum(data['histogram']),9)
        self.assertEqual(data['histogram'][0],2)
        self.assertEqual(data['histogram'][255],2)
        self.assertEqual(data['histogram'][64],1)
        image[1][0]=99
        self.assertEqual(data['profile'][0],0)

    def test_explicit_row_and_invalid_rows(self):
        self.assertEqual(engine.image_analysis([[3],[9]],0)['profile'],[3])
        for row in (-1,2,True,0.5):
            with self.assertRaises(ValueError):
                engine.image_analysis([[3],[9]],row)

    def test_prepare_and_every_method_return_consistent_analysis(self):
        saved=server.DATA
        tokens=[]
        try:
            with tempfile.TemporaryDirectory() as folder:
                server.DATA=Path(folder)
                clean=[[x*20+y for x in range(9)] for y in range(9)]
                core.write_png_gray(server.DATA/'sample.png',clean)
                for noise in (5,10,20,30):
                    req=Request('/api/prepare',dict(image='sample.png',noise=noise,seed=42))
                    server.Handler.do_POST(req)
                    self.assertEqual(req.status,200)
                    data=req.data;token=data['session'];tokens.append(token)
                    self.assertEqual(server.SESSIONS[token]['results'],{})
                    self.assertEqual(data['baseline']['original'],dict(mse=0,psnr=None,ssim=1))
                    noisy=core.add_salt_pepper(clean,noise,42)
                    for key,image in [('original',clean),('noisy',noisy)]:
                        self.assertEqual(data['analysis'][key],engine.image_analysis(image))
                        measured=engine.manual_metrics(clean,image)
                        self.assertEqual(data['baseline'][key],{k:measured[k] for k in ('mse','psnr','ssim')})
                    for method,fn in enumerate((core.median_filter,core.adaptive_median_filter,core.gaussian_filter)):
                        req=Request('/api/process',dict(session=token,method=method))
                        server.Handler.do_POST(req)
                        events=[json.loads(line) for line in req.wfile.getvalue().splitlines()]
                        result=events[-1]
                        self.assertEqual(result['type'],'result')
                        self.assertEqual(result['analysis'],engine.image_analysis(fn(noisy)))
                        json.dumps(result,allow_nan=False)
        finally:
            server.DATA=saved
            for token in tokens:server.SESSIONS.pop(token,None)


if __name__=='__main__':unittest.main()
