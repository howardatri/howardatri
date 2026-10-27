#!/usr/bin/env python3
"""Generate the profile stats strip as a light/dark SVG pair.

Numbers come from the public GitHub REST API, so the output is reproducible:
anyone can re-run this and get the same picture. No third-party card service is
involved, which is deliberate -- github-readme-stats lives on *.vercel.app, and
that domain is DNS-poisoned for mainland-China visitors, so the cards would
render as broken images for exactly the audience this profile targets.

Usage:
    python scripts/gen_stats.py            # no token, 60 req/h
    GITHUB_TOKEN=ghp_... python scripts/gen_stats.py
"""

from __future__ import annotations

import collections
import json
import os
import pathlib
import urllib.request

USER = "howardatri"
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"

SANS = "ui-sans-serif, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"

THEMES = {
    "light": {
        "bg": "#FFFFFF",
        "ink": "#1F2328",
        "muted": "#656D76",
        "rule": "#DDE1E5",
        # monochrome ramp off the page accent, darkest first
        "ramp": ["#2E5D4F", "#5A8F7D", "#8FB3A6", "#C3D5CD", "#DDE6E1"],
    },
    "dark": {
        "bg": "#0D1117",
        "ink": "#E6EDF3",
        "muted": "#8B949E",
        "rule": "#30363D",
        "ramp": ["#8FC2AC", "#6BA18C", "#4A7A69", "#33584C", "#243B34"],
    },
}


def get(url: str):
    headers = {"User-Agent": "howardatri-profile-stats", "Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def collect() -> dict:
    user = get(f"https://api.github.com/users/{USER}")
    repos = get(f"https://api.github.com/users/{USER}/repos?per_page=100&sort=pushed")
    own = [r for r in repos if not r["fork"]]

    langs = collections.Counter(r["language"] for r in own if r["language"])
    ordered = langs.most_common()

    return {
        "repos": len(own),
        "followers": user["followers"],
        "last_push": max(r["pushed_at"] for r in repos)[:7],
        "langs": ordered,
        "langs_total": sum(n for _, n in ordered),
    }


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def mono_w(text: str, size: float) -> float:
    """Rough advance width for a monospace string."""
    return len(text) * size * 0.6


def render(data: dict, t: dict) -> str:
    W, H = 880, 196
    metrics = [
        ("ORIGINAL REPOS", str(data["repos"])),
        ("LANGUAGES", str(len(data["langs"]))),
        ("FOLLOWERS", str(data["followers"])),
        ("LAST PUSH", data["last_push"]),
    ]

    out: list[str] = []
    add = out.append
    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="GitHub stats: {data["repos"]} repositories, {len(data["langs"])} languages, '
        f'{data["followers"]} followers, last push {data["last_push"]}">')
    add("  <title>GitHub stats</title>")
    add(f'  <rect width="{W}" height="{H}" fill="{t["bg"]}"/>')
    add(f'  <line x1="0" y1="0.5" x2="{W}" y2="0.5" stroke="{t["rule"]}" stroke-width="1"/>')

    for i, (label, value) in enumerate(metrics):
        x = i * 220
        add(f'  <text x="{x}" y="40" font-family="{MONO}" font-size="10" letter-spacing="1.7" '
            f'fill="{t["muted"]}">{esc(label)}</text>')
        add(f'  <text x="{x}" y="80" font-family="{MONO}" font-size="30" fill="{t["ink"]}">{esc(value)}</text>')

    add(f'  <line x1="0" y1="104" x2="{W}" y2="104" stroke="{t["rule"]}" stroke-width="1"/>')

    add(f'  <text x="0" y="130" font-family="{MONO}" font-size="10" letter-spacing="1.7" '
        f'fill="{t["muted"]}">LANGUAGES &#183; BY ORIGINAL REPOSITORY</text>')

    # stacked share bar -- gaps and rounded ends so it reads as a chart,
    # not as another hairline
    bar_y, bar_h, gap = 144, 10, 3
    total = max(data["langs_total"], 1)
    cursor = 0.0
    n_items = len(data["langs"])
    for i, (name, n) in enumerate(data["langs"]):
        span = W * n / total
        x = cursor + (gap if i else 0)
        w = span - (gap if i else 0) - (gap if i < n_items - 1 else 0)
        add(f'  <rect x="{x:.2f}" y="{bar_y}" width="{max(w, 0):.2f}" height="{bar_h}" rx="2" '
            f'fill="{t["ramp"][min(i, len(t["ramp"]) - 1)]}"/>')
        cursor += span

    # legend
    lx = 0.0
    size = 11
    for i, (name, n) in enumerate(data["langs"]):
        color = t["ramp"][min(i, len(t["ramp"]) - 1)]
        add(f'  <circle cx="{lx + 3.5:.2f}" cy="174" r="3.5" fill="{color}"/>')
        text = f"{name} {n}"
        add(f'  <text x="{lx + 13:.2f}" y="178" font-family="{MONO}" font-size="{size}" '
            f'fill="{t["muted"]}">{esc(text)}</text>')
        lx += 13 + mono_w(text, size) + 28

    add(f'  <line x1="0" y1="{H - 0.5}" x2="{W}" y2="{H - 0.5}" stroke="{t["rule"]}" stroke-width="1"/>')
    add("</svg>")
    return "\n".join(out) + "\n"


def main() -> None:
    data = collect()
    OUT.mkdir(parents=True, exist_ok=True)
    for name, theme in THEMES.items():
        path = OUT / f"stats-{name}.svg"
        path.write_text(render(data, theme), encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")
    print(f"  {data['repos']} original repos · {data['followers']} followers · last push {data['last_push']}")
    print("  languages: " + ", ".join(f"{k}={v}" for k, v in data["langs"]))


if __name__ == "__main__":
    main()
