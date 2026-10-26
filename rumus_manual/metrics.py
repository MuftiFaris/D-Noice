"""Implementasi rumus manual; operasi skalar dan perulangan Python."""
import math


def psnr(original, restored):
    h, w = len(original), len(original[0])
    mse = sum((original[y][x] - restored[y][x]) ** 2
              for y in range(h) for x in range(w)) / (h * w)
    return float("inf") if mse == 0 else 10 * math.log10((255 * 255) / mse)


def ssim_block_average(original, restored, block=8):
    """SSIM formula computed on non-overlapping 8x8 blocks, then averaged."""
    h, w = len(original), len(original[0])
    k1, k2, L = 0.01, 0.03, 255
    c1, c2 = (k1 * L) ** 2, (k2 * L) ** 2
    values = []
    for y0 in range(0, h, block):
        for x0 in range(0, w, block):
            a, b = [], []
            for y in range(y0, min(y0 + block, h)):
                for x in range(x0, min(x0 + block, w)):
                    a.append(float(original[y][x]))
                    b.append(float(restored[y][x]))
            n = len(a)
            ma, mb = sum(a) / n, sum(b) / n
            va = sum((v - ma) ** 2 for v in a) / (n - 1) if n > 1 else 0.0
            vb = sum((v - mb) ** 2 for v in b) / (n - 1) if n > 1 else 0.0
            cov = sum((a[i] - ma) * (b[i] - mb) for i in range(n)) / (n - 1) if n > 1 else 0.0
            numerator = (2 * ma * mb + c1) * (2 * cov + c2)
            denominator = (ma * ma + mb * mb + c1) * (va + vb + c2)
            values.append(numerator / denominator)
    return sum(values) / len(values)


def manual_metrics(original, restored, on_progress=None):
    """MSE, PSNR, dan SSIM blok 8x8; semua statistik dijumlahkan manual."""
    height, width = len(original), len(original[0])
    squared_error = 0
    samples = []
    for y in range(height):
        for x in range(width):
            a, b = original[y][x], restored[y][x]
            delta = a - b
            square = delta * delta
            squared_error += square
            if len(samples) < 8 and (square or y == height - 1):
                samples.append(dict(x=x, y=y, original=a, result=b, delta=delta, square=square))
        if on_progress:
            on_progress('mse', y + 1, height, squared_error)
    mse = squared_error / (height * width)
    ratio = 65025 / mse if mse else None
    logarithm = math.log10(ratio) if ratio is not None else None
    psnr = 10 * logarithm if logarithm is not None else None
    c1, c2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
    block_count = ((height + 7) // 8) * ((width + 7) // 8)
    total_ssim, processed, first = 0.0, 0, None
    for y0 in range(0, height, 8):
        for x0 in range(0, width, 8):
            pairs = []
            sum_a = sum_b = 0.0
            for y in range(y0, min(y0 + 8, height)):
                for x in range(x0, min(x0 + 8, width)):
                    a, b = float(original[y][x]), float(restored[y][x])
                    pairs.append(dict(x=x, y=y, a=a, b=b))
                    sum_a += a
                    sum_b += b
            n = len(pairs)
            ma, mb = sum_a / n, sum_b / n
            va_sum = vb_sum = cov_sum = 0.0
            for pair in pairs:
                da, db = pair['a'] - ma, pair['b'] - mb
                aa, bb, ab = da * da, db * db, da * db
                va_sum += aa
                vb_sum += bb
                cov_sum += ab
                if first is None:
                    pair.update(da=da, db=db, aa=aa, bb=bb, ab=ab)
            divisor = n - 1 if n > 1 else 1
            va, vb, cov = va_sum / divisor, vb_sum / divisor, cov_sum / divisor
            lum_n, structure_n = 2 * ma * mb + c1, 2 * cov + c2
            lum_d, structure_d = ma * ma + mb * mb + c1, va + vb + c2
            value = (lum_n * structure_n) / (lum_d * structure_d)
            if first is None:
                first = dict(n=n, sum_a=sum_a, sum_b=sum_b, mean_original=ma, mean_result=mb,
                             variance_original=va, variance_result=vb, covariance=cov,
                             va_sum=va_sum, vb_sum=vb_sum, cov_sum=cov_sum, divisor=divisor,
                             c1=c1, c2=c2, numerator_luminance=lum_n, numerator_structure=structure_n,
                             denominator_luminance=lum_d, denominator_structure=structure_d,
                             numerator=lum_n * structure_n, denominator=lum_d * structure_d,
                             value=value, pairs=pairs, rows=min(8,height), columns=min(8,width))
            total_ssim += value
            processed += 1
            if on_progress:
                on_progress('ssim', processed, block_count, total_ssim)
    return dict(mse=mse, sum_squared_error=squared_error, pixel_count=height*width,
                ratio=ratio, logarithm=logarithm, psnr=psnr, ssim=total_ssim / processed,
                ssim_sum=total_ssim, block_count=processed, samples=samples, ssim_block=first)
