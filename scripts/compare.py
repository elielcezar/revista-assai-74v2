#!/usr/bin/env python
"""Compara original x render: fatias lado a lado + medicoes em px por linha.

    python scripts/compare.py reference/original_native.png reference/render.png reference/cmp 800
"""
import sys, os
import numpy as np
from PIL import Image


def extent(row, thresh=245):
    """Extensao horizontal nao-branca de uma linha (x_min, x_max) ou None."""
    nz = np.where(row.min(axis=1) < thresh)[0]
    if len(nz) == 0:
        return None
    return int(nz[0]), int(nz[-1])


def main():
    a_path, b_path, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
    slice_h = int(sys.argv[4]) if len(sys.argv) > 4 else 800

    os.makedirs(outdir, exist_ok=True)
    A = Image.open(a_path).convert("RGB")
    B = Image.open(b_path).convert("RGB")
    W = A.width
    if B.width != W:
        B = B.resize((W, round(B.height * W / B.width)), Image.LANCZOS)

    print(f"original: {A.size}   render: {B.size}   delta_h={B.height - A.height:+d}")

    a = np.asarray(A).astype(np.int16)
    b = np.asarray(B).astype(np.int16)

    n = max(A.height, B.height)
    gap = 16
    for i, y0 in enumerate(range(0, n, slice_h)):
        y1 = min(y0 + slice_h, n)
        canvas = Image.new("RGB", (W * 2 + gap, y1 - y0), (255, 0, 255))
        if y0 < A.height:
            canvas.paste(A.crop((0, y0, W, min(y1, A.height))), (0, 0))
        if y0 < B.height:
            canvas.paste(B.crop((0, y0, W, min(y1, B.height))), (W + gap, 0))
        p = os.path.join(outdir, f"cmp_{i:02d}_{y0}-{y1}.png")
        canvas.save(p)
        print("  ->", p)

    print("\ny      original[x0..x1]   render[x0..x1]     dx0   dx1   meandiff")
    step = max(1, n // 120)
    for y in range(0, n, step):
        ea = extent(a[y]) if y < A.height else None
        eb = extent(b[y]) if y < B.height else None
        if ea is None and eb is None:
            continue
        sa = f"{ea[0]:>4}..{ea[1]:<4}" if ea else "   --     "
        sb = f"{eb[0]:>4}..{eb[1]:<4}" if eb else "   --     "
        if ea and eb:
            d0, d1 = eb[0] - ea[0], eb[1] - ea[1]
            md = int(np.abs(a[y] - b[y]).mean()) if y < A.height and y < B.height else -1
            flag = "  <<<" if (abs(d0) > 3 or abs(d1) > 3 or md > 60) else ""
            print(f"{y:<6} {sa}       {sb}     {d0:>+4} {d1:>+4}   {md:>4}{flag}")
        else:
            print(f"{y:<6} {sa}       {sb}")


if __name__ == "__main__":
    main()
