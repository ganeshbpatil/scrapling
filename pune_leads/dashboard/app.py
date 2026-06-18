import json, os
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Pune Real Estate Lead Intelligence", layout="wide")
st.title("🏠 Pune Real Estate Lead Intelligence Dashboard")

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
LEADS_FILE = os.path.join(OUTPUT_DIR, "leads.json")

@st.cache_data(ttl=30)
def load_leads():
    if not os.path.exists(LEADS_FILE):
        return pd.DataFrame()
    with open(LEADS_FILE) as f:
        data = json.load(f)
    return pd.DataFrame(data)

df = load_leads()

if df.empty:
    st.warning("No leads found. Run the spider first: `python main.py spider --all`")
    st.stop()

st.sidebar.header("Filters")
def sidebar_select(label, col):
    opts = ["All"] + sorted(df[col].dropna().unique().tolist()) if col in df else ["All"]
    return st.sidebar.selectbox(label, opts)

sel_source = sidebar_select("Lead Source", "lead_source")
sel_config = sidebar_select("Configuration", "configuration")
sel_location = sidebar_select("Location", "location_interest")

fdf = df.copy()
if sel_source != "All":
    fdf = fdf[fdf["lead_source"] == sel_source]
if sel_config != "All":
    fdf = fdf[fdf["configuration"] == sel_config]
if sel_location != "All":
    fdf = fdf[fdf["location_interest"] == sel_location]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Leads", len(fdf))
c2.metric("Avg Confidence", f"{fdf['confidence_score'].mean():.0f}" if "confidence_score" in fdf.columns and not fdf.empty else "—")
c3.metric("Top Location", fdf["location_interest"].mode()[0] if "location_interest" in fdf.columns and not fdf.empty else "—")
c4.metric("Top Config", fdf["configuration"].mode()[0] if "configuration" in fdf.columns and not fdf.empty else "—")

st.divider()
r1c1, r1c2 = st.columns(2)
with r1c1:
    st.subheader("Leads by Configuration")
    d = fdf["configuration"].value_counts().reset_index()
    d.columns = ["Configuration", "Count"]
    st.plotly_chart(px.bar(d, x="Configuration", y="Count", color="Configuration"), use_container_width=True)

with r1c2:
    st.subheader("Leads by Area (Top 10)")
    d = fdf["location_interest"].value_counts().head(10).reset_index()
    d.columns = ["Location", "Count"]
    st.plotly_chart(px.bar(d, x="Location", y="Count", color="Location"), use_container_width=True)

r2c1, r2c2 = st.columns(2)
with r2c1:
    st.subheader("Leads by Source")
    d = fdf["lead_source"].value_counts().reset_index()
    d.columns = ["Source", "Count"]
    st.plotly_chart(px.pie(d, names="Source", values="Count"), use_container_width=True)

with r2c2:
    st.subheader("Lead Intent")
    d = fdf["intent"].value_counts().reset_index()
    d.columns = ["Intent", "Count"]
    st.plotly_chart(px.bar(d, x="Intent", y="Count", color="Intent"), use_container_width=True)

st.divider()
st.subheader("Lead Data Table")
show_cols = ["name", "phone", "email", "configuration", "location_interest",
             "budget", "lead_source", "lead_date", "intent", "confidence_score"]
st.dataframe(fdf[[c for c in show_cols if c in fdf.columns]], use_container_width=True)
