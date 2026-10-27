#!/usr/bin/env python3
"""Build a self-contained preview of the profile README.

The preview panel serves the HTML from a throwaway static route, so any
`<img src="../../assets/...">` reference 404s there even though it works when
the file is opened over file://. Inline the SVGs instead: one file, no
sibling assets, renders the same however it is served.

Usage:
    python scripts/build_preview.py
"""

from __future__ import annotations

import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / ".workbuddy-ai" / "preview" / "preview.html"

ASSETS = {
    "header_light": "header-light.svg",
    "header_dark": "header-dark.svg",
    "result_light": "result-light.svg",
    "result_dark": "result-dark.svg",
    "stats_light": "stats-light.svg",
    "stats_dark": "stats-dark.svg",
}


def load(name: str) -> str:
    text = (ROOT / "assets" / ASSETS[name]).read_text(encoding="utf-8").strip()
    # drop the xml prolog if present; width/height are overridden by CSS
    if text.startswith("<?xml"):
        text = text.split("?>", 1)[1].strip()
    return text


TEMPLATE = """<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>README 预览 · howardatri</title>
<style>
  :root {{
    --bg: #ffffff;
    --fg: #1f2328;
    --muted: #59636e;
    --border: #d1d9e0;
    --link: #0969da;
    --bar: #f6f8fa;
  }}
  html[data-theme="dark"] {{
    --bg: #0d1117;
    --fg: #e6edf3;
    --muted: #9198a1;
    --border: #3d444d;
    --link: #4493f8;
    --bar: #151b23;
  }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; padding: 0; }}
  body {{
    background: var(--bg);
    color: var(--fg);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
    font-size: 16px;
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
  }}

  .bar {{
    position: sticky; top: 0; z-index: 10;
    display: flex; align-items: center; justify-content: space-between;
    gap: 16px; padding: 10px 20px;
    background: var(--bar);
    border-bottom: 1px solid var(--border);
  }}
  .bar .file {{
    font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
    font-size: 12px; color: var(--muted); letter-spacing: .02em;
  }}
  .bar .file b {{ color: var(--fg); font-weight: 600; }}
  .seg {{ display: flex; border: 1px solid var(--border); border-radius: 6px; overflow: hidden; }}
  .seg button {{
    appearance: none; border: 0; background: transparent; color: var(--muted);
    font: inherit; font-size: 12px; padding: 4px 12px; cursor: pointer; line-height: 1.6;
  }}
  .seg button + button {{ border-left: 1px solid var(--border); }}
  .seg button[aria-pressed="true"] {{ background: var(--bg); color: var(--fg); font-weight: 600; }}

  .page {{ max-width: 880px; margin: 0 auto; padding: 28px 0 88px; }}

  .markdown-body svg {{ display: block; width: 100%; height: auto; }}
  html[data-theme="light"] .dark-only {{ display: none; }}
  html[data-theme="dark"] .light-only {{ display: none; }}

  .markdown-body p {{ margin: 0 0 16px; }}
  .markdown-body h3 {{
    font-size: 1.25em; font-weight: 600; line-height: 1.25;
    margin: 32px 0 16px; letter-spacing: -0.005em;
  }}
  .markdown-body strong {{ font-weight: 600; }}
  .markdown-body a {{ color: var(--link); text-decoration: none; }}
  .markdown-body a:hover {{ text-decoration: underline; }}
  .markdown-body sub {{ font-size: 0.75em; color: var(--muted); line-height: 1.6; }}
  .markdown-body > *:first-child {{ margin-top: 0; }}
  .spacer-24 {{ height: 24px; }}
</style>
</head>
<body>

<div class="bar">
  <div class="file"><b>howardatri</b> / README.md &nbsp;·&nbsp; 预览（近似 GitHub 渲染）</div>
  <div class="seg" role="group" aria-label="主题">
    <button id="btn-light" aria-pressed="true">Light</button>
    <button id="btn-dark" aria-pressed="false">Dark</button>
  </div>
</div>

<div class="page">
<div class="markdown-body">

  <div class="light-only">{header_light}</div>
  <div class="dark-only">{header_dark}</div>

  <div class="spacer-24"></div>

  <p>I build small systems, and then the instrument that decides whether they actually work.</p>

  <h3>Now</h3>

  <p><strong>hoagent</strong> — a lightweight ReAct coding agent in Python. Multi-provider, 19 tools, built to be measured rather than demoed.</p>

  <p><strong>LLM for IR</strong> — my research direction: generative retrieval. The model emits a document's identifier directly, instead of scoring a fixed candidate set. Right now that means reproducing OneRec, which applies the same idea to recommendation.</p>

  <div class="light-only">{result_light}</div>
  <div class="dark-only">{result_dark}</div>

  <h3>Before that</h3>

  <p><strong><a href="https://github.com/howardatri/chat">chat</a></strong> — C++ service work: gRPC + protobuf, Redis, MySQL.</p>

  <h3>Activity</h3>

  <div class="light-only">{stats_light}</div>
  <div class="dark-only">{stats_dark}</div>

  <h3>Elsewhere</h3>

  <p><a href="https://howardatri.github.io">Blog</a> &nbsp;·&nbsp; <a href="mailto:Howard22022@outlook.com">Howard22022@outlook.com</a></p>

  <p><sub>写系统，也写能证伪它的仪器。上面那个 −39.4% 不花一分钱 API 费就能复现。</sub></p>

</div>
</div>

<script>
  const root = document.documentElement;
  const bl = document.getElementById('btn-light');
  const bd = document.getElementById('btn-dark');

  function setTheme(t) {{
    root.dataset.theme = t;
    bl.setAttribute('aria-pressed', t === 'light');
    bd.setAttribute('aria-pressed', t === 'dark');
  }}
  bl.onclick = () => setTheme('light');
  bd.onclick = () => setTheme('dark');

  const q = new URLSearchParams(location.search).get('theme');
  if (q === 'dark' || q === 'light') setTheme(q);
  else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) setTheme('dark');
</script>
</body>
</html>
"""


def main() -> None:
    parts = {k: load(k) for k in ASSETS}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(TEMPLATE.format(**parts), encoding="utf-8")
    size = OUT.stat().st_size
    print(f"wrote {OUT.relative_to(ROOT)}  ({size / 1024:.1f} KB, self-contained)")


if __name__ == "__main__":
    main()
