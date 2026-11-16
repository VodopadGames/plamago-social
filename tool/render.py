"""Render Plamago social slides: every *.html in a post folder -> 1080x1080 PNG.

Usage: python3 render.py <post_dir> <out_dir>
The HTML files reference ../../tool/base.css relative to themselves via the
<base> tag written by the build scripts, so they must be opened from disk.
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

post_dir, out_dir = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
out_dir.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1080, "height": 1080}, device_scale_factor=1)
    for html in sorted(post_dir.glob("*.html")):
        page.goto(html.as_uri())
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(200)
        # Fail loudly if content overflows the square instead of clipping silently.
        over = page.evaluate(
            "(() => { const s = document.querySelector('.slide');"
            " return [s.scrollWidth - s.clientWidth, s.scrollHeight - s.clientHeight]; })()"
        )
        fonts = page.evaluate("[...document.fonts].filter(f => f.status === 'loaded').map(f => f.family)")
        target = out_dir / (html.stem + ".png")
        page.screenshot(path=str(target), clip={"x": 0, "y": 0, "width": 1080, "height": 1080})
        print(f"{target.name}: overflow={over} fonts={sorted(set(fonts))}")
    browser.close()
