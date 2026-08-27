"""
streamlit_app.py  —  pharmasafe-kg/phase5/streamlit_app.py
-----------------------------------------------------------
PharmaSafe-KG — Clinical Web Interface

HOW TO RUN:
    Terminal 1:  uvicorn phase3.app.main:app --reload --port 8000
    Terminal 2:  streamlit run phase5/streamlit_app.py

Then open: http://localhost:8501

DEPLOY FREE:
    Push to GitHub → go to share.streamlit.io → connect repo
    Set secrets:  API_BASE_URL = https://your-render-app.onrender.com
"""

import streamlit as st
import requests
import json
from pathlib import Path

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title = "PharmaSafe-KG",
    page_icon  = "💊",
    layout     = "wide",
    initial_sidebar_state = "collapsed",
)

# ── API URL ───────────────────────────────────────────────────────────────────
# Reads from Streamlit secrets (cloud) or falls back to localhost
try:
    API_BASE = st.secrets.get("API_BASE_URL", "http://localhost:8000")
except Exception:
    API_BASE = "http://localhost:8000"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CSS — clean clinical styling
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<style>
/* ── Global ─────────────────────────── */
[data-testid="stAppViewContainer"] { background: #0F1117; }
[data-testid="stHeader"]            { background: transparent; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

/* ── Header bar ─────────────────────── */
.pharma-header {
    background: linear-gradient(135deg, #1a1f35 0%, #0d1b2a 100%);
    border: 1px solid #2d3748;
    border-radius: 12px;
    padding: 1.2rem 1.8rem;
    margin-bottom: 1.5rem;
    display: flex; align-items: center; gap: 1rem;
}
.pharma-header h1 {
    color: #e2e8f0; font-size: 1.6rem;
    font-weight: 700; margin: 0;
}
.pharma-header p {
    color: #94a3b8; font-size: 0.85rem;
    margin: 0.2rem 0 0;
}

/* ── Severity cards ─────────────────── */
.card-major {
    background: linear-gradient(135deg, #2d1515 0%, #1a0d0d 100%);
    border: 1px solid #e53e3e; border-left: 4px solid #e53e3e;
    border-radius: 10px; padding: 1.1rem 1.3rem; margin: 0.6rem 0;
}
.card-moderate {
    background: linear-gradient(135deg, #2d2015 0%, #1a130d 100%);
    border: 1px solid #d97706; border-left: 4px solid #d97706;
    border-radius: 10px; padding: 1.1rem 1.3rem; margin: 0.6rem 0;
}
.card-minor {
    background: linear-gradient(135deg, #152d1b 0%, #0d1a10 100%);
    border: 1px solid #38a169; border-left: 4px solid #38a169;
    border-radius: 10px; padding: 1.1rem 1.3rem; margin: 0.6rem 0;
}
.card-safe {
    background: #13161f; border: 1px solid #2d3748;
    border-radius: 10px; padding: 0.8rem 1.1rem; margin: 0.4rem 0;
}

/* ── Badges ─────────────────────────── */
.badge-major    { background:#e53e3e; color:#fff; padding:3px 10px;
                  border-radius:20px; font-size:0.75rem; font-weight:700; }
.badge-moderate { background:#d97706; color:#fff; padding:3px 10px;
                  border-radius:20px; font-size:0.75rem; font-weight:700; }
.badge-minor    { background:#38a169; color:#fff; padding:3px 10px;
                  border-radius:20px; font-size:0.75rem; font-weight:700; }
.badge-safe     { background:#2d3748; color:#94a3b8; padding:3px 10px;
                  border-radius:20px; font-size:0.75rem; }

/* ── Drug pill chips ─────────────────── */
.drug-pill {
    display:inline-block; background:#1e293b; border:1px solid #3d4f6a;
    color:#93c5fd; padding:4px 12px; border-radius:20px;
    font-size:0.82rem; margin:2px 3px;
}

/* ── Mechanism text ─────────────────── */
.mechanism-text {
    color:#94a3b8; font-size:0.82rem; line-height:1.6;
    background:#0d1117; border-radius:6px; padding:0.7rem 0.9rem;
    margin-top:0.5rem; border: 1px solid #1e293b;
}

/* ── Ingredient tag ─────────────────── */
.ingredient-tag {
    background:#1e3a5f; color:#93c5fd; padding:2px 8px;
    border-radius:6px; font-size:0.78rem; font-family:monospace;
    margin: 0 3px;
}

/* ── Summary banner ─────────────────── */
.summary-banner {
    background:#1a1f35; border:1px solid #3d4f6a;
    border-radius:10px; padding:1rem 1.3rem; margin: 1rem 0;
    display:flex; gap:2rem; align-items:center;
}
.stat-item { text-align:center; }
.stat-num  { font-size:1.6rem; font-weight:700; color:#e2e8f0; }
.stat-lbl  { font-size:0.72rem; color:#64748b; text-transform:uppercase;
             letter-spacing:.05em; }

/* ── Info box ────────────────────────── */
.info-box {
    background:#0d1b2a; border:1px solid #1e3a5f;
    border-radius:8px; padding:0.7rem 1rem; margin:0.5rem 0;
    color:#64748b; font-size:0.8rem;
}
</style>
""", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Helper functions
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def api_check(drugs: list[str]) -> dict | None:
    try:
        r = requests.post(f"{API_BASE}/check", json={"drugs": drugs}, timeout=30)
        if r.status_code == 200:
            return r.json()
        else:
            st.error(f"API error {r.status_code}: {r.json().get('detail', 'Unknown error')}")
            return None
    except requests.exceptions.ConnectionError:
        st.error(
            "❌ Cannot connect to PharmaSafe-KG API.\n\n"
            f"Start the server:  `uvicorn phase3.app.main:app --reload --port 8000`"
        )
        return None
    except Exception as e:
        st.error(f"Request failed: {e}")
        return None


def api_search(query: str) -> list[str]:
    try:
        r = requests.get(f"{API_BASE}/search", params={"q": query, "limit": 15}, timeout=5)
        return r.json().get("results", []) if r.status_code == 200 else []
    except Exception:
        return []


def api_graph(drugs: list[str]) -> dict | None:
    try:
        r = requests.get(f"{API_BASE}/graph", params={"drugs": drugs}, timeout=15)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def render_severity_card(interaction: dict):
    sev  = interaction["severity"]
    ba   = interaction["brand_a"]
    bb   = interaction["brand_b"]
    ia   = interaction["ingredient_a"]
    ib   = interaction["ingredient_b"]
    mech = interaction["mechanism"]

    card_class  = {"MAJOR": "card-major", "MODERATE": "card-moderate", "MINOR": "card-minor"}.get(sev, "card-safe")
    badge_class = {"MAJOR": "badge-major", "MODERATE": "badge-moderate", "MINOR": "badge-minor"}.get(sev, "badge-safe")
    icon        = {"MAJOR": "🔴", "MODERATE": "🟡", "MINOR": "🟢"}.get(sev, "⚪")

    st.markdown(f"""
    <div class="{card_class}">
      <div style="display:flex; align-items:center; gap:0.7rem; margin-bottom:0.5rem;">
        <span class="{badge_class}">{icon} {sev}</span>
        <span style="color:#e2e8f0; font-weight:600; font-size:0.95rem;">
          {ba} &nbsp;↔&nbsp; {bb}
        </span>
      </div>
      <div style="color:#94a3b8; font-size:0.82rem; margin-bottom:0.5rem;">
        Active ingredients:
        <span class="ingredient-tag">{ia}</span> interacts with
        <span class="ingredient-tag">{ib}</span>
      </div>
      <div class="mechanism-text">{mech[:400]}{"..." if len(mech)>400 else ""}</div>
    </div>
    """, unsafe_allow_html=True)


def render_pyvis_graph(graph_data: dict):
    """Renders the interactive Pyvis graph inline in Streamlit."""
    try:
        from pyvis.network import Network
        import streamlit.components.v1 as components

        net = Network(height="480px", width="100%", bgcolor="#0F1117",
                      font_color="#e2e8f0", directed=False)
        net.set_options("""
        {
          "nodes": {"font": {"size": 13, "face": "Arial"}},
          "edges": {"font": {"size": 11, "color": "#94a3b8"}},
          "physics": {
            "forceAtlas2Based": {"gravitationalConstant": -50,
                                  "centralGravity": 0.01,
                                  "springLength": 120},
            "solver": "forceAtlas2Based",
            "stabilization": {"iterations": 100}
          }
        }
        """)

        for node in graph_data["nodes"]:
            shape = "dot" if node["type"] == "Drug" else "ellipse"
            net.add_node(
                node["id"],
                label=node["label"],
                color=node["color"],
                size=node["size"],
                shape=shape,
                title=f"Type: {node['type']}<br>Name: {node['label']}",
            )

        for edge in graph_data["edges"]:
            sev   = edge.get("severity", "")
            title = edge.get("title", edge.get("label", ""))
            net.add_edge(
                edge["from"], edge["to"],
                label=edge["label"],
                color=edge["color"],
                width=edge["width"],
                title=str(title)[:150] if title else "",
            )

        # Save to temp HTML and embed (Windows + Linux compatible)
        import tempfile, os
        tmp_dir  = tempfile.gettempdir()
        html_path = os.path.join(tmp_dir, "pharmasafe_graph.html")
        net.save_graph(html_path)
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        components.html(html_content, height=500)

    except ImportError:
        st.info("Install pyvis for interactive graph: `pip install pyvis`")
    except Exception as e:
        st.warning(f"Graph rendering error: {e}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN APP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    # ── Header ────────────────────────────────────────────────────
    st.markdown("""
    <div class="pharma-header">
      <div style="font-size:2rem;">💊</div>
      <div>
        <h1>PharmaSafe-KG</h1>
        <p>Explainable Knowledge Graph-Based Drug Interaction Detection for Indian Medicines</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Layout: Input column | Results column ─────────────────────
    col_input, col_results = st.columns([1, 2], gap="large")

    # ══════════════════════════════════════════════════════════════
    # LEFT COLUMN — Drug Input
    # ══════════════════════════════════════════════════════════════
    with col_input:
        st.markdown("### 🔍 Patient Medications")
        st.markdown(
            '<div class="info-box">Enter 2–10 Indian brand or generic drug names. '
            'The system checks all combinations automatically.</div>',
            unsafe_allow_html=True
        )

        # Text input for typing drug names
        drug_input = st.text_input(
            "Type a drug name",
            placeholder="e.g. Combiflam, Ecosprin, Dolo 650...",
            key="drug_input",
            label_visibility="collapsed",
        )

        # Autocomplete suggestions
        if drug_input and len(drug_input) >= 2:
            suggestions = api_search(drug_input)
            if suggestions:
                st.caption("Suggestions:")
                cols = st.columns(2)
                for i, s in enumerate(suggestions[:6]):
                    if cols[i % 2].button(s, key=f"sug_{s}", use_container_width=True):
                        if "selected_drugs" not in st.session_state:
                            st.session_state["selected_drugs"] = []
                        if s not in st.session_state["selected_drugs"]:
                            st.session_state["selected_drugs"].append(s)
                        st.rerun()

        # Manual add button
        if drug_input:
            if st.button("➕ Add drug", use_container_width=True, type="secondary"):
                if "selected_drugs" not in st.session_state:
                    st.session_state["selected_drugs"] = []
                name = drug_input.strip()
                if name and name not in st.session_state["selected_drugs"]:
                    st.session_state["selected_drugs"].append(name)
                    st.rerun()

        st.divider()

        # Show selected drugs as chips
        if "selected_drugs" not in st.session_state:
            st.session_state["selected_drugs"] = []

        selected = st.session_state["selected_drugs"]

        if selected:
            st.markdown("**Selected drugs:**")
            for drug in selected:
                c1, c2 = st.columns([3, 1])
                c1.markdown(f'<span class="drug-pill">💊 {drug}</span>', unsafe_allow_html=True)
                if c2.button("✕", key=f"remove_{drug}", help=f"Remove {drug}"):
                    st.session_state["selected_drugs"].remove(drug)
                    st.rerun()
            st.markdown(f"<br>", unsafe_allow_html=True)

        # Quick demo presets
        # NOTE: Use brand names that exist in az_medicine_india.csv
        # Generic names like "Warfarin" resolve directly via ALIASES in resolver.py
        st.markdown("**Quick demo:**")
        presets = {
            "Warfarin case":    ["warfarin", "Combiflam", "Pantop 40"],
            "Cardiac combo":    ["Atorva 10", "Ecosprin", "Metolar XR"],
            "Diabetes regimen": ["Metformin 500", "Glibenclamide", "Ecosprin"],
            "5-drug poly":      ["Combiflam", "Ecosprin", "Pantop 40", "Metformin 500", "Atorva 10"],
        }
        for label, drugs in presets.items():
            if st.button(f"▶ {label}", key=f"preset_{label}", use_container_width=True):
                st.session_state["selected_drugs"] = list(drugs)
                st.rerun()

        st.divider()

        # Check button
        check_disabled = len(selected) < 2
        if st.button(
            "🔍 Check Interactions",
            type="primary",
            use_container_width=True,
            disabled=check_disabled,
        ):
            st.session_state["check_result"] = None
            st.session_state["check_result"] = api_check(selected)

        if check_disabled and selected:
            st.caption("Add at least 2 drugs to check interactions.")
        elif not selected:
            st.caption("No drugs added yet.")

        # Clear button
        if selected:
            if st.button("🗑️ Clear all", use_container_width=True):
                st.session_state["selected_drugs"] = []
                st.session_state.pop("check_result", None)
                st.rerun()

    # ══════════════════════════════════════════════════════════════
    # RIGHT COLUMN — Results
    # ══════════════════════════════════════════════════════════════
    with col_results:
        result = st.session_state.get("check_result")

        if result is None:
            # Placeholder when no query run yet
            st.markdown("### 📋 Results")
            st.markdown("""
            <div style="background:#13161f; border:1px dashed #2d3748;
                        border-radius:12px; padding:2.5rem; text-align:center;
                        color:#475569; margin-top:1rem;">
              <div style="font-size:2.5rem; margin-bottom:0.8rem;">🔬</div>
              <div style="font-size:1rem; font-weight:500; color:#64748b;">
                Add drugs and click "Check Interactions"
              </div>
              <div style="font-size:0.82rem; margin-top:0.5rem;">
                Supports 2–10 drugs simultaneously.<br>
                Uses Indian brand names like Combiflam, Dolo 650, Ecosprin.
              </div>
            </div>
            """, unsafe_allow_html=True)
            return

        # ── Summary banner ─────────────────────────────────────────
        n_drugs    = result["total_drugs"]
        n_pairs    = result["pairs_checked"]
        n_found    = result["interactions_found"]
        n_safe     = result["safe_pairs"]
        summary    = result["summary"]

        danger_col = "#e53e3e" if n_found > 0 else "#38a169"
        st.markdown(f"""
        <div class="summary-banner">
          <div class="stat-item">
            <div class="stat-num" style="color:{danger_col}">{n_found}</div>
            <div class="stat-lbl">Interactions</div>
          </div>
          <div class="stat-item">
            <div class="stat-num">{n_safe}</div>
            <div class="stat-lbl">Safe pairs</div>
          </div>
          <div class="stat-item">
            <div class="stat-num">{n_drugs}</div>
            <div class="stat-lbl">Drugs</div>
          </div>
          <div class="stat-item">
            <div class="stat-num">{n_pairs}</div>
            <div class="stat-lbl">Pairs checked</div>
          </div>
          <div style="flex:1; color:#94a3b8; font-size:0.85rem;">{summary}</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Resolved drugs section ─────────────────────────────────
        with st.expander("🔗 How drugs were resolved to generics", expanded=False):
            for rd in result.get("resolved_drugs", []):
                m_type = rd["match_type"]
                icon   = "✅" if m_type == "exact" else ("🔄" if m_type == "fuzzy" else "❌")
                conf   = f" ({rd['confidence']}%)" if m_type == "fuzzy" else ""
                gens   = ", ".join(rd["generics"]) if rd["generics"] else "not resolved"
                st.markdown(
                    f"**{rd['input']}** → `{gens}` &nbsp; {icon} *{m_type}{conf}*"
                )

        # ── Interactions ───────────────────────────────────────────
        st.markdown("### ⚠️ Detected Interactions")
        interactions = result.get("interactions", [])

        if not interactions:
            st.markdown("""
            <div style="background:#0d1f14; border:1px solid #276749;
                        border-radius:10px; padding:1.2rem 1.5rem; text-align:center;">
              <span style="font-size:1.4rem;">✅</span>
              <span style="color:#48bb78; font-size:1rem; font-weight:600;
                           margin-left:0.5rem;">No interactions detected</span>
              <div style="color:#68d391; font-size:0.82rem; margin-top:0.4rem;">
                All drug combinations appear safe based on the Knowledge Graph.
              </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for interaction in interactions:
                render_severity_card(interaction)

        # ── Safe pairs ─────────────────────────────────────────────
        safe = result.get("safe_pairs_detail", [])
        if safe:
            with st.expander(f"✅ Safe combinations ({len(safe)})", expanded=False):
                for sp in safe:
                    st.markdown(
                        f'<div class="card-safe">'
                        f'<span class="badge-safe">✅ SAFE</span> &nbsp;'
                        f'<span style="color:#94a3b8; font-size:0.88rem;">'
                        f'{sp["brand_a"]} &nbsp;+&nbsp; {sp["brand_b"]}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

        # ── Interactive graph ──────────────────────────────────────
        st.markdown("### 🕸️ Drug Interaction Graph")
        st.caption("Blue = Brand drug · Green = Generic ingredient · "
                   "Red edge = Major · Orange = Moderate · Green = Minor")

        graph_data = api_graph(selected)
        if graph_data:
            render_pyvis_graph(graph_data)
        else:
            st.info("Graph data unavailable — check API connection.")


if __name__ == "__main__":
    main()
