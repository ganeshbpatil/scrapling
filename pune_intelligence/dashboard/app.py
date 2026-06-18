import json, os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Pune Property Market Intelligence", layout="wide", page_icon="📊")
st.title("📊 Pune Real Estate — Market Intelligence Dashboard")

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output/intelligence")
SIGNALS_FILE = os.path.join(OUTPUT_DIR, "signals.json")
REPORT_FILE  = os.path.join(OUTPUT_DIR, "daily_report.json")

@st.cache_data(ttl=60)
def load_signals():
    if not os.path.exists(SIGNALS_FILE):
        return []
    with open(SIGNALS_FILE) as f:
        return json.load(f)

@st.cache_data(ttl=60)
def load_report():
    if not os.path.exists(REPORT_FILE):
        return {}
    with open(REPORT_FILE) as f:
        data = json.load(f)
    return data[-1] if isinstance(data, list) and data else (data or {})

signals = load_signals()
report  = load_report()

if not signals and not report:
    st.warning("No intelligence data yet. Run: `python intelligence.py collect`")
    st.code("python intelligence.py collect\npython intelligence.py collect --demo")
    st.stop()

# ── KPI Row ──────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Signals", len(signals))
k2.metric("Today's Signals", len([s for s in signals if s.get("collected_at","").startswith(datetime.now().strftime("%Y-%m-%d"))]))
k3.metric("Sources Active", len({s.get("source") for s in signals}))
hot = report.get("hot_markets", [{}])
k4.metric("Hottest Market", hot[0].get("micro_market", "—") if hot else "—")
top_cfg = report.get("config_demand", [{}])
k5.metric("Top Configuration", top_cfg[0].get("configuration", "—") if top_cfg else "—")

st.divider()
tabs = st.tabs(["🏘️ Micro-Market Demand", "🔍 Search Trends", "🏢 Competitor Intelligence", "💡 Recommendations", "📰 Signal Feed"])

# ── Tab 1: Micro-Market Demand ────────────────────────────────────────────
with tabs[0]:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Market Demand Ranking")
        demand = report.get("market_demand_rank", [])
        if demand:
            df_d = pd.DataFrame(demand)
            fig = px.bar(df_d, x="micro_market", y="demand_score",
                         color="sentiment_score",
                         color_continuous_scale=["red","yellow","green"],
                         labels={"demand_score": "Demand Score", "micro_market": "Area"})
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No market demand data yet.")

    with col2:
        st.subheader("Sentiment by Area")
        if demand:
            df_s = pd.DataFrame(demand).head(10)
            fig2 = go.Figure(data=[
                go.Bar(name="Positive", x=df_s["micro_market"], y=df_s["positive_mentions"], marker_color="green"),
                go.Bar(name="Negative", x=df_s["micro_market"], y=df_s["negative_mentions"], marker_color="red"),
            ])
            fig2.update_layout(barmode="group", xaxis_tickangle=-45)
            st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Configuration Demand")
    cfg = report.get("config_demand", [])
    if cfg:
        df_c = pd.DataFrame(cfg)
        st.plotly_chart(px.pie(df_c, names="configuration", values="mentions", hole=0.4), use_container_width=True)

# ── Tab 2: Search Trends ─────────────────────────────────────────────────
with tabs[1]:
    st.subheader("Daily Signal Volume")
    daily = report.get("daily_trend", [])
    if daily:
        df_dt = pd.DataFrame(daily)
        st.plotly_chart(px.line(df_dt, x="date", y="signals", markers=True,
                                title="Signals Collected Per Day"), use_container_width=True)
    else:
        st.info("Collect data daily to see trend lines.")

    st.subheader("Intent Breakdown")
    intent = report.get("intent_breakdown", {})
    if intent:
        df_i = pd.DataFrame([{"intent": k, "count": v["count"], "pct": v["pct"]} for k, v in intent.items()])
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(px.bar(df_i, x="intent", y="count", color="intent"), use_container_width=True)
        with c2:
            st.plotly_chart(px.pie(df_i, names="intent", values="count"), use_container_width=True)

    st.subheader("Signal Sources")
    src = report.get("source_breakdown", {})
    if src:
        df_src = pd.DataFrame([{"source": k, "count": v} for k, v in src.items()])
        st.plotly_chart(px.bar(df_src, x="source", y="count", color="source"), use_container_width=True)

# ── Tab 3: Competitor Intelligence ───────────────────────────────────────
with tabs[2]:
    st.subheader("Share of Voice")
    comps = report.get("competitor_share_of_voice", [])
    if comps:
        df_comp = pd.DataFrame(comps)
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(px.bar(df_comp.head(10), x="competitor", y="share_of_voice_pct",
                                   color="net_sentiment",
                                   color_discrete_map={"positive":"green","negative":"red"},
                                   title="Share of Voice (%)"), use_container_width=True)
        with c2:
            st.plotly_chart(go.Figure(data=[
                go.Bar(name="Positive", x=df_comp["competitor"][:10], y=df_comp["positive"][:10], marker_color="green"),
                go.Bar(name="Negative", x=df_comp["competitor"][:10], y=df_comp["negative"][:10], marker_color="red"),
            ]).update_layout(barmode="group", title="Sentiment Split"), use_container_width=True)
        st.dataframe(df_comp, use_container_width=True)
    else:
        st.info("No competitor mentions found yet.")

# ── Tab 4: Recommendations ────────────────────────────────────────────────
with tabs[3]:
    st.subheader("💡 AI-Powered Recommendations")
    recs = report.get("recommendations", [])
    if recs:
        for rec in recs:
            priority_color = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(rec.get("priority",""), "⚪")
            with st.expander(f"{priority_color} [{rec.get('type','').upper()}] {rec.get('title','')}"):
                st.write(rec.get("detail",""))
                st.info(f"**Action:** {rec.get('action','')}")
    else:
        st.info("Collect more data to generate recommendations.")

# ── Tab 5: Signal Feed ────────────────────────────────────────────────────
with tabs[4]:
    st.subheader("📰 Live Signal Feed")
    if signals:
        df_sig = pd.DataFrame(signals)
        # Filters
        fc1, fc2, fc3 = st.columns(3)
        sources = ["All"] + sorted(df_sig["source"].dropna().unique().tolist())
        intents = ["All"] + sorted(df_sig.get("intent", pd.Series()).dropna().unique().tolist()) if "intent" in df_sig else ["All"]
        sel_src = fc1.selectbox("Source", sources)
        sel_int = fc2.selectbox("Intent", intents)
        sel_sent = fc3.selectbox("Sentiment", ["All", "positive", "negative", "neutral"])

        fdf = df_sig.copy()
        if sel_src != "All": fdf = fdf[fdf["source"] == sel_src]
        if sel_int != "All" and "intent" in fdf: fdf = fdf[fdf["intent"] == sel_int]
        if sel_sent != "All" and "sentiment" in fdf: fdf = fdf[fdf["sentiment"] == sel_sent]

        show = ["source","title","micro_markets","intent","sentiment","collected_at"]
        st.dataframe(fdf[[c for c in show if c in fdf.columns]].head(200), use_container_width=True)
    else:
        st.info("No signals collected yet.")
