import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time

# 1. Configure the WebApp Layout
st.set_page_config(page_title="UNU Macau 2026: Agentic Orchestration", layout="wide")

st.title("UNU Macau 2026: Shared Capacity Command Center")
st.markdown("### Interactive Prototype: Overcoming the Stubborn Planner Bottleneck")
st.markdown("This live simulation demonstrates how dynamic state interrupts save GPU resources during human-in-the-loop workflows.")
st.divider()

# 2. Initialize Session State (To track the live simulation)
if 'step' not in st.session_state:
    st.session_state.step = 2  # Start at the blocked state
    # Initial data representing the Agent falling into the loop trap
    st.session_state.telemetry = [
        {"step": 1, "layer": "Agent Layer (Non-Det)", "status": "Loop Trap", "cum_tokens": 1600, "cum_time_sec": 1.55},
        {"step": 2, "layer": "Sensor Layer (Det)", "status": "Blocked", "cum_tokens": 1850, "cum_time_sec": 1.85}
    ]

df = pd.DataFrame(st.session_state.telemetry)

# 3. Top KPI Metric Cards
st.subheader("System State Diagnostics: Live Remote Context")
col1, col2, col3 = st.columns(3)

max_tokens = int(df['cum_tokens'].max())
max_latency = float(df['cum_time_sec'].max())
current_status = df['status'].iloc[-1]

# Dynamic color coding for status
status_color = "normal" if current_status == "Resolved" else "inverse"

col1.metric(label="Total Token Draw", value=f"{max_tokens} Tokens", delta="0 Tokens (During Pause)" if st.session_state.step >= 3 else None)
col2.metric(label="Total Latency Horizon", value=f"{max_latency:.2f} s")
col3.metric(label="System Status", value=current_status, delta="Requires Intervention" if st.session_state.step == 2 else "Compliant", delta_color=status_color)

st.divider()

# 4. Interactive Layout: Chart on Left, Staging Area on Right
left_col, right_col = st.columns([3, 2])

with left_col:
    st.subheader("Real-Time Performance Telemetry")
    
    fig = go.Figure()

    # Add Token Overhead Line
    fig.add_trace(go.Scatter(
        x=df['step'], y=df['cum_tokens'],
        name="Cumulative Tokens", mode='lines+markers',
        line=dict(color='#2c3e50', width=3), marker=dict(size=10)
    ))

    # Add Latency Horizon Line on Secondary Y-Axis
    fig.add_trace(go.Scatter(
        x=df['step'], y=df['cum_time_sec'],
        name="Cumulative Latency (s)", mode='lines+markers', yaxis="y2",
        line=dict(color='#e74c3c', width=3, dash='dash'), marker=dict(size=10, symbol='square')
    ))

    # Configure Dual Axis and Interrupt Boundary
    fig.update_layout(
        xaxis=dict(title=dict(text="Workflow Steps (Meso-Level)"), tickmode='linear', range=[0.8, 4.2]),
        yaxis=dict(title=dict(text="Token Consumption (Counts)", font=dict(color="#2c3e50")), tickfont=dict(color="#2c3e50"), range=[1000, 2500]),
        yaxis2=dict(title=dict(text="Processing Latency (Seconds)", font=dict(color="#e74c3c")), tickfont=dict(color="#e74c3c"), anchor="x", overlaying="y", side="right", range=[0, 8]),
        legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.8)'),
        height=450,
        margin=dict(l=20, r=20, t=30, b=20)
    )

    # Draw the boundary only if we have reached or passed it
    if st.session_state.step >= 2:
        fig.add_shape(type="line", x0=3, x1=3, y0=0, y1=1, xref="x", yref="paper", line=dict(color="gray", width=2, dash="dot"))
        fig.add_annotation(x=3.1, y=0.1, xref="x", yref="paper", text="Human Override Boundary", showarrow=False, font=dict(color="gray"))

    st.plotly_chart(fig, use_container_width=True)

with right_col:
    st.subheader("Interactive Staging Area (AG-UI)")
    
    if st.session_state.step == 2:
        st.error("⚠️ **CRITICAL ALARM:** Banned Port `9999` invocation detected. System paused to prevent token drain.")
        st.info("The agent's state has been serialized to the database. GPU resources are currently disconnected (Zero Token Draw).")
        
        with st.form("intervention_form"):
            st.markdown("**Review Proposed Payload:**")
            st.code("initialize_mcp_channel(gateway_port=9999)")
            
            # Interactive Input for the User
            new_port = st.number_input("Modify Gateway Port (Hint: Authorized port is 5432):", value=9999, step=1)
            
            submit_override = st.form_submit_button("Approve Override & Resume Workflow", type="primary")
            
            if submit_override:
                if new_port == 9999:
                    st.warning("You must change the port to a compliant value before resuming.")
                else:
                    # Simulate Human Intervention (Step 3)
                    st.session_state.telemetry.append({
                        "step": 3, "layer": "Human UI Layer", "status": "Overridden", 
                        "cum_tokens": 1850, # Token consumption is FROZEN
                        "cum_time_sec": 6.85 # Simulated human thought time
                    })
                    # Simulate Final Resolution (Step 4)
                    st.session_state.telemetry.append({
                        "step": 4, "layer": "Sensor Layer (Det)", "status": "Resolved", 
                        "cum_tokens": 2100, 
                        "cum_time_sec": 6.97
                    })
                    st.session_state.step = 4
                    st.rerun()
                    
    elif st.session_state.step == 4:
        st.success("✨ **COMPLIANCE SUCCESS:** Session initialized securely on authorized Port 5432.")
        st.markdown("**Executed Payload:**")
        st.code("initialize_mcp_channel(gateway_port=5432) # Verified by Operator")
        
        st.markdown("""
        **Outcome Analysis:**
        Notice the flat dark line between Step 2 and Step 3 on the chart. While the system waited for your input, it consumed **0 additional tokens**.
        """)
        
        if st.button("Reset Simulation", icon="🔄"):
            st.session_state.step = 2
            st.session_state.telemetry = st.session_state.telemetry[:2]
            st.rerun()

# 5. Granular Data Table
st.subheader("Raw Event Logs (CHAP Protocol Auditing)")
st.dataframe(df, use_container_width=True)
