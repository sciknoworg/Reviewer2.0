import json
import streamlit as st
from UI import config as ui_config
from UI import util

import reviewer2 as REVIEWER2

sidebar_image_rounded = util.make_circle(ui_config.LOGO_PATH)
# ---------------------------
# Page setup
# ---------------------------
st.set_page_config(
    page_title="AI Reviewer – Prototype",
    page_icon=ui_config.LOGO_PATH,
    layout="wide",
)

# ---- Custom styles
st.markdown(ui_config.CUSTOM_STYLES, unsafe_allow_html=True)

# ---------------------------
# Sidebar
# ---------------------------
with st.sidebar:
    st.markdown(f"""
        <div style="text-align:center;">
            <img src="data:image/png;base64,{sidebar_image_rounded}" style="width:120px; height:120px;" />
            <p style="font-size:20px; font-weight:bold; margin-top:5px;">Reviewer 2.0</p>
            <p style="font-size:14px;  margin-top:5px;">The AI becomes the ultimate “Reviewer 2” (automated nitpicker).</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**How it works:**")
    st.write(
        "1. Upload a PDF paper.\n"
        "2. Click **Generate review**.\n"
        "3. Switch across **tabs** to view rubric-wise feedback.\n"
        "4. Download the review as **Markdown** or **JSON**."
    )
    st.markdown("---")
    st.markdown("**Settings**")
    show_scores = st.toggle("Show Rubrics (1–10)", value=True)
    show_bullets = st.toggle("Show bullet notes", value=True)

# ---------------------------
# Main content
# ---------------------------
st.markdown("<span class='badge'>Upload your paper (PDF)</span>", unsafe_allow_html=True)
uploaded = st.file_uploader("", type=["pdf", "json"])

if "reviews" not in st.session_state:
    st.session_state.reviews = None
if "paper_title" not in st.session_state:
    st.session_state.paper_title = None
if "paper_abstract" not in st.session_state:
    st.session_state.paper_abstract = None
    
colA, colB = st.columns([1,1])

with colA:
    disabled = uploaded is None
    gen = st.button("🚀 Generate Review", disabled=disabled, use_container_width=True)
with colB:
    reset = st.button("♻️ Reset", use_container_width=True)

if reset:
    st.session_state.reviews = None
    st.session_state.paper_title = None
    st.session_state.paper_abstract = None

if gen and uploaded is not None:
    file_bytes = uploaded.getvalue()
    ai_reviews = REVIEWER2.review(file_bytes, uploaded.name) # Build reviews
    st.session_state.paper_abstract = ai_reviews['abstract']
    st.session_state.paper_title = ai_reviews['title']
    st.session_state.reviews = ai_reviews['reviews']

# Header card
# st.markdown("")
with st.container():
    if st.session_state.paper_title:
        st.markdown("---")
        st.markdown("<div>", unsafe_allow_html=True)
        st.markdown("<span class='badge'>You have uploaded the paper with following title and abstract</span>", unsafe_allow_html=True)
        st.subheader(st.session_state.paper_title)
        st.write(st.session_state.paper_abstract)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        pass

st.markdown("---")

if st.session_state.reviews:
    # Overall summary row
    scores = [v["score"] for v in st.session_state.reviews.values() if "score" in v]
    avg = sum(scores) / len(scores) if scores else 0.0
    rec = REVIEWER2.overall_recommendation(avg)
    st.markdown("<span class='badge'>Overall Recommendation</span>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Average Rubrics:", f"{avg:.1f} / 10")
    with c2:
        st.metric("Recommendation:", rec)
    st.markdown("---")
    st.markdown("<span class='badge'>Justification Per Rubrics</span>", unsafe_allow_html=True)

    # Inject CSS to make tabs scroll horizontally instead of hiding
    st.markdown(ui_config.SCROLLABLE_TABS_STYLES, unsafe_allow_html=True)

    # Tabs per Rubrics
    tabs = st.tabs([c["key"] for c in REVIEWER2.CRITERIA])
    for i, c in enumerate(REVIEWER2.CRITERIA):
        with tabs[i]:
            rv = st.session_state.reviews.get(c["key"], {})
            st.markdown(f"### {c['key']}")
            if c["synonyms"]:
                st.caption("Synonyms: " + ", ".join(c["synonyms"]))
            if c["desc"]:
                st.markdown(f"<span class='muted'>{c['desc']}</span>", unsafe_allow_html=True)
            st.markdown("")
            if show_scores and rv.get("score") is not None:
                st.metric("Score", f"{rv['score']} / 10")
            if rv.get("text"):
                st.write(rv["text"])
            if show_bullets and rv.get("bullets"):
                st.write("**Comments:**")
                for b in rv["bullets"]:
                    st.write(f"- {b}")

    # Export row
    st.markdown("---")
    md = REVIEWER2.build_markdown_export(st.session_state.paper_title or "Unknown Title", st.session_state.reviews, avg, rec)
    json_blob = json.dumps({"title": st.session_state.paper_title,
                            "abstract": st.session_state.paper_abstract,
                            "average_score": avg, "recommendation": rec,
                            "rubrics": st.session_state.reviews}, indent=1)
    st.markdown("<span class='badge'>Download the Reviews</span>", unsafe_allow_html=True)
    colx, coly = st.columns([1,1])
    with colx:
        st.download_button("⬇️ Download Markdown", data=md.encode("utf-8"),
                           file_name="review.md", mime="text/markdown",
                           use_container_width=True)
    with coly:
        st.download_button("⬇️ Download JSON", data=json_blob.encode("utf-8"), 
                           file_name="review.json", mime="application/json",
                           use_container_width=True)
else:
    st.info("Upload a PDF and click **Generate review** to see the per-rubrics reviews.")
