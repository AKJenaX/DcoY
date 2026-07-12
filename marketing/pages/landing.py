"""Premium public marketing experience for DcoY."""

import streamlit as st

from marketing.sections.marketing_sections import (
    get_marketing_nav_items,
    get_platform_cards,
    get_trust_stats,
    get_quotes,
)


def render_marketing_page():
    """Render a full-screen, cinematic enterprise marketing experience."""
    st.set_page_config(page_title="DcoY | AI-native SOC Platform", page_icon="🛡️", layout="wide")

    st.markdown(
        """
        <style>
        html { scroll-behavior: smooth; }
        .marketing-shell { margin: -1.5rem -2rem 0; padding: 0 2rem 3rem; background:
            radial-gradient(circle at top left, rgba(59,130,246,0.18), transparent 24%),
            radial-gradient(circle at 80% 10%, rgba(34,211,238,0.15), transparent 20%),
            linear-gradient(180deg, rgba(11,18,32,0.95), rgba(9,14,24,1));
        }
        .marketing-nav {
            position: sticky; top: 0; z-index: 20; display: flex; flex-wrap: wrap; gap: 0.6rem; align-items: center;
            padding: 1rem 0 1.25rem; backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
        }
        .marketing-nav a {
            color: var(--text-secondary); text-decoration: none; font-size: 0.82rem; font-weight: 600; letter-spacing: 0.08em;
            text-transform: uppercase; padding: 0.5rem 0.8rem; border-radius: 999px; border: 1px solid var(--border-color);
            background: rgba(255,255,255,0.04);
        }
        .marketing-nav a:hover { color: var(--text-primary); border-color: rgba(59,130,246,0.3); }
        .marketing-section { min-height: 100vh; padding: 3rem 0; display: flex; align-items: center; }
        .section-card {
            border: 1px solid var(--border-color); border-radius: 28px; padding: 1.4rem; background: rgba(17,24,39,0.82);
            box-shadow: 0 20px 55px rgba(0,0,0,0.25); backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px);
        }
        .hero-visual {
            position: relative; min-height: 500px; border-radius: 24px; border: 1px solid var(--border-color);
            background: linear-gradient(135deg, rgba(59,130,246,0.16), rgba(34,211,238,0.08)); padding: 1rem;
            overflow: hidden;
        }
        .hero-visual::before {
            content: ""; position: absolute; inset: 0; background: radial-gradient(circle at top right, rgba(255,255,255,0.12), transparent 30%);
            animation: drift 7s ease-in-out infinite alternate;
        }
        .hero-float { animation: lift 5s ease-in-out infinite; }
        .hero-float.delay { animation-delay: 1s; }
        .hero-float.slower { animation-duration: 7s; }
        .metric-pill { display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.4rem 0.7rem; border-radius: 999px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-secondary); border: 1px solid var(--border-color); background: rgba(255,255,255,0.05); }
        .hero-kicker { color: var(--secondary); font-size: 0.75rem; font-weight: 700; letter-spacing: 0.18em; text-transform: uppercase; }
        .headline { font-size: clamp(2.55rem, 5vw, 4.6rem); line-height: 0.95; letter-spacing: -0.03em; margin: 0.45rem 0 0.8rem; color: var(--text-primary); }
        .subcopy { font-size: 1.04rem; color: var(--text-secondary); line-height: 1.7; max-width: 720px; }
        .cta-link { display: inline-flex; align-items: center; justify-content: center; text-decoration: none; padding: 0.75rem 1rem; border-radius: 999px; font-weight: 700; margin-right: 0.6rem; }
        .cta-primary { background: linear-gradient(90deg, var(--primary), var(--secondary)); color: white; }
        .cta-secondary { color: var(--text-primary); border: 1px solid var(--border-color); background: rgba(255,255,255,0.05); }
        .bento-card { border: 1px solid var(--border-color); border-radius: 20px; padding: 1rem; background: rgba(255,255,255,0.03); transition: transform 0.25s ease, border-color 0.25s ease; min-height: 120px; }
        .bento-card:hover { transform: translateY(-4px); border-color: rgba(59,130,246,0.35); }
        .flow-node { border: 1px solid var(--border-color); border-radius: 16px; padding: 0.85rem; background: rgba(255,255,255,0.04); }
        .terminal-stream { padding: 0.9rem; border-radius: 16px; background: rgba(5,11,20,0.82); border: 1px solid rgba(59,130,246,0.25); font-family: "Courier New", Courier, monospace; font-size: 0.8rem; color: #cbd5e1; line-height: 1.65; }
        .cursor { animation: blink 1s steps(1) infinite; color: var(--secondary); }
        .tiny-label { font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.12em; color: var(--text-secondary); }
        .big-number { font-size: 1.6rem; font-weight: 800; color: var(--text-primary); }
        .soft-divider { border-top: 1px solid var(--border-color); margin: 1rem 0; }
        @keyframes lift { 0%,100% { transform: translateY(0px); } 50% { transform: translateY(-8px); } }
        @keyframes drift { from { transform: translate3d(-3%, -2%, 0); } to { transform: translate3d(3%, 2%, 0); } }
        @keyframes blink { 50% { opacity: 0; } }
        @media (max-width: 900px) { .marketing-section { min-height: auto; padding: 2.2rem 0; } .hero-visual { min-height: 380px; margin-top: 1rem; } }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="marketing-shell">', unsafe_allow_html=True)

    nav_items = get_marketing_nav_items()
    nav_html = "".join([f'<a href="{item["href"]}">{item["label"]}</a>' for item in nav_items])
    st.markdown(f'<div class="marketing-nav">{nav_html}</div>', unsafe_allow_html=True)

    st.markdown('<section id="landing" class="marketing-section">', unsafe_allow_html=True)
    left, right = st.columns([1.15, 0.95], gap="large")
    with left:
        st.markdown('<div class="hero-kicker">AI-native Security Operations</div>', unsafe_allow_html=True)
        st.markdown('<h1 class="headline">The premium AI SOC platform that turns signal into decisive action.</h1>', unsafe_allow_html=True)
        st.markdown('<p class="subcopy">DcoY unifies threat intelligence, detection engineering, threat hunting, investigations, and executive reporting into one cinematic cognitive workflow for modern enterprise defenders.</p>', unsafe_allow_html=True)
        st.markdown('<div style="margin-top: 1rem;">', unsafe_allow_html=True)
        st.markdown('<a class="cta-link cta-primary" href="#contact">Request Demo</a>', unsafe_allow_html=True)
        st.markdown('<a class="cta-link cta-secondary" href="#platform">Explore Platform</a>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div style="margin-top: 1.15rem; display:flex; flex-wrap:wrap; gap:0.6rem;">', unsafe_allow_html=True)
        for chip in ["SOC teams move 3x faster", "99.99% platform availability", "Evidence-first AI reasoning"]:
            st.markdown(f'<span class="metric-pill">{chip}</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="hero-visual section-card hero-float">', unsafe_allow_html=True)
        st.markdown('<div class="tiny-label">Live SOC telemetry</div>', unsafe_allow_html=True)
        st.markdown('<div class="big-number" style="margin-top:0.25rem;">12 active incidents • 94% confidence</div>', unsafe_allow_html=True)
        st.markdown('<div class="soft-divider"></div>', unsafe_allow_html=True)
        top_row, bottom_row = st.columns(2)
        with top_row:
            st.markdown('<div class="bento-card hero-float delay">', unsafe_allow_html=True)
            st.markdown('<div class="tiny-label">Threat graph</div>', unsafe_allow_html=True)
            st.markdown('<div class="big-number">4 linked IOCs</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with bottom_row:
            st.markdown('<div class="bento-card hero-float slower">', unsafe_allow_html=True)
            st.markdown('<div class="tiny-label">MITRE coverage</div>', unsafe_allow_html=True)
            st.markdown('<div class="big-number">T1055 · T1110</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="bento-card" style="margin-top:0.8rem;">', unsafe_allow_html=True)
        st.markdown('<div class="tiny-label">AI reasoning</div>', unsafe_allow_html=True)
        st.markdown('<div class="terminal-stream">Reasoning: adversary pivoted from credential spray to persistence.<br/>Evidence: 6 correlated alerts, 2 compromised identities.<br/>Recommendation: isolate host and block lateral movement<span class="cursor">|</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</section>', unsafe_allow_html=True)

    st.markdown('<section id="trust" class="marketing-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="tiny-label">Enterprise trust</div>', unsafe_allow_html=True)
    st.markdown('<h2 class="headline" style="font-size: clamp(1.8rem, 3vw, 2.6rem);">Trusted by security teams that need clarity, speed, and control.</h2>', unsafe_allow_html=True)
    stats = get_trust_stats()
    stat_cols = st.columns(4)
    for idx, stat in enumerate(stats):
        with stat_cols[idx]:
            st.markdown(f'<div class="bento-card" style="margin-bottom:0.8rem;"><div class="big-number">{stat["value"]}</div><div class="tiny-label" style="margin-top:0.35rem;">{stat["label"]}</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="soft-divider"></div>', unsafe_allow_html=True)
    customer_names = ["Apex Bank", "Northwind Health", "Horizon Energy", "Novacore"]
    chips = "".join([f'<span class="metric-pill">{name}</span>' for name in customer_names])
    st.markdown(f'<div style="display:flex; flex-wrap:wrap; gap:0.6rem;">{chips}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</section>', unsafe_allow_html=True)

    st.markdown('<section id="platform" class="marketing-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="tiny-label">Platform overview</div>', unsafe_allow_html=True)
    st.markdown('<h2 class="headline" style="font-size: clamp(1.8rem, 3vw, 2.6rem);">A premium operating system for the modern SOC.</h2>', unsafe_allow_html=True)
    cards = get_platform_cards()
    cols = st.columns(4)
    for idx, card in enumerate(cards):
        with cols[idx % 4]:
            st.markdown(f'<div class="bento-card" style="margin-bottom:0.8rem;"><div class="tiny-label">{card["badge"]}</div><div style="font-size: 1rem; font-weight: 700; color: var(--text-primary); margin: 0.4rem 0 0.25rem;">{card["title"]}</div><div style="font-size: 0.86rem; color: var(--text-secondary);">{card["description"]}</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</section>', unsafe_allow_html=True)

    st.markdown('<section id="analyst" class="marketing-section">', unsafe_allow_html=True)
    left, right = st.columns([1.1, 0.9], gap="large")
    with left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="tiny-label">AI Security Analyst</div>', unsafe_allow_html=True)
        st.markdown('<h2 class="headline" style="font-size: clamp(1.8rem, 3vw, 2.6rem);">Conversational intelligence for every investigation.</h2>', unsafe_allow_html=True)
        st.markdown('<div class="terminal-stream">Analyst: Investigate the lateral movement pattern from the finance subnet.<br/>DcoY: Reasoning confirms a probable credential spray followed by persistence.<br/>Evidence: 7 matching detections, 3 unusual authentications, 1 suspicious admin login.<br/>Confidence: 0.95<br/>Recommendation: isolate, review MFA reset, and notify incident response<span class="cursor">|</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="bento-card"><div class="tiny-label">Reasoning</div><div class="big-number">Cognitive triage</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="bento-card" style="margin-top:0.8rem;"><div class="tiny-label">Evidence</div><div class="big-number">6 correlated alerts</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="bento-card" style="margin-top:0.8rem;"><div class="tiny-label">Confidence</div><div class="big-number">0.95</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="bento-card" style="margin-top:0.8rem;"><div class="tiny-label">MITRE mapping</div><div class="big-number">T1110 · T1059</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</section>', unsafe_allow_html=True)

    st.markdown('<section id="intel" class="marketing-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="tiny-label">Threat intelligence</div>', unsafe_allow_html=True)
    st.markdown('<h2 class="headline" style="font-size: clamp(1.8rem, 3vw, 2.6rem);">A living intelligence layer for active campaigns and emerging risk.</h2>', unsafe_allow_html=True)
    left, right = st.columns([1.1, 0.9])
    with left:
        st.markdown('<div class="terminal-stream">[10:41] Beaconing from new infrastructure<br/>[10:47] IOC enrichment matched a known intrusion set<br/>[10:52] MITRE ATT&CK link attached to initial access and credential access<span class="cursor">|</span></div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="bento-card"><div class="tiny-label">Coverage</div><div class="big-number">24 threat feeds</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="bento-card" style="margin-top:0.8rem;"><div class="tiny-label">Enrichment</div><div class="big-number">Real-time context</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</section>', unsafe_allow_html=True)

    st.markdown('<section id="hunting" class="marketing-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="tiny-label">Threat hunting</div>', unsafe_allow_html=True)
    st.markdown('<h2 class="headline" style="font-size: clamp(1.8rem, 3vw, 2.6rem);">Proactive hunting with behavioral insight and rapid pivoting.</h2>', unsafe_allow_html=True)
    hunt_cols = st.columns(3)
    for idx, item in enumerate([("Hypothesis", "Investigate unusual privileged access"), ("Pivot", "Resolve actor relationships across telemetry"), ("Action", "Escalate and contain")]):
        with hunt_cols[idx]:
            st.markdown(f'<div class="bento-card"><div class="tiny-label">{item[0]}</div><div class="big-number" style="font-size: 1.08rem; margin-top:0.3rem;">{item[1]}</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</section>', unsafe_allow_html=True)

    st.markdown('<section id="engineering" class="marketing-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="tiny-label">Detection engineering</div>', unsafe_allow_html=True)
    st.markdown('<h2 class="headline" style="font-size: clamp(1.8rem, 3vw, 2.6rem);">Treat detection quality as a product discipline.</h2>', unsafe_allow_html=True)
    eng_cols = st.columns(3)
    for idx, item in enumerate([("Rule tuning", "Improve signal fidelity"), ("Validation", "Reduce noise automatically"), ("Coverage", "Map detections to knowledge")]):
        with eng_cols[idx]:
            st.markdown(f'<div class="bento-card"><div class="tiny-label">{item[0]}</div><div class="big-number" style="font-size: 1.08rem; margin-top:0.3rem;">{item[1]}</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</section>', unsafe_allow_html=True)

    st.markdown('<section id="executive" class="marketing-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="tiny-label">Executive intelligence</div>', unsafe_allow_html=True)
    st.markdown('<h2 class="headline" style="font-size: clamp(1.8rem, 3vw, 2.6rem);">Executive-ready insights that bridge the SOC to the boardroom.</h2>', unsafe_allow_html=True)
    exec_cols = st.columns(4)
    for idx, item in enumerate([("Threat posture", "Stable"), ("Response efficiency", "3.4x faster"), ("Coverage gaps", "7"), ("Leadership reporting", "Instant")]):
        with exec_cols[idx]:
            st.markdown(f'<div class="bento-card"><div class="tiny-label">{item[0]}</div><div class="big-number" style="font-size: 1.08rem; margin-top:0.3rem;">{item[1]}</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</section>', unsafe_allow_html=True)

    st.markdown('<section id="workflow" class="marketing-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="tiny-label">SOC workflow</div>', unsafe_allow_html=True)
    st.markdown('<h2 class="headline" style="font-size: clamp(1.8rem, 3vw, 2.6rem);">An end-to-end operating rhythm from telemetry to response.</h2>', unsafe_allow_html=True)
    steps = ["Telemetry", "Detection", "Threat Hunting", "Investigation", "Executive Reporting", "Response"]
    step_html = "".join([f'<div class="flow-node">{step}</div>' for step in steps])
    st.markdown(f'<div style="display:grid; gap:0.75rem; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));">{step_html}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</section>', unsafe_allow_html=True)

    st.markdown('<section id="integrations" class="marketing-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="tiny-label">Integrations</div>', unsafe_allow_html=True)
    st.markdown('<h2 class="headline" style="font-size: clamp(1.8rem, 3vw, 2.6rem);">Deploy into your environment without breaking the stack.</h2>', unsafe_allow_html=True)
    integrations = ["Microsoft 365", "CrowdStrike", "Sentinel", "Splunk", "Okta", "ServiceNow", "Slack", "PagerDuty"]
    chips = "".join([f'<span class="metric-pill">{name}</span>' for name in integrations])
    st.markdown(f'<div style="display:flex; flex-wrap:wrap; gap:0.6rem;">{chips}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</section>', unsafe_allow_html=True)

    st.markdown('<section id="success" class="marketing-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="tiny-label">Customer success</div>', unsafe_allow_html=True)
    quotes = get_quotes()
    quote_cols = st.columns(2)
    for idx, quote in enumerate(quotes):
        with quote_cols[idx]:
            st.markdown(f'<div class="bento-card"><div style="font-size: 1rem; color: var(--text-primary); margin-bottom: 0.65rem;">“{quote["quote"]}”</div><div class="tiny-label">{quote["author"]}</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</section>', unsafe_allow_html=True)

    st.markdown('<section id="contact" class="marketing-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="tiny-label">Final CTA</div>', unsafe_allow_html=True)
    st.markdown('<h2 class="headline" style="font-size: clamp(1.8rem, 3vw, 2.6rem);">See how DcoY feels in your environment.</h2>', unsafe_allow_html=True)
    st.markdown('<p class="subcopy">Bring a premium AI-native security operations experience to your analysts, leadership, and responders.</p>', unsafe_allow_html=True)
    st.markdown('<div style="margin-top: 1rem;">', unsafe_allow_html=True)
    st.markdown('<a class="cta-link cta-primary" href="mailto:hello@dcoy.ai">Contact the team</a>', unsafe_allow_html=True)
    st.markdown('<a class="cta-link cta-secondary" href="?page=overview">Open live console</a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</section>', unsafe_allow_html=True)

    st.markdown('<footer style="padding: 1rem 0 2rem; color: var(--text-secondary); border-top: 1px solid var(--border-color);">', unsafe_allow_html=True)
    st.markdown('<div style="display:flex; flex-wrap:wrap; justify-content:space-between; gap:1rem; align-items:center;">', unsafe_allow_html=True)
    st.markdown('<div><strong style="color: var(--text-primary);">DcoY</strong> · AI-native Security Operations</div>', unsafe_allow_html=True)
    st.markdown('<div>hello@dcoy.ai · Enterprise-ready deployment · Trusted by modern SOC teams</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</footer>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
