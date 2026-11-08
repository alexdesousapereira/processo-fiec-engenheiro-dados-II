#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_bounds.py — validador de geometria dos mockups SVG (/corporate-pbi-mockup).

Verifica a regra inviolável do svg-kit: "NADA ultrapassa a moldura do card".
Para cada grupo de card (`<g id="kpi-*">` / `<g id="visual-*">`), pega o 1º <rect>
como moldura e checa se cada elemento-filho (text/rect/circle/line/polyline/ícone)
cabe dentro dela, com folga mínima. Reporta:
  - ERRO  : elemento cruza a borda da moldura (o bug real).
  - AVISO : elemento a menos de PAD_MIN px da borda (respiro apertado).

Uso:  python check_bounds.py tela-01.svg [tela-02.svg ...]
Saída: lista de problemas por arquivo + código de saída 1 se houver ERRO.
NÃO valida XML bem-formado (use xmllint/minidom antes) nem estética — só limites.
"""
import sys, re
import xml.etree.ElementTree as ET

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

NS = "{http://www.w3.org/2000/svg}"
EPS = 0.6        # tolerância p/ considerar "cruzou a borda"
PAD_MIN = 4.0    # respiro mínimo desejado (borda) p/ elementos de dado/texto

def tag(e): return e.tag.replace(NS, "")

def parse_transform(t):
    ops = []
    for m in re.finditer(r"(translate|scale|rotate|matrix)\s*\(([^)]*)\)", t or ""):
        args = [float(x) for x in re.split(r"[ ,]+", m.group(2).strip()) if x != ""]
        ops.append((m.group(1), args))
    return ops

def compose(parent, t):
    """parent e retorno: (sx, sy, ox, oy) mapeando ponto local -> espaço da moldura.
    Suporta translate/scale; rotate/matrix ignorados p/ bbox (aprox. p/ donut centrado)."""
    sx, sy, ox, oy = parent
    lsx = lsy = 1.0; lox = loy = 0.0
    for name, a in parse_transform(t):
        if name == "translate":
            tx = a[0]; ty = a[1] if len(a) > 1 else 0.0
            lox, loy = lox + lsx * tx, loy + lsy * ty
        elif name == "scale":
            s = a[0]; s2 = a[1] if len(a) > 1 else a[0]
            lsx *= s; lsy *= s2
    return (sx * lsx, sy * lsy, ox + sx * lox, oy + sy * loy)

def mapbox(M, x0, y0, x1, y1):
    sx, sy, ox, oy = M
    xs = [ox + sx * x0, ox + sx * x1]; ys = [oy + sy * y0, oy + sy * y1]
    return (min(xs), min(ys), max(xs), max(ys))

def fget(e, k, d=0.0):
    v = e.get(k)
    try: return float(v)
    except (TypeError, ValueError): return d

def textwidth(s, fs, weight, ls):
    f = 0.62 if str(weight) in ("600", "700", "bold") else 0.55
    w = len(s) * fs * f
    if ls: w += ls * max(0, len(s) - 1)
    return w

def alltext(e):
    parts = [e.text or ""]
    for c in e:
        if tag(c) == "tspan":
            parts.append(c.text or "")
        parts.append(c.tail or "")
    return "".join(parts).strip()

def elem_bbox(e, M, style):
    tg = tag(e)
    if tg == "rect":
        return mapbox(M, fget(e, "x"), fget(e, "y"),
                      fget(e, "x") + fget(e, "width"), fget(e, "y") + fget(e, "height"))
    if tg in ("circle",):
        cx, cy, r = fget(e, "cx"), fget(e, "cy"), fget(e, "r")
        return mapbox(M, cx - r, cy - r, cx + r, cy + r)
    if tg == "ellipse":
        cx, cy, rx, ry = fget(e, "cx"), fget(e, "cy"), fget(e, "rx"), fget(e, "ry")
        return mapbox(M, cx - rx, cy - ry, cx + rx, cy + ry)
    if tg == "line":
        return mapbox(M, fget(e, "x1"), fget(e, "y1"), fget(e, "x2"), fget(e, "y2"))
    if tg == "polyline" or tg == "polygon":
        pts = [float(v) for v in re.split(r"[ ,]+", (e.get("points") or "").strip()) if v != ""]
        xs = pts[0::2]; ys = pts[1::2]
        if not xs: return None
        return mapbox(M, min(xs), min(ys), max(xs), max(ys))
    if tg == "path":
        # Ícone Material: caixa nominal 0..960 x, -960..0 y (o translate(0,960) está no transform)
        return mapbox(M, 0, -960, 960, 0)
    if tg == "text":
        s = alltext(e)
        if not s: return None
        fs = style["fs"]; anchor = style["anchor"]
        w = textwidth(s, fs, style["weight"], style["ls"])
        x = fget(e, "x"); y = fget(e, "y")
        if anchor == "end":   x0, x1 = x - w, x
        elif anchor == "middle": x0, x1 = x - w / 2, x + w / 2
        else: x0, x1 = x, x + w
        return mapbox(M, x0, y - fs * 0.78, x1, y + fs * 0.22)
    return None

def child_style(e, style):
    st = dict(style)
    if e.get("font-size"):   st["fs"] = fget(e, "font-size", st["fs"])
    if e.get("font-weight"): st["weight"] = e.get("font-weight")
    if e.get("letter-spacing"): st["ls"] = fget(e, "letter-spacing", 0)
    if e.get("text-anchor"): st["anchor"] = e.get("text-anchor")
    return st

def walk(e, M, style, cw, ch, frame_rect, out, label):
    for c in e:
        if c is frame_rect:
            continue
        tg = tag(c)
        Mc = compose(M, c.get("transform")) if c.get("transform") else M
        st = child_style(c, style)
        if tg == "g":
            walk(c, Mc, st, cw, ch, None, out, label)
            continue
        bb = elem_bbox(c, Mc, st)
        if bb is None:
            continue
        x0, y0, x1, y1 = bb
        desc = tg + (f' "{alltext(c)[:28]}"' if tg == "text" else "")
        # ERRO: cruzou a borda
        if x1 > cw + EPS or x0 < -EPS or y1 > ch + EPS or y0 < -EPS:
            edges = []
            if x1 > cw + EPS: edges.append(f"dir (+{x1-cw:.1f})")
            if x0 < -EPS:     edges.append(f"esq ({x0:.1f})")
            if y1 > ch + EPS: edges.append(f"base (+{y1-ch:.1f})")
            if y0 < -EPS:     edges.append(f"topo ({y0:.1f})")
            out.append(("ERRO", label, desc, ", ".join(edges)))
        # AVISO: respiro apertado (só p/ text/rect de dado).
        # Barras/réguas decorativas finas (h<=4 ou w<=4) encostam de propósito → ignorar.
        elif tg in ("text", "rect"):
            thin = tg == "rect" and (min(x1 - x0, y1 - y0) <= 4.0)
            if not thin:
                pad = min(x0, y0, cw - x1, ch - y1)
                if pad < PAD_MIN:
                    out.append(("AVISO", label, desc, f"respiro {pad:.1f}px (< {PAD_MIN:.0f})"))

OVL = 0.5  # sobreposição mínima (px) p/ considerar colisão de cards

# Cores SEMÂNTICAS (bom/ruim/atenção). No chrome DECORATIVO do card (barra de acento,
# chip de ícone, ícone) elas não podem aparecer — cor de status vai no NÚMERO/contexto,
# não no acento (regra do cards.svg). Se o chrome usa semântica, vaza pro background como
# um destaque colorido sem dado que o explique. Pode dar falso-positivo se a marca do
# cliente for laranja/vermelho/verde → é AVISO, não ERRO.
SEMANTIC = {"#e0a458", "#f4a261", "#d64545", "#ff6b6b", "#b5283c", "#2e9e5b", "#3fbf77"}

def norm_hex(v): return (v or "").strip().lower()

def check_accents(root, out):
    for g in root.iter(NS + "g"):
        gid = g.get("id") or ""
        if not gid.startswith("kpi-"):
            continue
        for c in g:
            t = tag(c)
            is_accent = t == "rect" and min(fget(c, "width"), fget(c, "height")) <= 4
            is_chip = t == "rect" and c.get("rx") in ("8", "9")
            is_icon = t == "g" and "scale" in (c.get("transform") or "")
            if (is_accent or is_chip or is_icon) and norm_hex(c.get("fill")) in SEMANTIC:
                kind = "acento" if is_accent else ("chip" if is_chip else "ícone")
                out.append(("AVISO", gid, f"{kind} do KPI",
                            f"cor semântica {norm_hex(c.get('fill'))} no chrome "
                            f"(use marca/neutro; status vai no número)"))

def collect_frames(e, M, frames):
    """Coleta a moldura ABSOLUTA de cada card (kpi-*/visual-*), acumulando transforms
    dos ancestrais — p/ detectar colisão entre cards na grid."""
    for c in e:
        if tag(c) != "g":
            continue
        Mc = compose(M, c.get("transform")) if c.get("transform") else M
        gid = c.get("id") or ""
        if gid.startswith("kpi-") or gid.startswith("visual-"):
            frame = next((k for k in c if tag(k) == "rect"), None)
            if frame is not None:
                fx, fy = fget(frame, "x"), fget(frame, "y")
                frames.append((gid, mapbox(Mc, fx, fy,
                               fx + fget(frame, "width"), fy + fget(frame, "height"))))
        collect_frames(c, Mc, frames)

def check(path):
    tree = ET.parse(path); root = tree.getroot()
    base = (1.0, 1.0, 0.0, 0.0)
    out = []
    for g in root.iter(NS + "g"):
        gid = g.get("id") or ""
        if not (gid.startswith("kpi-") or gid.startswith("visual-")):
            continue
        frame = next((c for c in g if tag(c) == "rect"), None)
        if frame is None:
            continue
        cw = fget(frame, "x") + fget(frame, "width")
        ch = fget(frame, "y") + fget(frame, "height")
        # Coordenadas são LOCAIS ao card: o transform do próprio grupo posiciona a
        # moldura E os filhos juntos, então se cancela — mede-se a partir da identidade.
        style = {"fs": 12.0, "weight": "400", "ls": 0.0, "anchor": "start"}
        walk(g, base, style, cw, ch, frame, out, gid)
    # COLISÃO entre cards (molduras absolutas)
    frames = []
    collect_frames(root, base, frames)
    for i in range(len(frames)):
        gi, a = frames[i]
        for j in range(i + 1, len(frames)):
            gj, b = frames[j]
            ox = min(a[2], b[2]) - max(a[0], b[0])
            oy = min(a[3], b[3]) - max(a[1], b[1])
            if ox > OVL and oy > OVL:
                out.append(("COLISAO", "grid", f"{gi} × {gj}",
                            f"sobrepõe {ox:.1f}×{oy:.1f}px"))
    check_accents(root, out)
    return out

def main(argv):
    total_err = 0
    for path in argv:
        out = check(path)
        errs = [o for o in out if o[0] in ("ERRO", "COLISAO")]
        warns = [o for o in out if o[0] == "AVISO"]
        nco = sum(1 for o in out if o[0] == "COLISAO")
        total_err += len(errs)
        status = "OK" if not errs else "FALHOU"
        print(f"\n[{status}] {path} — {len(errs)} erro(s) ({nco} colisão), {len(warns)} aviso(s)")
        for lvl, label, desc, info in out:
            mark = "  ~" if lvl == "AVISO" else "  x"
            print(f"{mark} {lvl} [{label}] {desc} -> {info}")
    print(f"\n== total: {total_err} erro(s) ==")
    return 1 if total_err else 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("uso: python check_bounds.py <arquivo.svg> [...]"); sys.exit(2)
    sys.exit(main(sys.argv[1:]))
