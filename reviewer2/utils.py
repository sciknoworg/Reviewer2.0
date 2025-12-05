from reviewer2.criteria import CRITERIA

def build_markdown_export(title: str, reviews: dict, avg: float, rec: str) -> str:
    lines = [f"# Review for: {title}", "", f"**Overall score (avg)**: {avg:.1f}/10",
             f"**Recommendation**: {rec}", "", "---", ""]
    for c in CRITERIA:
        k = c["key"]
        rv = reviews.get(k, {})
        lines.append(f"## {k}")
        if c["synonyms"]:
            lines.append(f"*Synonyms*: {', '.join(c['synonyms'])}")
        if c["desc"]:
            lines.append(f"*Description*: {c['desc']}")
        lines.append("")
        if rv.get("score") is not None:
            lines.append(f"**Score**: {rv['score']}/10")
        if rv.get("text"):
            lines.append(rv["text"])
        if rv.get("bullets"):
            lines.append("")
            lines.append("**Comments**")
            for b in rv["bullets"]:
                lines.append(f"- {b}")
        lines.append("")
    return "\n".join(lines)

