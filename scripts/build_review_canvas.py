#!/usr/bin/env python3
"""Build a browser-based annotation canvas for media review."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


VALID_MEDIA_TYPES = {"image", "video", "slide", "storyboard", "mixed"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create an HTML annotation review canvas.")
    parser.add_argument("--media", required=True, help="Path or URL to the media preview.")
    parser.add_argument("--media-type", required=True, choices=sorted(VALID_MEDIA_TYPES))
    parser.add_argument("--out", required=True, help="Output HTML path.")
    parser.add_argument("--title", default="Media review")
    parser.add_argument("--timestamp", default="", help="Optional video timestamp represented by this frame.")
    return parser.parse_args()


def media_markup(media: str, media_type: str) -> str:
    safe = html.escape(media, quote=True)
    if media_type == "video":
        return f'<video id="media" class="media" src="{safe}" controls></video>'
    if media_type in {"image", "slide", "storyboard", "mixed"}:
        return f'<img id="media" class="media" src="{safe}" alt="Review target">'
    raise ValueError(f"Unsupported media type: {media_type}")


def build_html(media: str, media_type: str, title: str, timestamp: str) -> str:
    payload = {
        "schema": "annotated-media-fix/v1",
        "media_type": media_type,
        "media": {"src": media, "timestamp": timestamp or None},
        "annotations": [],
    }
    payload_json = html.escape(json.dumps(payload, ensure_ascii=False), quote=False)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{ color-scheme: light; --ink:#101318; --muted:#5b6472; --line:#d9dde5; --bg:#f6f7f9; --panel:#ffffff; --accent:#ff3b30; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: Arial, sans-serif; color: var(--ink); background: var(--bg); }}
    header, .toolbar, .side {{ background: var(--panel); border-bottom: 1px solid var(--line); }}
    header {{ padding: 14px 18px; display: flex; gap: 12px; align-items: baseline; justify-content: space-between; }}
    h1 {{ font-size: 18px; margin: 0; }}
    .meta {{ color: var(--muted); font-size: 13px; }}
    main {{ display: grid; grid-template-columns: minmax(0, 1fr) 360px; min-height: calc(100vh - 58px); }}
    .stage-wrap {{ padding: 16px; overflow: auto; }}
    .stage {{ position: relative; width: min(100%, 1280px); margin: 0 auto; background: #111; border: 1px solid var(--line); }}
    .media {{ display: block; width: 100%; height: auto; max-height: calc(100vh - 120px); object-fit: contain; background: #111; }}
    canvas {{ position: absolute; inset: 0; width: 100%; height: 100%; cursor: crosshair; touch-action: none; }}
    .side {{ border-left: 1px solid var(--line); border-bottom: 0; padding: 14px; overflow: auto; }}
    .toolbar {{ display: flex; gap: 8px; flex-wrap: wrap; padding: 10px; margin: -14px -14px 14px; }}
    button, select, input, textarea {{ font: inherit; }}
    button {{ border: 1px solid var(--line); background: #fff; border-radius: 6px; padding: 8px 10px; cursor: pointer; }}
    button.active {{ border-color: var(--accent); color: var(--accent); }}
    textarea {{ width: 100%; min-height: 74px; resize: vertical; border: 1px solid var(--line); border-radius: 6px; padding: 8px; }}
    .row {{ display: grid; gap: 6px; margin-bottom: 12px; }}
    .annotation {{ border: 1px solid var(--line); border-radius: 8px; padding: 8px; margin-bottom: 8px; background: #fff; }}
    .annotation strong {{ font-size: 13px; }}
    pre {{ white-space: pre-wrap; word-break: break-word; background: #101318; color: #e8edf4; padding: 10px; border-radius: 8px; max-height: 240px; overflow: auto; }}
    @media (max-width: 920px) {{ main {{ grid-template-columns: 1fr; }} .side {{ border-left: 0; border-top: 1px solid var(--line); }} }}
  </style>
</head>
<body>
  <header>
    <h1>{html.escape(title)}</h1>
    <div class="meta">schema: annotated-media-fix/v1 · type: {html.escape(media_type)}</div>
  </header>
  <main>
    <section class="stage-wrap">
      <div id="stage" class="stage">
        {media_markup(media, media_type)}
        <canvas id="canvas"></canvas>
      </div>
    </section>
    <aside class="side">
      <div class="toolbar">
        <button id="rect" class="active" type="button">Area</button>
        <button id="arrow" type="button">Arrow</button>
        <button id="pen" type="button">Pen</button>
        <button id="undo" type="button">Undo</button>
        <button id="clear" type="button">Clear</button>
      </div>
      <div class="row">
        <label for="note">Note for next mark</label>
        <textarea id="note" placeholder="Write the correction instruction for the next mark."></textarea>
      </div>
      <div class="row">
        <button id="save" type="button">Save annotation JSON (PC)</button>
        <button id="copy" type="button">Copy JSON (mobile)</button>
      </div>
      <div id="list"></div>
      <pre id="json">{payload_json}</pre>
    </aside>
  </main>
  <script>
    const initialPayload = {payload_json};
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    const stage = document.getElementById('stage');
    const note = document.getElementById('note');
    const jsonOut = document.getElementById('json');
    const list = document.getElementById('list');
    const payload = initialPayload;
    let tool = 'rect';
    let drawing = false;
    let start = null;
    let currentPath = [];

    function resize() {{
      const r = stage.getBoundingClientRect();
      canvas.width = Math.round(r.width);
      canvas.height = Math.round(r.height);
      drawAll();
    }}

    function pos(event) {{
      const r = canvas.getBoundingClientRect();
      return {{ x: Math.round(event.clientX - r.left), y: Math.round(event.clientY - r.top) }};
    }}

    function setTool(next) {{
      tool = next;
      for (const id of ['rect', 'arrow', 'pen']) document.getElementById(id).classList.toggle('active', id === tool);
    }}

    function nextId() {{ return 'a' + String(payload.annotations.length + 1).padStart(2, '0'); }}

    function addAnnotation(item) {{
      item.id = nextId();
      item.note = note.value.trim();
      item.color = '#ff3b30';
      payload.annotations.push(item);
      note.value = '';
      drawAll();
      renderList();
      renderJson();
    }}

    function drawAll() {{
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.lineWidth = 4;
      ctx.strokeStyle = '#ff3b30';
      ctx.fillStyle = '#ff3b30';
      ctx.font = '14px Arial';
      for (const a of payload.annotations) {{
        ctx.beginPath();
        if (a.type === 'rect') ctx.rect(a.x, a.y, a.w, a.h);
        if (a.type === 'arrow') {{
          ctx.moveTo(a.x1, a.y1); ctx.lineTo(a.x2, a.y2);
          const angle = Math.atan2(a.y2 - a.y1, a.x2 - a.x1);
          for (const d of [0.75, -0.75]) {{
            ctx.moveTo(a.x2, a.y2);
            ctx.lineTo(a.x2 - 18 * Math.cos(angle + d), a.y2 - 18 * Math.sin(angle + d));
          }}
        }}
        if (a.type === 'pen') {{
          a.points.forEach((p, i) => i ? ctx.lineTo(p.x, p.y) : ctx.moveTo(p.x, p.y));
        }}
        ctx.stroke();
        ctx.fillText(a.id, (a.x || a.x1 || (a.points && a.points[0].x) || 8) + 6, (a.y || a.y1 || (a.points && a.points[0].y) || 18) + 16);
      }}
    }}

    function renderList() {{
      list.innerHTML = payload.annotations.map(a => `<div class="annotation"><strong>${{a.id}} · ${{a.type}}</strong><div>${{(a.note || '').replace(/[<>&]/g, c => ({{'<':'&lt;','>':'&gt;','&':'&amp;'}}[c]))}}</div></div>`).join('');
    }}

    function renderJson() {{
      payload.media.width = canvas.width;
      payload.media.height = canvas.height;
      jsonOut.textContent = JSON.stringify(payload, null, 2);
    }}

    canvas.addEventListener('pointerdown', (event) => {{
      drawing = true;
      start = pos(event);
      currentPath = [start];
      canvas.setPointerCapture(event.pointerId);
    }});
    canvas.addEventListener('pointermove', (event) => {{
      if (!drawing) return;
      const p = pos(event);
      if (tool === 'pen') currentPath.push(p);
      drawAll();
      ctx.setLineDash([8, 6]);
      ctx.beginPath();
      if (tool === 'rect') ctx.rect(start.x, start.y, p.x - start.x, p.y - start.y);
      if (tool === 'arrow') {{ ctx.moveTo(start.x, start.y); ctx.lineTo(p.x, p.y); }}
      if (tool === 'pen') currentPath.forEach((q, i) => i ? ctx.lineTo(q.x, q.y) : ctx.moveTo(q.x, q.y));
      ctx.stroke();
      ctx.setLineDash([]);
    }});
    canvas.addEventListener('pointerup', (event) => {{
      if (!drawing) return;
      drawing = false;
      const p = pos(event);
      if (tool === 'rect') addAnnotation({{ type: 'rect', x: start.x, y: start.y, w: p.x - start.x, h: p.y - start.y }});
      if (tool === 'arrow') addAnnotation({{ type: 'arrow', x1: start.x, y1: start.y, x2: p.x, y2: p.y }});
      if (tool === 'pen') addAnnotation({{ type: 'pen', points: currentPath }});
    }});

    document.getElementById('rect').onclick = () => setTool('rect');
    document.getElementById('arrow').onclick = () => setTool('arrow');
    document.getElementById('pen').onclick = () => setTool('pen');
    document.getElementById('undo').onclick = () => {{ payload.annotations.pop(); drawAll(); renderList(); renderJson(); }};
    document.getElementById('clear').onclick = () => {{ payload.annotations.length = 0; drawAll(); renderList(); renderJson(); }};
    document.getElementById('copy').onclick = async () => {{
      renderJson();
      await navigator.clipboard.writeText(jsonOut.textContent).catch(() => {{}});
    }};
    document.getElementById('save').onclick = () => {{
      renderJson();
      const blob = new Blob([jsonOut.textContent], {{ type: 'application/json' }});
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'annotations.json';
      a.click();
      URL.revokeObjectURL(url);
    }};
    window.addEventListener('resize', resize);
    resize();
  </script>
</body>
</html>
"""


def main() -> None:
    args = parse_args()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_html(args.media, args.media_type, args.title, args.timestamp), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
