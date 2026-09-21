#!/usr/bin/env python
"""Compara, no ambito de cada no do Figma, o screenshot do no com o mesmo recorte do render.

O frame da GESTAO tem 9507px e o servidor MCP do Figma limita screenshots a 1024px,
entao nao existe uma referencia de pagina inteira. Em vez disso comparamos no a no:

  - nos graficos: o screenshot do Figma tem exatamente o tamanho da caixa do no,
    logo a comparacao e direta nas coordenadas do no;
  - nos de texto: o Figma recorta o screenshot na tinta, entao alinhamos as duas
    imagens pela bounding box de tinta antes de comparar.

    python scripts/nodecmp.py <dir_screenshots> <nodes.json> <render.png> [saida]
"""
import sys, os, json, io
import numpy as np
from PIL import Image


def safe(t):
    return t.encode('ascii', 'replace').decode()


def ink_bbox(a, thresh=12):
    """Bounding box do que difere da cor de fundo dominante."""
    ai = a.astype(np.int64)
    bg = np.bincount((ai[..., 0] * 65536 + ai[..., 1] * 256 + ai[..., 2]).ravel()).argmax()
    bgc = np.array([(bg >> 16) & 255, (bg >> 8) & 255, bg & 255])
    d = np.abs(a.astype(int) - bgc).max(axis=2) > thresh
    if not d.any():
        return None
    ys, xs = np.where(d)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def main():
    shots, nodes_json, render_png = sys.argv[1], sys.argv[2], sys.argv[3]
    out = sys.argv[4] if len(sys.argv) > 4 else None

    nodes = json.load(io.open(nodes_json, encoding="utf-8"))
    R = Image.open(render_png).convert("RGB")
    rows = []

    for n in nodes:
        if n["depth"] != 1:
            continue
        p = os.path.join(shots, n["id"].replace(":", "_") + ".png")
        if not os.path.exists(p):
            continue
        F = Image.open(p).convert("RGB")
        x, y, w, h = n["x"], n["y"], n["w"], n["h"]
        # o Figma corta o screenshot no frame: nos que sangram comecam em x=0
        cx = int(round(max(0.0, x)))
        cy = int(round(y))

        if abs(F.width - round(w)) <= 1 and abs(F.height - round(h)) <= 1 and x >= -0.5:
            crop = R.crop((cx, cy, cx + F.width, cy + F.height))
            mode = "caixa"
        else:
            # texto recortado na tinta (ou no sangrado): alinha pelas bounding boxes
            x0 = max(0, cx - 6); x1 = min(402, cx + int(w) + 6)
            y0 = max(0, cy - 6); y1 = min(R.height, cy + int(h) + 6)
            if x1 - x0 < 4 or y1 - y0 < 4:
                continue
            box = R.crop((x0, y0, x1, y1))
            ba, bb = ink_bbox(np.asarray(F)), ink_bbox(np.asarray(box))
            if ba is None or bb is None:
                continue
            fw, fh = ba[2] - ba[0], ba[3] - ba[1]
            crop = box.crop((bb[0], bb[1], bb[0] + fw, bb[1] + fh))
            F = F.crop(ba)
            mode = "tinta"
            if crop.size != F.size:
                crop = crop.resize(F.size)

        if crop.size != F.size or crop.size[0] == 0:
            continue
        a = np.asarray(F).astype(int)
        b = np.asarray(crop).astype(int)
        d = np.abs(a - b).mean(axis=2)
        rows.append((d.mean(), 100 * (d > 40).mean(), n, mode))

    rows.sort(key=lambda r: -r[0])
    print(f"{'meandiff':>9}{'%>40':>8}  {'modo':<6} {'y':>6} {'no':<15} nome")
    print("-" * 92)
    for md, pc, n, mode in rows:
        flag = "  <<<" if md > 22 else ""
        print(f"{md:>9.2f}{pc:>7.1f}%  {mode:<6} {n['y']:>6.0f} {n['id']:<15} {safe(n['name'])[:34]}{flag}")
    if rows:
        print("-" * 92)
        print(f"nos comparados: {len(rows)}   media geral: {np.mean([r[0] for r in rows]):.2f}   "
              f"acima de 22: {sum(1 for r in rows if r[0] > 22)}")
    if out:
        json.dump([{"id": n["id"], "name": n["name"], "y": n["y"], "diff": md, "mode": mode}
                   for md, pc, n, mode in rows], io.open(out, "w", encoding="utf-8"), ensure_ascii=False)


if __name__ == "__main__":
    main()
