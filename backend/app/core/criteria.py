# The rubric registry: each entry drives GET /api/criteria (so the frontend's
# rubric picker reflects this automatically), and `agent_instructions` becomes
# the system prompt for that rubric's dedicated worker agent (see agents.py).
# "needs_citation_tools" marks the one rubric whose agent is also given the
# reference-list/Semantic-Scholar tools.

RUBRICS = [
    {
        "key": "Originality",
        "synonyms": ["Novelty", "Originality and Novelty"],
        "desc": "Is the contribution new and clearly differentiated?",
        "needs_citation_tools": False,
        "agent_instructions": """
Evaluate the **Originality** of this paper: is the contribution new and clearly
differentiated from existing work?
- Is the problem formulation novel or does it offer a fresh perspective?
- Are the proposed methods, techniques, or algorithms meaningfully different from prior art?
- Does the paper introduce new concepts, frameworks, or theoretical insights?
- Are the claims of originality well-supported and not overstated?
Look at the title, abstract, introduction, and related work as needed.
""",
    },
    {
        "key": "Soundness",
        "synonyms": ["Technical Quality", "Scientific quality", "Design & Technical quality", "Technical soundness"],
        "desc": "Are methods appropriate and claims supported?",
        "needs_citation_tools": False,
        "agent_instructions": """
Evaluate the **Soundness** of this paper: are the methods appropriate and are
claims properly supported?
- Are the chosen methods appropriate for the research questions?
- Are experimental setups properly designed and controlled?
- Do the results actually support the claims made?
- Are there logical flaws, unsupported leaps, or unstated assumptions?
Look at the methodology, experimental setup, and results sections as needed.
""",
    },
    {
        "key": "Impact",
        "synonyms": ["Significance", "Relevance", "Scientific impact"],
        "desc": "Will this advance the field or enable new capabilities?",
        "needs_citation_tools": False,
        "agent_instructions": """
Evaluate the **Impact** of this paper: will it advance the field or enable new
capabilities?
- Does the work address an important problem or gap in the field?
- Are the results significant enough to influence future research or practice?
- Is the contribution substantial or merely incremental?
- Will practitioners or other researchers likely adopt or build upon this work?
Look at the introduction, results, and conclusion/discussion as needed.
""",
    },
    {
        "key": "Presentation",
        "synonyms": ["Clarity", "Quality of presentation"],
        "desc": "Is the paper well-written, organized, and easy to follow?",
        "needs_citation_tools": False,
        "agent_instructions": """
Evaluate the **Presentation** quality of this paper: is it well-written,
organized, and easy to follow?
- Is the writing clear, precise, and grammatically correct?
- Is the paper logically structured with good flow between sections?
- Are technical terms properly defined and consistently used?
- Does the abstract accurately reflect the paper's content?
Use the header list to judge overall structure, and check the abstract directly.
""",
    },
    {
        "key": "Positioning w.r.t Related Work",
        "synonyms": ["Meaningful Comparison"],
        "desc": "Is prior work covered fairly, with proper comparison?",
        "needs_citation_tools": False,
        "agent_instructions": """
Evaluate how this paper **positions itself with respect to related work**.
- Are relevant prior works adequately cited and discussed?
- Are the differences from prior work clearly explained?
- Are comparisons fair and accurate (not strawman arguments)?
- Are there obvious missing references or unfair characterizations?
Look at the introduction and related work section as needed.
""",
    },
    {
        "key": "Reference & Citation Quality",
        "synonyms": ["Citation Check", "Bibliography Quality"],
        "desc": "Are citations accurate, sufficient, and do the cited works actually exist?",
        "needs_citation_tools": True,
        "agent_instructions": """
Evaluate the **Reference & Citation Quality** of this paper.
- Use `list_references` to see the paper's parsed bibliography.
- Use `semantic_scholar_lookup` to verify a representative sample of ~5-10
  references (favor ones central to the paper's claims) actually exist in the
  literature and check their reported venue/year/citation count for plausibility.
  Do not look up every reference — sample enough to judge overall bibliography quality.
- Assess whether citation coverage looks adequate for the paper's claims (use
  `get_section` on the related work/introduction if useful) and whether the
  reference list appears well-formed and appropriately used.
Note any references you could not verify, but don't treat "not found on
Semantic Scholar" alone as proof a work doesn't exist (coverage gaps happen).
""",
    },
    {
        "key": "Reproducibility & Artifacts",
        "synonyms": ["Reproducibility", "Code/Data Availability"],
        "desc": "Is there enough detail to reproduce the work, and are artifacts available?",
        "needs_citation_tools": False,
        "agent_instructions": """
Evaluate the **Reproducibility & Artifacts** of this paper.
- Is there sufficient detail (hyperparameters, data preprocessing, training
  setup) to reproduce the reported results?
- Are code, data, and/or trained models made available, or is there a clear
  statement about their (non-)availability?
- Are datasets, baselines, and evaluation protocols clearly specified?
Look at the methodology/experimental setup section and any availability
statement as needed.
""",
    },
    {
        "key": "Ethical Considerations & Broader Impact",
        "synonyms": ["Ethics", "Broader Impact"],
        "desc": "Are ethical considerations and broader societal impact adequately addressed?",
        "needs_citation_tools": False,
        "agent_instructions": """
Evaluate the **Ethical Considerations & Broader Impact** of this paper.
- Does the paper address relevant ethical considerations (e.g. data consent,
  potential harms, dual-use risks) where applicable to its subject matter?
- Is the broader societal impact of the work discussed?
- If the paper's subject matter has no meaningful ethical dimension, say so
  plainly rather than inventing concerns.
Look at any ethics statement, broader impact, or discussion/conclusion section
as needed.
""",
    },
]

CRITERIA = RUBRICS  # backward-compatible alias used by the API layer

RUBRICS_BY_KEY = {r["key"]: r for r in RUBRICS}
