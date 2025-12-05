import os

LOGO_PATH = os.path.join(os.path.dirname(__file__), 'images', 'logo.png')

CUSTOM_STYLES = """
<style>
    /* Global tweaks */
    .main > div { padding-top: 1.2rem; }
    .uploadedFile { max-width: 540px !important; }

    /* Tabs: make them prominent at the top */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.25rem;
        border-bottom: 1px solid rgba(49,51,63,0.2);
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        padding: 8px 16px;
        border-radius: 10px 10px 0 0;
        background: rgba(49,51,63,0.03);
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background: var(--primary-color, #6c47ff);
        color: white;
    }

    /* Badge */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: .5rem;
        padding: .25rem .6rem;
        border-radius: 999px;
        background: rgba(108,71,255,.1);
        color: #5436d6;
        font-weight: 600;
        font-size: 0.85rem;
    }

    /* Card */
    .card {
        border: 1px solid rgba(49,51,63,0.15);
        border-radius: 14px;
        padding: 0.1rem 1.1rem;
        background: rgba(255,255,255,0.6);
    }

    /* Tiny muted text */
    .muted {
        color: rgba(49,51,63,0.8);
        font-size: 0.9rem;
    }
    </style>
"""

SCROLLABLE_TABS_STYLES = """
<style>
/* Force tabs to always show in a scrollable row */
.stTabs [role="tablist"] {
    flex-wrap: nowrap !important;
    overflow-x: auto !important;
    scrollbar-width: thin;
}
.stTabs [role="tab"] {
    flex: 0 0 auto !important;  /* Prevent shrinking */
    white-space: nowrap !important;
}
</style>
"""