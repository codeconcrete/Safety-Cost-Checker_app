# -*- coding: utf-8 -*-
"""
건설업 안전관리비 물품 확인 앱
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
근거: 고용노동부고시 제2025-11호
      「건설업 산업안전보건관리비 계상 및 사용기준」
      (2025.02.12 시행)
"""

import streamlit as st
from safety_cost_data import (
    CATEGORIES,
    CATEGORY_LEGAL_DETAILS,
    ITEMS,
    PROHIBITED_ITEMS,
    CHANGES_2025_2026,
    CASES_AND_PRECEDENTS,
    search_items,
)


def render_legal_detail(legal_detail: dict) -> str:
    """법적 근거 상세 정보를 HTML로 렌더링합니다."""
    if not legal_detail:
        return ""
    parts = []
    if "상위법" in legal_detail:
        parts.append(f'📜 <strong>상위법:</strong> {legal_detail["상위법"]}')
    if "시행령" in legal_detail:
        parts.append(f'📑 <strong>시행령:</strong> {legal_detail["시행령"]}')
    if "고시" in legal_detail:
        parts.append(f'📋 <strong>고시:</strong> {legal_detail["고시"]}')
    if "관련조항" in legal_detail and legal_detail["관련조항"]:
        refs = "".join(f"<li>{r}</li>" for r in legal_detail["관련조항"])
        parts.append(f'📎 <strong>관련 조항:</strong><ul style="margin:0.2rem 0 0 1.2rem; padding:0;">{refs}</ul>')
    return "<br>".join(parts)

# ──────────────────────────────────────────────
# Page Config
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="건설업 안전관리비 물품 확인",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────
# Viewport Meta for Mobile
# ──────────────────────────────────────────────
st.markdown('<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">', unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Custom CSS — Premium Dark Theme
# ──────────────────────────────────────────────
st.markdown("""
<style>
/* ── Import Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700;900&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
}
.stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #1a1a3e 40%, #24243e 100%);
}

/* ── Hero Header ── */
.hero-header {
    text-align: center;
    padding: 2rem 1rem 1.5rem;
    background: linear-gradient(135deg, rgba(99,102,241,0.15) 0%, rgba(168,85,247,0.10) 100%);
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 2rem;
    backdrop-filter: blur(10px);
}
.hero-header h1 {
    font-size: 2.2rem;
    font-weight: 900;
    background: linear-gradient(135deg, #818cf8, #a78bfa, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    letter-spacing: -0.5px;
}
.hero-sub {
    color: #ffffff;
    font-size: 0.95rem;
    margin-top: 0.5rem;
    font-weight: 300;
}
.hero-badge {
    display: inline-block;
    background: rgba(99,102,241,0.25);
    color: #ffffff;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 500;
    margin-top: 0.7rem;
    border: 1px solid rgba(99,102,241,0.3);
}

/* ── Search Box Styling ── */
.search-container {
    max-width: 700px;
    margin: 0 auto 2rem;
}
.stTextInput > div > div > input,
.stTextInput input,
[data-testid="stTextInput"] input,
input[type="text"] {
    background: #1e1b4b !important;
    background-color: #1e1b4b !important;
    border: 2px solid rgba(99,102,241,0.3) !important;
    border-radius: 16px !important;
    padding: 16px 20px !important;
    font-size: 1.15rem !important;
    color: #e2e8f0 !important;
    font-family: 'Noto Sans KR', sans-serif !important;
    transition: all 0.3s ease !important;
}
.stTextInput > div > div > input:focus,
.stTextInput input:focus,
[data-testid="stTextInput"] input:focus {
    border-color: #818cf8 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.2) !important;
    background: #252262 !important;
    background-color: #252262 !important;
}
.stTextInput > div > div > input::placeholder,
.stTextInput input::placeholder,
[data-testid="stTextInput"] input::placeholder,
input::placeholder {
    color: #9ca3af !important;
    opacity: 1 !important;
}

/* ── Result Cards ── */
.result-card {
    background: rgba(255,255,255,0.04);
    border-radius: 16px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 1rem;
    border: 1px solid rgba(255,255,255,0.08);
    transition: all 0.3s ease;
    backdrop-filter: blur(5px);
}
.result-card:hover {
    background: rgba(255,255,255,0.07);
    border-color: rgba(255,255,255,0.15);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.3);
}
.result-card.allowed {
    border-left: 4px solid #34d399;
}
.result-card.conditional {
    border-left: 4px solid #fbbf24;
}
.result-card.prohibited {
    border-left: 4px solid #f87171;
}

.card-status {
    font-size: 0.75rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 8px;
    display: inline-block;
    margin-bottom: 0.5rem;
    letter-spacing: 0.5px;
    color: #ffffff !important;
}
.status-allowed {
    background: rgba(52,211,153,0.15);
    color: #ffffff !important;
}
.status-conditional {
    background: rgba(251,191,36,0.15);
    color: #ffffff !important;
}
.status-prohibited {
    background: rgba(248,113,113,0.15);
    color: #ffffff !important;
}

.card-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #ffffff !important;
    margin: 0.3rem 0;
}
.card-category {
    font-size: 0.85rem;
    color: #ffffff !important;
    font-weight: 500;
    margin-bottom: 0.4rem;
}
.card-note {
    font-size: 0.85rem;
    color: #ffffff !important;
    line-height: 1.6;
    margin-top: 0.3rem;
}
.card-legal {
    font-size: 0.75rem;
    color: #ffffff !important;
    margin-top: 0.5rem;
    padding-top: 0.5rem;
    border-top: 1px solid rgba(255,255,255,0.06);
}
.card-legal-detail {
    font-size: 0.78rem;
    color: #ffffff !important;
    margin-top: 0.6rem;
    padding: 0.8rem 1rem;
    background: rgba(99,102,241,0.06);
    border-radius: 10px;
    border: 1px solid rgba(99,102,241,0.12);
    line-height: 1.7;
}
.card-legal-detail ul {
    list-style-type: '→ ';
    font-size: 0.75rem;
    color: #ffffff !important;
}
.card-legal-detail li {
    margin-bottom: 2px;
    color: #ffffff !important;
}

/* ── Summary Stat Cards ── */
.stat-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
    flex-wrap: wrap;
}
.stat-card {
    flex: 1;
    min-width: 180px;
    background: rgba(255,255,255,0.04);
    border-radius: 14px;
    padding: 1.2rem;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.08);
}
.stat-number {
    font-size: 2rem;
    font-weight: 900;
    margin: 0;
}
.stat-number.green { color: #34d399; }
.stat-number.yellow { color: #fbbf24; }
.stat-number.red { color: #f87171; }
.stat-label {
    color: #ffffff !important;
    font-size: 0.8rem;
    margin-top: 0.3rem;
}

/* ── Section Headers ── */
.section-header {
    font-size: 1.3rem;
    font-weight: 700;
    color: #ffffff !important;
    margin: 1.5rem 0 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid rgba(99,102,241,0.3);
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* ── Empty State ── */
.empty-state {
    text-align: center;
    padding: 3rem 1rem;
    color: #ffffff !important;
}
.empty-state .icon {
    font-size: 3rem;
    margin-bottom: 1rem;
}
.empty-state p {
    font-size: 1rem;
    line-height: 1.8;
    color: #ffffff !important;
}

/* ── Category Browse Card ── */
.cat-card {
    background: rgba(255,255,255,0.04);
    border-radius: 14px;
    padding: 1.2rem;
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 0.8rem;
    transition: all 0.2s ease;
}
.cat-card:hover {
    background: rgba(255,255,255,0.07);
}
.cat-card-title {
    font-size: 1rem;
    font-weight: 600;
    color: #ffffff !important;
}
.cat-card-desc {
    font-size: 0.82rem;
    color: #ffffff !important;
    margin-top: 0.3rem;
    line-height: 1.5;
}

/* ── Changes Timeline ── */
.change-item {
    background: rgba(255,255,255,0.04);
    border-radius: 14px;
    padding: 1.2rem;
    margin-bottom: 0.8rem;
    border: 1px solid rgba(255,255,255,0.08);
    border-left: 3px solid #818cf8;
}
.change-year {
    display: inline-block;
    background: rgba(99,102,241,0.2);
    color: #ffffff !important;
    padding: 2px 10px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 600;
}
.change-title {
    font-size: 1rem;
    font-weight: 600;
    color: #ffffff !important;
    margin: 0.4rem 0;
}
.change-detail {
    font-size: 0.85rem;
    color: #ffffff !important;
    line-height: 1.6;
}

/* ── Case Card ── */
.case-card {
    background: rgba(255,255,255,0.04);
    border-radius: 14px;
    padding: 1.2rem;
    margin-bottom: 0.8rem;
    border: 1px solid rgba(255,255,255,0.08);
    border-left: 3px solid #f59e0b;
}
.case-type {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 600;
    color: #ffffff !important;
}
.case-type.판례 {
    background: rgba(248,113,113,0.15);
    color: #ffffff !important;
}
.case-type.적발사례 {
    background: rgba(251,191,36,0.15);
    color: #ffffff !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: rgba(255,255,255,0.03);
    border-radius: 14px;
    padding: 4px;
    border: 1px solid rgba(255,255,255,0.06);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    color: #ffffff;
    font-weight: 500;
    padding: 10px 20px;
    font-family: 'Noto Sans KR', sans-serif;
}
.stTabs [aria-selected="true"] {
    background: rgba(99,102,241,0.2) !important;
    color: #ffffff !important;
}
.stTabs [data-baseweb="tab-border"] {
    display: none;
}
.stTabs [data-baseweb="tab-highlight"] {
    display: none;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: rgba(255,255,255,0.04) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: #ffffff !important;
    font-family: 'Noto Sans KR', sans-serif !important;
}
.streamlit-expanderHeader:hover {
    background: rgba(99,102,241,0.15) !important;
    color: #ffffff !important;
}
/* Ensure expander content text is readable */
[data-testid="stExpander"] summary {
    color: #ffffff !important;
}
[data-testid="stExpander"] summary:hover {
    color: #ffffff !important;
}
[data-testid="stExpander"] summary span {
    color: inherit !important;
}
[data-testid="stExpander"] details[open] summary {
    background: rgba(99,102,241,0.12) !important;
    color: #ffffff !important;
}
[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
    background: rgba(15,12,41,0.95) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-top: none !important;
    border-radius: 0 0 12px 12px !important;
}

/* ── Divider ── */
hr {
    border-color: rgba(255,255,255,0.06) !important;
}

/* ── Footer ── */
.footer {
    text-align: center;
    padding: 2rem 1rem;
    color: #ffffff;
    font-size: 0.75rem;
    line-height: 1.8;
    border-top: 1px solid rgba(255,255,255,0.05);
    margin-top: 3rem;
}

/* ── Quick Suggestions ── */
.suggestions {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    justify-content: center;
    margin-top: 1rem;
}
.suggestion-chip {
    background: rgba(99,102,241,0.12);
    border: 1px solid rgba(99,102,241,0.25);
    color: #ffffff;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 0.82rem;
    cursor: pointer;
    transition: all 0.2s ease;
    text-decoration: none;
}
.suggestion-chip:hover {
    background: rgba(99,102,241,0.25);
    border-color: rgba(99,102,241,0.4);
}

/* ── Hide Streamlit branding ── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ── Force all Streamlit text widgets to be readable ── */
.stMarkdown p, .stMarkdown li, .stMarkdown span {
    color: #ffffff !important;
}
.stMarkdown div, .stMarkdown strong, .stMarkdown em {
    color: #ffffff !important;
}
[data-testid="stForm"] label,
[data-testid="stTextInput"] label {
    color: #ffffff !important;
}

/* ── Force white on ALL custom elements ── */
.result-card, .result-card *,
.stat-card, .stat-card *,
.change-item, .change-item *,
.case-card, .case-card *,
.cat-card, .cat-card *,
.hero-header, .hero-header *,
.footer, .footer *,
.empty-state, .empty-state * {
    color: #ffffff !important;
}
/* Keep stat numbers their original accent colors */
.stat-number.green { color: #34d399 !important; }
.stat-number.yellow { color: #fbbf24 !important; }
.stat-number.red { color: #f87171 !important; }
/* Keep hero h1 gradient text */
.hero-header h1 {
    -webkit-text-fill-color: transparent !important;
}

/* ══════════════════════════════════════════════════
   MOBILE RESPONSIVE STYLES
   ══════════════════════════════════════════════════ */

/* ── Viewport & Streamlit layout overrides ── */
.stApp > header { display: none !important; }
[data-testid="stAppViewContainer"] {
    padding: 0 !important;
}
.block-container {
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    max-width: 100% !important;
}

/* ── Mobile: screens up to 768px ── */
@media screen and (max-width: 768px) {
    /* Global padding */
    .block-container {
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        padding-top: 0.5rem !important;
    }

    /* Hero Header */
    .hero-header {
        padding: 1.2rem 0.8rem 1rem;
        border-radius: 14px;
        margin-bottom: 1.2rem;
    }
    .hero-header h1 {
        font-size: 1.4rem !important;
        letter-spacing: -0.3px;
    }
    .hero-sub {
        font-size: 0.8rem;
    }
    .hero-badge {
        font-size: 0.65rem;
        padding: 3px 10px;
    }

    /* Search Box */
    .search-container {
        max-width: 100% !important;
        margin: 0 0 1rem !important;
    }
    .stTextInput > div > div > input,
    .stTextInput input,
    [data-testid="stTextInput"] input,
    input[type="text"] {
        padding: 12px 14px !important;
        font-size: 1rem !important;
        border-radius: 12px !important;
    }

    /* Stat Cards — stack vertically */
    .stat-row {
        flex-direction: column;
        gap: 0.6rem;
        margin-bottom: 1.2rem;
    }
    .stat-card {
        min-width: unset;
        padding: 0.8rem;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        text-align: left;
    }
    .stat-number {
        font-size: 1.5rem;
        margin: 0;
        order: 2;
    }
    .stat-label {
        font-size: 0.8rem;
        margin-top: 0;
        order: 1;
    }

    /* Section Headers */
    .section-header {
        font-size: 1.05rem;
        margin: 1rem 0 0.7rem;
        padding-bottom: 0.4rem;
    }

    /* Result Cards */
    .result-card {
        padding: 0.9rem 1rem;
        border-radius: 12px;
        margin-bottom: 0.7rem;
    }
    .card-status {
        font-size: 0.68rem;
        padding: 2px 8px;
        border-radius: 6px;
    }
    .card-title {
        font-size: 0.95rem !important;
    }
    .card-category {
        font-size: 0.78rem;
    }
    .card-note {
        font-size: 0.78rem;
        line-height: 1.5;
    }
    .card-legal {
        font-size: 0.7rem;
    }
    .card-legal-detail {
        font-size: 0.72rem;
        padding: 0.6rem 0.8rem;
        border-radius: 8px;
    }
    .card-legal-detail ul {
        font-size: 0.68rem;
        padding-left: 1rem;
    }

    /* Category Browse Cards */
    .cat-card {
        padding: 0.9rem;
        border-radius: 10px;
    }
    .cat-card-title {
        font-size: 0.9rem;
    }
    .cat-card-desc {
        font-size: 0.75rem;
    }

    /* Change Timeline */
    .change-item {
        padding: 0.9rem;
        border-radius: 10px;
    }
    .change-year {
        font-size: 0.68rem;
        padding: 2px 8px;
    }
    .change-title {
        font-size: 0.88rem;
    }
    .change-detail {
        font-size: 0.78rem;
    }

    /* Case Cards */
    .case-card {
        padding: 0.9rem;
        border-radius: 10px;
    }
    .case-type {
        font-size: 0.65rem;
        padding: 2px 8px;
    }

    /* Tabs — compact for mobile */
    .stTabs [data-baseweb="tab-list"] {
        border-radius: 10px;
        padding: 3px;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 10px;
        font-size: 0.75rem;
        border-radius: 8px;
        white-space: nowrap;
    }

    /* Expander */
    .streamlit-expanderHeader {
        border-radius: 10px !important;
        font-size: 0.85rem !important;
        padding: 0.6rem 0.8rem !important;
    }

    /* Two-column layout collapse */
    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
    }
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        gap: 0.5rem !important;
    }

    /* Empty State */
    .empty-state {
        padding: 2rem 0.8rem;
    }
    .empty-state .icon {
        font-size: 2rem;
    }
    .empty-state p {
        font-size: 0.85rem;
    }

    /* Suggestion Chips */
    .suggestions {
        gap: 0.4rem;
    }
    .suggestion-chip {
        font-size: 0.72rem;
        padding: 5px 12px;
    }

    /* Footer */
    .footer {
        padding: 1.2rem 0.8rem;
        font-size: 0.65rem;
        margin-top: 2rem;
    }
}

/* ── Extra small screens (≤ 400px) ── */
@media screen and (max-width: 400px) {
    .hero-header h1 {
        font-size: 1.15rem !important;
    }
    .hero-sub {
        font-size: 0.72rem;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 6px 8px;
        font-size: 0.68rem;
    }
    .card-title {
        font-size: 0.88rem !important;
    }
    .section-header {
        font-size: 0.95rem;
    }
}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Header
# ──────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <h1>🏗️ 건설업 안전관리비 물품 확인</h1>
    <div class="hero-sub">구매하려는 물품이 산업안전보건관리비로 구입 가능한 물품인지 확인하세요</div>
    <div class="hero-badge">📋 고용노동부고시 제2025-11호 기준 (2025.02.12 시행)</div>
</div>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Tabs
# ──────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 물품 확인",
    "📋 항목별 조회",
    "⚖️ 법령·판례",
    "❌ 사용 불가 항목",
])


# ═══════════════════════════════════════════════
# TAB 1: 물품 검색
# ═══════════════════════════════════════════════
with tab1:
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    query = st.text_input(
        "물품명을 입력하세요",
        placeholder="예: 안전모, 소화기, CCTV, 프린터, 커피 ...",
        label_visibility="collapsed",
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # Search & display results
    if query:
        results = search_items(query)
        total_allowed = len(results["allowed"])
        total_conditional = len(results["conditional"])
        total_prohibited = len(results["prohibited"])
        total = total_allowed + total_conditional + total_prohibited

        if total == 0:
            st.markdown(f"""
            <div class="empty-state">
                <div class="icon">🔎</div>
                <p><strong>'{query}'</strong>에 대한 검색 결과가 없습니다.<br>
                다른 키워드로 검색하거나, <strong>항목별 조회</strong> 탭에서 직접 확인해 보세요.<br>
                <span style="color:#ffffff; font-size:0.82rem;">
                ※ 판단이 모호한 물품은 해당 지역 노동지청에 사전 질의하시기 바랍니다.</span></p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Summary stats
            st.markdown(f"""
            <div class="stat-row">
                <div class="stat-card">
                    <p class="stat-number green">{total_allowed}</p>
                    <p class="stat-label">✅ 사용 가능</p>
                </div>
                <div class="stat-card">
                    <p class="stat-number yellow">{total_conditional}</p>
                    <p class="stat-label">⚠️ 조건부 가능</p>
                </div>
                <div class="stat-card">
                    <p class="stat-number red">{total_prohibited}</p>
                    <p class="stat-label">❌ 사용 불가</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Allowed items
            if results["allowed"]:
                st.markdown('<div class="section-header">✅ 사용 가능 항목</div>', unsafe_allow_html=True)
                for item in results["allowed"]:
                    limit_html = f'<br>📊 <strong>한도:</strong> {item["limit"]}' if item.get("limit") else ""
                    legal_html = render_legal_detail(item.get("legal_detail", {}))
                    st.markdown(f"""
                    <div class="result-card allowed">
                        <span class="card-status status-allowed">✅ 사용 가능</span>
                        <div class="card-title">{item["name"]}</div>
                        <div class="card-category">📁 항목 {item["category_id"]}. {item["category_name"]}</div>
                        <div class="card-note">{item["note"]}{limit_html}</div>
                        <div class="card-legal-detail">{legal_html}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # Conditional items
            if results["conditional"]:
                st.markdown('<div class="section-header">⚠️ 조건부 사용 가능 항목</div>', unsafe_allow_html=True)
                for item in results["conditional"]:
                    limit_html = f'<br>📊 <strong>한도:</strong> {item["limit"]}' if item.get("limit") else ""
                    legal_html = render_legal_detail(item.get("legal_detail", {}))
                    st.markdown(f"""
                    <div class="result-card conditional">
                        <span class="card-status status-conditional">⚠️ 조건부</span>
                        <div class="card-title">{item["name"]}</div>
                        <div class="card-category">📁 항목 {item["category_id"]}. {item["category_name"]}</div>
                        <div class="card-note">{item["note"]}{limit_html}</div>
                        <div class="card-legal-detail">{legal_html}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # Prohibited items
            if results["prohibited"]:
                st.markdown('<div class="section-header">❌ 사용 불가 항목</div>', unsafe_allow_html=True)
                for item in results["prohibited"]:
                    legal_html = render_legal_detail(item.get("legal_detail", {}))
                    st.markdown(f"""
                    <div class="result-card prohibited">
                        <span class="card-status status-prohibited">❌ 사용 불가</span>
                        <div class="card-title">{item["name"]}</div>
                        <div class="card-note">🚫 사유: {item["reason"]}</div>
                        <div class="card-legal-detail">{legal_html}</div>
                    </div>
                    """, unsafe_allow_html=True)



# ═══════════════════════════════════════════════
# TAB 2: 항목별 조회
# ═══════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">📋 9대 사용항목별 물품 목록</div>', unsafe_allow_html=True)
    st.markdown("""
    <p style="color:#ffffff; font-size:0.88rem; margin-bottom:1.5rem;">
    고용노동부고시 제7조에 따른 산업안전보건관리비 사용항목입니다. 각 항목을 펼쳐 구매 가능 물품을 확인하세요.
    </p>
    """, unsafe_allow_html=True)

    for cat_id, cat_info in CATEGORIES.items():
        limit_text = f"  |  📊 한도: {cat_info['limit']}" if cat_info.get("limit") else ""
        with st.expander(f"**항목 {cat_id}. {cat_info['name']}**{limit_text}", expanded=False):
            legal_detail = CATEGORY_LEGAL_DETAILS.get(cat_id, {})
            legal_html = render_legal_detail(legal_detail)
            st.markdown(f"""
            <p style="color:#ffffff; font-size:0.85rem; margin-bottom:0.8rem;">
            {cat_info['description']}
            </p>
            <div class="card-legal-detail" style="margin-bottom:1rem;">{legal_html}</div>
            """, unsafe_allow_html=True)

            cat_items = [item for item in ITEMS if item["category"] == cat_id]
            if cat_items:
                for item in cat_items:
                    if item["status"] == "allowed":
                        status_cls = "allowed"
                        status_label = "✅ 사용 가능"
                        status_badge = "status-allowed"
                    else:
                        status_cls = "conditional"
                        status_label = "⚠️ 조건부"
                        status_badge = "status-conditional"

                    st.markdown(f"""
                    <div class="result-card {status_cls}" style="padding:0.9rem 1.2rem;">
                        <span class="card-status {status_badge}">{status_label}</span>
                        <span class="card-title" style="font-size:0.95rem; margin-left:0.5rem;">{item["name"]}</span>
                        <div class="card-note" style="margin-top:0.3rem;">{item["note"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <p style="color:#ffffff; font-size:0.85rem; text-align:center; padding:1rem;">
                해당 항목의 세부 물품은 별도 확인이 필요합니다.
                </p>
                """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# TAB 3: 법령·판례
# ═══════════════════════════════════════════════
with tab3:
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown('<div class="section-header">📌 2025-2026 주요 변경사항</div>', unsafe_allow_html=True)
        for change in CHANGES_2025_2026:
            st.markdown(f"""
            <div class="change-item">
                <span class="change-year">{change["year"]}</span>
                <div class="change-title">{change["title"]}</div>
                <div class="change-detail">{change["detail"]}</div>
                <div class="card-legal">⚖️ {change["legal_basis"]}</div>
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="section-header">⚖️ 관련 판례 및 주요 적발 사례</div>', unsafe_allow_html=True)
        for case in CASES_AND_PRECEDENTS:
            case_type_cls = "판례" if case["type"] == "판례" else "적발사례"
            st.markdown(f"""
            <div class="case-card">
                <span class="case-type {case_type_cls}">{case["type"]}</span>
                <div class="change-title" style="font-size:0.95rem;">{case["title"]}</div>
                <div class="change-detail">{case["summary"]}</div>
                <div class="card-note" style="margin-top:0.5rem;">
                    <strong>💡 핵심 포인트:</strong> {case["key_point"]}
                </div>
            </div>
            """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# TAB 4: 사용 불가 항목
# ═══════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">❌ 안전관리비 사용 불가 항목 목록</div>', unsafe_allow_html=True)
    st.markdown("""
    <p style="color:#ffffff; font-size:0.88rem; margin-bottom:1.5rem;">
    아래 항목들은 안전관리비로 구입·사용이 <strong>명확하게 불가</strong>한 것으로 판정된 물품입니다.<br>
    부적정 사용 시 과태료 부과, 반복 위반 시 공사 참여 제한 및 형사 고발이 가능합니다.
    </p>
    """, unsafe_allow_html=True)

    for item in PROHIBITED_ITEMS:
        st.markdown(f"""
        <div class="result-card prohibited">
            <span class="card-status status-prohibited">❌ 사용 불가</span>
            <div class="card-title">{item["name"]}</div>
            <div class="card-note">🚫 <strong>사유:</strong> {item["reason"]}</div>
        </div>
        """, unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Footer
# ──────────────────────────────────────────────
st.markdown("""
<div class="footer">
    <strong>⚠️ 면책 조항</strong><br>
    본 앱은 고용노동부고시 제2025-11호 「건설업 산업안전보건관리비 계상 및 사용기준」을 근거로 참고 목적으로 제공됩니다.<br>
    실제 사용 가능 여부의 최종 판단은 해당 지역 <strong>고용노동부 지방노동관서(노동지청)</strong>에 사전 질의하시기 바랍니다.<br>
    법령 개정 시 내용이 변경될 수 있으며, 본 앱의 정보에 따른 법적 책임은 사용자에게 있습니다.<br><br>
    <span style="color:#ffffff;">© 2025-2026 건설업 안전관리비 물품 확인 앱 | Built with Streamlit</span>
</div>
""", unsafe_allow_html=True)
