#!/usr/bin/env python
"""Self-contained local website and image-processing API; standard library only."""
import base64
import json
import argparse
import threading
import time
import uuid
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from denoise_manual import add_salt_pepper, adaptive_median_filter, gaussian_filter, median_filter, psnr, read_png_gray, ssim_block_average, write_png_gray
from denoise_manual import png_gray_bytes
from rumus_manual import filter_trace, manual_metrics, image_analysis

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "Set12"
OUTPUT = ROOT / "hasil"
SESSIONS = {}
SESSION_LOCK = threading.Lock()
LABELS = ['Median Filter', 'Adaptive Median', 'Gaussian Filter']


def image_data(image):
    return 'data:image/png;base64,' + base64.b64encode(png_gray_bytes(image)).decode('ascii')


def integer(body, key, default=None):
    value = body.get(key, default)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f'{key} harus bilangan bulat.')
    return value


def session_for(body):
    with SESSION_LOCK:
        session = SESSIONS.get(str(body.get('session', '')))
        if session is None or time.monotonic() - session['created'] > 5400:
            raise ValueError('Sesi tidak tersedia. Buat noise lagi untuk memulai.')
        return session


# Legacy route uses the same canonical manual metrics.
detailed_metrics = manual_metrics


def image_url(image, path):
    write_png_gray(path, image)
    return "data:image/png;base64," + base64.b64encode(Path(path).read_bytes()).decode("ascii")


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def send_json(self, status, obj):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/api/images":
            self.send_json(200, {"images": sorted(p.name for p in DATA.glob("*.png"))})
            return
        super().do_GET()

    def do_POST(self):
        if self.path in ('/api/prepare', '/api/trace', '/api/process'):
            self.do_lesson()
            return
        if self.path != "/api/run":
            self.send_json(404, {"error": "Halaman tidak ditemukan."})
            return
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))))
            name = str(body.get("image", ""))
            if Path(name).name != name or not name.endswith(".png") or not (DATA / name).is_file():
                raise ValueError("Pilih gambar dari dataset Set12.")
            level, seed = int(body.get("noise", 10)), int(body.get("seed", 42))
            if level not in (5, 10, 20, 30):
                raise ValueError("Pilih tingkat noise 5%, 10%, 20%, atau 30%.")
            if not 0 <= seed <= 2147483647:
                raise ValueError("Seed harus di antara 0 dan 2147483647.")

            clean = read_png_gray(DATA / name)
            noisy = add_salt_pepper(clean, level, seed)
            outputs = [median_filter(noisy, 3), adaptive_median_filter(noisy, 7), gaussian_filter(noisy)]
            labels = ["Median Filter", "Adaptive Median", "Gaussian Filter"]
            images = {"original": image_url(clean, OUTPUT / "terakhir_asli.png"), "noisy": image_url(noisy, OUTPUT / "terakhir_noise.png")}
            methods = {}
            for i, (label, output) in enumerate(zip(labels, outputs)):
                key = f"method{i}"
                images[key] = image_url(output, OUTPUT / f"terakhir_{key}.png")
                methods[label] = detailed_metrics(clean, output)
            self.send_json(200, {"image": name, "noise": level, "seed": seed, "width": len(clean[0]), "height": len(clean), "images": images, "methods": methods})
        except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
            self.send_json(400, {"error": str(exc)})
        except Exception as exc:
            self.send_json(500, {"error": f"Pengolahan gagal: {exc}"})

    def log_message(self, format, *args):
        print("[website] " + format % args)

    def do_lesson(self):
        streaming = False
        session = None
        claimed = False
        def emit(event):
            self.wfile.write((json.dumps(event, ensure_ascii=False, allow_nan=False) + '\n').encode('utf-8'))
            self.wfile.flush()
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if length < 1 or length > 16384:
                raise ValueError('Ukuran permintaan tidak valid.')
            body = json.loads(self.rfile.read(length))
            if not isinstance(body, dict):
                raise ValueError('Permintaan harus berupa objek JSON.')
            if self.path == '/api/prepare':
                name = body.get('image')
                available = {p.name for p in DATA.glob('*.png')}
                if not isinstance(name, str) or name not in available:
                    raise ValueError('Pilih gambar dari galeri Set12.')
                level, seed = integer(body, 'noise', 10), integer(body, 'seed', 42)
                if level not in (5, 10, 20, 30) or not 0 <= seed <= 2147483647:
                    raise ValueError('Noise atau seed tidak valid.')
                clean = read_png_gray(DATA / name)
                noisy = add_salt_pepper(clean, level, seed)
                h, w = len(clean), len(clean[0])
                analysis = dict(original=image_analysis(clean), noisy=image_analysis(noisy))
                # Acuan dan baseline juga dinilai dengan rumus yang sama.
                baseline = {}
                for label, candidate in (('original', clean), ('noisy', noisy)):
                    measured = manual_metrics(clean, candidate)
                    baseline[label] = {key: measured[key] for key in ('mse', 'psnr', 'ssim')}
                # Pilih lokasi rusak terdekat pusat sebagai contoh; bukan angka fiktif.
                x0, y0, best = w // 2, h // 2, float('inf')
                for y in range(h):
                    for x in range(w):
                        if clean[y][x] != noisy[y][x]:
                            distance = (x-w//2)**2 + (y-h//2)**2
                            if distance < best:
                                x0, y0, best = x, y, distance
                token = uuid.uuid4().hex
                session = dict(clean=clean, noisy=noisy, results={}, created=time.monotonic(), busy=False)
                with SESSION_LOCK:
                    stale = [k for k,v in SESSIONS.items() if time.monotonic()-v['created'] > 5400]
                    for k in stale:
                        del SESSIONS[k]
                    if len(SESSIONS) >= 8:
                        idle = [k for k,v in SESSIONS.items() if not v['busy']]
                        if not idle:
                            raise ValueError('Semua sesi sedang berjalan. Coba kembali sebentar lagi.')
                        del SESSIONS[min(idle, key=lambda k:SESSIONS[k]['created'])]
                    SESSIONS[token] = session
                self.send_json(200, dict(session=token, image=name, noise=level, seed=seed,
                    width=w, height=h, count=round(w*h*level/100), x=x0, y=y0,
                    original=image_data(clean), noisy=image_data(noisy), analysis=analysis, baseline=baseline))
                return
            session = session_for(body)
            method = integer(body, 'method')
            if method not in (0,1,2):
                raise ValueError('Metode tidak dikenal.')
            if self.path == '/api/trace':
                x, y = integer(body, 'x'), integer(body, 'y')
                if not (0 <= x < len(session['noisy'][0]) and 0 <= y < len(session['noisy'])):
                    raise ValueError('Koordinat di luar gambar.')
                self.send_json(200, filter_trace(session['noisy'], method, x, y))
                return
            with SESSION_LOCK:
                if session['busy']:
                    raise ValueError('Perhitungan sesi ini masih berjalan.')
                session['busy'] = True
                claimed = True
            self.send_response(200)
            self.send_header('Content-Type', 'application/x-ndjson; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            streaming = True
            if method in session['results']:
                emit(dict(type='result', cached=True, **session['results'][method]))
                return
            def progress(phase, done, total, accumulator=None):
                if done == 1 or done == total or done % max(1,total//40) == 0:
                    emit(dict(type='progress', phase=phase, done=done, total=total, accumulator=accumulator))
            fn = (median_filter, adaptive_median_filter, gaussian_filter)[method]
            def preview(rows, done, total):
                # These are completed output rows, not a timer or an estimated image.
                if done == total or done % max(1, total//12) == 0:
                    frame = rows[:done] + session['noisy'][done:]
                    emit(dict(type='preview', image=image_data(frame), done=done, total=total))
            restored = fn(session['noisy'],
                on_progress=lambda done,total:progress('filter',done,total), on_preview=preview)
            preview = image_data(restored)
            emit(dict(type='filtered', image=preview))
            metrics = manual_metrics(session['clean'], restored, on_progress=progress)
            result = dict(method=method, label=LABELS[method], image=preview, metrics=metrics,
                          analysis=image_analysis(restored))
            session['results'][method] = result
            emit(dict(type='result', cached=False, **result))
        except (BrokenPipeError, ConnectionResetError):
            pass
        except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
            if streaming:
                emit(dict(type='error', error=str(exc)))
            else:
                self.send_json(400, dict(error=str(exc)))
        except Exception as exc:
            if streaming:
                emit(dict(type='error', error=f'Perhitungan gagal: {exc}'))
            else:
                self.send_json(500, dict(error=f'Perhitungan gagal: {exc}'))
        finally:
            if claimed:
                with SESSION_LOCK:
                    session['busy'] = False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--data', type=Path, default=DATA)
    args = parser.parse_args()
    DATA = args.data.resolve()
    if not any(DATA.glob("*.png")):
        raise SystemExit(f"Dataset Set12 tidak ditemukan: {DATA}")
    print(f"Website siap dibuka: http://127.0.0.1:{args.port}")
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()
