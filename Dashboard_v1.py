import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime, timezone, timedelta

# Load data
df = pd.read_csv("Pipeline tool_Current.csv")

# Clean column names
df.columns = df.columns.str.strip()

# Clean string fields
fields_to_clean = ['field_1', 'field_2', 'field_4', 'field_6']
for field in fields_to_clean:
    if field in df.columns:
        df[field] = df[field].astype(str).str.strip()

# Parse deadline field to datetime
df['field_6'] = pd.to_datetime(df['field_6'], errors='coerce')

# Configure page
st.set_page_config(page_title="Pipeline Tool Dashboard", layout="wide")
st.title("📊 Interactive Pipeline Tool Dashboard")

# Sidebar filters
st.sidebar.header("🔎 Filter Options")

people = st.sidebar.multiselect("Responsible Person", sorted(df['field_2'].dropna().unique()))
countries = st.sidebar.multiselect("Country", sorted(df['field_4'].dropna().unique()))
statuses = st.sidebar.multiselect("Status", sorted(df['field_1'].dropna().unique()))

# Apply filters
filtered_df = df.copy()
if people:
    filtered_df = filtered_df[filtered_df['field_2'].isin(people)]
if countries:
    filtered_df = filtered_df[filtered_df['field_4'].isin(countries)]
if statuses:
    filtered_df = filtered_df[filtered_df['field_1'].isin(statuses)]

# Side-by-side Pie and Sunburst charts
st.subheader("📌 Status Distribution")
col1, col2 = st.columns(2)

with col1:
    pie_fig = px.pie(
        filtered_df,
        names='field_1',
        title="Pie Chart: Opportunities by Status",
        hole=0.4,
        labels={'field_1': 'Status'}
    )
    pie_fig.update_traces(hovertemplate="%{label}: %{value} opportunities")
    st.plotly_chart(pie_fig, use_container_width=True)

with col2:
    sunburst_fig = px.sunburst(
        filtered_df,
        path=['field_1', 'field_4'],  # You can add more like ['field_1', 'field_2'] if desired
        title="Sunburst Chart: Opportunities by Status",
        labels={'field_1': 'Status'}
    )
    sunburst_fig.update_traces(
        hovertemplate="<b>Status:</b> %{label}<br><b>Count:</b> %{value}",
        insidetextorientation='radial'
    )
    sunburst_fig.update_layout(margin=dict(t=40, l=10, r=10, b=10))
    st.plotly_chart(sunburst_fig, use_container_width=True)


# Bar chart: Opportunities by country
st.subheader("🌍 Opportunities by Country")
country_counts = filtered_df['field_4'].value_counts().reset_index()
country_counts.columns = ['Country', 'Count']

if not country_counts.empty:
    bar_fig = px.bar(
        country_counts,
        x='Country',
        y='Count',
        title="Number of Opportunities per Country",
        text='Count',
        labels={'Country': 'Country', 'Count': 'Number of Opportunities'}
    )
    bar_fig.update_traces(textposition='outside')
    st.plotly_chart(bar_fig, use_container_width=True)
else:
    st.warning("No data to display for bar chart.")

# Deadline timeline: next 7 days
st.subheader("📅 Deadlines Approaching in the Next 7 Days")
today = datetime.now(timezone.utc)

upcoming_deadline_df = filtered_df[
    (filtered_df['field_6'].notna()) &
    (filtered_df['field_6'] >= today) &
    (filtered_df['field_6'] <= today + timedelta(days=7))
][['Title', 'field_6']].sort_values('field_6')

# Format date and rename columns
upcoming_deadline_df['field_6'] = upcoming_deadline_df['field_6'].dt.strftime('%Y-%m-%d')
upcoming_deadline_df.columns = ['Opportunity Title', 'Deadline']

# Display deadline table
if not upcoming_deadline_df.empty:
    st.dataframe(upcoming_deadline_df.reset_index(drop=True), use_container_width=True)
else:
    st.info("No opportunities with deadlines in the next 7 days.")
