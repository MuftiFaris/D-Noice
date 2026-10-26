#!/usr/bin/env python3
"""Self-contained local website and image-processing API; standard library only."""
import base64
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from denoise_manual import add_salt_pepper, adaptive_median_filter, gaussian_filter, median_filter, psnr, read_png_gray, ssim_block_average, write_png_gray

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "Set12"
OUTPUT = ROOT / "hasil"


def detailed_metrics(original, restored):
    height, width = len(original), len(original[0])
    total = 0
    samples = []
    for y in range(height):
        for x in range(width):
            delta = original[y][x] - restored[y][x]
            square = delta * delta
            total += square
            if square and len(samples) < 8:
                samples.append({"x": x, "y": y, "original": original[y][x], "result": restored[y][x], "square": square})
    mse = total / (width * height)

    a = [float(original[y][x]) for y in range(min(8, height)) for x in range(min(8, width))]
    b = [float(restored[y][x]) for y in range(min(8, height)) for x in range(min(8, width))]
    n = len(a)
    mean_a, mean_b = sum(a) / n, sum(b) / n
    var_a = sum((v - mean_a) ** 2 for v in a) / (n - 1) if n > 1 else 0.0
    var_b = sum((v - mean_b) ** 2 for v in b) / (n - 1) if n > 1 else 0.0
    covariance = sum((a[i] - mean_a) * (b[i] - mean_b) for i in range(n)) / (n - 1) if n > 1 else 0.0
    c1, c2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
    ssim_block = ((2 * mean_a * mean_b + c1) * (2 * covariance + c2)) / ((mean_a**2 + mean_b**2 + c1) * (var_a + var_b + c2))
    return {
        "mse": mse, "sum_squared_error": total, "pixel_count": width * height,
        "psnr": psnr(original, restored), "ssim": ssim_block_average(original, restored),
        "samples": samples,
        "ssim_block": {"mean_original": mean_a, "mean_result": mean_b, "variance_original": var_a,
                       "variance_result": var_b, "covariance": covariance, "c1": c1, "c2": c2, "value": ssim_block},
    }


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


if __name__ == "__main__":
    if not any(DATA.glob("*.png")):
        raise SystemExit(f"Dataset Set12 tidak ditemukan: {DATA}")
    print("Website siap dibuka: http://127.0.0.1:8000")
    ThreadingHTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
