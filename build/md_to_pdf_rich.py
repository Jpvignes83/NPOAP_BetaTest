from pathlib import Path
import re
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
)


def _format_inline_md(text: str) -> str:
    text = escape(text)
    text = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", text)
    return text


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.grey)
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Page {doc.page}")
    canvas.restoreState()


def build_pdf(md_path: Path, pdf_path: Path) -> None:
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle(
        "H1",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        spaceBefore=12,
        spaceAfter=8,
        textColor=colors.HexColor("#1f3c88"),
    )
    h2 = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        spaceBefore=10,
        spaceAfter=6,
        textColor=colors.HexColor("#0f5c99"),
    )
    h3 = ParagraphStyle(
        "H3",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        spaceBefore=8,
        spaceAfter=4,
    )
    body = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=14,
        spaceBefore=2,
        spaceAfter=4,
    )
    bullet = ParagraphStyle(
        "Bullet",
        parent=body,
        leftIndent=16,
        firstLineIndent=-8,
        spaceAfter=2,
    )
    code = ParagraphStyle(
        "Code",
        parent=styles["Code"],
        fontName="Courier",
        fontSize=9,
        leading=11,
        backColor=colors.HexColor("#f5f5f5"),
        borderColor=colors.HexColor("#dddddd"),
        borderWidth=0.5,
        borderPadding=6,
        leftIndent=4,
        rightIndent=4,
        spaceBefore=4,
        spaceAfter=6,
    )

    story = []
    lines = md_path.read_text(encoding="utf-8", errors="ignore").splitlines()

    in_code = False
    code_buf = []
    para_buf = []

    def flush_para():
        nonlocal para_buf
        if para_buf:
            text = " ".join(s.strip() for s in para_buf if s.strip())
            if text:
                story.append(Paragraph(_format_inline_md(text), body))
            para_buf = []

    def flush_code():
        nonlocal code_buf
        if code_buf:
            story.append(Preformatted("\n".join(code_buf), code))
            code_buf = []

    for raw in lines:
        line = raw.rstrip("\n")
        stripped = line.strip()

        if stripped.startswith("```"):
            flush_para()
            if in_code:
                flush_code()
                in_code = False
            else:
                in_code = True
            continue

        if in_code:
            code_buf.append(line)
            continue

        if not stripped:
            flush_para()
            story.append(Spacer(1, 6))
            continue

        if re.match(r"^---+$", stripped):
            flush_para()
            story.append(Spacer(1, 8))
            continue

        m_h = re.match(r"^(#{1,3})\s+(.+)$", stripped)
        if m_h:
            flush_para()
            level = len(m_h.group(1))
            text = _format_inline_md(m_h.group(2))
            if level == 1:
                story.append(Paragraph(text, h1))
            elif level == 2:
                story.append(Paragraph(text, h2))
            else:
                story.append(Paragraph(text, h3))
            continue

        m_num = re.match(r"^(\d+)\.\s+(.+)$", stripped)
        if m_num:
            flush_para()
            story.append(Paragraph(_format_inline_md(m_num.group(2)), bullet, bulletText=f"{m_num.group(1)}."))
            continue

        m_b = re.match(r"^[-*]\s+(.+)$", stripped)
        if m_b:
            flush_para()
            story.append(Paragraph(_format_inline_md(m_b.group(1)), bullet, bulletText="•"))
            continue

        para_buf.append(line)

    flush_para()
    if in_code:
        flush_code()

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="MANUEL_UTILISATEUR",
        author="NPOAP",
    )
    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)


if __name__ == "__main__":
    base = Path(__file__).resolve().parents[1]
    md = base / "docs" / "MANUEL_UTILISATEUR.md"
    out = base / "docs" / "MANUEL_UTILISATEUR_rich.pdf"
    build_pdf(md, out)
    print(out)

