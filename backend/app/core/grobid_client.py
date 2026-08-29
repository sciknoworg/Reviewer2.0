import httpx
from lxml import etree

from app.config import settings

TEI_NS = {"tei": "http://www.tei-c.org/ns/1.0"}


class GrobidError(Exception):
    """Raised when GROBID is unreachable or fails to process a PDF."""


def extract_tei_xml(pdf_bytes: bytes) -> str:
    """Send a PDF to GROBID's full-text endpoint and return the TEI XML response."""
    url = f"{settings.GROBID_URL}/api/processFulltextDocument"
    try:
        response = httpx.post(
            url,
            files={"input": ("paper.pdf", pdf_bytes, "application/pdf")},
            data={"consolidateHeader": "1", "consolidateCitations": "1"},
            timeout=120.0,
        )
    except httpx.HTTPError as e:
        raise GrobidError(f"Could not reach GROBID at {settings.GROBID_URL}: {e}") from e

    if response.status_code != 200:
        raise GrobidError(f"GROBID returned status {response.status_code}: {response.text[:500]}")

    return response.text


def _paragraph_text(p_el) -> str:
    return "".join(p_el.itertext()).strip()


def tei_to_markdown(tei_xml: str) -> str:
    """
    Convert GROBID's TEI XML into the same flat '# Heading' markdown structure
    that paper_sectioning_tool's regex splitter expects, so the rest of the
    review pipeline works identically for PDF and pre-parsed JSON uploads.
    """
    root = etree.fromstring(tei_xml.encode("utf-8"))

    lines = []

    title_el = root.find(".//tei:titleStmt/tei:title", TEI_NS)
    title = title_el.text.strip() if title_el is not None and title_el.text else "Untitled"
    lines.append(f"# {title}\n")

    abstract_paragraphs = root.findall(".//tei:abstract//tei:p", TEI_NS)
    if abstract_paragraphs:
        lines.append("# Abstract\n")
        for p in abstract_paragraphs:
            lines.append(_paragraph_text(p) + "\n")

    for div in root.findall(".//tei:body/tei:div", TEI_NS):
        head_el = div.find("tei:head", TEI_NS)
        heading = head_el.text.strip() if head_el is not None and head_el.text else None
        if not heading:
            continue
        lines.append(f"# {heading}\n")
        for p in div.findall("tei:p", TEI_NS):
            text = _paragraph_text(p)
            if text:
                lines.append(text + "\n")

    return "\n".join(lines)


def extract_bibliography(tei_xml: str) -> list[dict]:
    """Parse GROBID's consolidated reference list into {title, authors, year, doi} entries."""
    root = etree.fromstring(tei_xml.encode("utf-8"))

    entries = []
    for bibl in root.findall(".//tei:back//tei:listBibl/tei:biblStruct", TEI_NS):
        title_el = bibl.find(".//tei:title[@level='a']", TEI_NS)
        if title_el is None:
            title_el = bibl.find(".//tei:title", TEI_NS)
        title = title_el.text.strip() if title_el is not None and title_el.text else None
        if not title:
            continue

        authors = []
        for surname_el in bibl.findall(".//tei:author/tei:persName/tei:surname", TEI_NS):
            if surname_el.text:
                authors.append(surname_el.text.strip())

        date_el = bibl.find(".//tei:date", TEI_NS)
        year = ""
        if date_el is not None:
            when = date_el.get("when") or ""
            year = when[:4]

        doi_el = bibl.find(".//tei:idno[@type='DOI']", TEI_NS)
        doi = doi_el.text.strip() if doi_el is not None and doi_el.text else None

        entries.append({"title": title, "authors": authors, "year": year, "doi": doi})

    return entries
