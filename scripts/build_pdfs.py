"""Render the written deliverables to submission-ready PDFs.

    python scripts/build_pdfs.py

Each document in `docs/` becomes an A4 PDF in `docs/pdf/` with a title
page, running footers and the team details, and the seven are then merged
into one file for portals that accept a single upload. The slide deck is
converted alongside them so the whole submission is one folder.

Requires WeasyPrint. On macOS its Pango and Cairo libraries live under
Homebrew, which the dynamic linker does not search by default:

    DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib python scripts/build_pdfs.py

The script sets that itself if it is missing, and re-executes once.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
OUT = DOCS / "pdf"

COURSE = "CE725 Construction Economics and Finance"
TOPIC = "Topic 7 — Earned Value Management Dashboard"
TEAM = "Team 40"
WHEN = "November 2026"
MEMBERS = [
    ("Sajjad Nakhwa", "23B0702", "Project Lead and Finance Modeller"),
    ("Dependar Arya", "23B0331", "Data Lead"),
    ("Neel Shah", "23B4244", "AI and Tool Developer"),
    ("Akshat Karkar", "23B4229", "Validation Engineer"),
    ("Pearsh Gumasta", "23B4232", "Documentation and Reflection Lead"),
]

# (source, title shown on the title page and in the footer, page orientation,
#  dense).
# The AI usage log is landscape: its Annexure A table is eight columns of
# prose and is unreadable at portrait width. The user manual is set dense,
# with its screenshots at 60% width, because the brief caps it at five
# pages and the alternative is deleting the assumptions and limitations
# sections — which are the part of a manual worth reading.
DOCUMENTS = [
    ("01-project-charter.md", "Project Charter", "portrait", False),
    ("02-method-note.md", "Method Note and Data Sources", "portrait", False),
    ("03-user-manual.md", "User Manual", "portrait", True),
    ("04-validation-report.md", "Validation Report", "portrait", False),
    ("05-ai-usage-log.md", "AI Usage Log", "landscape", False),
    ("06-learnings-and-reflection.md", "Learnings and Reflection Report", "portrait", False),
    ("07-presentation.md", "Presentation Script and Viva Preparation", "portrait", False),
]

DECK = DOCS / "presentation" / "CE725_Team40_EVM_Dashboard.pptx"
DECK_PDF_NAME = "08-presentation-slides.pdf"

# Page counts the brief specifies, checked after the build rather than assumed.
EXPECTED_PAGES = {
    "User Manual": (3, 5),
    "Learnings and Reflection Report": (10, 15),
}


def _ensure_libraries() -> None:
    """Re-exec once with Homebrew on the library path if WeasyPrint needs it."""
    if os.environ.get("_EVM_PDF_RELAUNCHED"):
        return
    try:
        import weasyprint  # noqa: F401
    except OSError:
        env = dict(os.environ)
        env["DYLD_FALLBACK_LIBRARY_PATH"] = (
            "/opt/homebrew/lib:" + env.get("DYLD_FALLBACK_LIBRARY_PATH", "")
        )
        env["_EVM_PDF_RELAUNCHED"] = "1"
        os.execve(sys.executable, [sys.executable, *sys.argv], env)


_ensure_libraries()

import markdown  # noqa: E402
from weasyprint import HTML  # noqa: E402

CSS = """
@page {{
  size: A4 {orientation};
  margin: {margin};
  @bottom-left  {{ content: "{footer}"; font-size: 7.5pt; color: #8a9499;
                   font-family: Helvetica, Arial, sans-serif; }}
  @bottom-right {{ content: counter(page) " of " counter(pages); font-size: 7.5pt;
                   color: #8a9499; font-family: Helvetica, Arial, sans-serif; }}
}}
@page :first {{ margin: 0; @bottom-left {{ content: ""; }} @bottom-right {{ content: ""; }} }}

body {{ font-family: Charter, Georgia, "Times New Roman", serif;
        font-size: {body_pt}pt; line-height: {leading}; color: #1a1f22; hyphens: auto; }}

/* ---- title page ---- */
.title-page {{ page-break-after: always; padding: 52mm 22mm 0 22mm; height: 100%; }}
.title-page .course {{ font-family: Helvetica, Arial, sans-serif; font-size: 10.5pt;
    letter-spacing: 0.06em; text-transform: uppercase; color: #7d8e97; }}
.title-page .topic {{ font-size: 12pt; color: #3e5660; margin-top: 3mm; }}
.title-page h1 {{ font-family: Charter, Georgia, serif; font-size: 27pt; font-weight: bold;
    color: #1a1f22; margin: 14mm 0 0 0; line-height: 1.2; }}
.title-page .team {{ margin-top: 16mm; font-family: Helvetica, Arial, sans-serif;
    font-size: 11pt; font-weight: bold; color: #1a1f22; }}
.title-page table.members {{ margin-top: 4mm; border: none; font-size: 10pt; width: auto; }}
.title-page table.members td {{ border: none; padding: 1.1mm 7mm 1.1mm 0; }}
.title-page td.roll {{ color: #7d8e97; font-family: Helvetica, Arial, sans-serif;
    font-size: 9pt; }}
.title-page td.role {{ color: #3e5660; }}
.title-page .when {{ margin-top: 14mm; font-size: 10pt; color: #7d8e97; }}

/* ---- headings ---- */
h2 {{ font-family: Helvetica, Arial, sans-serif; font-size: 14pt; color: #1a1f22;
      margin: {h2_top} 0 2.5mm 0; page-break-after: avoid; }}
h3 {{ font-family: Helvetica, Arial, sans-serif; font-size: 11.5pt; color: #26353d;
      margin: 6mm 0 2mm 0; page-break-after: avoid; }}
h4 {{ font-family: Helvetica, Arial, sans-serif; font-size: 10pt; color: #3e5660;
      margin: 4.5mm 0 1.5mm 0; page-break-after: avoid; }}
p {{ margin: 0 0 2.6mm 0; orphans: 2; widows: 2; }}

/* ---- tables ---- */
table {{ border-collapse: collapse; width: 100%; margin: 3mm 0 4mm 0; font-size: 9pt;
         page-break-inside: auto; }}
th, td {{ border: 0.5pt solid #d5dbde; padding: 1.3mm 1.8mm; text-align: left;
          vertical-align: top; }}
th {{ background: #edf0f1; font-family: Helvetica, Arial, sans-serif; font-size: 8.5pt;
      font-weight: bold; }}
tr {{ page-break-inside: avoid; }}
table.wide {{ font-size: 7.5pt; }}
table.wide th {{ font-size: 7pt; }}
table.wide th, table.wide td {{ padding: 0.9mm 1.2mm; }}

/* ---- blocks ---- */
blockquote {{ margin: 3mm 0; padding: 2mm 0 2mm 5mm; border-left: 2.5pt solid #c1553b;
              color: #26353d; }}
blockquote p:last-child {{ margin-bottom: 0; }}
pre {{ font-family: Menlo, "Courier New", monospace; font-size: 8pt; line-height: 1.35;
       background: #f4f7f8; border: 0.5pt solid #e1e7ea; padding: 2.5mm 3mm;
       white-space: pre; page-break-inside: avoid; margin: 3mm 0; }}
code {{ font-family: Menlo, "Courier New", monospace; font-size: 8.8pt;
        background: #f4f7f8; padding: 0 0.6mm; }}
pre code {{ background: none; font-size: 8pt; padding: 0; }}
ul, ol {{ margin: 0 0 2.6mm 0; padding-left: 6mm; }}
li {{ margin-bottom: 1mm; }}
hr {{ border: none; border-top: 0.5pt solid #dde3e6; margin: 6mm 0; }}
img {{ max-width: {img_width}; border: 0.5pt solid #dde3e6; margin: 2mm 0; }}
a {{ color: #3e5660; text-decoration: none; }}
"""


def strip_front_matter(md: str) -> str:
    """Drop the leading H1 and the bold course lines that follow it.

    The title page already carries both, and repeating them under it reads
    as a formatting mistake.
    """
    lines = md.split("\n")
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and lines[i].startswith("# "):
        i += 1
        while i < len(lines) and (
            not lines[i].strip() or re.fullmatch(r"\*\*.+\*\*", lines[i].strip())
        ):
            i += 1
    return "\n".join(lines[i:])


def tidy_tables(html: str) -> str:
    """Shrink wide tables, and drop header rows that carry no labels.

    Several documents use a headerless markdown table (`| | |`) for
    two-column layouts. Markdown still emits a <thead>, which renders as an
    empty shaded strip above the table.
    """
    def repl(m: re.Match) -> str:
        table = m.group(0)
        head = re.search(r"<thead>.*?</thead>", table, re.S)
        if head and not re.sub(r"<[^>]+>|\s", "", head.group(0)):
            table = table.replace(head.group(0), "", 1)
            head = None
        row = re.search(r"<tr>.*?</tr>", table, re.S)
        cols = len(re.findall(r"<t[hd][ >]", row.group(0))) if row else 0
        return table.replace("<table>", '<table class="wide">', 1) if cols > 6 else table

    return re.sub(r"<table>.*?</table>", repl, html, flags=re.S)


def title_page(title: str) -> str:
    rows = "".join(
        f'<tr><td><b>{n}</b></td><td class="roll">{r}</td><td class="role">{role}</td></tr>'
        for n, r, role in MEMBERS
    )
    return f"""<div class="title-page">
  <div class="course">{COURSE}</div>
  <div class="topic">{TOPIC}</div>
  <h1>{title}</h1>
  <div class="team">{TEAM}</div>
  <table class="members">{rows}</table>
  <div class="when">Semester course project &middot; {WHEN}</div>
</div>"""


LAYOUT = {
    False: dict(margin="19mm 18mm 17mm 18mm", body_pt="10.5", leading="1.5",
                img_width="100%", h2_top="9mm"),
    True:  dict(margin="15mm 15mm 14mm 15mm", body_pt="9.8", leading="1.38",
                img_width="60%", h2_top="6mm"),
}


def build(source: str, title: str, orientation: str, dense: bool = False) -> Path:
    md_text = strip_front_matter((DOCS / source).read_text())
    body = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "attr_list", "sane_lists", "md_in_html"],
    )
    html = (
        "<!doctype html><html><head><meta charset='utf-8'>"
        f"<style>{CSS.format(orientation=orientation, footer=f'{TEAM} \u00B7 {title}', **LAYOUT[dense])}</style>"
        f"</head><body>{title_page(title)}{tidy_tables(body)}</body></html>"
    )
    target = OUT / (Path(source).stem + ".pdf")
    HTML(string=html, base_url=str(DOCS)).write_pdf(target)
    return target


def convert_deck() -> Path | None:
    if not DECK.exists():
        return None
    subprocess.run(
        ["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(OUT), str(DECK)],
        check=True, capture_output=True,
    )
    produced = OUT / (DECK.stem + ".pdf")
    target = OUT / DECK_PDF_NAME
    if produced.exists():
        produced.replace(target)
    return target if target.exists() else None


def main() -> int:
    OUT.mkdir(exist_ok=True)
    from pypdf import PdfReader, PdfWriter

    built: list[tuple[str, Path, int]] = []
    for source, title, orientation, dense in DOCUMENTS:
        path = build(source, title, orientation, dense)
        pages = len(PdfReader(path).pages)
        built.append((title, path, pages))
        print(f"{path.name:36s} {pages:3d} pages")

    deck = convert_deck()
    if deck:
        pages = len(PdfReader(deck).pages)
        built.append(("Presentation slides", deck, pages))
        print(f"{deck.name:36s} {pages:3d} pages")

    writer = PdfWriter()
    for _, path, _ in built:
        for page in PdfReader(path).pages:
            writer.add_page(page)
    combined = OUT / "CE725_Team40_Topic7_All_Deliverables.pdf"
    with open(combined, "wb") as fh:
        writer.write(fh)
    print(f"\n{combined.name:36s} {len(writer.pages):3d} pages (all of the above)")

    problems = [
        f"  {title}: {pages} pages, brief asks for {lo}-{hi}"
        for title, _, pages in built
        if (bounds := EXPECTED_PAGES.get(title)) and not (lo := bounds[0]) <= pages <= (hi := bounds[1])
    ]
    if problems:
        print("\nOutside the page counts the brief specifies:")
        print("\n".join(problems))
        return 1
    print("\nAll page counts are within the brief's limits.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
