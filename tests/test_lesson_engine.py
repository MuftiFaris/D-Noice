import io
import json
import math
import random
import unittest

import denoise_manual as core
import lesson_engine as engine
import server


class Request:
    """Exercise real handlers without opening a network port or browser."""
    do_lesson = server.Handler.do_lesson
    def __init__(self, path, body):
        raw = json.dumps(body).encode()
        self.path, self.rfile = path, io.BytesIO(raw)
        self.headers, self.wfile = {'Content-Length': str(len(raw))}, io.BytesIO()
        self.response_headers = {}
    def send_json(self, status, data):
        self.status, self.data = status, data
    def send_response(self, status):
        self.status = status
    def send_header(self, key, value):
        self.response_headers[key] = value
    def end_headers(self):
        pass


class LessonTests(unittest.TestCase):
    def setUp(self):
        rng = random.Random(42)
        self.image = [[rng.randrange(256) for _ in range(9)] for _ in range(7)]

    def test_trace_matches_actual_filter_at_every_pixel_and_border(self):
        for method, fn in enumerate((core.median_filter, core.adaptive_median_filter, core.gaussian_filter)):
            output = fn(self.image)
            for y in range(7):
                for x in range(9):
                    self.assertEqual(engine.filter_trace(self.image,method,x,y)['value'],output[y][x])

    def test_filter_progress_is_actual_completed_rows(self):
        for fn in (core.median_filter, core.adaptive_median_filter, core.gaussian_filter):
            calls=[]
            fn(self.image,on_progress=lambda done,total:calls.append((done,total)))
            self.assertEqual(calls,[(i,7) for i in range(1,8)])

    def test_metrics_match_existing_manual_definitions(self):
        for fn in (core.median_filter, core.adaptive_median_filter, core.gaussian_filter):
            restored=fn(self.image)
            m=engine.manual_metrics(self.image,restored)
            self.assertAlmostEqual(m['psnr'],core.psnr(self.image,restored),places=12)
            self.assertAlmostEqual(m['ssim'],core.ssim_block_average(self.image,restored),places=12)
            self.assertAlmostEqual(m['mse'],m['sum_squared_error']/m['pixel_count'])
            b=m['ssim_block']
            self.assertEqual(b['n'],56)
            self.assertEqual(b['divisor'],55)
            self.assertAlmostEqual(b['value'],b['numerator']/b['denominator'])
            self.assertAlmostEqual(sum(p['aa'] for p in b['pairs']),b['va_sum'])
            self.assertAlmostEqual(sum(p['ab'] for p in b['pairs']),b['cov_sum'])

    def test_identical_images_and_single_pixel_are_finite_json(self):
        m=engine.manual_metrics([[80]],[[80]])
        self.assertEqual(m['mse'],0)
        self.assertIsNone(m['psnr'])
        self.assertEqual(m['ssim'],1)
        json.dumps(m,allow_nan=False)

    def test_metric_progress_ends_at_exact_totals(self):
        calls=[]
        engine.manual_metrics(self.image,core.median_filter(self.image),lambda phase,done,total,acc:calls.append((phase,done,total,acc)))
        mse=[x for x in calls if x[0]=='mse'];ssim=[x for x in calls if x[0]=='ssim']
        self.assertEqual(mse[-1][1:3],(7,7))
        self.assertEqual(ssim[-1][1:3],(2,2))

    def test_stream_handler_progress_then_results_and_cache(self):
        import time
        token='test-session'
        server.SESSIONS[token]=dict(clean=self.image,noisy=self.image,results={},created=time.monotonic(),busy=False)
        for method in range(3):
            request=Request('/api/process',dict(session=token,method=method))
            server.Handler.do_POST(request)
            self.assertEqual(request.status,200)
            events=[json.loads(line) for line in request.wfile.getvalue().splitlines()]
            self.assertEqual(events[-1]['type'],'result')
            self.assertFalse(events[-1]['cached'])
            self.assertEqual({e['phase'] for e in events if e['type']=='progress'},{'filter','mse','ssim'})
            self.assertTrue(any(e['type']=='filtered' for e in events))
            again=Request('/api/process',dict(session=token,method=method))
            server.Handler.do_POST(again)
            cached=json.loads(again.wfile.getvalue())
            self.assertTrue(cached['cached'])
            self.assertEqual(cached['metrics'],events[-1]['metrics'])
        self.assertFalse(server.SESSIONS[token]['busy'])
        del server.SESSIONS[token]

    def test_invalid_session_method_and_coordinates(self):
        import time
        for path,body in [('/api/process',{'session':'missing','method':0}),('/api/prepare',{'image':'../server.py','noise':10,'seed':42})]:
            request=Request(path,body);server.Handler.do_POST(request);self.assertEqual(request.status,400)
        server.SESSIONS['coord']=dict(clean=self.image,noisy=self.image,results={},created=time.monotonic(),busy=False)
        for method,x,y in [(3,0,0),(0,-1,0),(0,9,0),(0,0,7),(True,0,0)]:
            r=Request('/api/trace',dict(session='coord',method=method,x=x,y=y))
            server.Handler.do_POST(r)
            self.assertEqual(r.status,400)
        del server.SESSIONS['coord']


if __name__=='__main__':
    unittest.main()
