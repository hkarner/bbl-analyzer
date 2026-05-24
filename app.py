import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="BBL Attendance Analyzer", layout="wide")
st.title("🧬 BBL Event Attendance Analyzer")
st.caption("All data is anonymized. No attendee names are stored or displayed.")

# --- File upload ---
uploaded = st.file_uploader("Upload your cleaned CSV", type="csv")
if not uploaded:
    st.info("Upload `bbl_attendance_clean.csv` to get started.")
    st.stop()

df = pd.read_csv(uploaded)

# --- Sidebar filters ---
st.sidebar.header("Filters")
events = st.sidebar.multiselect("Events", df["event_name"].unique(), default=df["event_name"].unique())
df = df[df["event_name"].isin(events)]

# --- Summary metrics ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total attendances", len(df))
col2.metric("Unique attendees", df["attendee_id"].nunique())
col3.metric("Events", df["event_name"].nunique())

# Repeat attendees = IDs seen at more than one event
repeat_ids = df.groupby("attendee_id")["event_name"].nunique()
col4.metric("Repeat attendees", int((repeat_ids > 1).sum()))

st.divider()

# --- Chart 1: Attendance by event ---
st.subheader("Attendance by Event")
event_counts = df.groupby("event_name").size().reset_index(name="count")
fig1 = px.bar(event_counts, x="event_name", y="count", color="count",
              color_continuous_scale="teal", labels={"event_name": "Event", "count": "Attendees"})
st.plotly_chart(fig1, use_container_width=True)

# --- Chart 2: Career stage breakdown ---
if "career_stage" in df.columns:
    st.subheader("Career Stage Breakdown")
    stage_counts = df["career_stage"].value_counts().reset_index()
    stage_counts.columns = ["career_stage", "count"]
    fig2 = px.pie(stage_counts, names="career_stage", values="count", hole=0.4)
    st.plotly_chart(fig2, use_container_width=True)

# --- Chart 3: Location breakdown ---
if "location" in df.columns:
    st.subheader("Top Locations / Institutions")
    loc_counts = df["location"].value_counts().head(15).reset_index()
    loc_counts.columns = ["location", "count"]
    fig3 = px.bar(loc_counts, x="count", y="location", orientation="h",
                  color="count", color_continuous_scale="teal")
    fig3.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig3, use_container_width=True)


# --- Chart 4: Repeat vs. first-time ---
st.subheader("Repeat vs. First-Time Attendees")
attendee_event_count = df.groupby("attendee_id")["event_name"].nunique()
df["attendee_type"] = df["attendee_id"].map(
    lambda x: "Repeat" if attendee_event_count.get(x, 1) > 1 else "First-time"
)
type_counts = df["attendee_type"].value_counts().reset_index()
type_counts.columns = ["type", "count"]
fig4 = px.pie(type_counts, names="type", values="count", hole=0.4,
              color_discrete_sequence=["#2ec4b6", "#e9c46a"])
st.plotly_chart(fig4, use_container_width=True)

# --- Export ---
st.divider()
st.subheader("Export")
st.download_button("Download filtered data as CSV",
                   df.to_csv(index=False),
                   file_name="bbl_filtered.csv",
                   mime="text/csv")