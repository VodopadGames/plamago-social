"""Build slide HTML for a post from its spec, then render it.

Usage: python3 tool/build.py src/NN
Reads src/NN/spec.json, writes src/NN/slide*.html and renders posts/NN/*.png.

Templates (spec["template"]):
  "single"        one slide: headline, keyword chips, phone screenshot
  "before_after"  three slides: before mock post, after screenshot, how it works

Every text in the spec is used verbatim. Screenshots are files next to the spec.
"""
import html
import json
import subprocess
import sys
from pathlib import Path

HEAD = """<!doctype html>
<html lang="bg"><head><meta charset="utf-8">
<link rel="stylesheet" href="../../tool/base.css">
<style>{css}</style></head><body>
{body}
</body></html>
"""

CHECK = ('<svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#16A34A" stroke-width="2.6" '
         'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>')
ARROW_DOWN = ('<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#FF6B2C" stroke-width="2.6" '
              'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 5v14"/><path d="M6 13l6 6 6-6"/></svg>')
ARROW_RIGHT = ('<svg width="38" height="38" viewBox="0 0 24 24" fill="none" stroke="#FF6B2C" stroke-width="2.6" '
               'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="M13 6l6 6-6 6"/></svg>')


def e(text):
    return html.escape(text, quote=False)


def brand(icon=True):
    img = '<img src="../../tool/icon.png" alt="">' if icon else ""
    return f'<div class="brand">{img}Plamago</div>'


def chips(items, cls="chip"):
    return "".join(f'<div class="{cls}">{e(i)}</div>' for i in items)


def phone(src, alt):
    return f'<div class="stage"><div class="phone"><div class="screen"><img src="{src}" alt="{e(alt)}"></div></div></div>'


def how_it_works(spec, count):
    css = """
.slide { justify-content: space-between; }
h1 { font-size: 50px; }
.card { background: #fff; border: 2px solid var(--line); border-radius: 28px; padding: 26px 30px; display: flex; flex-direction: column; gap: 16px; margin-top: 22px; }
.cap { font-weight: 600; font-size: 26px; color: var(--muted); }
.row { display: flex; flex-wrap: wrap; gap: 12px; }
.chip { font-size: 28px; padding: 10px 20px; }
.tag { padding: 8px 18px; border-radius: 14px; border: 2px solid var(--line); font-weight: 600; font-size: 26px; }
.then { display: flex; align-items: center; gap: 18px; margin-top: 26px; }
.ok { display: flex; align-items: center; gap: 10px; padding: 10px 20px; border-radius: 999px; background: #fff; border: 2px solid var(--line); font-weight: 700; font-size: 26px; }
"""
    body = f"""<div class="slide">
  <div class="top"><div class="label">Как работи</div><div class="count">{count}</div></div>
  <div>
    <h1>Ти пишеш няколко думи.</h1>
    <div class="card">
      <div class="cap">Ключови думи / тема</div>
      <div class="row">{chips(spec["keywords"])}</div>
      <div class="row">{chips([spec["platform"], spec["niche"]], "tag")}</div>
    </div>
    <div class="then">{ARROW_DOWN}<h1>Plamago пише поста.</h1></div>
    <div class="row" style="margin-top: 20px">
      <div class="ok">{CHECK}Готов текст</div><div class="ok">{CHECK}Хаштагове</div><div class="ok">{CHECK}За секунди</div>
    </div>
  </div>
  <div class="cta">
    <div><div class="q">Искаш ранен достъп?</div><div class="a">Линкът е в био.</div></div>
    {brand(icon=False)}
  </div>
</div>"""
    return HEAD.format(css=css, body=body)


def single(spec):
    css = """
.slide { justify-content: flex-start; gap: 20px; }
h1 { font-size: 56px; }
.row { display: flex; flex-wrap: wrap; gap: 12px; }
.chip { font-size: 28px; padding: 10px 20px; }
.stage { flex: 1; min-height: 0; display: flex; justify-content: center; }
.phone { width: 640px; height: 100%; }
"""
    body = f"""<div class="slide">
  <div class="top"><div class="label">{e(spec["label"])}</div>{brand()}</div>
  <h1>{e(spec["headline"])}</h1>
  <div class="row">{chips(spec["keywords"])}</div>
  {phone(spec["screenshot"], spec["alt"])}
  <div class="note">{e(spec["note"])}</div>
</div>"""
    return {"slide1": HEAD.format(css=css, body=body)}


def before_after(spec):
    b = spec["before"]
    css1 = """
h1 { font-size: 62px; }
.post { background: #fff; border: 2px solid var(--line); border-radius: 28px; overflow: hidden; margin-top: 30px; }
.who { display: flex; align-items: center; gap: 18px; padding: 26px 32px 0; }
.av { width: 64px; height: 64px; border-radius: 999px; background: #D1D5DB; }
.name { font-weight: 700; font-size: 28px; }
.when { font-weight: 500; font-size: 26px; color: var(--muted); }
.txt { padding: 26px 32px 34px; font-family: "Inter", "Noto Color Emoji", sans-serif; font-weight: 600; font-size: 40px; line-height: 1.25; }
.acts { display: flex; justify-content: space-around; padding: 20px 32px; border-top: 2px solid #F3F4F6; font-weight: 600; font-size: 26px; color: var(--muted); }
"""
    body1 = f"""<div class="slide">
  <div class="top"><div class="label">Преди</div><div class="count">1 / 3</div></div>
  <div>
    <h1>{e(b["headline"])}</h1>
    <div class="post">
      <div class="who"><div class="av"></div><div><div class="name">{e(b["account"])}</div><div class="when">{e(b["when"])}</div></div></div>
      <div class="txt">{e(b["text"])}</div>
      <div class="acts"><div>Харесване</div><div>Коментар</div><div>Споделяне</div></div>
    </div>
  </div>
  <div class="bottom"><div class="note">{e(b["note"])}</div><div class="brand"><img src="../../tool/icon.png" alt="">Plamago {ARROW_RIGHT}</div></div>
</div>"""
    a = spec["after"]
    css2 = """
.slide { justify-content: flex-start; gap: 22px; }
h1 { font-size: 52px; }
.stage { flex: 1; min-height: 0; display: flex; justify-content: center; }
.phone { width: 680px; height: 100%; box-shadow: 0 30px 60px rgba(20, 20, 19, 0.3); }
"""
    body2 = f"""<div class="slide orange">
  <div class="top"><div class="label">След</div><div class="count">2 / 3</div></div>
  <h1>{e(a["headline"])}</h1>
  {phone(a["screenshot"], a["alt"])}
  <div class="bottom"><div class="note">{e(a["note"])}</div>{brand(icon=False)}</div>
</div>"""
    return {
        "slide1": HEAD.format(css=css1, body=body1),
        "slide2": HEAD.format(css=css2, body=body2),
        "slide3": how_it_works(spec["how"], "3 / 3"),
    }


TEMPLATES = {"single": single, "before_after": before_after}

if __name__ == "__main__":
    src = Path(sys.argv[1]).resolve()
    spec = json.loads((src / "spec.json").read_text(encoding="utf-8"))
    for name, doc in TEMPLATES[spec["template"]](spec).items():
        (src / f"{name}.html").write_text(doc, encoding="utf-8")
    out = src.parent.parent / "posts" / src.name
    subprocess.run([sys.executable, str(Path(__file__).with_name("render.py")), str(src), str(out)], check=True)
