"""
Build the published legal pages from the markdown sources.

The markdown files are the single source of truth. Edit those, re-run this, commit
the generated HTML. Keeping the sources in the repo means the published text has
a readable diff history — useful for a document you may have to prove the state
of on a given date.

    python build.py

Needs the `markdown` package. If it is not installed, use a throwaway venv rather
than adding it globally:

    python -m venv .venv && .venv/Scripts/python -m pip install markdown
    .venv/Scripts/python build.py
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

try:
    import markdown
except ImportError:  # pragma: no cover
    sys.exit("markdown not installed — see the module docstring")

ROOT = Path(__file__).resolve().parent

#: (source markdown, output directory, <title>, short description)
PAGES = [
    ("src/privacy-policy.md", "privacy", "Privacy Policy",
     "How CoUnity, LLC handles information in its Discord applications."),
    ("src/terms-of-service.md", "terms", "Terms of Service",
     "The terms governing use of CoUnity's Discord applications."),
]

# Deliberately self-contained: no fonts, no CDN, no JS. A legal page has to render
# for anyone, on anything, years from now, and must not depend on a design system
# that will change. Styles both colour schemes because the reader's preference is
# not ours to override.
TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · CoUnity, LLC</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<!-- Favicon inlined as a data URI: keeps the page self-contained, so there is no
     second request that can 404 or be blocked. A plain "C" monogram — no
     wordmark, so it needs no maintenance if branding changes. -->
<link rel="icon" href="data:image/svg+xml,{favicon}">
<style>
  :root {{
    --bg: #ffffff; --fg: #1a1a1a; --muted: #5c5c5c; --rule: #e4e4e4;
    --link: #1a4fd6; --code-bg: #f4f4f5; --accent: #6b46c1;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --bg: #14141a; --fg: #e8e8ea; --muted: #a0a0aa; --rule: #2e2e38;
      --link: #8fb4ff; --code-bg: #1e1e26; --accent: #b794f6;
    }}
  }}
  * {{ box-sizing: border-box; }}
  html {{ -webkit-text-size-adjust: 100%; }}
  body {{
    margin: 0; background: var(--bg); color: var(--fg);
    font: 16px/1.65 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
          Helvetica, Arial, sans-serif;
  }}
  .wrap {{ max-width: 46rem; margin: 0 auto; padding: 3rem 1.25rem 6rem; }}
  nav.top {{
    font-size: .875rem; padding-bottom: 2rem; margin-bottom: 2rem;
    border-bottom: 1px solid var(--rule);
  }}
  nav.top a {{ margin-right: 1.25rem; }}
  h1 {{ font-size: 1.9rem; line-height: 1.25; margin: 0 0 1.5rem; }}
  h2 {{
    font-size: 1.3rem; margin: 2.75rem 0 .85rem; padding-top: .5rem;
    border-top: 1px solid var(--rule);
  }}
  h3 {{ font-size: 1.05rem; margin: 2rem 0 .6rem; }}
  h2 + h3 {{ margin-top: 1rem; }}
  p, ul, ol, table {{ margin: 0 0 1.1rem; }}
  ul, ol {{ padding-left: 1.4rem; }}
  li {{ margin-bottom: .4rem; }}
  a {{ color: var(--link); text-decoration: underline; text-underline-offset: 2px; }}
  strong {{ font-weight: 650; }}
  code {{
    background: var(--code-bg); padding: .12em .35em; border-radius: 3px;
    font: .875em/1.4 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  }}
  hr {{ border: 0; border-top: 1px solid var(--rule); margin: 2.5rem 0; }}
  blockquote {{
    margin: 0 0 1.1rem; padding: .1rem 0 .1rem 1rem;
    border-left: 3px solid var(--accent); color: var(--muted);
  }}
  /* Wide tables scroll inside their own box; the page never scrolls sideways. */
  .table-wrap {{ overflow-x: auto; margin: 0 0 1.1rem; }}
  table {{ border-collapse: collapse; width: 100%; font-size: .925rem; }}
  th, td {{
    text-align: left; padding: .5rem .7rem; border-bottom: 1px solid var(--rule);
    vertical-align: top;
  }}
  th {{ font-weight: 650; }}
  /* The contact address is an H2 in the source so it stands out; keep it doing so. */
  h2 a[href^="mailto:"] {{ text-decoration: none; }}
  footer {{
    margin-top: 4rem; padding-top: 1.5rem; border-top: 1px solid var(--rule);
    font-size: .875rem; color: var(--muted);
  }}
  @media print {{
    body {{ background: #fff; color: #000; }}
    nav.top, footer {{ display: none; }}
    .wrap {{ max-width: none; padding: 0; }}
    a {{ color: #000; }}
  }}
</style>
</head>
<body>
<div class="wrap">
<nav class="top">
  <a href="{base}/">CoUnity Legal</a>
  <a href="{base}/privacy/">Privacy Policy</a>
  <a href="{base}/terms/">Terms of Service</a>
</nav>
{body}
<footer>
  CoUnity, LLC · Questions or requests:
  <a href="mailto:privacy@counity.xyz">privacy@counity.xyz</a>
</footer>
</div>
</body>
</html>
"""

INDEX_BODY = """<h1>CoUnity, LLC — Legal</h1>
<p>These documents govern the Discord applications operated by CoUnity, LLC.</p>
<ul>
  <li><a href="{base}/privacy/"><strong>Privacy Policy</strong></a> — what is collected,
      how it is used and shared, and how to opt out or have it deleted.</li>
  <li><a href="{base}/terms/"><strong>Terms of Service</strong></a> — the terms for using
      the applications.</li>
</ul>
<h2>Opting out or deleting your data</h2>
<p>Email <a href="mailto:privacy@counity.xyz">privacy@counity.xyz</a> with
<strong>&ldquo;Opt-Out Request&rdquo;</strong> or
<strong>&ldquo;Data Deletion Request&rdquo;</strong> in the subject line and your
numeric Discord user ID. Requests are acknowledged promptly and completed within
30 days. The <a href="{base}/privacy/">Privacy Policy</a> sets out the full
process.</p>
"""

# A "C" monogram. Deliberately not a wordmark: nothing to update if the brand
# changes, and it stays legible at 16px where lettering usually does not.
_FAVICON_SVG = (
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'>"
    "<rect width='32' height='32' rx='7' fill='%236b46c1'/>"
    "<text x='16' y='23' font-family='-apple-system,Segoe UI,Helvetica,Arial,sans-serif'"
    " font-size='20' font-weight='600' fill='%23ffffff' text-anchor='middle'>C</text>"
    "</svg>"
)

_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def render(md_text: str) -> str:
    """Markdown to HTML, with source comments stripped.

    Stripping comments matters: the privacy source carries an internal engineering
    note about not claiming a security control before it exists. That belongs in
    the repo, not in the page source of a public legal document.
    """
    md_text = _COMMENT_RE.sub("", md_text)
    body = markdown.markdown(md_text, extensions=["tables", "sane_lists", "attr_list"])
    # Let wide tables scroll on their own rather than the whole page.
    body = body.replace("<table>", '<div class="table-wrap"><table>')
    body = body.replace("</table>", "</table></div>")
    return body


def main() -> int:
    base = (ROOT / "BASE_URL").read_text(encoding="utf-8").strip().rstrip("/")

    written = []
    for src, outdir, title, description in PAGES:
        source = ROOT / src
        if not source.exists():
            sys.exit(f"missing source: {src}")
        target_dir = ROOT / outdir
        target_dir.mkdir(parents=True, exist_ok=True)
        page = TEMPLATE.format(
            title=html.escape(title),
            description=html.escape(description),
            canonical=f"{base}/{outdir}/",
            favicon=_FAVICON_SVG,
            base=base,
            body=render(source.read_text(encoding="utf-8")),
        )
        (target_dir / "index.html").write_text(page, encoding="utf-8")
        written.append(f"{outdir}/index.html")

    index = TEMPLATE.format(
        title="Legal",
        description="Privacy Policy and Terms of Service for CoUnity's Discord applications.",
        canonical=f"{base}/",
            favicon=_FAVICON_SVG,
        base=base,
        body=INDEX_BODY.format(base=base),
    )
    (ROOT / "index.html").write_text(index, encoding="utf-8")
    written.append("index.html")

    # GitHub Pages runs Jekyll by default, which would ignore files it does not
    # like the look of. This turns that off.
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")

    for w in written:
        print(f"  wrote {w}")
    print(f"\nbase URL: {base}")
    print("Edit src/*.md and re-run this; commit the generated HTML.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
