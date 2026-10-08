"""Gera um .excalidraw e uma página HTML com o Excalidraw embutido a partir de um spec compacto.

Uso: python excalidraw_build.py spec.json --out-dir pasta [--name slug]

O spec descreve seções (fluxo, pilha de fichas/tabelas ou posicionamento manual) e o script
calcula posições, setas, legendas, alturas e a disposição das seções em fileiras.
Formato completo em references/excalidraw-spec.md.
"""
import argparse
import base64
import hashlib
import json
import math
import os
import random
import textwrap

STROKE = "#1e1e1e"
MUTED = "#5c5f66"
FILLS = {
    "gray": "#e9ecef",
    "red": "#ffc9c9",
    "green": "#b2f2bb",
    "yellow": "#ffec99",
    "blue": "#a5d8ff",
    "white": "#ffffff",
    "dashed": "#ffffff",
    "none": "transparent",
}
SUBTITLE_COLORS = {
    "gray": "#5c5f66",
    "red": "#7a2e2e",
    "green": "#2b6a3a",
    "yellow": "#6f5a0e",
    "blue": "#1f4e79",
    "white": "#5c5f66",
    "dashed": "#5c5f66",
    "none": "#5c5f66",
}
LEGEND_LABELS = {
    "gray": "já existe, não muda",
    "red": "onde está o problema",
    "green": "novo ou alterado",
    "yellow": "decisão ou pendência",
    "blue": "sistema externo",
    "dashed": "fora do fluxo, acontece depois",
}
LEGEND_ORDER = ["gray", "green", "red", "yellow", "blue", "dashed"]
FONT = 1
LINE_HEIGHT = 1.25
CHAR_W = 0.55
PAD = 10
MARGIN = 64
SECTION_GAP_X = 80
ROW_GAP_Y = 320
FLOW_W = 720
BOX_W = 440
BOX_H = 88
BOX_GAP = 56
STACK_GAP = 20

_counter = [0]


def _id(prefix):
    _counter[0] += 1
    return f"{prefix}-{_counter[0]}-{hashlib.md5(str(_counter[0]).encode()).hexdigest()[:6]}"


def _base(el_type, x, y, w, h, **kw):
    el = {
        "id": kw.pop("id", None) or _id(el_type),
        "type": el_type,
        "x": x,
        "y": y,
        "width": w,
        "height": h,
        "angle": 0,
        "strokeColor": STROKE,
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 2,
        "strokeStyle": "solid",
        "roughness": 1,
        "opacity": 100,
        "groupIds": [],
        "frameId": None,
        "roundness": None,
        "seed": random.randint(1, 2**31 - 1),
        "version": 1,
        "versionNonce": random.randint(1, 2**31 - 1),
        "isDeleted": False,
        "boundElements": [],
        "updated": 1,
        "link": None,
        "locked": False,
    }
    el.update(kw)
    return el


def wrap(text, width_px, font_size):
    max_chars = max(8, int((width_px - 2 * PAD) / (font_size * CHAR_W)))
    lines = []
    for para in str(text).split("\n"):
        lines.extend(textwrap.wrap(para, max_chars) or [""])
    return lines


def text_el(x, y, text, font_size, color=STROKE, align="left", width=None, container=None, valign="top", frame=None, group=None):
    lines = text.split("\n")
    w = width if width is not None else max(len(l) for l in lines) * font_size * CHAR_W
    h = len(lines) * font_size * LINE_HEIGHT
    el = _base(
        "text", x, y, w, h,
        strokeColor=color,
        text=text,
        originalText=text,
        fontSize=font_size,
        fontFamily=FONT,
        textAlign=align,
        verticalAlign=valign,
        containerId=container,
        lineHeight=LINE_HEIGHT,
        baseline=font_size,
        strokeWidth=1,
    )
    if frame:
        el["frameId"] = frame
    if group:
        el["groupIds"] = [group]
    return el


def rect_el(x, y, w, h, style="white", frame=None, group=None, stroke_width=2, radius=True):
    el = _base(
        "rectangle", x, y, w, h,
        backgroundColor=FILLS.get(style, FILLS["white"]),
        strokeStyle="dashed" if style == "dashed" else "solid",
        strokeWidth=stroke_width,
        roundness={"type": 3} if radius else None,
    )
    if frame:
        el["frameId"] = frame
    if group:
        el["groupIds"] = [group]
    return el


def bound_text(container, text, font_size, color=STROKE, align="left", valign="top"):
    lines = wrap(text, container["width"], font_size)
    t = text_el(
        container["x"] + PAD, container["y"] + PAD, "\n".join(lines), font_size, color=color, align=align,
        width=container["width"] - 2 * PAD, container=container["id"], valign=valign,
        frame=container["frameId"], group=container["groupIds"][0] if container["groupIds"] else None,
    )
    t["originalText"] = text
    container["boundElements"].append({"id": t["id"], "type": "text"})
    return t


def text_height(text, width_px, font_size):
    return len(wrap(text, width_px, font_size)) * font_size * LINE_HEIGHT + 2 * PAD


class Section:
    def __init__(self, spec):
        self.spec = spec
        self.id = spec["id"]
        self.w = spec.get("w") or (FLOW_W if "flow" in spec else 896)
        self.h = spec.get("h")
        self.x = spec.get("x")
        self.y = spec.get("y")
        self.frame = None
        self.boxes = {}
        self.styles_used = []
        self.max_bottom = 0

    def content_top(self):
        top = 40 + 28 * LINE_HEIGHT + 16
        if self.spec.get("note"):
            top += len(wrap(self.spec["note"], self.w - 2 * MARGIN, 16)) * 16 * LINE_HEIGHT + 24
        return math.ceil(top / 8) * 8


class Builder:
    def __init__(self, spec):
        self.spec = spec
        self.elements = []
        self.sections = {}

    def build(self):
        secs = [Section(s) for s in self.spec.get("sections", [])]
        for s in secs:
            self.sections[s.id] = s
        for s in secs:
            self.measure(s)
        self.place(secs)
        for s in secs:
            self.render(s)
        for a in self.spec.get("arrows", []):
            self.arrow(a, None)
        return self.elements

    def measure(self, s):
        if s.h:
            return
        sp = s.spec
        top = s.content_top()
        if "flow" in sp:
            n = len(sp["flow"])
            bottom = top + n * BOX_H + (n - 1) * BOX_GAP
        elif "stack" in sp:
            bottom = top
            for item in sp["stack"]:
                bottom += self.item_height(s, item) + STACK_GAP
            bottom -= STACK_GAP
        else:
            bottom = max([b["y"] + b["h"] for b in sp.get("boxes", [])] + [top])
        legend = self.legend_styles(s)
        if legend:
            bottom += 32 + 16
        s.h = math.ceil((bottom + MARGIN - 8) / 8) * 8

    def item_height(self, s, item):
        if "card" in item:
            c = item["card"]
            w = c.get("w") or (s.w - 2 * MARGIN)
            return c.get("h") or text_height(self.card_text(c), w, 16)
        if "table" in item:
            return self.table_height(s, item["table"])
        if "columns" in item:
            cols = item["columns"]
            w = (s.w - 2 * MARGIN - STACK_GAP * (len(cols) - 1)) / len(cols)
            return max(c.get("h") or text_height(self.card_text(c), w, 16) for c in cols)
        return 0

    def card_text(self, c):
        heading = c.get("heading")
        body = c.get("text", "")
        return f"{heading}\n{body}" if heading else body

    def table_widths(self, s, t):
        if t.get("widths"):
            return t["widths"]
        ncols = len(t["header"]) if t.get("header") else len(t["rows"][0])
        total = s.w - 2 * MARGIN
        return [total / ncols] * ncols

    def table_rows(self, t):
        rows = []
        if t.get("header"):
            rows.append(("header", t["header"]))
        rows.extend(("row", r) for r in t["rows"])
        return rows

    def table_height(self, s, t):
        widths = self.table_widths(s, t)
        font = t.get("fontSize", 15)
        total = 0
        for _, cells in self.table_rows(t):
            texts = [c["text"] if isinstance(c, dict) else str(c) for c in cells]
            total += max(text_height(tx, w, font) for tx, w in zip(texts, widths))
        return total

    def legend_styles(self, s):
        sp = s.spec
        if sp.get("legend") is False:
            return []
        styles = []
        if "flow" in sp:
            styles = [b.get("style", "gray") for b in sp["flow"]]
        else:
            styles = [b.get("style", "gray") for b in sp.get("boxes", []) if b.get("title")]
        used = [st for st in LEGEND_ORDER if st in styles]
        if len(used) < 2 and not isinstance(sp.get("legend"), dict):
            return []
        return used

    def place(self, secs):
        rows = {}
        for s in secs:
            if s.x is None or s.y is None:
                rows.setdefault(s.spec.get("row", 1), []).append(s)
        y = 0
        for row in sorted(rows):
            x = 0
            tallest = 0
            for s in rows[row]:
                s.x, s.y = x, y
                x += s.w + SECTION_GAP_X
                tallest = max(tallest, s.h)
            y += tallest + ROW_GAP_Y

    def render(self, s):
        sp = s.spec
        fr = _base("frame", s.x, s.y, s.w, s.h, name=sp["title"], strokeWidth=1, roughness=0)
        s.frame = fr["id"]
        self.elements.append(fr)
        self.elements.append(text_el(s.x + MARGIN, s.y + 40, sp["title"], 28, frame=s.frame))
        if sp.get("note"):
            lines = "\n".join(wrap(sp["note"], s.w - 2 * MARGIN, 16))
            self.elements.append(text_el(s.x + MARGIN, s.y + 84, lines, 16, color=MUTED, width=s.w - 2 * MARGIN, frame=s.frame))
        top = s.content_top()
        if "flow" in sp:
            self.render_flow(s, top)
        elif "stack" in sp:
            self.render_stack(s, top)
        else:
            for b in sp.get("boxes", []):
                self.box(s, b)
            for a in sp.get("arrows", []):
                self.arrow(a, s)
            for n in sp.get("labels", []):
                self.elements.append(text_el(s.x + n["x"], s.y + n["y"], n["text"], n.get("fontSize", 16), color=n.get("color", MUTED), frame=s.frame))
        self.render_legend(s)

    def render_flow(self, s, top):
        bx = (s.w - BOX_W) / 2
        prev = None
        for i, b in enumerate(s.spec["flow"]):
            b = dict(b)
            b.setdefault("id", f"{s.id}-{i + 1}")
            b.update({"x": bx, "y": top + i * (BOX_H + BOX_GAP), "w": BOX_W, "h": BOX_H})
            self.box(s, b)
            if prev:
                dashed = b.get("style") == "dashed" or b.get("arrow") == "dashed"
                self.arrow({"from": prev, "to": b["id"], "style": "dashed" if dashed else "solid", "label": b.get("arrowLabel")}, s)
            prev = b["id"]

    def render_stack(self, s, top):
        y = top
        for item in s.spec["stack"]:
            if "card" in item:
                c = item["card"]
                self.card(s, MARGIN, y, c.get("w") or (s.w - 2 * MARGIN), c)
            elif "table" in item:
                self.table(s, MARGIN, y, item["table"])
            elif "columns" in item:
                cols = item["columns"]
                w = (s.w - 2 * MARGIN - STACK_GAP * (len(cols) - 1)) / len(cols)
                h = self.item_height(s, item)
                for j, c in enumerate(cols):
                    self.card(s, MARGIN + j * (w + STACK_GAP), y, w, c, h)
            y += self.item_height(s, item) + STACK_GAP

    def box(self, s, b):
        x, y = s.x + b["x"], s.y + b["y"]
        group = _id("g")
        r = rect_el(x, y, b["w"], b["h"], b.get("style", "gray"), frame=s.frame, group=group)
        r["id"] = b.get("id") or _id("box")
        self.elements.append(r)
        s.boxes[r["id"]] = r
        s.max_bottom = max(s.max_bottom, b["y"] + b["h"])
        if not b.get("title"):
            return
        title_lines = "\n".join(wrap(b["title"], b["w"], 20))
        title_h = (title_lines.count("\n") + 1) * 20 * LINE_HEIGHT
        sub = b.get("subtitle")
        if sub:
            sub_lines = "\n".join(wrap(sub, b["w"], 14))
            sub_h = (sub_lines.count("\n") + 1) * 14 * LINE_HEIGHT
            ty = y + (b["h"] - title_h - sub_h - 4) / 2
            self.elements.append(text_el(x + PAD, ty, title_lines, 20, align="center", width=b["w"] - 2 * PAD, frame=s.frame, group=group))
            self.elements.append(text_el(x + PAD, ty + title_h + 4, sub_lines, 14, color=SUBTITLE_COLORS.get(b.get("style", "gray"), MUTED), align="center", width=b["w"] - 2 * PAD, frame=s.frame, group=group))
        else:
            self.elements.append(text_el(x + PAD, y + (b["h"] - title_h) / 2, title_lines, 20, align="center", width=b["w"] - 2 * PAD, frame=s.frame, group=group))

    def card(self, s, x, y, w, c, h=None):
        full = self.card_text(c)
        h = h or c.get("h") or text_height(full, w, 16)
        r = rect_el(s.x + x, s.y + y, w, h, c.get("style", "white"), frame=s.frame)
        self.elements.append(r)
        self.elements.append(bound_text(r, full, 16))
        s.max_bottom = max(s.max_bottom, y + h)

    def table(self, s, x0, y0, t):
        widths = self.table_widths(s, t)
        font = t.get("fontSize", 15)
        y = y0
        for kind, cells in self.table_rows(t):
            texts = [c["text"] if isinstance(c, dict) else str(c) for c in cells]
            h = max(text_height(tx, w, font) for tx, w in zip(texts, widths))
            x = x0
            for cell, w in zip(cells, widths):
                style = cell.get("style", "none") if isinstance(cell, dict) else "none"
                if kind == "header":
                    style = "none"
                r = rect_el(s.x + x, s.y + y, w, h, style, frame=s.frame, stroke_width=1, radius=False)
                self.elements.append(r)
                tx = cell["text"] if isinstance(cell, dict) else str(cell)
                self.elements.append(bound_text(r, tx, font, color=MUTED if kind == "header" else STROKE))
                x += w
            y += h
        s.max_bottom = max(s.max_bottom, y)

    def render_legend(self, s):
        styles = self.legend_styles(s)
        if not styles:
            return
        overrides = s.spec.get("legend") if isinstance(s.spec.get("legend"), dict) else {}
        x = s.x + (s.spec.get("legendX") or (140 if "flow" in s.spec else MARGIN))
        y = s.y + s.max_bottom + 32
        for st in styles:
            label = overrides.get(st, LEGEND_LABELS[st])
            self.elements.append(rect_el(x, y, 16, 16, st, frame=s.frame, stroke_width=1))
            self.elements.append(text_el(x + 24, y - 2, label, 14, color=MUTED, frame=s.frame))
            x += 24 + len(label) * 14 * CHAR_W + 32

    def find_box(self, box_id, s):
        if s and box_id in s.boxes:
            return s.boxes[box_id], s
        for sec in self.sections.values():
            if box_id in sec.boxes:
                return sec.boxes[box_id], sec
        raise KeyError(f"caixa não encontrada: {box_id}")

    def edge_points(self, r):
        cx, cy = r["x"] + r["width"] / 2, r["y"] + r["height"] / 2
        return {
            "top": (cx, r["y"]),
            "bottom": (cx, r["y"] + r["height"]),
            "left": (r["x"], cy),
            "right": (r["x"] + r["width"], cy),
        }

    def nearest_edge(self, r, pt):
        return min(self.edge_points(r).values(), key=lambda p: math.hypot(p[0] - pt[0], p[1] - pt[1]))

    def arrow(self, a, s):
        src, ssec = self.find_box(a["from"], s)
        dst, _ = self.find_box(a["to"], s)
        gap = 6
        via = a.get("via")
        if via:
            via_abs = [(ssec.x + vx, ssec.y + vy) for vx, vy in via]
            pts = [self.nearest_edge(src, via_abs[0])] + via_abs + [self.nearest_edge(dst, via_abs[-1])]
        else:
            se, de = self.edge_points(src), self.edge_points(dst)
            if dst["y"] >= src["y"] + src["height"]:
                pts = [se["bottom"], de["top"]]
            elif dst["x"] >= src["x"] + src["width"]:
                pts = [se["right"], de["left"]]
            elif dst["x"] + dst["width"] <= src["x"]:
                pts = [se["left"], de["right"]]
            else:
                pts = [se["top"], de["bottom"]]
        pts = [list(p) for p in pts]

        def shorten(p, q):
            dx, dy = q[0] - p[0], q[1] - p[1]
            d = math.hypot(dx, dy) or 1
            return [p[0] + dx / d * gap, p[1] + dy / d * gap]

        pts[0] = shorten(pts[0], pts[1])
        pts[-1] = shorten(pts[-1], pts[-2])
        ox, oy = pts[0]
        rel = [[round(px - ox, 2), round(py - oy, 2)] for px, py in pts]
        xs = [p[0] for p in rel]
        ys = [p[1] for p in rel]
        arrow_el = _base(
            "arrow", ox, oy, max(xs) - min(xs), max(ys) - min(ys),
            points=rel,
            lastCommittedPoint=None,
            startBinding={"elementId": src["id"], "focus": 0, "gap": gap},
            endBinding={"elementId": dst["id"], "focus": 0, "gap": gap},
            startArrowhead=None,
            endArrowhead="arrow",
            strokeStyle="dashed" if a.get("style") == "dashed" else "solid",
            strokeColor=a.get("color", STROKE),
        )
        arrow_el["frameId"] = src["frameId"]
        src["boundElements"].append({"id": arrow_el["id"], "type": "arrow"})
        dst["boundElements"].append({"id": arrow_el["id"], "type": "arrow"})
        self.elements.append(arrow_el)
        if a.get("label"):
            mid = pts[1] if len(pts) > 2 else [(pts[0][0] + pts[-1][0]) / 2, (pts[0][1] + pts[-1][1]) / 2]
            self.elements.append(text_el(mid[0] + 10, mid[1] - 24, a["label"], 14, color=MUTED, frame=src["frameId"]))


HTML = """<meta charset="utf-8">
<title>__TITLE__</title>
<style>
:root { --bg: #ffffff; --fg: #1e1e1e; color-scheme: light; }
html, body { margin: 0; height: 100%; background: var(--bg); color: var(--fg); }
#app { position: fixed; inset: 0; }
@font-face { font-family: "Virgil"; src: url(data:font/woff2;base64,__VIRGIL__) format("woff2"); font-display: block; }
</style>
<script>window.EXCALIDRAW_ASSET_PATH = "https://unpkg.com/@excalidraw/excalidraw@0.17.6/dist/";</script>
<script src="https://unpkg.com/react@18.2.0/umd/react.production.min.js"></script>
<script src="https://unpkg.com/react-dom@18.2.0/umd/react-dom.production.min.js"></script>
<script src="https://unpkg.com/@excalidraw/excalidraw@0.17.6/dist/excalidraw.production.min.js"></script>
<div id="app"></div>
<script id="scene" type="application/json">__SCENE__</script>
<script id="virgil" type="text/plain">data:font/woff2;base64,__VIRGIL__</script>
<script>
(function () {
  var scene = JSON.parse(document.getElementById("scene").textContent);
  var virgil = document.getElementById("virgil").textContent;
  Array.prototype.forEach.call(document.querySelectorAll("style"), function (st) {
    if (st.textContent.indexOf("Virgil.woff2") !== -1) {
      st.textContent = st.textContent.replace(/url\\([^)]*Virgil\\.woff2[^)]*\\)/g, "url(" + virgil + ")");
    }
  });
  var face = new FontFace("Virgil", "url(" + virgil + ")");
  document.fonts.add(face);
  var App = function () {
    return React.createElement(ExcalidrawLib.Excalidraw, {
      initialData: { elements: scene.elements, appState: { viewBackgroundColor: "#ffffff" }, scrollToContent: true },
      langCode: "pt-BR",
      theme: "light",
      UIOptions: { canvasActions: { loadScene: false, saveToActiveFile: false } }
    });
  };
  face.load().catch(function () {}).then(function () {
    ReactDOM.createRoot(document.getElementById("app")).render(React.createElement(App));
  });
})();
</script>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--name", default=None)
    args = ap.parse_args()
    with open(args.spec, encoding="utf-8") as f:
        spec = json.load(f)
    name = args.name or os.path.basename(args.spec).replace(".spec.json", "").replace(".json", "")
    random.seed(hashlib.md5(json.dumps(spec, sort_keys=True).encode()).hexdigest())
    elements = Builder(spec).build()
    scene = {
        "type": "excalidraw",
        "version": 2,
        "source": "tech-walkthrough",
        "elements": elements,
        "appState": {"viewBackgroundColor": "#ffffff", "gridSize": None},
        "files": {},
    }
    os.makedirs(args.out_dir, exist_ok=True)
    exc_path = os.path.join(args.out_dir, name + ".excalidraw")
    with open(exc_path, "w", encoding="utf-8") as f:
        json.dump(scene, f, ensure_ascii=False)
    font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Virgil.woff2")
    with open(font_path, "rb") as f:
        virgil = base64.b64encode(f.read()).decode("ascii")
    html_path = os.path.join(args.out_dir, name + ".html")
    page = HTML.replace("__TITLE__", spec.get("title", "Tech walkthrough")).replace("__VIRGIL__", virgil).replace(
        "__SCENE__", json.dumps({"elements": elements}, ensure_ascii=False).replace("</", "<\\/"))
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(page)
    print(exc_path)
    print(html_path)
    if spec.get("artifact"):
        print("artifact: " + spec["artifact"])


if __name__ == "__main__":
    main()
