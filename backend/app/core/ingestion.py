import json
import re

from app.core.grobid_client import extract_bibliography, extract_tei_xml, tei_to_markdown

HEADING_RE = re.compile(
    r'(?ms)^(?P<level>#{1,6})\s*(?P<title>.+?)\s*$\n(?P<body>.*?)(?=(?:\n^#{1,6}\s)|\Z)',
    re.MULTILINE | re.DOTALL
)


def ingest_paper(file_bytes: bytes, filename: str) -> tuple[str, list[dict]]:
    """
    Load a PDF or pre-parsed JSON paper into markdown, plus a parsed
    bibliography when available (PDFs, via GROBID; empty for JSON uploads).
    """
    is_pdf = filename.lower().endswith(".pdf")
    is_json = filename.lower().endswith(".json")

    if not (is_pdf or is_json):
        raise ValueError("Unsupported file type. Only PDF or JSON allowed.")

    if is_pdf:
        tei_xml = extract_tei_xml(file_bytes)
        return tei_to_markdown(tei_xml), extract_bibliography(tei_xml)

    data = json.loads(file_bytes)
    return data["markdown"], []


def section_paper(md: str) -> dict:
    """Parse markdown into a {level, title, body} list plus a numbered headers string."""
    sections = []
    for m in HEADING_RE.finditer(md):
        sections.append({
            "level": len(m.group("level")),
            "title": m.group("title").strip(),
            "body": m.group("body").rstrip(),
        })

    headers = "\n"
    for idx, section in enumerate(sections):
        headers += f"{idx + 1} : {section['title']}\n"

    return {"headers": headers, "sections": sections}
