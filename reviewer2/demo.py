import io
import random
from reviewer2.criteria import CRITERIA

try:
    from PyPDF2 import PdfReader
    PDF_OK = True
except Exception:
    PDF_OK = False

RECOMMENDATIONS = [
    "Strong Accept", "Accept", "Weak Accept", "Borderline", "Weak Reject", "Reject"
]

DUMMY_SENTENCES = [
    "The problem statement is well-motivated and grounded in current literature.",
    "However, the empirical evidence is not entirely conclusive due to limited baselines.",
    "The methodology is clearly described with sensible assumptions.",
    "Ablation analyses shed light on which components matter most, though more seeds would strengthen claims.",
    "The paper positions itself among recent work but could broaden comparisons to adjacent subfields.",
    "Results are promising and suggest potential impact on practical deployments.",
    "Presentation quality is high; figures and tables are easy to read.",
    "Reproducibility would benefit from releasing training scripts and exact preprocessing steps.",
    "Citations mostly cover key papers, yet a few recent preprints are missing.",
    "The work would be stronger with a deeper error analysis and failure cases.",
    "Compute and efficiency reporting are adequate but could be more explicit about hardware and wall-clock time.",
    "The contribution is incremental but well-executed.",
    "Given the scope, the limitations are reasonably acknowledged."
]

# ---------------------------
# Helpers
# ---------------------------


def seeded_rng_from_bytes(b: bytes) -> random.Random:
    seed = int.from_bytes(b[:8], byteorder="little", signed=False) if b else random.randrange(1<<30)
    rng = random.Random(seed)
    return rng

def generate_dummy_review(rng: random.Random, criterion_key: str) -> dict:
    # Create a random short paragraph 2-4 sentences
    n_sent = rng.randint(2, 4)
    sentences = rng.sample(DUMMY_SENTENCES, k=n_sent)
    text = " ".join(sentences)
    score = rng.randint(1, 10)  # 1–10 scale for a bit more resolution
    # Two bullets
    bullets = rng.sample(DUMMY_SENTENCES, k=2)
    return {"text": text, "score": score, "bullets": bullets}

def overall_recommendation(avg_score: float) -> str:
    # Map 1–10 avg to recommendation label
    if avg_score >= 8.5:
        return "Strong Accept"
    if avg_score >= 7.5:
        return "Accept"
    if avg_score >= 6.5:
        return "Weak Accept"
    if avg_score >= 5.5:
        return "Borderline"
    if avg_score >= 4.5:
        return "Weak Reject"
    return "Reject"

from reviewer2.agent import paper_tool, paper_sectioning_tool, extract_section_tool

def review(file_bytes, filename):
    # Seed RNG so results are stable per upload
    rng = seeded_rng_from_bytes(file_bytes)
    print("*****************************")
    # paper = paper_tool(file_bytes, filename)
    paper = paper_tool.run({"file_bytes": file_bytes, "filename": filename})
    sections = paper_sectioning_tool.run({"md": paper})
    
    print(sections['headers'])
    print("*****************************")
    title = extract_section_tool.run({"headers": sections['headers'], "sections": sections["sections"], "section":"paper title"})
    abstract = extract_section_tool.run({"headers": sections['headers'], "sections": sections["sections"], "section":"paper abstract"})

    # Build reviews
    reviews = {}
    for c in CRITERIA:
        reviews[c["key"]] = generate_dummy_review(rng, c["key"])
    return {"title": title, "abstract": abstract, "reviews": reviews}


    