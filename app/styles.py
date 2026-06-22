def get_custom_css():
    return """
<style>
    /* ── Google Fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ── Root Variables ── */
    :root {
        --primary: #6366f1;
        --primary-light: #818cf8;
        --primary-dark: #4f46e5;
        --secondary: #06b6d4;
        --accent: #f59e0b;
        --success: #10b981;
        --danger: #ef4444;
        --bg-main: #020617;
        --bg-card: #0f172a;
        --bg-card2: #1e293b;
        --bg-glass: rgba(15, 23, 42, 0.8);
        --border: rgba(99, 102, 241, 0.2);
        --border-hover: rgba(99, 102, 241, 0.5);
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --text-muted: #475569;
        --gradient-1: linear-gradient(135deg, #6366f1 0%, #06b6d4 100%);
        --gradient-2: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%);
        --gradient-3: linear-gradient(135deg, #10b981 0%, #06b6d4 100%);
        --shadow: 0 4px 24px rgba(0,0,0,0.4);
        --shadow-glow: 0 0 40px rgba(99,102,241,0.15);
    }

    /* ── Global Reset ── */
    * { box-sizing: border-box; }

    .stApp {
        background: var(--bg-main) !important;
        font-family: 'Inter', sans-serif !important;
        color: var(--text-primary) !important;
    }

    /* ── Animated background gradient ── */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background:
            radial-gradient(ellipse at 20% 20%, rgba(99,102,241,0.08) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 80%, rgba(6,182,212,0.06) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 50%, rgba(245,158,11,0.03) 0%, transparent 70%);
        pointer-events: none;
        z-index: 0;
    }

    /* ── Hide Streamlit branding ── */
    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }

    /* ── Main content area ── */
    .main .block-container {
        padding: 1.5rem 2rem 2rem !important;
        max-width: 1400px !important;
    }

    /* ── HEADER ── */
    .documind-header {
        background: linear-gradient(135deg, rgba(99,102,241,0.15) 0%, rgba(6,182,212,0.1) 100%);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(20px);
    }

    .documind-header::before {
        content: '';
        position: absolute;
        top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: conic-gradient(from 0deg at 50% 50%,
            transparent 0deg,
            rgba(99,102,241,0.05) 60deg,
            transparent 120deg);
        animation: rotate 20s linear infinite;
    }

    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }

    .header-content {
        position: relative;
        z-index: 1;
        display: flex;
        align-items: center;
        gap: 1.5rem;
    }

    .header-icon {
        width: 64px; height: 64px;
        background: var(--gradient-1);
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        box-shadow: 0 8px 32px rgba(99,102,241,0.4);
        flex-shrink: 0;
    }

    .header-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: var(--gradient-1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        line-height: 1.2;
        letter-spacing: -0.5px;
    }

    .header-subtitle {
        color: var(--text-secondary);
        font-size: 0.95rem;
        margin: 0.3rem 0 0 0;
        font-weight: 400;
        letter-spacing: 0.3px;
    }

    .header-badges {
        display: flex;
        gap: 0.5rem;
        margin-top: 0.8rem;
        flex-wrap: wrap;
    }

    .badge {
        background: rgba(99,102,241,0.15);
        border: 1px solid rgba(99,102,241,0.3);
        color: var(--primary-light);
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 500;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    .badge-cyan {
        background: rgba(6,182,212,0.15);
        border-color: rgba(6,182,212,0.3);
        color: #22d3ee;
    }

    .badge-amber {
        background: rgba(245,158,11,0.15);
        border-color: rgba(245,158,11,0.3);
        color: #fbbf24;
    }

    .badge-green {
        background: rgba(16,185,129,0.15);
        border-color: rgba(16,185,129,0.3);
        color: #34d399;
    }

    /* ── SIDEBAR ── */
    section[data-testid="stSidebar"] {
        background: var(--bg-card) !important;
        border-right: 1px solid var(--border) !important;
    }

    section[data-testid="stSidebar"] > div {
        background: transparent !important;
        padding: 1.5rem 1rem !important;
    }

    .sidebar-brand {
        text-align: center;
        padding: 1rem 0 1.5rem 0;
        border-bottom: 1px solid var(--border);
        margin-bottom: 1.5rem;
    }

    .sidebar-logo {
        width: 56px; height: 56px;
        background: var(--gradient-1);
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.8rem;
        margin: 0 auto 0.8rem auto;
        box-shadow: 0 8px 24px rgba(99,102,241,0.35);
    }

    .sidebar-title {
        font-size: 1.2rem;
        font-weight: 700;
        background: var(--gradient-1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .sidebar-version {
        font-size: 0.7rem;
        color: var(--text-muted);
        margin-top: 0.2rem;
    }

    .sidebar-section-title {
        font-size: 0.7rem;
        font-weight: 600;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin: 1.2rem 0 0.6rem 0;
        padding: 0 0.5rem;
    }

    /* ── FILE UPLOADER ── */
    .stFileUploader {
        border: 2px dashed var(--border) !important;
        border-radius: 16px !important;
        background: rgba(99,102,241,0.03) !important;
        transition: all 0.3s ease !important;
        padding: 0.5rem !important;
    }

    .stFileUploader:hover {
        border-color: var(--border-hover) !important;
        background: rgba(99,102,241,0.06) !important;
        box-shadow: var(--shadow-glow) !important;
    }

    /* ── TABS ── */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--bg-card) !important;
        border-radius: 14px !important;
        padding: 0.4rem !important;
        border: 1px solid var(--border) !important;
        gap: 0.3rem !important;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 10px !important;
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
        padding: 0.6rem 1.2rem !important;
        transition: all 0.2s ease !important;
        border: none !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(99,102,241,0.1) !important;
        color: var(--text-primary) !important;
    }

    .stTabs [aria-selected="true"] {
        background: var(--gradient-1) !important;
        color: white !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(99,102,241,0.4) !important;
    }

    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1.5rem !important;
    }

    /* ── BUTTONS ── */
    .stButton > button {
        background: var(--gradient-1) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 0.6rem 1.4rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(99,102,241,0.3) !important;
        letter-spacing: 0.3px !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(99,102,241,0.45) !important;
        filter: brightness(1.1) !important;
    }

    .stButton > button:active {
        transform: translateY(0px) !important;
    }

    /* ── CHAT MESSAGES ── */
    .stChatMessage {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 16px !important;
        margin-bottom: 0.8rem !important;
        backdrop-filter: blur(10px) !important;
        transition: all 0.2s ease !important;
    }

    .stChatMessage:hover {
        border-color: var(--border-hover) !important;
        box-shadow: var(--shadow-glow) !important;
    }

    [data-testid="stChatMessageContent"] {
        color: var(--text-primary) !important;
        font-size: 0.92rem !important;
        line-height: 1.7 !important;
    }

    /* ── CHAT INPUT ── */
    .stChatInput {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 14px !important;
    }

    .stChatInput textarea {
        background: transparent !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
    }

    .stChatInput:focus-within {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
    }

    /* ── METRICS ── */
    [data-testid="stMetric"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 14px !important;
        padding: 1rem 1.2rem !important;
        transition: all 0.3s ease !important;
    }

    [data-testid="stMetric"]:hover {
        border-color: var(--border-hover) !important;
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-glow) !important;
    }

    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
        font-size: 0.78rem !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
    }

    [data-testid="stMetricValue"] {
        color: var(--text-primary) !important;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        background: var(--gradient-1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* ── EXPANDER ── */
    .streamlit-expanderHeader {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }

    .streamlit-expanderHeader:hover {
        border-color: var(--border-hover) !important;
        background: var(--bg-card2) !important;
    }

    .streamlit-expanderContent {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-top: none !important;
        border-radius: 0 0 12px 12px !important;
    }

    /* ── SELECT BOX ── */
    .stSelectbox > div > div {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        color: var(--text-primary) !important;
        transition: all 0.2s ease !important;
    }

    .stSelectbox > div > div:hover {
        border-color: var(--border-hover) !important;
    }

    /* ── TEXT INPUT ── */
    .stTextInput > div > div > input {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
    }

    /* ── DATAFRAME ── */
    .stDataFrame {
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }

    /* ── INFO / SUCCESS / ERROR boxes ── */
    .stInfo {
        background: rgba(6,182,212,0.08) !important;
        border: 1px solid rgba(6,182,212,0.25) !important;
        border-radius: 12px !important;
        color: #22d3ee !important;
    }

    .stSuccess {
        background: rgba(16,185,129,0.08) !important;
        border: 1px solid rgba(16,185,129,0.25) !important;
        border-radius: 12px !important;
        color: #34d399 !important;
    }

    .stWarning {
        background: rgba(245,158,11,0.08) !important;
        border: 1px solid rgba(245,158,11,0.25) !important;
        border-radius: 12px !important;
        color: #fbbf24 !important;
    }

    .stError {
        background: rgba(239,68,68,0.08) !important;
        border: 1px solid rgba(239,68,68,0.25) !important;
        border-radius: 12px !important;
        color: #f87171 !important;
    }

    /* ── DIVIDER ── */
    hr {
        border: none !important;
        border-top: 1px solid var(--border) !important;
        margin: 1rem 0 !important;
    }

    /* ── CUSTOM CARDS ── */
    .doc-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.6rem;
        display: flex;
        align-items: center;
        gap: 0.8rem;
        transition: all 0.2s ease;
    }

    .doc-card:hover {
        border-color: var(--border-hover);
        background: var(--bg-card2);
        transform: translateX(4px);
        box-shadow: var(--shadow-glow);
    }

    .doc-icon {
        width: 36px; height: 36px;
        background: rgba(99,102,241,0.15);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        flex-shrink: 0;
    }

    .doc-name {
        font-size: 0.85rem;
        font-weight: 500;
        color: var(--text-primary);
        flex: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    /* ── STAT CARD ── */
    .stat-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1.2rem;
        text-align: center;
        transition: all 0.3s ease;
    }

    .stat-card:hover {
        border-color: var(--border-hover);
        box-shadow: var(--shadow-glow);
        transform: translateY(-3px);
    }

    .stat-number {
        font-size: 2rem;
        font-weight: 800;
        background: var(--gradient-1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.2;
    }

    .stat-label {
        font-size: 0.75rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-weight: 500;
        margin-top: 0.3rem;
    }

    /* ── CONFIDENCE BADGES ── */
    .conf-high {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(16,185,129,0.15);
        border: 1px solid rgba(16,185,129,0.3);
        color: #34d399;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    .conf-medium {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(245,158,11,0.15);
        border: 1px solid rgba(245,158,11,0.3);
        color: #fbbf24;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    .conf-low {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(239,68,68,0.15);
        border: 1px solid rgba(239,68,68,0.3);
        color: #f87171;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    /* ── SCROLLBAR ── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg-main); }
    ::-webkit-scrollbar-thumb {
        background: var(--border-hover);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover { background: var(--primary); }

    /* ── SPINNER ── */
    .stSpinner > div {
        border-top-color: var(--primary) !important;
    }

    /* ── TOOLTIP ── */
    .stTooltipIcon { color: var(--text-muted) !important; }

    /* ── CODE BLOCKS ── */
    code {
        background: var(--bg-card2) !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
        color: var(--primary-light) !important;
        font-family: 'JetBrains Mono', monospace !important;
        padding: 0.1rem 0.4rem !important;
    }

    /* ── PROGRESS BAR ── */
    .stProgress > div > div {
        background: var(--gradient-1) !important;
        border-radius: 4px !important;
    }

    /* ── SIDEBAR METRICS ── */
    .sidebar-stat {
        background: rgba(99,102,241,0.08);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 0.8rem 1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-top: 0.5rem;
    }

    .sidebar-stat-label {
        font-size: 0.78rem;
        color: var(--text-secondary);
        font-weight: 500;
    }

    .sidebar-stat-value {
        font-size: 1.1rem;
        font-weight: 700;
        background: var(--gradient-1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* ── AGENT REASONING BOX ── */
    .reasoning-box {
        background: rgba(245,158,11,0.05);
        border: 1px solid rgba(245,158,11,0.2);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
    }

    .reasoning-title {
        font-size: 0.78rem;
        font-weight: 600;
        color: #fbbf24;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 0.5rem;
    }

    /* ── SOURCE CHIP ── */
    .source-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        background: rgba(99,102,241,0.12);
        border: 1px solid rgba(99,102,241,0.25);
        color: var(--primary-light);
        padding: 0.25rem 0.7rem;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 500;
        margin: 0.2rem;
    }

    /* ── PULSE ANIMATION for loading ── */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    .pulse { animation: pulse 2s infinite; }

    /* ── FADE IN ── */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .fade-in { animation: fadeIn 0.4s ease forwards; }

</style>
"""