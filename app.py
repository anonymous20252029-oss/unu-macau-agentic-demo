import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Configure the WebApp Layout
st.set_page_config(page_title="UNU Macau 2026: Agentic Orchestration", layout="wide")

st.title("UNU Macau 2026: Shared Capacity Command Center")
st.markdown("### Interactive Telemetry Dashboard: Overcoming the Stubborn Planner Bottleneck")
st.markdown("This dashboard ingests telemetry from the **comparative_benchmarking_dataset.csv** to demonstrate how dynamic state interrupts save GPU resources during human-in-the-loop workflows.")
st.divider()

# 2. Load the Dataset
@st.cache_data
def load_data():
    # Reading the exact file generated from the Colab pipeline
    df = pd.read_csv("comparative_benchmarking_dataset.csv")
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("Error: 'comparative_benchmarking_dataset.csv' not found. Please ensure the file is uploaded to the repository.")
    st.stop()

# 3. Sidebar Configuration
st.sidebar.header("System Controls")
dataset_choice = st.sidebar.radio("Select Active Knowledge Context:", df['dataset'].unique())
filtered_df = df[df['dataset'] == dataset_choice]

# 4. Top KPI Metric Cards
st.subheader(f"System State Diagnostics: {dataset_choice}")
col1, col2, col3 = st.columns(3)

max_tokens = int(filtered_df['cum_tokens'].max())
max_latency = float(filtered_df['cum_time_sec'].max())

col1.metric(label="Total Token Draw", value=f"{max_tokens} Tokens", delta="0 Tokens (During Interruption)", delta_color="inverse")
col2.metric(label="Total Latency Horizon", value=f"{max_latency} s")
col3.metric(label="System Status", value="Resolved & Compliant")

st.divider()

# 5. Interactive Dual-Axis Telemetry Plot
st.subheader("Interactive Performance Telemetry")

fig = go.Figure()

# Add Token Overhead Line
fig.add_trace(go.Scatter(
    x=filtered_df['step'], 
    y=filtered_df['cum_tokens'],
    name="Cumulative Tokens",
    mode='lines+markers',
    line=dict(color='#2c3e50', width=3),
    marker=dict(size=10)
))

# Add Latency Horizon Line on Secondary Y-Axis
fig.add_trace(go.Scatter(
    x=filtered_df['step'], 
    y=filtered_df['cum_time_sec'],
    name="Cumulative Latency (s)",
    mode='lines+markers',
    yaxis="y2",
    line=dict(color='#e74c3c', width=3, dash='dash'),
    marker=dict(size=10, symbol='square')
))

# Configure Dual Axis and Interrupt Boundary
fig.update_layout(
    xaxis=dict(
        title=dict(text="Workflow Steps (Meso-Level)"), 
        tickmode='linear'
    ),
    yaxis=dict(
        title=dict(text="Token Consumption (Counts)", font=dict(color="#2c3e50")), 
        tickfont=dict(color="#2c3e50")
    ),
    yaxis2=dict(
        title=dict(text="Processing Latency (Seconds)", font=dict(color="#e74c3c")), 
        tickfont=dict(color="#e74c3c"), 
        anchor="x", 
        overlaying="y", 
        side="right"
    ),
    legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.8)'),
    shapes=[
        # Vertical Line indicating Human Intervention
        dict(type="line", x0=3, x1=3, y0=0, y1=1, xref="x", yref="paper", line=dict(color="gray", width=2, dash="dot"))
    ],
    annotations=[
        dict(x=3.1, y=0.1, xref="x", yref="paper", text="Human Override Boundary", showarrow=False, font=dict(color="gray"))
    ]
)

st.plotly_chart(fig, use_container_width=True)

# 6. Granular Data Table
st.subheader("Raw Event Logs (CHAP Protocol Auditing)")
st.dataframe(filtered_df[['step', 'layer', 'status', 'tokens', 'cum_tokens', 'cum_time_sec']], use_container_width=True)
